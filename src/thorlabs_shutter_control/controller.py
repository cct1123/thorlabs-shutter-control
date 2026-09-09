"""A small, serialized wrapper around the official Kinesis KSC101 .NET API.

State is controller-reported feedback, never independent optical verification.
No device is connected or enabled when this module is imported.
"""

from __future__ import annotations

import math
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from types import SimpleNamespace


class ShutterError(RuntimeError):
    """An operation failed; the message includes its context and original error."""


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
    error: str | None = None


_sdk_lock = RLock()
_loaded_sdk = None


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
            from Thorlabs.MotionControl.KCube.SolenoidCLI import KCubeSolenoid, SolenoidStatus

            _loaded_sdk = SimpleNamespace(
                manager=DeviceManagerCLI,
                device_type=KCubeSolenoid,
                enums=SolenoidStatus,
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


class KSC101Controller:
    """One KSC101, owned by one process. Calls on this object are serialized.

    connect() starts communication/polling only. open_shutter() explicitly selects
    Manual mode and enables the output. close_shutter() requests Inactive even in
    another mode, then selects Manual to disarm timed/triggered operation.
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
        if serial_number is not None and not re.fullmatch(r"68[0-9]{6}", serial_number):
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

    def discover(self) -> list[str]:
        """Enumerate KSC101 USB identities without connecting or actuating."""
        with self._lock:
            try:
                self._sdk = self._sdk or _load_sdk(self.kinesis_dir)
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
                if not re.fullmatch(r"68[0-9]{6}", serial_number):
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
            self._fault = None
            try:
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
                self._description = str(self._device.GetDeviceInfo().Description)
                time.sleep(2 * self.polling_ms / 1000)
                return self._read_status()
            except BaseException as exc:
                errors = self._release()
                if not isinstance(exc, Exception):
                    raise
                self._fault = f"Connect failed: {exc}" + (
                    f"; cleanup: {'; '.join(errors)}" if errors else ""
                )
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

    def _read_status(self) -> ShutterStatus:
        self._check_connection()
        self._device.RequestStatus()
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
        )
        self._check_connection()
        return status

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

    def _wait_for(self, predicate, description: str) -> ShutterStatus:
        deadline = time.monotonic() + self.timeout
        while True:
            # Allow a poll after a write. Kinesis still owns cache freshness/USB timeout.
            time.sleep(self.polling_ms / 1000)
            status = self._read_status()
            if predicate(status):
                return status
            if time.monotonic() >= deadline:
                raise ShutterError(
                    f"Timed out waiting for {description}; reported state: {status}."
                )

    def open_shutter(self) -> ShutterStatus:
        """Request manual Open and wait for controller feedback, not optical proof."""
        with self._lock:
            status = self.get_status()
            if status.connection != "connected":
                raise ShutterError(status.error or "Connect before opening the shutter.")
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
                self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)
                self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Manual)
                self._wait_for(lambda s: s.operating_mode == "manual", "Manual mode")
                self._device.EnableDevice()
                self._device.SetOperatingState(self._sdk.enums.OperatingStates.Active)
                return self._wait_for(
                    lambda s: (
                        s.shutter_state == "open"
                        and s.operating_state == "active"
                        and s.operating_mode == "manual"
                        and s.key_enabled
                        and s.interlock_enabled
                    ),
                    "reported Open",
                )
            except BaseException as exc:
                # A failed Open may have actuated; attempt Inactive and preserve the failure.
                recovery = ""
                try:
                    self._device.SetOperatingState(self._sdk.enums.OperatingStates.Inactive)
                except Exception as close_exc:
                    recovery = f"; recovery close also failed: {close_exc}"
                self._fault = f"Open failed: {exc}{recovery}. Physical state is unverified."
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
                self._device.SetOperatingMode(self._sdk.enums.OperatingModes.Manual)
                return self._wait_for(
                    lambda s: (
                        s.shutter_state == "closed"
                        and s.operating_state == "inactive"
                        and s.operating_mode == "manual"
                    ),
                    "reported Closed",
                )
            except Exception as exc:
                self._fault = f"Close failed: {exc}. Physical closure is unverified."
                raise ShutterError(self._fault) from exc

    def _release(self) -> list[str]:
        errors = []
        if self._device is not None:
            try:
                self._device.StopPolling()
            except Exception as exc:
                errors.append(f"stop polling: {exc}")
            try:
                self._device.Disconnect()
            except Exception as exc:
                errors.append(f"disconnect: {exc}")
            else:
                self._device = None
        return errors

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
                errors.extend(self._release())
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
