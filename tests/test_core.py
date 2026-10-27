"""The essential device and hub contracts, using software devices only."""

import pytest

from thorlabs_shutter_control import (
    KCubeShutter,
    ShutterError,
    ShutterHub,
    TriggerConfig,
    controller,
)


def test_construction_is_passive(bench):
    hub = ShutterHub()
    assert len(hub.controllers) == 3
    assert all(not c.get_cached_status().has_device for c in hub.controllers)
    hub.safe_shutdown()
    assert not bench.loads and not bench.manager.calls


def test_usb_commands_and_feedback_are_separate(bench):
    c = KCubeShutter(bench.usb.serial)
    assert c.discover() == [bench.usb.serial]
    c.connect()
    assert c.identify_device()["serial_number"] == bench.usb.serial
    bench.usb.calls.clear()
    assert c.open_shutter() is None
    assert bench.usb.calls == [("state", "Active")]
    assert c.get_shutter_state() == "open"
    c.close_shutter()
    assert c.get_operating_status().is_closed_manual
    c.disconnect(close_shutter=False)
    assert not bench.usb.IsConnected


def test_ttl_round_trip_arm_and_disarm(bench):
    c = KCubeShutter(bench.usb.serial)
    c.connect()
    settings = TriggerConfig("disabled", "high", "input", "low")
    c.configure_triggers(settings)
    assert c.get_trigger_config() == settings
    c.arm_triggers()
    assert c.get_operating_status().ttl_armed
    c.disarm_triggers()
    assert c.get_operating_status().is_closed_manual
    c.safe_shutdown()


def test_feedback_reads_do_not_add_polling_delays(bench):
    c = KCubeShutter(bench.usb.serial)
    c.connect()
    start = controller.time.monotonic()
    assert c.get_status().is_closed_manual
    assert c.get_operating_status().is_closed_manual
    assert c.get_trigger_config() == TriggerConfig()
    assert c.get_shutter_state() == "closed"
    assert c.get_operating_state() == "inactive"
    assert c.get_operating_mode() == "manual"
    assert c.get_status_bits() == 0x2000
    assert controller.time.monotonic() == start
    c.safe_shutdown()


def test_wrong_identity_releases_without_output_commands(bench):
    bench.usb.identity = "68000009"
    with pytest.raises(ShutterError, match="identity mismatch"):
        KCubeShutter(bench.usb.serial).connect()
    assert not bench.usb.IsConnected
    assert not any(call[0] in {"state", "mode", "enable"} for call in bench.usb.calls)


def test_failed_release_keeps_exclusive_ownership_until_retry(bench):
    owner = KCubeShutter(bench.usb.serial)
    other = KCubeShutter(bench.usb.serial)
    owner.connect()
    bench.usb.fail = "disconnect"
    with pytest.raises(ShutterError, match="disconnect"):
        owner.disconnect(close_shutter=False)
    with pytest.raises(ShutterError, match="already owned"):
        other.connect()
    assert owner.get_cached_status().has_device
    bench.usb.fail = None
    owner.disconnect(close_shutter=False)
    other.connect()
    other.safe_shutdown()


def test_shutdown_attempts_every_slot_after_close_failure(bench):
    hub = ShutterHub(slots=2, ethernet_endpoints=[None, bench.endpoint])
    hub.connect(0, bench.usb.serial)
    hub.connect(1, bench.lan.serial)
    bench.usb.fail = "state"
    with pytest.raises(ShutterError, match="Shutdown incomplete"):
        hub.safe_shutdown()
    assert all(not d.IsConnected for d in bench.devices.values())
    assert ("state", "Inactive") in bench.lan.calls


def test_lan_discovery_waits_for_identity_then_connects_exact_route(bench):
    bench.manager.ready_after = 3
    hub = ShutterHub([bench.lan.serial], ethernet_endpoints=[bench.endpoint])
    assert hub.discover() == [bench.lan.serial]
    assert bench.manager.refreshes == 3
    assert bench.manager.calls.count(("build",)) == 1
    assert hub.connect(0, bench.lan.serial).connection == "connected"
    hub.disconnect(0, close_shutter=False)
    assert not any(call[0] in {"state", "mode", "enable"} for call in bench.lan.calls)


def test_unified_discovery_returns_usb_and_lan_without_connecting(bench):
    routes, warnings = ShutterHub().discover_available()
    assert routes == {bench.usb.serial: None, bench.lan.serial: bench.endpoint}
    assert not warnings
    assert ("scan", "192.0.2.0", "192.0.2.255", 40303, 100) in bench.manager.calls
    assert all(not d.calls for d in bench.devices.values())


def test_lan_scan_failure_preserves_usb_results(bench):
    bench.manager.scan_error = True
    routes, warnings = ShutterHub().discover_available()
    assert routes == {bench.usb.serial: None}
    assert any("LAN discovery failed" in warning for warning in warnings)
