import inspect
from types import SimpleNamespace

import pytest
from test_gui import invoke

from thorlabs_shutter_control import KCubeShutter, ShutterError, ShutterHub, TriggerConfig
from thorlabs_shutter_control import controller as controller_module
from thorlabs_shutter_control import controller as driver
from thorlabs_shutter_control.gui import create_app


def three_shutters(rig):
    rig.serials[:] = list(rig.devices)
    hub = ShutterHub(controllers=[KCubeShutter(timeout=0.5) for _ in range(3)])
    for slot, serial in enumerate(rig.serials):
        hub.connect(slot, serial)
    return hub


def test_default_construction_and_disconnected_shutdown_do_not_load_sdk(monkeypatch):
    def forbidden_sdk_load(directory):
        pytest.fail("Passive hub construction/shutdown must not load the SDK.")

    monkeypatch.setattr(controller_module, "_load_sdk", forbidden_sdk_load)
    hub = ShutterHub()
    assert len(hub.controllers) == 3
    assert len({id(controller) for controller in hub.controllers}) == 3
    assert all(not controller.get_status().has_device for controller in hub.controllers)
    hub.safe_shutdown()


@pytest.mark.parametrize("serials", [["68000001"] * 2, ["68000001"] * 4, ["invalid"]])
def test_invalid_serial_configuration_is_rejected_without_device_access(rig, serials):
    with pytest.raises(ValueError):
        ShutterHub(serials)
    assert rig.manager_calls == []
    assert all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("preselected", [None, "68000001"])
def test_missing_selection_never_automatically_connects(rig, preselected):
    hub = ShutterHub(controllers=[KCubeShutter(preselected)])
    with pytest.raises(ShutterError, match="Select a KSC101 serial"):
        hub.connect(0, None)
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, SystemExit])
def test_shutdown_preserves_interrupt_after_attempting_every_slot(rig, monkeypatch, exception_type):
    hub = three_shutters(rig)
    for controller in hub.controllers:
        controller.open_shutter()
    interrupt = exception_type("Injected interruption")

    def interrupt_close():
        raise interrupt

    monkeypatch.setattr(hub.controllers[0], "close_shutter", interrupt_close)
    rig.devices["68000002"].fail.add("set_state")
    with pytest.raises(exception_type) as caught:
        hub.safe_shutdown()
    assert caught.value is interrupt
    assert "Shutter 1 (68000001)" in interrupt.__notes__[-1]
    assert "Shutter 2 (68000002)" in interrupt.__notes__[-1]
    assert all(not device.IsConnected for device in rig.devices.values())
    assert rig.devices["68000003"].state == "Closed"


def test_serial_count_expands_default_and_explicit_count_must_fit(rig):
    serials = [f"6800{n:04d}" for n in range(1, 10)]  # Fictional test identities.
    hub = ShutterHub(serials)
    assert [c.serial_number for c in hub.controllers] == serials
    assert len(ShutterHub(controllers=hub.controllers).controllers) == 9
    with pytest.raises(ValueError, match="fit all supplied"):
        ShutterHub(serials, slots=6)
    assert not rig.manager_calls and not rig.device.calls


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
    hub = ShutterHub([68000001], slots=1, ethernet_endpoints=(transport["endpoint"],))
    return SimpleNamespace(hub=hub, transport=transport, entries=entries, rig=rig)


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
        ShutterHub(ethernet_endpoints=(endpoint,), slots=1)
    assert not rig.device.calls and not rig.manager_calls


def test_ethernet_passive_connection_does_not_require_usb_or_write_output(ethernet, monkeypatch):
    d = ethernet.rig.device
    connect = d.Connect

    def ethernet_connect(serial):
        connect(serial)
        d.USBConnected = "Disconnected"

    monkeypatch.setattr(d, "Connect", ethernet_connect)
    try:
        assert ethernet.hub.connect(0, 68000001).connection == "connected"
        assert ethernet.hub.identify_device(0)["serial_number"] == "68000001"
        assert ethernet.hub.get_status(0).connection == "connected"
    finally:
        ethernet.hub.disconnect(0, close_shutter=False)
    assert ethernet.entries == ["192.0.2.10:40304"]
    assert d.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert not any(c[0] in {"set_state", "set_mode", "enable", "set_triggers"} for c in d.calls)


