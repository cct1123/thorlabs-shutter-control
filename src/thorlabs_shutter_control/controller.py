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
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from types import SimpleNamespace


class ShutterError(RuntimeError):
    """An operation failed; the message includes its context and original error."""


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
_device_owners: dict[str, KCubeShutter] = {}


def _load_sdk(directory: str | Path | None):
    """Load one Kinesis installation per process, retaining native DLL search paths."""
    global _loaded_sdk
    if sys.platform != "win32":
        raise ShutterError("The Kinesis hardware backend requires Windows.")
    directory = directory or os.environ.get("KINESIS_DIR")
    if directory is None:
        directory = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Thorlabs/Kinesis"
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
                "or set KINESIS_DIR / --kinesis-dir to its folder. Missing: " + ", ".join(missing)
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


class KCubeShutter:
    """One KSC101, with exclusive ownership within this Python process.

    Calls on this object are serialized; separate serials have separate handles.
    Shared SDK enumeration and handle creation are serialized across controllers.
    Other processes must still be excluded by the operator.

    connect() starts communication/polling only. open_shutter() explicitly selects
    Manual mode and enables the output. close_shutter() requests Inactive even in
    another mode, verifies Closed/Inactive, then selects Manual to disarm
    timed/triggered operation. Manual Open refuses Triggered until disarmed.
    disconnect() and safe_shutdown() attempt closure before releasing the device.
    """

    def __init__(
        self,
        serial_number: str | None = None,
        *,
        kinesis_dir: str | Path | None = None,
        timeout: float = 5.0,
        polling_ms: int = 250,
    ):
        if serial_number is not None and (
            not isinstance(serial_number, str) or not re.fullmatch(r"68[0-9]{6}", serial_number)
        ):
            raise ValueError("KSC101 serial number must be eight digits beginning with 68.")
        if not math.isfinite(timeout) or not 0.5 <= timeout <= 60:
            raise ValueError("timeout must be finite and between 0.5 and 60 seconds.")
        if isinstance(polling_ms, bool) or not isinstance(polling_ms, int):
            raise ValueError("polling_ms must be an integer.")
        if not 100 <= polling_ms <= 1000 or timeout < 2 * polling_ms / 1000:
            raise ValueError("polling_ms must be 100..1000 and timeout at least two polls.")
        self.serial_number = serial_number
        self.kinesis_dir = kinesis_dir
        self.timeout = timeout
        self.polling_ms = polling_ms
        self._lock = RLock()
        self._sdk = None
        self._device = None
        self._description = None
        self._fault = None
        self._claimed_serial = None

    def discover(self) -> list[str]:
        """Enumerate KSC101 USB identities without connecting or actuating."""
        with self._lock:
            try:
                self._sdk = self._sdk or _load_sdk(self.kinesis_dir)
                with _sdk_lock:
                    self._sdk.manager.BuildDeviceList()
                    return sorted(str(s) for s in self._sdk.manager.GetDeviceList(68))
            except ShutterError:
                raise
            except Exception as exc:
                raise ShutterError(f"Device discovery failed: {exc}") from exc

    def connect(self, serial_number: str | None = None) -> ShutterStatus:
        """Connect the selected device, or the only discovered KSC101. No output write."""
        with self._lock:
            if serial_number is not None:
                if not isinstance(serial_number, str) or not re.fullmatch(
                    r"68[0-9]{6}", serial_number
                ):
                    raise ShutterError(
                        "Select an eight-digit KSC101 serial number beginning with 68."
                    )
                if self._device is not None and serial_number != self.serial_number:
                    raise ShutterError("Disconnect before selecting another device.")
                self.serial_number = serial_number
            if self._device is not None:
                status = self.get_status()
                if status.connection != "connected":
                    raise ShutterError(status.error or "Disconnect before reconnecting.")
                return status
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
                time.sleep(2 * self.polling_ms / 1000)
                return self._read_status()
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
            try:
                self._check_connection()
                info = self._device.GetDeviceInfo()
                return {
                    "serial_number": str(info.SerialNumberText),
                    "description": str(info.Description),
                }
            except Exception as exc:
                self._fault = f"Read identity failed: {exc}"
                raise ShutterError(self._fault) from exc

    def _check_connection(self):
        if self._device is None:
            raise ShutterError("No device connected.")
        if not self._device.IsConnected or str(self._device.USBConnected) != "Connected":
            raise ShutterError("USB connection lost; disconnect and reconnect.")
        if str(self._device.CommsStatus) != "OK":
            raise ShutterError(f"Kinesis communication status: {self._device.CommsStatus}.")

    def _read_status(self, *, include_triggers: bool = True) -> ShutterStatus:
        self._check_connection()
        self._device.RequestStatus()
        # Read operating feedback after the settings wait, rather than holding
        # key/interlock/state values sampled before that delay. Closure waits
        # need only operating feedback and must survive a TTL-settings fault.
        config = self._read_trigger_config() if include_triggers else None
        bits = int(self._device.GetStatusBits())
        state = str(self._device.GetSolenoidState()).lower()
        status = ShutterStatus(
            connection="connected",
            has_device=True,
            serial_number=self.serial_number,
            description=self._description,
            shutter_state=state if state in ("open", "closed") else "unknown",
            operating_state=str(self._device.GetOperatingState()).lower(),
            operating_mode=str(self._device.GetOperatingMode()).lower(),
            key_enabled=bool(self._device.Status.KeyEnabled),
            interlock_enabled=bool(bits & 0x1000),
            trigger_config=config,
        )
        self._check_connection()
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
        """Request vendor settings readback; this does not measure pin voltage."""
        with self._lock:
            status = self.get_status()
            if status.connection != "connected":
                raise ShutterError(status.error or "Connect before reading TTL settings.")
            return status.trigger_config

    def configure_triggers(self, config: TriggerConfig) -> TriggerConfig:
        """Apply both ports only when reported Closed/Inactive in Manual mode.

        Readback must match before returning. No PersistSettings/EEPROM call is made.
        """
        if not isinstance(config, TriggerConfig):
            raise ValueError("config must be a TriggerConfig.")
        with self._lock:
            status = self.get_status()
            if not (
                status.connection == "connected"
                and status.operating_mode == "manual"
                and status.operating_state == "inactive"
                and status.shutter_state == "closed"
            ):
                raise ShutterError(status.error or "Disarm/Close before configuring TTL.")
            try:
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
                        settings,
                        f"Trigger{port}Mode",
                        mode_values[getattr(config, f"trig{port}_mode")],
                    )
                    setattr(
                        settings,
                        f"Trigger{port}Polarity",
                        polarity_values[getattr(config, f"trig{port}_polarity")],
                    )
                self._device.SetTriggerConfigParams(settings)
                deadline = time.monotonic() + self.timeout
                while True:
                    reported = self._read_trigger_config()
                    self._check_connection()
                    if reported == config:
                        return reported
                    if time.monotonic() >= deadline:
                        raise ShutterError(
                            f"TTL readback mismatch: requested {config}; got {reported}."
                        )
            except BaseException as exc:
                self._fault = f"TTL configuration failed: {exc}"
                if not isinstance(exc, Exception):
                    exc.add_note(self._fault)
                    raise
                raise ShutterError(self._fault) from exc

    def arm_triggers(self) -> ShutterStatus:
        """Explicitly prime external TTL. An active input can open immediately.

        Uses current device settings, never unapplied GUI selections. At least
        one input, key and interlock are required. Failure attempts Disarm/Close.
        """
        with self._lock:
            status = self.get_status()
            if status.connection != "connected":
                raise ShutterError(status.error or "Connect before arming TTL.")
            if not status.key_enabled or not status.interlock_enabled:
                raise ShutterError("Arm refused: controller key or interlock is not enabled.")
            config = status.trigger_config
            if "input" not in (config.trig1_mode, config.trig2_mode):
                raise ShutterError("Arm refused: configure at least one trigger input.")
            if status.ttl_armed:
                return status
            try:
                self.close_shutter()
                self._device.EnableDevice()
                self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Triggered)
                self._device.SetOperatingState(self._sdk.enums.OperatingStates.Active)
                deadline = time.monotonic() + self.timeout
                while True:
                    time.sleep(self.polling_ms / 1000)
                    reported = self._read_status()
                    if (
                        reported.ttl_armed
                        and reported.key_enabled
                        and reported.interlock_enabled
                        and reported.trigger_config == config
                    ):
                        return reported
                    if time.monotonic() >= deadline:
                        raise ShutterError(
                            f"Timed out waiting for TTL arming feedback: {reported}."
                        )
            except BaseException as exc:
                failure = (
                    f"TTL arm failed: {str(exc) or type(exc).__name__}. "
                    "Physical state is unverified."
                )
                self._fault = failure
                try:
                    self.close_shutter()
                except BaseException as close_exc:
                    self._fault = f"{failure}; Disarm/Close also failed: {close_exc}"
                    if not isinstance(close_exc, Exception):
                        close_exc.add_note(self._fault)
                        raise
                if not isinstance(exc, Exception):
                    exc.add_note(self._fault)
                    raise
                raise ShutterError(self._fault) from exc

    def disarm_triggers(self) -> ShutterStatus:
        """Request Inactive then Manual and verify closure, including after faults."""
        return self.close_shutter()

    def get_status(self) -> ShutterStatus:
        """Return polled vendor feedback. A fault invalidates all cached state.

        Kinesis owns the poll cache and communication timeout; this is not a
        synchronous physical measurement. Faults latch until disconnect/reconnect.
        """
        with self._lock:
            if self._device is not None and self._fault is None:
                try:
                    return self._read_status()
                except Exception as exc:
                    self._fault = f"Status read failed: {exc}"
            return ShutterStatus(
                connection="fault" if self._fault else "disconnected",
                has_device=self._device is not None,
                serial_number=self.serial_number,
                description=self._description,
                error=self._fault,
            )

    def _wait_for_state(self, shutter_state: str, *, manual: bool = True) -> ShutterStatus:
        operating_state = "active" if shutter_state == "open" else "inactive"
        deadline = time.monotonic() + self.timeout
        while True:
            # Allow a poll after a write. Kinesis still owns cache freshness/USB timeout.
            time.sleep(self.polling_ms / 1000)
            status = self._read_status(include_triggers=False)
            if (
                status.shutter_state == shutter_state
                and status.operating_state == operating_state
                and (not manual or status.operating_mode == "manual")
                and (shutter_state != "open" or (status.key_enabled and status.interlock_enabled))
            ):
                return status
            if time.monotonic() >= deadline:
                raise ShutterError(
                    f"Timed out waiting for reported {shutter_state.title()}/"
                    f"{operating_state.title()}"
                    f"{' in Manual mode' if manual else ''}; reported state: {status}."
                )

    def open_shutter(self) -> ShutterStatus:
        """Request manual Open and wait for controller feedback, not optical proof."""
        with self._lock:
            status = self.get_status()
            if status.connection != "connected":
                raise ShutterError(status.error or "Connect before opening the shutter.")
            if status.operating_mode == "triggered":
                raise ShutterError("Disarm TTL before requesting manual Open.")
            if not status.key_enabled or not status.interlock_enabled:
                raise ShutterError("Open refused: controller key or interlock is not enabled.")
            if (
                status.shutter_state == "open"
                and status.operating_state == "active"
                and status.operating_mode == "manual"
            ):
                return status
            try:
                # Clear any existing timed/triggered activity before enabling Manual mode.
                self.close_shutter()
                self._device.EnableDevice()
                self._device.SetOperatingState(self._sdk.enums.OperatingStates.Active)
                return self._wait_for_state("open")
            except BaseException as exc:
                # A failed Open may have actuated; attempt Inactive and preserve the failure.
                self._fault = (
                    f"Open failed: {str(exc) or type(exc).__name__}. Physical state is unverified."
                )
                try:
                    self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)
                except BaseException as close_exc:
                    self._fault += f"; recovery close also failed: {close_exc}"
                    if not isinstance(close_exc, Exception):
                        close_exc.add_note(self._fault)
                        raise
                if not isinstance(exc, Exception):
                    exc.add_note(self._fault)
                    raise
                raise ShutterError(self._fault) from exc

    def close_shutter(self) -> ShutterStatus:
        """Attempt Inactive even after a communication fault, then verify feedback."""
        with self._lock:
            if self._device is None:
                raise ShutterError("No device connected; physical closure cannot be confirmed.")
            try:
                self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)
                # A primed Triggered/Active cube may be physically closed because
                # its input is inactive. Selecting Manual while still Active could
                # open it. Require Closed/Inactive feedback before changing mode.
                self._wait_for_state("closed", manual=False)
                self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Manual)
                return self._wait_for_state("closed")
            except BaseException as exc:
                self._fault = f"Close failed: {exc}. Physical closure is unverified."
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
        """Close by default, then stop polling and disconnect even if closure fails.

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


class ShutterHub:
    """Own fixed GUI slots and attempt shutdown of every controller.

    Up to three serials preselect slots; omitted slots remain unselected. Existing
    controllers can be injected instead. Construction never loads the SDK.
    The lock serializes GUI actions/status with shutdown; drivers also lock calls.
    """

    def __init__(
        self,
        serial_numbers: Sequence[str] = (),
        *,
        kinesis_dir: str | Path | None = None,
        controllers: Sequence[KCubeShutter] | None = None,
    ):
        if controllers is not None and (serial_numbers or kinesis_dir is not None):
            raise ValueError("Configure injected controllers directly, without hub options.")
        if controllers is None:
            serials = tuple(serial_numbers)
            if len(serials) > 3 or len(set(serials)) != len(serials):
                raise ValueError("Supply at most three distinct serial numbers.")
            controllers = (
                KCubeShutter(serial, kinesis_dir=kinesis_dir)
                for serial in serials + (None,) * (3 - len(serials))
            )
        self.controllers = tuple(controllers)
        if not 1 <= len(self.controllers) <= 3:
            raise ValueError("A shutter hub requires one to three controllers.")
        if len({id(controller) for controller in self.controllers}) != len(self.controllers):
            raise ValueError("Each shutter slot requires a distinct controller object.")
        self.lock = RLock()

    def discover(self) -> list[str]:
        """Perform one USB enumeration shared by every slot; do not connect."""
        with self.lock:
            return self.controllers[0].discover()

    def connect(self, slot: int, serial_number: str) -> ShutterStatus:
        """Connect one zero-based slot, rejecting another slot's retained device."""
        with self.lock:
            if type(slot) is not int or not 0 <= slot < len(self.controllers):
                raise ShutterError("Shutter slot must be an integer index within this hub.")
            if serial_number is None:
                raise ShutterError(
                    "Select a KSC101 serial number for this shutter before connecting."
                )
            return self.controllers[slot].connect(serial_number)

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
