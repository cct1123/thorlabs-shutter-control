"""KSC101 shutter control and hub cleanup through the official Kinesis .NET API.

State is controller-reported feedback, never independent optical verification.
No device is connected or enabled when this module is imported.
"""

from __future__ import annotations

import math
import os
import re
import sys
import time
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from ipaddress import IPv4Address
from pathlib import Path
from threading import RLock
from types import SimpleNamespace

from . import config


class ShutterError(RuntimeError):
    """An operation failed; the message includes its context and original error."""


def _normalize_serial(serial: str | int | None) -> str | None:
    if isinstance(serial, int) and not isinstance(serial, bool):
        serial = str(serial)
    if serial is not None and (
        not isinstance(serial, str) or not re.fullmatch(r"68[0-9]{6}", serial)
    ):
        raise ValueError(
            "KSC101 serial number must be eight digits beginning with 68, as a string or integer."
        )
    return serial


@dataclass(frozen=True)
class TriggerConfig:
    """TRIG1/TRIG2 direction and active polarity; construction never writes hardware."""

    trig1_mode: str = "input"
    trig1_polarity: str = "high"
    trig2_mode: str = "output"
    trig2_polarity: str = "high"

    def __post_init__(self):
        for port in (1, 2):
            if getattr(self, f"trig{port}_mode") not in ("disabled", "input", "output"):
                raise ValueError("Trigger mode must be disabled, input or output.")
            if getattr(self, f"trig{port}_polarity") not in ("high", "low"):
                raise ValueError("Trigger polarity must be high or low.")


@dataclass(frozen=True)
class LanDevice:
    serial_number: str
    endpoint: str


@dataclass(frozen=True)
class LanDiscovery:
    hub_addresses: tuple[str, ...]
    controllers: tuple[LanDevice, ...]


@dataclass(frozen=True)
class ShutterStatus:
    connection: str = "disconnected"
    has_device: bool = False
    serial_number: str | None = None
    description: str | None = None
    shutter_state: str = "unknown"
    operating_state: str = "unknown"
    operating_mode: str = "unknown"
    key_enabled: bool | None = None
    interlock_enabled: bool | None = None
    trigger_config: TriggerConfig | None = None
    error: str | None = None
    status_bits: int | None = None
    operator_interlock_confirmed: bool = False

    @property
    def interlock_ready(self) -> bool:
        """Informational metadata: reported enabled or explicitly operator-verified.

        A known negative report is never overridden. This is readiness evidence,
        not a command to alter the hardware interlock. Project operations do not
        gate on this property; users manage the physical circuit externally.
        """
        return self.connection == "connected" and (
            self.interlock_enabled is True
            or (self.interlock_enabled is None and self.operator_interlock_confirmed)
        )

    @property
    def is_closed_manual(self) -> bool:
        """Whether this observation establishes the manual operating baseline."""
        return (
            self.connection == "connected"
            and self.shutter_state == "closed"
            and self.operating_state == "inactive"
            and self.operating_mode == "manual"
        )

    @property
    def ttl_armed(self) -> bool | None:
        """Reported Triggered/Active means primed, regardless of shutter position."""
        if self.connection != "connected":
            return None
        if self.operating_mode == "triggered" and self.operating_state == "active":
            return True
        if self.operating_mode == "manual" or self.operating_state == "inactive":
            return False
        return None


_sdk_lock = RLock()
_loaded_sdk = None
# Keep owners alive until their SDK handles have actually been released. A failed
# disconnect must not let another controller open a competing handle to that cube.
_device_owners: dict[str, _KinesisShutter] = {}


def _load_sdk(directory: str | Path | None):
    """Load one Kinesis installation per process, retaining native DLL search paths."""
    global _loaded_sdk
    if sys.platform != "win32":
        raise ShutterError("The Kinesis hardware backend requires Windows.")
    if directory is None:
        directory = config.KINESIS_DIR
    path = Path(directory).expanduser().resolve()
    names = ("DeviceManagerCLI", "GenericMotorCLI", "KCube.SolenoidCLI")
    files = [path / f"Thorlabs.MotionControl.{name}.dll" for name in names]
    with _sdk_lock:
        if _loaded_sdk is not None:
            if _loaded_sdk.directory != path:
                raise ShutterError("Restart Python before selecting another Kinesis installation.")
            return _loaded_sdk
        missing = [f.name for f in files if not f.is_file()]
        if missing:
            raise ShutterError(
                f"Kinesis SDK not found in {path}. Install Kinesis matching Python's bitness "
                "or edit KINESIS_DIR in config.py (or pass kinesis_dir in Python). Missing: "
                + ", ".join(missing)
            )
        dll_handle = os.add_dll_directory(str(path))
        # Mixed-mode .NET assemblies also resolve dependencies through PATH/sys.path.
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(path) + os.pathsep + old_path
        sys.path.append(str(path))
        try:
            import pythonnet

            pythonnet.load("netfx")
            import clr

            for file in files:
                clr.AddReference(str(file))
            from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
            from Thorlabs.MotionControl.KCube.SolenoidCLI import (
                KCubeSolenoid,
                SolenoidStatus,
                TriggerConfigSettings,
            )

            _loaded_sdk = SimpleNamespace(
                manager=DeviceManagerCLI,
                device_type=KCubeSolenoid,
                enums=SolenoidStatus,
                trigger_settings=TriggerConfigSettings,
                directory=path,
                dll_handle=dll_handle,
            )
        except Exception as exc:
            dll_handle.close()
            sys.path.remove(str(path))
            os.environ["PATH"] = old_path
            raise ShutterError(
                "Cannot load Kinesis. Check matching Python/SDK bitness, .NET Framework "
                f"and vendor runtime dependencies; restart after correcting them: {exc}"
            ) from exc
        return _loaded_sdk


