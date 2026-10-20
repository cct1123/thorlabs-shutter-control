import pytest

from thorlabs_shutter_control import KCubeShutter, ShutterError, ShutterHub
from thorlabs_shutter_control import controller as controller_module


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


@pytest.mark.parametrize("serials", [[], ["68000003"], ["68000003", "68000001", "68000002"]])
def test_serial_construction_preselects_three_slots_without_sdk_access(rig, monkeypatch, serials):
    def forbidden_loader(directory):
        pytest.fail("Hub construction must be passive")

    monkeypatch.setattr(controller_module, "_load_sdk", forbidden_loader)
    hub = ShutterHub(serials, kinesis_dir="sdk-folder")
    assert [c.serial_number for c in hub.controllers] == serials + [None] * (3 - len(serials))
    assert all(
        c.kinesis_dir == "sdk-folder" and not c.get_status().has_device for c in hub.controllers
    )
    hub.safe_shutdown()
    assert rig.manager_calls == []
    assert all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("serials", [["68000001"] * 2, ["68000001"] * 4, ["invalid"]])
def test_invalid_serial_configuration_is_rejected_without_device_access(rig, serials):
    with pytest.raises(ValueError):
        ShutterHub(serials)
    assert rig.manager_calls == []
    assert all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize("options", [{"serial_numbers": ["68000001"]}, {"kinesis_dir": "sdk"}])
def test_injection_cannot_silently_ignore_hub_configuration(rig, options):
    with pytest.raises(ValueError, match="Configure injected controllers"):
        ShutterHub(controllers=[rig.controller], **options)
    assert rig.manager_calls == []


@pytest.mark.parametrize("count", [0, 4])
def test_invalid_hub_size_is_rejected(count):
    with pytest.raises(ValueError, match="one to three"):
        ShutterHub(controllers=[KCubeShutter() for _ in range(count)])


def test_explicit_single_controller_is_retained_and_repeated_objects_are_rejected(rig):
    assert ShutterHub(controllers=[rig.controller]).controllers == (rig.controller,)
    with pytest.raises(ValueError, match="distinct controller"):
        ShutterHub(controllers=[rig.controller, rig.controller])


def test_discovery_is_shared_passive_enumeration(rig):
    rig.serials[:] = list(reversed(rig.devices))
    hub = ShutterHub()
    assert hub.discover() == sorted(rig.devices)
    assert rig.manager_calls == ["discover"]
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize("slot", [-1, 3, True, "0"])
def test_invalid_slot_does_not_access_hardware(rig, slot):
    with pytest.raises(ShutterError, match="slot"):
        ShutterHub().connect(slot, "68000001")
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


@pytest.mark.parametrize("preselected", [None, "68000001"])
def test_missing_selection_never_automatically_connects(rig, preselected):
    hub = ShutterHub(controllers=[KCubeShutter(preselected)])
    with pytest.raises(ShutterError, match="Select a KSC101 serial"):
        hub.connect(0, None)
    assert rig.manager_calls == []
    assert all(device.calls == [] for device in rig.devices.values())


def test_three_connections_and_commands_have_independent_device_state(rig):
    hub = three_shutters(rig)
    assert [controller.serial_number for controller in hub.controllers] == list(rig.devices)
    assert all(device.IsConnected for device in rig.devices.values())
    assert all(
        not any(call[0] in {"set_state", "set_mode", "enable"} for call in device.calls)
        for device in rig.devices.values()
    )

    first, second, third = hub.controllers
    first.open_shutter()
    assert [device.state for device in rig.devices.values()] == ["Open", "Closed", "Closed"]
    second.open_shutter()
    third.open_shutter()
    second.disconnect()
    assert [device.state for device in rig.devices.values()] == ["Open", "Closed", "Open"]
    assert first.get_status().connection == third.get_status().connection == "connected"
    assert second.get_status().connection == "disconnected"
    hub.safe_shutdown()


