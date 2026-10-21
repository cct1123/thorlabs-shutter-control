from types import SimpleNamespace

import pytest
from test_gui import invoke

from thorlabs_shutter_control import KCubeShutter, ShutterError, ShutterHub, config
from thorlabs_shutter_control import controller as driver
from thorlabs_shutter_control.gui import create_app


@pytest.fixture
def lan(rig, monkeypatch):
    # All addresses and identities in this fixture are fictional.
    sdk = driver._load_sdk(None)
    events = []
    addresses = [
        "192.0.2.10",
        "192.0.2.11",
        "192.0.2.10",
        "bad",
        "192.0.3.10",
        "192.0.2.12:80",
    ]
    routes = {
        "68000001": ("TCPIP", "192.0.2.10:40304"),
        "68000002": ("TCPIP", "192.0.2.11:40306"),
        "68000003": ("FTDI", "USB"),
        "68000004": ("TCPIP", "192.0.2.99:40304"),
        "68000005": ("TCPIP", "192.0.2.10:40303"),
        "12000001": ("TCPIP", "192.0.2.10:40304"),
    }

    def scan(*args):
        events.append(("scan", *args))
        return addresses

    monkeypatch.setattr(sdk.manager, "ScanEthernetRange", scan, raising=False)
    monkeypatch.setattr(
        sdk.manager,
        "CreateManualDeviceEntry",
        lambda ep: events.append(("register", ep)),
        raising=False,
    )
    monkeypatch.setattr(sdk.manager, "BuildDeviceList", lambda: events.append(("build",)))
    refreshes = []

    def refresh():
        refreshes.append(True)
        events.append(("refresh",))

    monkeypatch.setattr(sdk.manager, "CheckForConnectionChanges", refresh)
    monkeypatch.setattr(
        sdk.manager,
        "GetDeviceList",
        lambda kind: (
            (list(routes) if len(refreshes) >= 3 else [s for s in routes if routes[s][0] == "FTDI"])
            if kind == 68
            else []
        ),
    )
    monkeypatch.setattr(
        sdk.manager,
        "GetTransportInfo",
        lambda serial: SimpleNamespace(
            GetProvider=lambda: routes[serial][0], GetComSpec=lambda: routes[serial][1]
        ),
    )
    hub = ShutterHub(controllers=[KCubeShutter(timeout=0.5)])
    return SimpleNamespace(
        hub=hub, sdk=sdk, events=events, addresses=addresses, routes=routes, rig=rig
    )


def test_scan_enumerates_all_bays_and_filters_exact_tcpip_cube_identities(lan):
    old = lan.hub.controllers[0]
    result = lan.hub.scan_lan("192.0.2.0", "192.0.2.255")
    assert result.hub_addresses == ("192.0.2.10", "192.0.2.11")
    assert [(d.serial_number, d.endpoint) for d in result.controllers] == [
        ("68000001", "192.0.2.10:40304"),
        ("68000002", "192.0.2.11:40306"),
    ]
    assert lan.events[0] == ("scan", "192.0.2.0", "192.0.2.255", 40303, 100)
    assert lan.events[1:9] == [
        ("register", f"192.0.2.{host}:{port}") for host in (10, 11) for port in range(40304, 40308)
    ]
    assert lan.events[9] == ("build",)
    assert lan.events.count(("build",)) == 1
    assert lan.hub.controllers[0] is old and lan.hub.ethernet_endpoints == (None,)
    assert not any(d.calls for d in lan.rig.devices.values())


@pytest.mark.parametrize(
    "start,end",
    [
        ("invalid", "192.0.2.255"),
        ("::1", "::2"),
        ("192.0.2.10", "192.0.2.1"),
        ("192.0.2.0", "192.0.3.0"),
    ],
)
def test_scan_rejects_bad_or_oversized_ranges_before_sdk_access(lan, start, end):
    with pytest.raises(ValueError, match="LAN range"):
        lan.hub.scan_lan(start, end)
    assert not lan.events


@pytest.mark.parametrize("address", [True, 3232235776, b"\xc0\xa8\x01\x00"])
def test_scan_does_not_interpret_non_string_values_as_ipv4_addresses(lan, address):
    with pytest.raises(ValueError, match="IPv4 address strings"):
        lan.hub.scan_lan(address, address)
    assert not lan.events


@pytest.mark.parametrize("timeout", [True, 0, 49, 1001, float("nan")])
def test_scan_rejects_bad_timeout_before_sdk_access(lan, timeout):
    with pytest.raises(ValueError, match="timeout"):
        lan.hub.scan_lan(open_timeout_ms=timeout)
    assert not lan.events


def test_empty_scan_does_not_register_or_build(lan):
    lan.addresses.clear()
    result = lan.hub.scan_lan()
    assert result.hub_addresses == () and result.controllers == ()
    assert lan.events == [("scan", "192.168.1.0", "192.168.1.255", 40303, 100)]