class _KinesisShutter:
    """Shared Kinesis commands, feedback and exclusive serial ownership.

    Calls on this object are serialized; separate serials have separate handles.
    Shared SDK enumeration and handle creation are serialized across controllers.
    Other processes must still be excluded by the operator.

    Setters send commands and return None: no feedback requests, sleeps or
    verification. Getters explicitly request feedback. Callers own sequencing
    and readiness checks; command completion is not proof of physical state.
    connect() verifies identity only. Shutdown requests Close then releases.
    """

    def __init__(
        self,
        serial_number: str | int | None = None,
        *,
        kinesis_dir: str | Path | None = None,
        timeout: float = 5.0,
        polling_ms: int = 250,
    ):
        self._lock = RLock()
        self._device = None
        self.serial_number = serial_number
        if not math.isfinite(timeout) or not 0.5 <= timeout <= 60:
            raise ValueError("timeout must be finite and between 0.5 and 60 seconds.")
        if isinstance(polling_ms, bool) or not isinstance(polling_ms, int):
            raise ValueError("polling_ms must be an integer.")
        if not 100 <= polling_ms <= 1000 or timeout < 2 * polling_ms / 1000:
            raise ValueError("polling_ms must be 100..1000 and timeout at least two polls.")
        self.kinesis_dir = kinesis_dir
        self.timeout = timeout
        self.polling_ms = polling_ms
        self._sdk = None
        self._description = None
        self._fault = None
        self._last_status = None
        self._claimed_serial = None

    @property
    def serial_number(self) -> str | None:
        return self._serial_number

    @serial_number.setter
    def serial_number(self, serial: str | int | None) -> None:
        with self._lock:
            serial = _normalize_serial(serial)
            if self._device is not None and serial != self._serial_number:
                raise ShutterError("Disconnect before selecting another device.")
            if serial != getattr(self, "_serial_number", None):
                self._operator_verified_serial = None
            self._serial_number = serial

    def confirm_interlock(self, serial: str | int) -> None:
        """Record explicit physical interlock verification for this selected serial.

        Call before connection only after the operator confirms the normal circuit
        and independent protection. No device command or persistent setting; the
        confirmation belongs to this object/serial and clears on retargeting.
        """
        with self._lock:
            serial = _normalize_serial(serial)
            if serial is None or serial != self.serial_number:
                raise ValueError("Interlock confirmation requires the selected explicit serial.")
            if self._device is not None:
                raise ShutterError("Disconnect before changing interlock confirmation.")
            self._operator_verified_serial = serial

    def connect(self, serial_number: str | int | None = None) -> ShutterStatus:
        """Connect the selected device, or the only discovered KSC101. No output write."""
        with self._lock:
            if serial_number is not None:
                try:
                    self.serial_number = serial_number
                except ValueError as exc:
                    raise ShutterError(
                        "Select an eight-digit KSC101 serial number beginning with 68."
                    ) from exc
            if self._device is not None:
                if self._fault:
                    raise ShutterError(self._fault)
                return self.get_cached_status()
            serials = self.discover()
            if self.serial_number is None:
                if len(serials) != 1:
                    raise ShutterError(
                        f"Expected one KSC101; found {len(serials)}. "
                        "Connect a device or explicitly select its serial number."
                    )
                self.serial_number = serials[0]
            if self.serial_number not in serials:
                raise ShutterError(f"KSC101 {self.serial_number} was not discovered.")
            with _sdk_lock:
                owner = _device_owners.get(self.serial_number)
                if owner is not None and owner is not self:
                    raise ShutterError(
                        f"KSC101 {self.serial_number} is already owned by another controller "
                        "in this process. Disconnect it before connecting again."
                    )
                _device_owners[self.serial_number] = self
                self._claimed_serial = self.serial_number
            self._fault = None
            try:
                with _sdk_lock:
                    if not self._matches_transport(self.serial_number):
                        raise ShutterError("Selected transport changed; refusing connection.")
                    self._device = self._sdk.device_type.CreateKCubeSolenoid(self.serial_number)
                if self._device is None:
                    raise ShutterError("Kinesis could not create the selected device.")
                self._device.Connect(self.serial_number)
                if not self._device.IsSettingsInitialized():
                    self._device.WaitForSettingsInitialized(int(self.timeout * 1000))
                if not self._device.IsSettingsInitialized():
                    raise ShutterError("Device settings did not initialize before the timeout.")
                self._device.StartPolling(self.polling_ms)
                if self._device.PollingDuration() <= 0:
                    raise ShutterError("Kinesis did not start status polling.")
                info = self._device.GetDeviceInfo()
                if str(info.SerialNumberText) != self.serial_number:
                    raise ShutterError(
                        f"Device identity mismatch: selected {self.serial_number}; "
                        f"connected {info.SerialNumberText}."
                    )
                self._description = str(info.Description)
                self._check_connection()
                self._last_status = None
                return self.get_cached_status()
            except BaseException as exc:
                errors, interrupted = self._release()
                self._fault = f"Connect failed: {str(exc) or type(exc).__name__}" + (
                    f"; cleanup: {'; '.join(errors)}" if errors else ""
                )
                if not isinstance(exc, Exception):
                    exc.add_note(self._fault)
                    raise
                if interrupted is not None:
                    interrupted.add_note(self._fault)
                    raise interrupted from exc
                raise ShutterError(self._fault) from exc

    def identify_device(self) -> dict[str, str]:
        """Read identity (does not invoke Kinesis IdentifyDevice's display flashing)."""
        with self._lock:
            with self._command("Read identity", reading=True):
                self._check_connection()
                info = self._device.GetDeviceInfo()
                return {
                    "serial_number": str(info.SerialNumberText),
                    "description": str(info.Description),
                }

    def _check_connection(self):
        if self._device is None:
            raise ShutterError("No device connected.")
        self._check_transport()
        comms_status = str(self._device.CommsStatus)
        if comms_status != "OK":
            raise ShutterError(f"Kinesis communication status: {comms_status}.")

    def _read_status(self, *, include_triggers: bool = True) -> ShutterStatus:
        self._check_connection()
        self._device.RequestStatus()
        self._device.RequestOperatingMode()
        self._device.RequestOperatingState()
        # Read operating feedback after the settings wait, rather than holding
        # key/interlock/state values sampled before that delay.
        config = self._read_trigger_config() if include_triggers else None
        if not include_triggers:
            time.sleep(self.polling_ms / 1000)
        bits = int(self._device.GetStatusBits())
        state = str(self._device.GetSolenoidState()).lower()
        operation = str(self._device.GetOperatingState()).lower()
        mode = str(self._device.GetOperatingMode()).lower()
        mode = {"singletoggle": "single", "autotoggle": "auto"}.get(mode, mode)
        operation = operation if operation in ("active", "inactive") else "unknown"
        mode = mode if mode in ("manual", "single", "auto", "triggered") else "unknown"
        status = ShutterStatus(
            connection="connected",
            has_device=True,
            serial_number=self.serial_number,
            description=self._description,
            shutter_state=state if state in ("open", "closed") else "unknown",
            operating_state=operation,
            operating_mode=mode,
            key_enabled=bool(self._device.Status.KeyEnabled),
            # Vendor docs name bit 12 as interlock, but a clear bit did not
            # distinguish jack installed/removed on the bench. Do not claim a
            # measured disabled circuit from that value; keep readiness unknown.
            interlock_enabled=True if bits & 0x1000 else None,
            trigger_config=config,
            status_bits=bits,
            operator_interlock_confirmed=(
                getattr(self, "_operator_verified_serial", None) == self.serial_number
            ),
        )
        self._check_connection()
        self._last_status = status
        return status

    def _read_trigger_config(self) -> TriggerConfig:
        self._device.RequestTriggerConfigParams()
        time.sleep(self.polling_ms / 1000)
        settings = self._device.GetTriggerConfigParams()
        modes = {"Disabled": "disabled", "TrigIN_GPI": "input", "TrigOUT_GPO": "output"}
        polarities = {"TriggerHigh": "high", "TriggerLow": "low"}
        return TriggerConfig(
            modes[str(settings.Trigger1Mode)],
            polarities[str(settings.Trigger1Polarity)],
            modes[str(settings.Trigger2Mode)],
            polarities[str(settings.Trigger2Polarity)],
        )

    def get_trigger_config(self) -> TriggerConfig:
        """Read only TTL settings; do not request unrelated operating feedback."""
        with self._lock, self._command("TTL settings read", reading=True):
            self._check_connection()
            config = self._read_trigger_config()
            self._check_connection()
            if self._last_status is not None:
                self._last_status = replace(self._last_status, trigger_config=config)
            return config

    def configure_triggers(self, config: TriggerConfig) -> None:
        """Write both TTL ports. No prerequisite read, readback or EEPROM persist."""
        if not isinstance(config, TriggerConfig):
            raise ValueError("config must be a TriggerConfig.")
        with self._lock, self._command("TTL configuration"):
            settings = self._sdk.trigger_settings()
            modes = self._sdk.trigger_settings.TriggerPortMode
            polarities = self._sdk.trigger_settings.TriggerPolarity
            mode_values = {
                "disabled": modes.Disabled,
                "input": modes.TrigIN_GPI,
                "output": modes.TrigOUT_GPO,
            }
            polarity_values = {"high": polarities.TriggerHigh, "low": polarities.TriggerLow}
            for port in (1, 2):
                setattr(
                    settings, f"Trigger{port}Mode", mode_values[getattr(config, f"trig{port}_mode")]
                )
                setattr(
                    settings,
                    f"Trigger{port}Polarity",
                    polarity_values[getattr(config, f"trig{port}_polarity")],
                )
            self._device.SetTriggerConfigParams(settings)

    def arm_triggers(self) -> None:
        """Enable, select Triggered and request Active. An active input may open."""
        with self._lock, self._command("TTL arm"):
            self._device.EnableDevice()
            self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Triggered)
            self._device.SetOperatingState(self._sdk.enums.OperatingStates.Active)

    def disarm_triggers(self) -> None:
        """Request Inactive then Manual; no feedback read."""
        with self._lock, self._command("TTL disarm", allow_fault=True):
            self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)
            self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Manual)

    def get_cached_status(self) -> ShutterStatus:
        """Return the last display observation without I/O; never authorize output."""
        with self._lock:
            if self._device is not None and self._fault is None and self._last_status is not None:
                return self._last_status
            return ShutterStatus(
                connection="fault"
                if self._fault
                else ("connected" if self._device is not None else "disconnected"),
                has_device=self._device is not None,
                serial_number=self.serial_number,
                description=self._description,
                error=self._fault,
                operator_interlock_confirmed=(
                    getattr(self, "_operator_verified_serial", None) == self.serial_number
                    and self.serial_number is not None
                ),
            )

    def _refresh_status(self, *, include_triggers: bool) -> ShutterStatus:
        """Own read fault handling for both fresh snapshot APIs."""
        with self._lock:
            if self._device is not None and self._fault is None:
                try:
                    return self._read_status(include_triggers=include_triggers)
                except Exception as exc:
                    self._fault = f"Status read failed: {exc}"
            return self.get_cached_status()

    def get_status(self) -> ShutterStatus:
        """Request full operating/TTL feedback; read failures latch a fault."""
        return self._refresh_status(include_triggers=True)

    def get_operating_status(self) -> ShutterStatus:
        """Request operating/safeguard feedback only; read failures latch a fault."""
        return self._refresh_status(include_triggers=False)

    def _get_value(self, request: str, getter: str):
        with self._lock, self._command("Read feedback", reading=True):
            self._check_connection()
            getattr(self._device, request)()
            time.sleep(self.polling_ms / 1000)
            value = getattr(self._device, getter)()
            self._check_connection()
            return value

    def get_shutter_state(self) -> str:
        """Request position feedback only; undefined values return 'unknown'."""
        state = str(self._get_value("RequestStatus", "GetSolenoidState")).lower()
        return state if state in ("open", "closed") else "unknown"

    def get_operating_state(self) -> str:
        """Request Active/Inactive feedback only; undefined values return 'unknown'."""
        state = str(self._get_value("RequestOperatingState", "GetOperatingState")).lower()
        return state if state in ("active", "inactive") else "unknown"

    def get_operating_mode(self) -> str:
        """Request operating-mode feedback only."""
        mode = str(self._get_value("RequestOperatingMode", "GetOperatingMode")).lower()
        return {
            "manual": "manual",
            "singletoggle": "single",
            "autotoggle": "auto",
            "triggered": "triggered",
        }.get(mode, "unknown")

    def get_status_bits(self) -> int:
        """Request controller status bits only; no operating/TTL requests."""
        return int(self._get_value("RequestStatus", "GetStatusBits"))

    def set_operating_state(self, state: str) -> None:
        """Send Active/Inactive only; does not change mode or enable the device."""
        if state not in ("active", "inactive"):
            raise ValueError("Operating state must be active or inactive.")
        with self._lock, self._command("Set operating state", allow_fault=state == "inactive"):
            self._device.SetOperatingState(getattr(self._sdk.enums.OperatingStates, state.title()))

    def set_operating_mode(self, mode: str) -> None:
        """Send Manual/Single/Auto/Triggered only; caller owns transition order."""
        names = {
            "manual": "Manual",
            "single": "SingleToggle",
            "auto": "AutoToggle",
            "triggered": "Triggered",
        }
        if mode not in names:
            raise ValueError("Operating mode must be manual, single, auto or triggered.")
        with self._lock, self._command("Set operating mode"):
            self._device.SetOperatingMode(getattr(self._sdk.enums.OperatingModes, names[mode]))

    def enable_device(self) -> None:
        """Explicitly enable the SDK channel; no mode/state change or readback."""
        with self._lock, self._command("Enable device"):
            self._device.EnableDevice()

    def open_shutter(self) -> None:
        """Send Active only, preserving mode and enable state. No reads or waits."""
        with self._lock, self._command("Open"):
            self._device.SetOperatingState(self._sdk.enums.OperatingStates.Active)

    def close_shutter(self) -> None:
        """Send Inactive only, preserving mode, including after faults. No verification."""
        with self._lock, self._command("Close", allow_fault=True):
            self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)

    @contextmanager
    def _command(self, name, *, allow_fault=False, reading=False):
        """Guard local handle ownership and preserve errors; never query feedback."""
        if self._device is None:
            raise ShutterError("No device connected.")
        if self._fault and not allow_fault:
            raise ShutterError(self._fault)
        if not reading:
            self._last_status = None
        try:
            yield
        except BaseException as exc:
            self._fault = (
                f"{name} failed: {str(exc) or type(exc).__name__}. Physical state is unverified."
            )
            if not isinstance(exc, Exception):
                exc.add_note(self._fault)
                raise
            raise ShutterError(self._fault) from exc

    def _release(self) -> tuple[list[str], BaseException | None]:
        errors = []
        interrupted = None
        if self._device is not None:
            for method, label in (("StopPolling", "stop polling"), ("Disconnect", "disconnect")):
                try:
                    getattr(self._device, method)()
                except BaseException as exc:
                    errors.append(f"{label}: {str(exc) or type(exc).__name__}")
                    if interrupted is None and not isinstance(exc, Exception):
                        interrupted = exc
                else:
                    if method == "Disconnect":
                        self._device = None
        if self._device is None:
            with _sdk_lock:
                if _device_owners.get(self._claimed_serial) is self:
                    del _device_owners[self._claimed_serial]
                self._claimed_serial = None
        return errors, interrupted

    def disconnect(self, *, close_shutter: bool = True) -> None:
        """Request Close, then release even if the command fails; no closure verification.

        close_shutter=False is an explicit communication-only release; it leaves
        the output unchanged and must not be mistaken for safe_shutdown().
        Failed disconnect retains the device handle for a subsequent cleanup attempt.
        """
        with self._lock:
            if self._device is None:
                return
            errors = []
            interrupted = None
            try:
                if close_shutter:
                    self.close_shutter()
            except BaseException as exc:
                errors.append(str(exc) or type(exc).__name__)
                if not isinstance(exc, Exception):
                    interrupted = exc
            finally:
                release_errors, release_interrupt = self._release()
                errors.extend(release_errors)
                interrupted = interrupted or release_interrupt
            self._description = None
            self._fault = "; ".join(errors) if errors else None
            if interrupted is not None:
                interrupted.add_note(f"Shutdown interrupted: {self._fault}")
                raise interrupted
            if errors:
                raise ShutterError(f"Shutdown incomplete: {self._fault}")

    def safe_shutdown(self) -> None:
        """Best-effort close and release; raises if any step fails. No firmware writes."""
        self.disconnect(close_shutter=True)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            self.safe_shutdown()
        except ShutterError as shutdown_error:
            if exc is None:
                raise
            exc.add_note(str(shutdown_error))
        return False