def test_duplicate_serial_is_rejected_before_second_connection(rig):
    hub = ShutterHub()
    hub.connect(0, "68000001")
    before = [call for call in rig.device.calls if call[0] == "connect"]
    with pytest.raises(ShutterError, match="already owned by another controller"):
        hub.connect(1, "68000001")
    assert [call for call in rig.device.calls if call[0] == "connect"] == before
    assert hub.controllers[0].get_status().has_device
    assert not hub.controllers[1].get_status().has_device

    hub.controllers[0].disconnect()
    assert hub.connect(1, "68000001").connection == "connected"
    hub.safe_shutdown()


def test_duplicate_assignment_does_not_read_or_fault_the_current_owner(rig):
    hub = ShutterHub()
    hub.connect(0, "68000001")
    rig.device.fail.add("status")
    calls = list(rig.device.calls)
    with pytest.raises(ShutterError, match="already owned"):
        hub.connect(1, "68000001")
    assert rig.device.calls == calls
    rig.device.fail.clear()
    assert hub.controllers[0].get_status().connection == "connected"
    hub.safe_shutdown()


def test_failed_connection_in_one_slot_does_not_affect_others(rig):
    rig.serials[:] = list(rig.devices)
    hub = ShutterHub(controllers=[KCubeShutter(timeout=0.5) for _ in range(3)])
    hub.connect(0, "68000001")
    rig.devices["68000002"].fail.add("connect")
    with pytest.raises(ShutterError, match="Connect failed"):
        hub.connect(1, "68000002")
    hub.connect(2, "68000003")
    assert hub.controllers[0].open_shutter().shutter_state == "open"
    assert hub.controllers[2].open_shutter().shutter_state == "open"
    assert not hub.controllers[1].get_status().has_device
    assert rig.devices["68000002"].calls[-1] == ("disconnect",)
    hub.safe_shutdown()


def test_shutdown_closes_and_releases_all_three_shutters(rig):
    hub = three_shutters(rig)
    for controller in hub.controllers:
        controller.open_shutter()
    hub.safe_shutdown()
    for device in rig.devices.values():
        assert device.state == "Closed"
        assert not device.IsConnected
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    hub.safe_shutdown()


def test_shutdown_aggregates_failures_and_still_attempts_remaining_slots(rig):
    hub = three_shutters(rig)
    for controller in hub.controllers:
        controller.open_shutter()
    rig.devices["68000001"].fail.add("set_state")
    rig.devices["68000002"].fail.add("disconnect")
    with pytest.raises(ShutterError) as caught:
        hub.safe_shutdown()
    message = str(caught.value)
    assert "Shutter 1 (68000001)" in message and "set_state" in message
    assert "Shutter 2 (68000002)" in message and "disconnect" in message
    for device in rig.devices.values():
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert not rig.devices["68000001"].IsConnected
    assert rig.devices["68000002"].IsConnected
    assert rig.devices["68000003"].state == "Closed"
    assert not rig.devices["68000003"].IsConnected
    rig.devices["68000002"].fail.clear()
    hub.safe_shutdown()
    assert not rig.devices["68000002"].IsConnected


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


@pytest.mark.parametrize("method", ["StopPolling", "Disconnect"])
@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, SystemExit])
def test_release_interruption_in_one_armed_slot_never_skips_other_slots(
    rig, monkeypatch, method, exception_type
):
    hub = three_shutters(rig)
    for shutter in hub.controllers:
        shutter.arm_triggers()
    original = getattr(rig.device, method)

    def interrupt():
        rig.device.record("stop_poll" if method == "StopPolling" else "disconnect")
        raise exception_type("Release interrupted")

    monkeypatch.setattr(rig.device, method, interrupt)
    with pytest.raises(exception_type) as caught:
        hub.safe_shutdown()
    assert "Shutter 1 (68000001)" in caught.value.__notes__[-1]
    for device in rig.devices.values():
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
        assert device.mode == "Manual" and device.state == "Closed"
    assert all(not d.IsConnected for d in list(rig.devices.values())[1:])
    monkeypatch.setattr(rig.device, method, original)
    hub.safe_shutdown()