def test_scan_does_not_acquire_channel_lock_inside_sdk_lock(lan, monkeypatch):
    def forbidden():
        pytest.fail("Channel locks must not be acquired after the SDK lock")

    monkeypatch.setattr(lan.hub.controllers[0], "get_cached_status", forbidden)
    lan.addresses.clear()
    assert lan.hub.scan_lan().controllers == ()


def test_hub_without_compatible_cubes_returns_hub_identity_only(lan):
    lan.routes.clear()
    result = lan.hub.scan_lan("192.0.2.0", "192.0.2.255")
    assert result.hub_addresses == ("192.0.2.10", "192.0.2.11")
    assert result.controllers == ()


def test_scan_sdk_error_is_contextual_and_does_not_change_route(lan, monkeypatch):
    def fail(*args):
        raise RuntimeError("injected SDK failure")

    monkeypatch.setattr(lan.sdk.manager, "ScanEthernetRange", fail)
    with pytest.raises(ShutterError, match="LAN discovery failed: injected SDK failure"):
        lan.hub.scan_lan()
    assert lan.hub.ethernet_endpoints == (None,)
    assert not lan.rig.device.calls


def test_scan_refuses_retained_handles_even_in_another_hub(lan, monkeypatch):
    monkeypatch.setattr(lan.sdk.manager, "GetDeviceList", lambda kind: ["68000003"])
    lan.rig.controller.connect("68000003")
    lan.events.clear()
    with pytest.raises(ShutterError, match="Disconnect all"):
        lan.hub.scan_lan()
    lan.rig.devices["68000003"].fail.add("disconnect")
    with pytest.raises(ShutterError):
        lan.rig.controller.disconnect(close_shutter=False)
    with pytest.raises(ShutterError, match="Disconnect all"):
        lan.hub.scan_lan()
    assert not lan.events
    lan.rig.devices["68000003"].fail.clear()
    lan.rig.controller.disconnect(close_shutter=False)