def test_lan_only_discovery_refreshes_tcpip_identities_without_usb_devices(rig, monkeypatch):
    sdk = driver._load_sdk(None)
    registered = []

    events = []

    def register(endpoint):
        registered.append(endpoint)
        events.append("register")

    def build():
        assert registered  # Manual TCPIP route must exist before the SDK rebuild.
        events.append("build")

    def refresh():
        assert events[-1] in {"build", "refresh"}
        events.append("refresh")
        return {"68000001": True}

    monkeypatch.setattr(sdk.manager, "BuildDeviceList", build)
    monkeypatch.setattr(sdk.manager, "CheckForConnectionChanges", refresh)
    monkeypatch.setattr(sdk.manager, "CreateManualDeviceEntry", register, raising=False)
    monkeypatch.setattr(
        sdk.manager,
        "GetDeviceList",
        lambda type_id: ["68000001"] if events[-1:] == ["refresh"] else [],
    )
    monkeypatch.setattr(
        sdk.manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: "TCPIP", GetComSpec=lambda: "192.0.2.10:40304"
        ),
    )
    hub = ShutterHub(ethernet_endpoints=["192.0.2.10:40304"])
    assert len(hub.controllers) == 1
    assert hub.discover() == ["68000001"]
    assert hub.connect(0, "68000001").serial_number == "68000001"
    hub.disconnect(0, close_shutter=False)
    assert registered == ["192.0.2.10:40304"] * 2
    assert events == ["register", "build", "refresh"] * 2
    assert not any(c[0] in {"set_state", "set_mode", "enable"} for c in rig.device.calls)


@pytest.mark.parametrize("responds", [True, False])
def test_lan_discovery_waits_for_async_refresh_without_restarting_build(rig, monkeypatch, responds):
    sdk = driver._load_sdk(None)
    events = []
    polls = []
    monkeypatch.setattr(
        sdk.manager, "CreateManualDeviceEntry", lambda ep: events.append(ep), raising=False
    )
    monkeypatch.setattr(sdk.manager, "BuildDeviceList", lambda: events.append("build"))
    monkeypatch.setattr(sdk.manager, "CheckForConnectionChanges", lambda: polls.append("refresh"))
    monkeypatch.setattr(
        sdk.manager,
        "GetDeviceList",
        lambda type_id: ["68000001"] if responds and len(polls) >= 4 else [],
    )
    monkeypatch.setattr(
        sdk.manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: "TCPIP", GetComSpec=lambda: "192.0.2.10:40304"
        ),
    )
    hub = ShutterHub(ethernet_endpoints=["192.0.2.10:40304"])
    start = driver.time.monotonic()
    assert hub.discover() == (["68000001"] if responds else [])
    assert events == ["192.0.2.10:40304", "build"]
    assert len(polls) >= 4
    assert driver.time.monotonic() - start == pytest.approx(0.3 if responds else 5.0)
    assert not rig.device.calls  # No Connect or output commands during discovery.


@pytest.mark.parametrize("field, value", [("provider", "FTDI"), ("endpoint", "192.0.2.10:40305")])
def test_wrong_transport_is_not_discovered_or_connected(ethernet, field, value):
    ethernet.transport[field] = value
    assert ethernet.hub.discover() == []
    with pytest.raises(ShutterError, match="not discovered"):
        ethernet.hub.connect(0, 68000001)
    assert not ethernet.rig.device.calls


def test_cube_has_no_network_option_and_filters_registered_network_devices(ethernet):
    assert "ethernet_endpoint" not in inspect.signature(KCubeShutter).parameters
    assert not hasattr(KCubeShutter(), "ethernet_endpoint")
    with pytest.raises(TypeError):
        KCubeShutter(ethernet_endpoint="192.0.2.10:40304")
    assert ethernet.hub.discover() == ["68000001"]
    assert ethernet.rig.controller.discover() == []  # Network registration cannot contaminate USB.
    assert not ethernet.rig.device.calls


def test_transport_change_before_handle_creation_is_refused(ethernet, monkeypatch):
    channel = ethernet.hub.controllers[0]
    discover = channel.discover

    def changed():
        serials = discover()
        ethernet.transport["provider"] = "FTDI"
        return serials

    monkeypatch.setattr(channel, "discover", changed)
    with pytest.raises(ShutterError, match="transport changed"):
        ethernet.hub.connect(0, 68000001)
    assert not ethernet.rig.device.calls


def test_endpoint_configuration_is_passive_and_immutable(rig):
    hub = ShutterHub([68000001], ethernet_endpoints=["192.0.2.10:40304"])
    assert hub.ethernet_endpoints == ("192.0.2.10:40304",)
    mixed = ShutterHub(slots=3, ethernet_endpoints=["192.0.2.10:40304"])
    assert mixed.ethernet_endpoints == ("192.0.2.10:40304", None, None)
    with pytest.raises(AttributeError):
        hub.ethernet_endpoints = (None,)
    with pytest.raises(ValueError, match="slots must fit"):
        ShutterHub(slots=1, ethernet_endpoints=[None, "192.0.2.10:40304"])
    with pytest.raises(ValueError, match="injected"):
        ShutterHub(controllers=[rig.controller], ethernet_endpoints=["192.0.2.10:40304"])
    assert not rig.manager_calls and not rig.device.calls