class KCubeShutter(_KinesisShutter):
    """One USB KSC101. Network connections and routing belong to ShutterHub."""

    def _matches_transport(self, serial: str) -> bool:
        info = self._sdk.manager.GetTransportInfo(serial)
        return info is not None and str(info.GetProvider()) == "FTDI"

    def discover(self) -> list[str]:
        """Enumerate USB KSC101s only, ignoring other registered transports."""
        with self._lock:
            try:
                self._sdk = self._sdk or _load_sdk(self.kinesis_dir)
                with _sdk_lock:
                    self._sdk.manager.BuildDeviceList()
                    return sorted(
                        str(serial)
                        for serial in self._sdk.manager.GetDeviceList(68)
                        if self._matches_transport(str(serial))
                    )
            except Exception as exc:
                raise ShutterError(f"USB discovery failed: {exc}") from exc

    def _check_transport(self) -> None:
        # Headless Kinesis may retain Connecting while IsConnected is true.
        with _sdk_lock:
            matches = self._matches_transport(self.serial_number)
        if (
            not matches
            or not self._device.IsConnected
            or str(self._device.USBConnected) not in ("Connected", "Connecting")
        ):
            raise ShutterError("USB connection lost/changed; disconnect and reconnect.")


class _HubChannel(_KinesisShutter):
    """A hub-owned SDK channel; transport selection is delegated to its hub."""

    def __init__(self, hub, slot, serial, *, kinesis_dir, timeout=5.0, polling_ms=250):
        super().__init__(serial, kinesis_dir=kinesis_dir, timeout=timeout, polling_ms=polling_ms)
        self._hub = hub
        self._slot = slot

    def discover(self) -> list[str]:
        return self._hub._discover_slot(self._slot)

    def _matches_transport(self, serial: str) -> bool:
        return self._hub._matches_endpoint(self._slot, serial)

    def _check_transport(self) -> None:
        if not self._matches_transport(self.serial_number) or not self._device.IsConnected:
            raise ShutterError("Ethernet connection lost/changed; disconnect and reconnect.")