def test_discover_combines_usb_lan_and_connect_selects_detected_route(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")
    app = create_app(lan.hub)
    layout = app.server.test_client().get("/_dash-layout").get_data(as_text=True)
    for removed in (
        "connection-type",
        "lan-endpoint",
        "apply-connection",
        "lan-device",
        "use-lan-device",
        "scan-lan",
        "lan-start",
        "lan-end",
        "Find devices on the LAN",
    ):
        assert removed not in layout
    result = invoke(app, "discover")
    assert result["serial"]["options"] == [
        {"label": "68000001 · Ethernet LAN · 192.0.2.10:40304", "value": "68000001"},
        {"label": "68000002 · Ethernet LAN · 192.0.2.11:40306", "value": "68000002"},
        {"label": "68000003 · USB", "value": "68000003"},
    ]
    assert result["serial"]["value"] is None
    assert lan.hub.ethernet_endpoints == (None,) and not lan.rig.device.calls
    result = invoke(app, "connect", serial="68000001")
    assert result["connection"]["children"] == "Connected"
    assert lan.hub.ethernet_endpoints == ("192.0.2.10:40304",)
    old = lan.hub.controllers[0]
    result = invoke(app, "connect", serial="68000003")  # Forged change around locked selector.
    assert "Disconnect" in result["message"]["children"]
    assert lan.hub.controllers[0] is old
    lan.events.clear()
    result = invoke(app, "discover", serial="68000001")
    assert "Disconnect all" in result["hub-message"]["children"]
    assert not any(event[0] == "scan" for event in lan.events)
    assert result["serial"]["value"] == "68000001"
    lan.hub.disconnect(0, close_shutter=False)
    result = invoke(app, "connect", serial="68000003")
    assert result["connection"]["children"] == "Connected"
    assert lan.hub.ethernet_endpoints == (None,)
    lan.hub.disconnect(0, close_shutter=False)
    assert not any(
        c[0] in {"enable", "set_state", "set_mode"}
        for d in lan.rig.devices.values()
        for c in d.calls
    )


def test_usb_failure_does_not_hide_successful_lan_results(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")

    def fail(_self):
        raise ShutterError("injected USB failure")

    monkeypatch.setattr(KCubeShutter, "discover", fail)
    found, warnings = lan.hub.discover_available()
    assert found == {"68000001": "192.0.2.10:40304", "68000002": "192.0.2.11:40306"}
    assert warnings == ("USB discovery: injected USB failure",)
    assert not any(d.calls for d in lan.rig.devices.values())


def test_partial_lan_failure_keeps_usb_and_drops_old_lan_choices(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")
    app = create_app(lan.hub)
    invoke(app, "discover")

    def fail(*args):
        raise RuntimeError("injected LAN failure")

    monkeypatch.setattr(lan.sdk.manager, "ScanEthernetRange", fail)
    result = invoke(app, "discover", serial="68000001")
    assert result["serial"]["options"] == [{"label": "68000003 · USB", "value": "68000003"}]
    assert result["serial"]["value"] == "68000003"  # Sole result in a single panel.
    assert "injected LAN failure" in result["hub-message"]["children"]
    result = invoke(app, "connect", serial="68000001")
    assert result["connection"]["children"] == "Disconnected"
    assert lan.hub.ethernet_endpoints == (None,)
    assert not any(d.calls for d in lan.rig.devices.values())


def test_multi_panel_discovery_and_automatic_route_target_only_selected_panel(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")
    hub = ShutterHub(slots=3)
    app = create_app(hub)
    result = invoke(app, "discover", serials=[None] * 3)
    assert sum(event[0] == "scan" for event in lan.events) == 1
    assert all(result[f"serial-{i}"]["value"] is None for i in (1, 2, 3))
    result = invoke(app, "connect-2", serials=[None, "68000002", None])
    assert result["connection-2"]["children"] == "Connected"
    assert hub.ethernet_endpoints == (None, "192.0.2.11:40306", None)
    assert not lan.rig.devices["68000001"].calls and not lan.rig.devices["68000003"].calls
    hub.disconnect(1, close_shutter=False)


def test_failed_rescan_cannot_reconnect_a_previously_configured_lan_target(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.255")
    app = create_app(lan.hub)
    invoke(app, "discover")
    invoke(app, "connect", serial="68000001")
    lan.hub.disconnect(0, close_shutter=False)

    def fail(*args):
        raise RuntimeError("injected LAN failure")

    monkeypatch.setattr(lan.sdk.manager, "ScanEthernetRange", fail)

    # Configured-route discovery also fails, but the old endpoint can still be
    # reached by a later Connect. A stale browser selection must not bypass the
    # current discovery snapshot simply because its route was configured before.
    def fail_configured():
        raise ShutterError("injected configured-route failure")

    monkeypatch.setattr(lan.hub, "discover_by_slot", fail_configured)
    result = invoke(app, "discover", serial="68000001")
    assert "68000001" not in [item["value"] for item in result["serial"]["options"]]
    before = list(lan.rig.device.calls)
    result = invoke(app, "connect", serial="68000001")
    assert result["connection"]["children"] == "Disconnected"
    assert "Discover" in result["message"]["children"]
    assert lan.rig.device.calls == before


def test_config_defaults_feed_both_api_and_gui_scan(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "192.0.2.0")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "192.0.2.15")
    monkeypatch.setattr(config, "LAN_SCAN_MAX_ADDRESSES", 16)
    monkeypatch.setattr(config, "LAN_SCAN_OPEN_TIMEOUT_MS", 250)
    lan.addresses.clear()
    lan.hub.scan_lan()
    assert lan.events == [("scan", "192.0.2.0", "192.0.2.15", 40303, 250)]
    lan.events.clear()
    app = create_app(lan.hub)
    result = invoke(app, "discover")
    assert "USB / Ethernet" in result["hub-message"]["children"]
    assert ("scan", "192.0.2.0", "192.0.2.15", 40303, 250) in lan.events
    assert not any(d.calls for d in lan.rig.devices.values())


def test_explicit_scan_arguments_override_config_defaults(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_START_IP", "invalid")
    monkeypatch.setattr(config, "LAN_SCAN_END_IP", "invalid")
    monkeypatch.setattr(config, "LAN_SCAN_OPEN_TIMEOUT_MS", 0)
    lan.addresses.clear()
    lan.hub.scan_lan("192.0.2.10", "192.0.2.10", open_timeout_ms=75)
    assert lan.events == [("scan", "192.0.2.10", "192.0.2.10", 40303, 75)]


@pytest.mark.parametrize("limit", [0, 257, True, None, 1.5])
def test_invalid_config_scan_limit_rejects_before_sdk(lan, monkeypatch, limit):
    monkeypatch.setattr(config, "LAN_SCAN_MAX_ADDRESSES", limit)
    with pytest.raises(ValueError, match="LAN_SCAN_MAX_ADDRESSES"):
        lan.hub.scan_lan()
    assert not lan.events


def test_config_scan_limit_reports_partial_discovery_error(lan, monkeypatch):
    monkeypatch.setattr(config, "LAN_SCAN_MAX_ADDRESSES", 16)
    app = create_app(lan.hub)
    result = invoke(app, "discover")
    assert "at most 16" in result["hub-message"]["children"]
    assert not any(event[0] == "scan" for event in lan.events)


@pytest.mark.parametrize(
    "setting,value",
    [
        ("LAN_SCAN_START_IP", "invalid"),
        ("LAN_SCAN_END_IP", "invalid"),
        ("LAN_SCAN_OPEN_TIMEOUT_MS", 0),
    ],
)
def test_invalid_config_defaults_reject_before_sdk(lan, monkeypatch, setting, value):
    monkeypatch.setattr(config, setting, value)
    with pytest.raises(ValueError, match="LAN"):
        lan.hub.scan_lan()
    assert not lan.events