@pytest.mark.parametrize(
    "method,args,writes",
    [
        ("enable_device", (), ["enable"]),
        ("open_shutter", (), ["set_state"]),
        ("close_shutter", (), ["set_state"]),
        ("arm_triggers", (), ["enable", "set_mode", "set_state"]),
        ("disarm_triggers", (), ["set_state", "set_mode"]),
        ("configure_triggers", (TriggerConfig(),), ["set_triggers"]),
        ("set_operating_mode", ("auto",), ["set_mode"]),
        ("set_operating_state", ("active",), ["set_state"]),
        ("set_operating_state", ("inactive",), ["set_state"]),
    ],
)
def test_hub_network_setters_send_only_writes(ethernet, monkeypatch, method, args, writes):
    hub, device = ethernet.hub, ethernet.rig.device
    hub.connect(0, 68000001)
    device.calls.clear()

    def forbidden(*args, **kwargs):
        pytest.fail("Hub setter requested feedback or waited")

    for name in dir(device):
        if name.startswith(("Get", "Request")):
            monkeypatch.setattr(device, name, forbidden)
    monkeypatch.setattr(driver.time, "sleep", forbidden)
    assert getattr(hub, method)(0, *args) is None
    assert [call[0] for call in device.calls] == writes
    hub.disconnect(0, close_shutter=False)


@pytest.mark.parametrize(
    "method,args",
    [
        ("open_shutter", ()),
        ("arm_triggers", ()),
        ("configure_triggers", (TriggerConfig(),)),
        ("set_operating_mode", ("triggered",)),
        ("set_operating_state", ("active",)),
    ],
)
def test_hub_refuses_output_after_route_changes_without_fallback(ethernet, method, args):
    ethernet.hub.connect(0, 68000001)
    ethernet.rig.device.calls.clear()
    ethernet.transport["endpoint"] = "192.0.2.10:40305"
    with pytest.raises(ShutterError, match="transport changed"):
        getattr(ethernet.hub, method)(0, *args)
    assert not ethernet.rig.device.calls
    assert ethernet.hub.get_cached_status(0).connection == "fault"
    ethernet.hub.disconnect(0, close_shutter=False)
    assert ethernet.entries == ["192.0.2.10:40304"]


def test_mixed_hub_routes_each_serial_to_its_configured_transport(rig, monkeypatch):
    rig.serials[:] = list(rig.devices)
    routes = {
        "68000001": ("FTDI", "USB"),
        "68000002": ("TCPIP", "192.0.2.10:40304"),
        "68000003": ("TCPIP", "192.0.2.10:40305"),
    }
    sdk = driver._load_sdk(None)
    entries = []

    def build_device_list():
        rig.manager_calls.append("discover")
        if entries:  # A USB slot also performs its own independent USB enumeration.
            assert entries[-2:] == ["192.0.2.10:40304", "192.0.2.10:40305"]

    monkeypatch.setattr(sdk.manager, "BuildDeviceList", build_device_list)
    monkeypatch.setattr(sdk.manager, "CreateManualDeviceEntry", entries.append, raising=False)
    monkeypatch.setattr(
        sdk.manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: routes[serial][0], GetComSpec=lambda: routes[serial][1]
        ),
    )
    hub = ShutterHub(
        rig.serials,
        slots=3,
        ethernet_endpoints=[None, routes["68000002"][1], routes["68000003"][1]],
    )
    assert hub.discover() == rig.serials
    assert rig.manager_calls == ["discover"]
    assert entries == ["192.0.2.10:40304", "192.0.2.10:40305"]
    app = create_app(hub)
    result = invoke(app, "discover", serials=[None, None, None])
    assert rig.manager_calls == ["discover"] * 3  # USB + configured routes, shared by all panels.
    for index, _serial in enumerate(rig.serials, 1):
        assert [item["value"] for item in result[f"serial-{index}"]["options"]] == rig.serials
    assert all(not device.calls for device in rig.devices.values())
    for slot, serial in enumerate(rig.serials):
        entries.clear()
        assert hub.connect(slot, serial).serial_number == serial
        if slot:
            rig.devices[serial].USBConnected = "Disconnected"  # TCP/IP has no USB dependency.
        assert hub.get_status(slot).connection == "connected"
    for device in rig.devices.values():
        device.calls.clear()
    hub.open_shutter(1)
    assert hub.get_shutter_state(1) == "open"
    assert hub.get_operating_state(1) == "active"
    assert hub.get_operating_mode(1) == "manual"
    assert hub.get_status_bits(1) == 0x1000
    assert not rig.devices["68000001"].calls and not rig.devices["68000003"].calls
    assert hub.get_cached_status(0).serial_number == "68000001"
    # A serial from another bay must not be sent to this slot, even if it is enumerated.
    hub.disconnect(1)
    entries.clear()
    with pytest.raises(ShutterError, match="not discovered"):
        hub.connect(1, 68000003)
    rig.devices["68000001"].fail.add("set_state")
    with pytest.raises(ShutterError, match="Shutter 1"):
        hub.safe_shutdown()
    assert all(not device.IsConnected for device in rig.devices.values())
    assert rig.devices["68000003"].calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_gui_uses_hub_dispatch_for_network_commands(ethernet, monkeypatch):
    hub = ethernet.hub
    app = create_app(hub)
    assert invoke(app, "connect", serial="68000001")["connection"]["children"] == "Connected"
    open_shutter = hub.open_shutter
    dispatched = []

    def open_slot(slot):
        dispatched.append(slot)
        return open_shutter(slot)

    monkeypatch.setattr(hub, "open_shutter", open_slot)
    assert invoke(app, "open", serial="68000001")["shutter-state"]["children"] == "Open"
    assert dispatched == [0]
    assert invoke(app, "close", serial="68000001")["shutter-state"]["children"] == "Closed"
    invoke(app, "disconnect", serial="68000001")
    assert not ethernet.rig.device.IsConnected


