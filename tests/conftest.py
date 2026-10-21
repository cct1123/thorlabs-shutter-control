"""Small protocol double: no DLL loading, sockets, physical timing or TTL model."""

from copy import copy
from types import SimpleNamespace as NS

import pytest

from thorlabs_shutter_control import config, controller


class TriggerSettings:
    TriggerPortMode = NS(Disabled="Disabled", TrigIN_GPI="TrigIN_GPI", TrigOUT_GPO="TrigOUT_GPO")
    TriggerPolarity = NS(TriggerHigh="TriggerHigh", TriggerLow="TriggerLow")

    def __init__(self):
        self.Trigger1Mode, self.Trigger1Polarity = "TrigIN_GPI", "TriggerHigh"
        self.Trigger2Mode, self.Trigger2Polarity = "TrigOUT_GPO", "TriggerHigh"


class Device:
    def __init__(self, serial):
        self.serial = self.identity = serial
        self.IsConnected, self.USBConnected = False, "Disconnected"
        self.CommsStatus, self.Status = "OK", NS(KeyEnabled=True)
        self.position, self.operation, self.mode = "Closed", "Inactive", "Manual"
        self.calls, self.fail, self.polling = [], None, 0
        self.settings = TriggerSettings()

    def record(self, name, *args):
        self.calls.append((name, *args))
        if self.fail == name:
            raise RuntimeError(f"{name} failed")

    def Connect(self, serial):
        self.record("connect", serial)
        self.IsConnected, self.USBConnected = True, "Connected"

    def IsSettingsInitialized(self):
        return True

    def StartPolling(self, milliseconds):
        self.record("poll", milliseconds)
        self.polling = milliseconds

    def PollingDuration(self):
        return self.polling

    def GetDeviceInfo(self):
        self.record("identity")
        return NS(SerialNumberText=self.identity, Description="FICTIONAL SOFTWARE DEVICE")

    def RequestStatus(self):
        self.record("status")

    def RequestOperatingState(self):
        self.record("operation")

    def RequestOperatingMode(self):
        self.record("mode_read")

    def GetStatusBits(self):
        return 0x2000

    def GetSolenoidState(self):
        return self.position

    def GetOperatingState(self):
        return self.operation

    def GetOperatingMode(self):
        return self.mode

    def SetOperatingState(self, value):
        self.record("state", value)
        self.operation = value
        self.position = "Open" if value == "Active" else "Closed"

    def SetOperatingMode(self, value):
        self.record("mode", value)
        self.mode = value

    def EnableDevice(self):
        self.record("enable")

    def RequestTriggerConfigParams(self):
        self.record("ttl_read")

    def GetTriggerConfigParams(self):
        return copy(self.settings)

    def SetTriggerConfigParams(self, settings):
        self.record("ttl_write")
        self.settings = copy(settings)

    def StopPolling(self):
        self.record("stop_poll")
        self.polling = 0

    def Disconnect(self):
        self.record("disconnect")
        self.IsConnected, self.USBConnected = False, "Disconnected"


class Manager:
    def __init__(self, routes):
        self.routes, self.entries, self.calls = routes, [], []
        self.refreshes, self.ready_after, self.scan_error = 0, 1, False

    def BuildDeviceList(self):
        self.calls.append(("build",))
        self.refreshes = 0

    def CreateManualDeviceEntry(self, endpoint):
        self.entries.append(endpoint)

    def CheckForConnectionChanges(self):
        self.refreshes += 1

    def GetDeviceList(self, kind):
        return [
            s
            for s, endpoint in self.routes.items()
            if endpoint is None or (endpoint in self.entries and self.refreshes >= self.ready_after)
        ]

    def GetTransportInfo(self, serial):
        endpoint = self.routes[serial]
        return NS(
            GetProvider=lambda: "TCPIP" if endpoint else "FTDI",
            GetComSpec=lambda: endpoint or "USB",
        )

    def ScanEthernetRange(self, start, end, port, timeout):
        self.calls.append(("scan", start, end, port, timeout))
        if self.scan_error:
            raise RuntimeError("LAN scan failed")
        return ["192.0.2.10"]


@pytest.fixture
def bench(monkeypatch):
    usb, lan = Device("68000001"), Device("68000002")
    devices = {d.serial: d for d in (usb, lan)}
    endpoint = "192.0.2.10:40304"
    manager = Manager({usb.serial: None, lan.serial: endpoint})
    sdk = NS(
        manager=manager,
        device_type=NS(CreateKCubeSolenoid=devices.__getitem__),
        trigger_settings=TriggerSettings,
        enums=NS(
            OperatingStates=NS(Active="Active", Inactive="Inactive"),
            OperatingModes=NS(
                Manual="Manual",
                SingleToggle="SingleToggle",
                AutoToggle="AutoToggle",
                Triggered="Triggered",
            ),
        ),
    )
    loads, clock = [], [0.0]

    def load(directory):
        loads.append(directory)
        return sdk

    def sleep(seconds):
        clock[0] += seconds

    monkeypatch.setattr(controller, "_load_sdk", load)
    monkeypatch.setattr(controller, "_device_owners", {})
    monkeypatch.setattr(controller, "time", NS(sleep=sleep, monotonic=lambda: clock[0]))
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")
    return NS(usb=usb, lan=lan, devices=devices, manager=manager, endpoint=endpoint, loads=loads)
