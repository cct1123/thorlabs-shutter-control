"""Software/protocol contracts only: no SDK import, USB or voltage measurement."""

import pytest

from thorlabs_shutter_control import ShutterError, TriggerConfig


@pytest.mark.parametrize(
    "m1,p1,m2,p2",
    [
        ("disabled", "high", "output", "low"),
        ("input", "low", "disabled", "high"),
        ("output", "high", "input", "low"),
    ],
)
def test_both_ports_round_trip_without_arming(rig, m1, p1, m2, p2):
    rig.controller.connect()
    config = TriggerConfig(m1, p1, m2, p2)
    rig.controller.configure_triggers(config)
    assert rig.controller.get_trigger_config() == config
    status = rig.controller.get_status()
    assert status.trigger_config == config and status.ttl_armed is False
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


@pytest.mark.parametrize(
    "mode,polarity,level,expected",
    [
        ("input", "high", False, "closed"),
        ("input", "low", False, "open"),
    ],
)
def test_trig2_can_control_armed_shutter_independently_of_priming_state(
    rig, mode, polarity, level, expected
):
    rig.controller.connect()
    rig.controller.configure_triggers(TriggerConfig("disabled", "high", mode, polarity))
    rig.device.inputs[1] = level
    rig.controller.arm_triggers()
    status = rig.controller.get_operating_status()
    assert status.ttl_armed is True and status.shutter_state == expected
    rig.device.inputs[1] = not level
    status = rig.controller.get_status()
    assert status.ttl_armed is True and status.shutter_state != expected
    rig.controller.disarm_triggers()
    assert rig.controller.get_operating_status().ttl_armed is False
    assert rig.device.state == "Closed" and rig.device.mode == "Manual"


def test_unsupported_vendor_enum_is_not_reported_as_valid_config(rig):
    rig.controller.connect()
    rig.device.trigger_config.Trigger1Mode = "UnexpectedFirmwareMode"
    status = rig.controller.get_status()
    assert status.connection == "fault" and status.trigger_config is None
    assert status.ttl_armed is None


def test_inactive_interrupt_skips_mode_transition_but_still_releases(rig, monkeypatch):
    rig.controller.connect()
    rig.device.calls.clear()

    def interrupt(state):
        raise KeyboardInterrupt("Inactive interrupted")

    monkeypatch.setattr(rig.device, "SetOperatingState", interrupt)
    with pytest.raises(KeyboardInterrupt):
        rig.controller.safe_shutdown()
    assert ("set_mode", "Manual") not in rig.device.calls
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_configuration_interrupt_is_latched_and_release_still_possible(rig, monkeypatch):
    rig.controller.connect()

    def interrupted(config):
        raise KeyboardInterrupt("Settings interrupted")

    monkeypatch.setattr(rig.device, "SetTriggerConfigParams", interrupted)
    with pytest.raises(KeyboardInterrupt):
        rig.controller.configure_triggers(TriggerConfig())
    assert rig.controller.get_status().ttl_armed is None
    rig.controller.safe_shutdown()


def test_ttl_read_detects_connection_loss_during_wait(rig, monkeypatch):
    from thorlabs_shutter_control import controller as driver

    rig.controller.connect()
    sleep = driver.time.sleep

    def lose_connection(seconds):
        sleep(seconds)
        rig.device.USBConnected = "Disconnected"

    monkeypatch.setattr(driver.time, "sleep", lose_connection)
    with pytest.raises(ShutterError, match="connection lost"):
        rig.controller.get_trigger_config()
    status = rig.controller.get_cached_status()
    assert status.connection == "fault" and status.trigger_config is None
    rig.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize("field,value", [("trig1_mode", None), ("trig2_polarity", "invalid")])
def test_invalid_trigger_config_has_no_device_access(rig, field, value):
    with pytest.raises(ValueError):
        TriggerConfig(**{field: value})
    assert not rig.manager_calls and not rig.device.calls
