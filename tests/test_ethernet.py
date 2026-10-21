"""Ethernet selection/health with software devices; never imports the real SDK."""

from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import KCubeShutter, ShutterError


@pytest.fixture
def ethernet(rig, monkeypatch):
    rig.controller.discover()
    manager = rig.controller._sdk.manager
    entries = []
    transport = {"provider": "TCPIP", "endpoint": "192.0.2.10:40304"}
    monkeypatch.setattr(manager, "CreateManualDeviceEntry", entries.append, raising=False)
    monkeypatch.setattr(
        manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: transport["provider"],
            GetComSpec=lambda: transport["endpoint"],
        ),
        raising=False,
    )
    controller = KCubeShutter("68000001", ethernet_endpoint=transport["endpoint"], timeout=0.5)
    return SimpleNamespace(controller=controller, transport=transport, entries=entries, rig=rig)


@pytest.mark.parametrize(
    "endpoint",
    [
        "192.0.2.10",
        "192.0.2.10:40303",
        "192.0.2.10:80",
        "bad:40304",
        "::1:40304",
        1,
        b"192.0.2.10:40304",
    ],
)
def test_invalid_endpoint_never_loads_sdk(endpoint, rig):
    with pytest.raises(ValueError, match="ethernet_endpoint"):
        KCubeShutter(ethernet_endpoint=endpoint)
    assert not rig.device.calls and not rig.manager_calls


def test_ethernet_passive_connection_does_not_require_usb_or_write_output(ethernet, monkeypatch):
    d = ethernet.rig.device
    connect = d.Connect

    def ethernet_connect(serial):
        connect(serial)
        d.USBConnected = "Disconnected"

    monkeypatch.setattr(d, "Connect", ethernet_connect)
    try:
        assert ethernet.controller.connect().connection == "connected"
        assert ethernet.controller.identify_device()["serial_number"] == "68000001"
        assert ethernet.controller.get_status().connection == "connected"
    finally:
        ethernet.controller.disconnect(close_shutter=False)
    assert ethernet.entries == ["192.0.2.10:40304"]
    assert d.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert not any(c[0] in {"set_state", "set_mode", "enable", "set_triggers"} for c in d.calls)


@pytest.mark.parametrize("field, value", [("provider", "FTDI"), ("endpoint", "192.0.2.10:40305")])
def test_wrong_transport_is_not_discovered_or_connected(ethernet, field, value):
    ethernet.transport[field] = value
    assert ethernet.controller.discover() == []
    with pytest.raises(ShutterError, match="not discovered"):
        ethernet.controller.connect()
    assert not ethernet.rig.device.calls


def test_transport_change_between_discovery_and_factory_is_refused(ethernet, monkeypatch):
    discover = ethernet.controller.discover

    def changed():
        serials = discover()
        ethernet.transport["provider"] = "FTDI"
        return serials

    monkeypatch.setattr(ethernet.controller, "discover", changed)
    with pytest.raises(ShutterError, match="transport changed"):
        ethernet.controller.connect()
    assert not ethernet.rig.device.calls
    ethernet.transport["provider"] = "TCPIP"
    monkeypatch.setattr(ethernet.controller, "discover", discover)
    assert ethernet.controller.connect().connection == "connected"
    ethernet.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize("failure", ["provider", "endpoint", "connection", "comms"])
def test_ethernet_health_failure_latches_fault_without_output(ethernet, monkeypatch, failure):
    ethernet.controller.connect()
    d = ethernet.rig.device
    if failure == "provider":
        ethernet.transport["provider"] = "FTDI"
    elif failure == "endpoint":
        ethernet.transport["endpoint"] = "192.0.2.10:40305"
    elif failure == "connection":
        d.IsConnected = False
    else:
        d.CommsStatus = "Timeout"
    status = ethernet.controller.get_status()
    assert status.connection == "fault" and status.shutter_state == "unknown"
    with pytest.raises(ShutterError):
        ethernet.controller.open_shutter()
    ethernet.controller.disconnect(close_shutter=False)
    assert not any(c[0] in {"set_state", "set_mode", "enable", "set_triggers"} for c in d.calls)


def test_ethernet_and_usb_share_serial_ownership(ethernet):
    ethernet.controller.connect()
    with pytest.raises(ShutterError, match="already owned"):
        ethernet.rig.controller.connect("68000001")
    ethernet.controller.disconnect(close_shutter=False)
    assert ethernet.rig.controller.connect("68000001").connection == "connected"
    ethernet.rig.controller.disconnect(close_shutter=False)


def test_ethernet_identity_mismatch_keeps_existing_guard(ethernet, monkeypatch):
    monkeypatch.setattr(
        ethernet.rig.device,
        "GetDeviceInfo",
        lambda: SimpleNamespace(SerialNumberText="68000099", Description="MISMATCH"),
    )
    with pytest.raises(ShutterError, match="identity mismatch"):
        ethernet.controller.connect()
    assert ethernet.rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