def test_gui_lan_discovery_preserves_a_retained_identity_after_route_loss(ethernet):
    hub = ethernet.hub
    hub.connect(0, "68000001")
    app = create_app(hub)
    ethernet.transport["provider"] = "FTDI"
    result = invoke(app, "discover", serial="68000001")
    assert [item["value"] for item in result["serial"]["options"]] == ["68000001"]
    assert result["serial"]["value"] == "68000001"
    assert result["connection"]["children"] == "Fault"
    assert result["disconnect"]["disabled"] is False
    hub.disconnect(0, close_shutter=False)
    assert not any(
        call[0] in {"enable", "set_state", "set_mode"} for call in ethernet.rig.device.calls
    )


def test_configure_slot_preserves_retained_handle_until_release(ethernet):
    hub = ShutterHub([68000001], slots=1)
    endpoint = "192.0.2.10:40304"
    before = list(ethernet.rig.manager_calls)
    hub.configure_slot(0, ethernet_endpoint=endpoint)
    assert hub.controllers[0].serial_number is None
    assert ethernet.rig.manager_calls == before and not ethernet.rig.device.calls
    hub.connect(0, "68000001")
    old = hub.controllers[0]
    with pytest.raises(ShutterError, match="Disconnect"):
        hub.configure_slot(0)
    ethernet.rig.device.fail.add("disconnect")
    with pytest.raises(ShutterError, match="Shutdown incomplete"):
        hub.disconnect(0, close_shutter=False)
    with pytest.raises(ShutterError, match="Disconnect"):
        hub.configure_slot(0)
    assert hub.controllers[0] is old
    ethernet.rig.device.fail.clear()
    hub.disconnect(0, close_shutter=False)
    hub.configure_slot(0)
    assert hub.ethernet_endpoints == (None,)
    assert isinstance(hub.controllers[0], KCubeShutter)
    assert hub.controllers[0].serial_number is None
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in ethernet.rig.device.calls)


@pytest.mark.parametrize("endpoint", ["", "not-an-ip:40304", "192.0.2.10:40303"])
def test_invalid_route_configuration_is_passive_and_preserves_route(rig, endpoint):
    hub = ShutterHub(controllers=[rig.controller])
    with pytest.raises(ValueError, match="ethernet_endpoints"):
        hub.configure_slot(0, ethernet_endpoint=endpoint)
    assert hub.controllers == (rig.controller,) and hub.ethernet_endpoints == (None,)
    assert not rig.manager_calls and not rig.device.calls


def test_failed_network_release_retains_ownership_until_retry(ethernet):
    device = ethernet.rig.device
    device.fail.update({"poll", "disconnect"})
    with pytest.raises(ShutterError, match="Connect failed"):
        ethernet.hub.connect(0, 68000001)
    assert ethernet.hub.get_cached_status(0).has_device
    replacement = ShutterHub([68000001], slots=1, ethernet_endpoints=["192.0.2.10:40304"])
    with pytest.raises(ShutterError, match="already owned"):
        replacement.connect(0, 68000001)
    device.fail.clear()
    ethernet.hub.disconnect(0, close_shutter=False)
    assert replacement.connect(0, 68000001).connection == "connected"
    replacement.disconnect(0, close_shutter=False)
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in device.calls)
