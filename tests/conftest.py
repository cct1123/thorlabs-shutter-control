"""Software-only .NET test double. It never imports Kinesis or contacts hardware."""

from copy import copy
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import KCubeShutter
from thorlabs_shutter_control import controller as module


class FakeTriggerSettings:
    TriggerPortMode = SimpleNamespace(
        Disabled="Disabled", TrigIN_GPI="TrigIN_GPI", TrigOUT_GPO="TrigOUT_GPO"
    )
    TriggerPolarity = SimpleNamespace(TriggerHigh="TriggerHigh", TriggerLow="TriggerLow")

    def __init__(self):
        self.Trigger1Mode = "TrigIN_GPI"
        self.Trigger1Polarity = "TriggerHigh"
        self.Trigger2Mode = "TrigOUT_GPO"
        self.Trigger2Polarity = "TriggerHigh"


class FakeDevice:
    def __init__(self, serial="68000001"):
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
        self.serial = serial  # Explicitly fictional test identity.
        self.fail = set()
        self.trigger_config = FakeTriggerSettings()
        self.inputs = [False, False]  # KSC101 open/disconnected trigger input is LOW.

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
        if self.mode == "Triggered":
            self._trigger_state()

    def _trigger_state(self):
        active = any(
            getattr(self.trigger_config, f"Trigger{port}Mode") == "TrigIN_GPI"
            and self.inputs[port - 1]
            == (getattr(self.trigger_config, f"Trigger{port}Polarity") == "TriggerHigh")
            for port in (1, 2)
        )
        self.state = (
            "Open"
            if (self.operation == "Active" and active and self.Status.KeyEnabled and self.interlock)
            else "Closed"
        )

    def GetStatusBits(self):
        return 0x1000 if self.interlock else 0

    def GetSolenoidState(self):
        return self.state

    def GetOperatingState(self):
        return self.operation

    def RequestOperatingState(self):
        self.record("request_operation")

    def RequestOperatingMode(self):
        self.record("request_mode")

    def GetOperatingMode(self):
        return self.mode

    def SetOperatingState(self, state):
        self.record("set_state", state)
        self.operation = state
        self.state = "Open" if state == "Active" else "Closed"
        if self.mode == "Triggered":
            self._trigger_state()

    def SetOperatingMode(self, mode):
        self.record("set_mode", mode)
        self.mode = mode
        if mode == "Manual":
            self.state = "Open" if self.operation == "Active" else "Closed"

    def EnableDevice(self):
        self.record("enable")

    def RequestTriggerConfigParams(self):
        self.record("request_triggers")

    def GetTriggerConfigParams(self):
        self.record("get_triggers")
        return copy(self.trigger_config)

    def SetTriggerConfigParams(self, config):
        self.record("set_triggers", copy(config))
        self.trigger_config = copy(config)

    def StopPolling(self):
        self.record("stop_poll")
        self.polling = 0

    def Disconnect(self):
        self.record("disconnect")
        self.IsConnected = False
        self.USBConnected = "Disconnected"


@pytest.fixture
def rig(monkeypatch):
    devices = {f"6800000{index}": FakeDevice(f"6800000{index}") for index in range(1, 4)}
    device = devices["68000001"]
    serials = [device.serial]
    manager_calls = []
    sdk = SimpleNamespace(
        manager=SimpleNamespace(
            BuildDeviceList=lambda: manager_calls.append("discover"),
            GetDeviceList=lambda type_id: serials if type_id == 68 else [],
        ),
        device_type=SimpleNamespace(CreateKCubeSolenoid=lambda serial: devices[serial]),
        enums=SimpleNamespace(
            OperatingStates=SimpleNamespace(Active="Active", Inactive="Inactive"),
            OperatingModes=SimpleNamespace(Manual="Manual", Triggered="Triggered"),
        ),
        trigger_settings=FakeTriggerSettings,
    )
    monkeypatch.setattr(module, "_device_owners", {}, raising=False)
    monkeypatch.setattr(module, "_load_sdk", lambda directory: sdk)
    clock = [0.0]

    def sleep(seconds):
        clock[0] += seconds

    monkeypatch.setattr(module, "time", SimpleNamespace(sleep=sleep, monotonic=lambda: clock[0]))
    return SimpleNamespace(
        device=device,
        devices=devices,
        controller=KCubeShutter(timeout=0.5),
        serials=serials,
        manager_calls=manager_calls,
    )
