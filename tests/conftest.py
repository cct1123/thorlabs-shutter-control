"""Software-only .NET test double. It never imports Kinesis or contacts hardware."""

from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import KSC101Controller
from thorlabs_shutter_control import controller as module


class FakeDevice:
    def __init__(self):
        self.calls = []
        self.IsConnected = False
        self.USBConnected = "Disconnected"
        self.CommsStatus = "OK"
        self.Status = SimpleNamespace(KeyEnabled=True)
        self.interlock = True
        self.state = "Closed"
        self.operation = "Inactive"
        self.mode = "Manual"
        self.initialized = True
        self.polling = 0
        self.serial = "68000001"  # Explicitly fictional test identity.
        self.fail = set()
        self.stuck = False

    def record(self, name, *args):
        self.calls.append((name, *args))
        if name in self.fail:
            raise RuntimeError(f"Injected {name} failure")

    def Connect(self, serial):
        self.record("connect", serial)
        self.serial = serial
        self.IsConnected = True
        self.USBConnected = "Connected"

    def IsSettingsInitialized(self):
        return self.initialized

    def WaitForSettingsInitialized(self, milliseconds):
        self.record("settings", milliseconds)

    def StartPolling(self, milliseconds):
        self.record("poll", milliseconds)
        self.polling = milliseconds

    def PollingDuration(self):
        return self.polling

    def GetDeviceInfo(self):
        self.record("identity")
        return SimpleNamespace(
            Description="TEST DOUBLE, NOT HARDWARE", SerialNumberText=self.serial
        )

    def RequestStatus(self):
        self.record("status")

    def GetStatusBits(self):
        return 0x1000 if self.interlock else 0

    def GetSolenoidState(self):
        return self.state

    def GetOperatingState(self):
        return self.operation

    def GetOperatingMode(self):
        return self.mode

    def SetOperatingState(self, state):
        self.record("set_state", state)
        self.operation = state
        if not self.stuck:
            self.state = "Open" if state == "Active" else "Closed"

    def SetOperatingMode(self, mode):
        self.record("set_mode", mode)
        self.mode = mode

    def EnableDevice(self):
        self.record("enable")

    def StopPolling(self):
        self.record("stop_poll")
        self.polling = 0

    def Disconnect(self):
        self.record("disconnect")
        self.IsConnected = False
        self.USBConnected = "Disconnected"


@pytest.fixture
def rig(monkeypatch):
    device = FakeDevice()
    serials = [device.serial]
    manager_calls = []
    sdk = SimpleNamespace(
        manager=SimpleNamespace(
            BuildDeviceList=lambda: manager_calls.append("discover"),
            GetDeviceList=lambda type_id: serials if type_id == 68 else [],
        ),
        device_type=SimpleNamespace(CreateKCubeSolenoid=lambda serial: device),
        enums=SimpleNamespace(
            OperatingStates=SimpleNamespace(Active="Active", Inactive="Inactive"),
            OperatingModes=SimpleNamespace(Manual="Manual"),
        ),
    )
    monkeypatch.setattr(module, "_load_sdk", lambda directory: sdk)
    clock = [0.0]

    def sleep(seconds):
        clock[0] += seconds

    monkeypatch.setattr(module, "time", SimpleNamespace(sleep=sleep, monotonic=lambda: clock[0]))
    return SimpleNamespace(
        device=device,
        controller=KSC101Controller(timeout=0.5),
        serials=serials,
        manager_calls=manager_calls,
        clock=clock,
    )