class ShutterHub:
    """Own slots, network routing and command dispatch for connected shutters.

    Serials preselect slots; omitted slots remain unselected. The default count
    is three for USB, or fits the supplied network routes. Existing controllers can
    be injected instead. Construction never loads the SDK.
    The lock serializes GUI actions/status with shutdown; drivers also lock calls.
    """

    @staticmethod
    def _validate_endpoint(endpoint):
        if endpoint is None:
            return
        try:
            address, port = endpoint.rsplit(":", 1)
            if str(IPv4Address(address)) != address or port not in (
                "40304",
                "40305",
                "40306",
                "40307",
            ):
                raise ValueError
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError(
                "ethernet_endpoints entries must be IPv4 KEH3 cube endpoints "
                "(ports 40304..40307), or None for USB."
            ) from exc

    def __init__(
        self,
        serial_numbers: Sequence[str | int] = (),
        *,
        kinesis_dir: str | Path | None = None,
        slots: int | None = None,
        controllers: Sequence[KCubeShutter] | None = None,
        ethernet_endpoints: Sequence[str | None] = (),
    ):
        if slots is not None and (type(slots) is not int or slots < 1):
            raise ValueError("slots must be a positive integer.")
        if not isinstance(ethernet_endpoints, Sequence) or isinstance(
            ethernet_endpoints, (str, bytes)
        ):
            raise ValueError("ethernet_endpoints must be a sequence of per-slot endpoints.")
        endpoints = tuple(ethernet_endpoints)
        for endpoint in endpoints:
            self._validate_endpoint(endpoint)
        if controllers is not None and (
            serial_numbers or kinesis_dir is not None or slots is not None or endpoints
        ):
            raise ValueError("Configure injected controllers directly, without hub options.")
        if controllers is None:
            serials = tuple(_normalize_serial(serial) for serial in serial_numbers)
            if len(set(serials)) != len(serials):
                raise ValueError("Supply distinct serial numbers.")
            default_count = max(len(serials), len(endpoints)) if endpoints else max(3, len(serials))
            count = default_count if slots is None else slots
            if max(len(serials), len(endpoints)) > count:
                raise ValueError("slots must fit all supplied serial numbers and endpoints.")
            self._ethernet_endpoints = endpoints + (None,) * (count - len(endpoints))
            controllers = tuple(
                _HubChannel(self, slot, serial, kinesis_dir=kinesis_dir)
                if self.ethernet_endpoints[slot] is not None
                else KCubeShutter(serial, kinesis_dir=kinesis_dir)
                for slot, serial in enumerate(serials + (None,) * (count - len(serials)))
            )
        else:
            controllers = tuple(controllers)
            if any(not isinstance(c, KCubeShutter) for c in controllers):
                raise ValueError(
                    "Injected controllers must be independent USB KCubeShutter objects."
                )
            self._ethernet_endpoints = (None,) * len(controllers)
        self.controllers = tuple(controllers)
        if not self.controllers:
            raise ValueError("A shutter hub requires at least one controller.")
        if len({id(controller) for controller in self.controllers}) != len(self.controllers):
            raise ValueError("Each shutter slot requires a distinct controller object.")
        self.lock = RLock()

    @property
    def ethernet_endpoints(self) -> tuple[str | None, ...]:
        """Read-only route snapshot; configure_slot changes only released slots."""
        return self._ethernet_endpoints

    def configure_slot(self, slot: int, *, ethernet_endpoint: str | None = None) -> None:
        """Passively choose USB (None) or LAN after releasing this slot's handle."""
        self._validate_endpoint(ethernet_endpoint)
        with self.lock:
            old = self._controller(slot)
            with old._lock:
                if old._device is not None:
                    raise ShutterError("Disconnect this controller before changing its connection.")
                if self.ethernet_endpoints[slot] == ethernet_endpoint:
                    return
                kwargs = dict(
                    kinesis_dir=old.kinesis_dir, timeout=old.timeout, polling_ms=old.polling_ms
                )
                replacement = (
                    KCubeShutter(**kwargs)
                    if ethernet_endpoint is None
                    else _HubChannel(self, slot, None, **kwargs)
                )
                replacement._sdk = old._sdk
                endpoints = list(self.ethernet_endpoints)
                endpoints[slot] = ethernet_endpoint
                controllers = list(self.controllers)
                controllers[slot] = replacement
                self._ethernet_endpoints = tuple(endpoints)
                self.controllers = tuple(controllers)

    def _matches_endpoint(self, slot: int, serial: str) -> bool:
        with _sdk_lock:
            info = self.controllers[slot]._sdk.manager.GetTransportInfo(serial)
            return (
                info is not None
                and str(info.GetProvider()) == "TCPIP"
                and str(info.GetComSpec()) == self.ethernet_endpoints[slot]
            )

    def scan_lan(
        self,
        start_address: str | None = None,
        end_address: str | None = None,
        *,
        open_timeout_ms: int | None = None,
    ) -> LanDiscovery:
        """Find KEH3 hosts and KSC101 bay identities without connecting a cube.

        Vendor scanning probes port 40303, then SDK registration enumerates the
        documented cube ports. Omitted arguments use config.LAN_SCAN_* defaults.
        Range is inclusive and limited by LAN_SCAN_MAX_ADDRESSES (at most 256).
        Async identity polling uses the controllers' timeout; native calls can
        exceed it. Release all process-owned handles before scanning.
        """
        start_address = config.LAN_SCAN_START_IP if start_address is None else start_address
        end_address = config.LAN_SCAN_END_IP if end_address is None else end_address
        open_timeout_ms = (
            config.LAN_SCAN_OPEN_TIMEOUT_MS if open_timeout_ms is None else open_timeout_ms
        )
        limit = config.LAN_SCAN_MAX_ADDRESSES
        if type(limit) is not int or not 1 <= limit <= 256:
            raise ValueError("LAN_SCAN_MAX_ADDRESSES must be an integer from 1 to 256.")
        if not isinstance(start_address, str) or not isinstance(end_address, str):
            raise ValueError("LAN range must contain two IPv4 address strings.")
        try:
            start, end = IPv4Address(start_address), IPv4Address(end_address)
        except (ValueError, TypeError) as exc:
            raise ValueError("LAN range must contain two IPv4 addresses.") from exc
        if not 0 <= int(end) - int(start) < limit:
            raise ValueError(f"LAN range must be ascending and contain at most {limit} addresses.")
        if type(open_timeout_ms) is not int or not 50 <= open_timeout_ms <= 1000:
            raise ValueError("LAN open timeout must be an integer from 50 to 1000 ms.")
        with self.lock, _sdk_lock:
            # Ownership/handle creation is serialized by _sdk_lock. Do not take
            # channel locks here: connect takes a channel lock before this lock.
            if _device_owners or any(c._device is not None for c in self.controllers):
                raise ShutterError("Disconnect all controllers before scanning the LAN.")
            try:
                first = self.controllers[0]
                sdk = first._sdk or _load_sdk(first.kinesis_dir)
                for channel in self.controllers:
                    channel._sdk = sdk
                addresses = sdk.manager.ScanEthernetRange(
                    str(start), str(end), 40303, open_timeout_ms
                )
                hosts = set()
                for entry in addresses:
                    # SDK versions may report a bare address or address:port.
                    address, sep, port = str(entry).partition(":")
                    if sep and port != "40303":
                        continue
                    try:
                        ip = IPv4Address(address)
                    except ValueError:
                        continue
                    if start <= ip <= end:
                        hosts.add(ip)
                ordered_hosts = tuple(str(ip) for ip in sorted(hosts))
                if not hosts:
                    return LanDiscovery((), ())
                candidates = {
                    f"{host}:{port}" for host in ordered_hosts for port in range(40304, 40308)
                }
                for endpoint in sorted(candidates):
                    sdk.manager.CreateManualDeviceEntry(endpoint)
                sdk.manager.BuildDeviceList()
                deadline = time.monotonic() + max(c.timeout for c in self.controllers)
                while True:
                    sdk.manager.CheckForConnectionChanges()
                    found = {}
                    for value in sdk.manager.GetDeviceList(68):
                        serial = str(value)
                        if not re.fullmatch(r"68[0-9]{6}", serial):
                            continue
                        info = sdk.manager.GetTransportInfo(serial)
                        if info is None or str(info.GetProvider()) != "TCPIP":
                            continue
                        endpoint = str(info.GetComSpec())
                        if endpoint in candidates:
                            found[serial] = LanDevice(serial, endpoint)
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    time.sleep(min(0.1, remaining))
                return LanDiscovery(ordered_hosts, tuple(found[s] for s in sorted(found)))
            except Exception as exc:
                raise ShutterError(f"LAN discovery failed: {exc}") from exc

    def discover(self) -> list[str]:
        """Register configured LAN entries, rebuild the SDK list and filter routes."""
        with self.lock:
            if not any(self.ethernet_endpoints):
                return self.controllers[0].discover()
            try:
                first = self.controllers[0]
                sdk = first._sdk or _load_sdk(first.kinesis_dir)
                with _sdk_lock:
                    for channel in self.controllers:
                        channel._sdk = sdk
                    # Vendor Ethernet sequence: register manual entries, then
                    # BuildDeviceList. Registration alone does not enumerate them.
                    # This rebuild is needed for TCPIP too; it does not require
                    # a USB-connected device and must not be skipped for LAN hubs.
                    for endpoint in dict.fromkeys(self.ethernet_endpoints):
                        if endpoint is not None:
                            sdk.manager.CreateManualDeviceEntry(endpoint)
                    sdk.manager.BuildDeviceList()
                    # TCPIP discovery completes asynchronously. Refresh its
                    # connection-change results until each network route has an
                    # identity or the controller discovery timeout expires.
                    # Register/build once: rebuilding each poll can restart work.
                    network_slots = [
                        slot
                        for slot, endpoint in enumerate(self.ethernet_endpoints)
                        if endpoint is not None
                    ]
                    deadline = time.monotonic() + max(
                        self.controllers[slot].timeout for slot in network_slots
                    )
                    while True:
                        sdk.manager.CheckForConnectionChanges()
                        found = sorted(
                            str(serial)
                            for serial in sdk.manager.GetDeviceList(68)
                            if any(c._matches_transport(str(serial)) for c in self.controllers)
                        )
                        if all(
                            any(self._matches_endpoint(slot, serial) for serial in found)
                            for slot in network_slots
                        ):
                            return found
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            return found
                        time.sleep(min(0.1, remaining))
            except Exception as exc:
                raise ShutterError(f"Hub discovery failed: {exc}") from exc

    def discover_available(self) -> tuple[dict[str, str | None], tuple[str, ...]]:
        """Return serial -> detected LAN endpoint (None for USB), plus warnings.

        This shared GUI discovery includes configured routes and a config-based
        LAN scan. A failed/skipped transport does not hide successful results.
        No slot route or device control handle is changed.
        """
        with self.lock:
            found = {}
            warnings = []
            first = self.controllers[0]
            usb = KCubeShutter(kinesis_dir=first.kinesis_dir)
            usb._sdk = first._sdk
            try:
                for serial in usb.discover():
                    found[serial] = None
            except ShutterError as exc:
                warnings.append(f"USB discovery: {exc}")
            if any(self.ethernet_endpoints):
                try:
                    for slot, serials in enumerate(self.discover_by_slot()):
                        for serial in serials:
                            found[serial] = self.ethernet_endpoints[slot]
                except ShutterError as exc:
                    warnings.append(f"Configured route discovery: {exc}")
            try:
                for device in self.scan_lan().controllers:
                    found[device.serial_number] = device.endpoint
            except (ShutterError, ValueError) as exc:
                warnings.append(f"LAN scan: {exc}")
            return dict(sorted(found.items())), tuple(warnings)

    def discover_by_slot(self) -> tuple[list[str], ...]:
        """Discover once, then group serials by each slot's configured transport."""
        with self.lock:
            serials = self.discover()
            if not any(self.ethernet_endpoints):
                return tuple(list(serials) for _ in self.controllers)
            with _sdk_lock:
                return tuple(
                    [serial for serial in serials if channel._matches_transport(serial)]
                    for channel in self.controllers
                )

    def _discover_slot(self, slot: int) -> list[str]:
        with self.lock:
            return [s for s in self.discover() if self._matches_endpoint(slot, s)]

    def _controller(self, slot: int) -> _KinesisShutter:
        if type(slot) is not int or not 0 <= slot < len(self.controllers):
            raise ShutterError("Shutter slot must be an integer index within this hub.")
        return self.controllers[slot]

    def connect(self, slot: int, serial_number: str | int) -> ShutterStatus:
        """Connect one zero-based slot, rejecting another slot's retained device."""
        with self.lock:
            controller = self._controller(slot)
            if serial_number is None:
                raise ShutterError(
                    "Select a KSC101 serial number for this shutter before connecting."
                )
            return controller.connect(serial_number)

    def _dispatch(self, slot: int, method: str, *args, **kwargs):
        with self.lock:
            controller = self._controller(slot)
            with controller._lock:
                # Check network routing metadata before ordinary writes, without
                # requesting operating feedback. Close still targets the retained
                # handle after a fault; it never rebinds or falls back to USB.
                check_route = method in (
                    "enable_device",
                    "open_shutter",
                    "arm_triggers",
                    "configure_triggers",
                    "set_operating_mode",
                ) or (method == "set_operating_state" and args[0] == "active")
                if (
                    self.ethernet_endpoints[slot] is not None
                    and controller._device is not None
                    and check_route
                ):
                    with controller._command("Hub routing"):
                        if not self._matches_endpoint(slot, controller.serial_number):
                            raise ShutterError(
                                "Selected Ethernet transport changed; refusing command."
                            )
                return getattr(controller, method)(*args, **kwargs)

    def identify_device(self, slot: int) -> dict[str, str]:
        return self._dispatch(slot, "identify_device")

    def confirm_interlock(self, slot: int, serial: str | int) -> None:
        self._dispatch(slot, "confirm_interlock", serial)

    def get_status(self, slot: int) -> ShutterStatus:
        return self._dispatch(slot, "get_status")

    def get_operating_status(self, slot: int) -> ShutterStatus:
        return self._dispatch(slot, "get_operating_status")

    def get_cached_status(self, slot: int) -> ShutterStatus:
        return self._dispatch(slot, "get_cached_status")

    def get_shutter_state(self, slot: int) -> str:
        return self._dispatch(slot, "get_shutter_state")

    def get_operating_state(self, slot: int) -> str:
        return self._dispatch(slot, "get_operating_state")

    def get_operating_mode(self, slot: int) -> str:
        return self._dispatch(slot, "get_operating_mode")

    def get_status_bits(self, slot: int) -> int:
        return self._dispatch(slot, "get_status_bits")

    def get_trigger_config(self, slot: int) -> TriggerConfig:
        return self._dispatch(slot, "get_trigger_config")

    def configure_triggers(self, slot: int, config: TriggerConfig) -> None:
        self._dispatch(slot, "configure_triggers", config)

    def set_operating_state(self, slot: int, state: str) -> None:
        self._dispatch(slot, "set_operating_state", state)

    def set_operating_mode(self, slot: int, mode: str) -> None:
        self._dispatch(slot, "set_operating_mode", mode)

    def enable_device(self, slot: int) -> None:
        self._dispatch(slot, "enable_device")

    def open_shutter(self, slot: int) -> None:
        self._dispatch(slot, "open_shutter")

    def close_shutter(self, slot: int) -> None:
        self._dispatch(slot, "close_shutter")

    def arm_triggers(self, slot: int) -> None:
        self._dispatch(slot, "arm_triggers")

    def disarm_triggers(self, slot: int) -> None:
        self._dispatch(slot, "disarm_triggers")

    def disconnect(self, slot: int, *, close_shutter: bool = True) -> None:
        self._dispatch(slot, "disconnect", close_shutter=close_shutter)

    def safe_shutdown(self) -> None:
        """Attempt closure and release for every slot, preserving all failures.

        A failed or interrupted shutdown never skips later slots. Interrupts are
        re-raised after the remaining attempts; ordinary failures are aggregated
        into one error with the slot and serial identity for each failed attempt.
        """
        with self.lock:
            errors = []
            interrupted = None
            first_error = None
            for index, controller in enumerate(self.controllers):
                serial = controller.serial_number or "unselected"
                try:
                    controller.safe_shutdown()
                except BaseException as exc:
                    errors.append(
                        f"Shutter {index + 1} ({serial}): {str(exc) or type(exc).__name__}"
                    )
                    if first_error is None:
                        first_error = exc
                    if interrupted is None and not isinstance(exc, Exception):
                        interrupted = exc
            if not errors:
                return
            message = "Shutdown incomplete: " + "; ".join(errors)
            if interrupted is not None:
                interrupted.add_note(message)
                raise interrupted
            raise ShutterError(message) from first_error
