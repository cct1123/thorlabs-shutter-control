"""Software/protocol contracts only: no SDK import, USB or voltage measurement."""

from itertools import product

import pytest

from thorlabs_shutter_control import ShutterError, ShutterHub, TriggerConfig


@pytest.mark.parametrize(
    "port,field,value", list(product((1, 2), ("mode", "polarity"), (None, "invalid", 1)))
)
def test_invalid_trigger_values_are_rejected_without_hardware(port, field, value, rig):
    with pytest.raises(ValueError):
        TriggerConfig(**{f"trig{port}_{field}": value})
    assert not rig.device.calls and not rig.manager_calls


@pytest.mark.parametrize(
    "m1,p1,m2,p2",
    list(
        product(
            ("disabled", "input", "output"),
            ("high", "low"),
            ("disabled", "input", "output"),
            ("high", "low"),
        )
    ),
)
def test_both_ports_round_trip_without_arming(rig, m1, p1, m2, p2):
    rig.controller.connect()
    config = TriggerConfig(m1, p1, m2, p2)
    assert rig.controller.configure_triggers(config) == config
    assert rig.controller.get_trigger_config() == config
    status = rig.controller.get_status()
    assert status.trigger_config == config and status.ttl_armed is False
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_connect_reads_existing_triggered_state_without_output_writes(rig):
    rig.device.mode = "Triggered"
    rig.device.operation = "Active"
    rig.device.trigger_config.Trigger1Polarity = "TriggerLow"
    status = rig.controller.connect()
    assert status.ttl_armed is True and status.shutter_state == "open"
    assert status.trigger_config.trig1_polarity == "low"
    assert not any(
        c[0] in {"set_triggers", "set_mode", "set_state", "enable"} for c in rig.device.calls
    )


def test_disconnected_ttl_methods_cannot_load_sdk_or_actuate(rig):
    assert rig.controller.get_status().ttl_armed is None
    for method in (
        rig.controller.get_trigger_config,
        rig.controller.arm_triggers,
        rig.controller.disarm_triggers,
        lambda: rig.controller.configure_triggers(TriggerConfig()),
    ):
        with pytest.raises(ShutterError):
            method()
    assert not rig.device.calls and not rig.manager_calls


@pytest.mark.parametrize(
    "mode,polarity,level,expected",
    [
        ("input", "high", False, "closed"),
        ("input", "high", True, "open"),
        ("input", "low", False, "open"),
        ("input", "low", True, "closed"),
    ],
)
def test_trig2_can_control_armed_shutter_independently_of_priming_state(
    rig, mode, polarity, level, expected
):
    rig.controller.connect()
    rig.controller.configure_triggers(TriggerConfig("disabled", "high", mode, polarity))
    rig.device.inputs[1] = level
    status = rig.controller.arm_triggers()
    assert status.ttl_armed is True and status.shutter_state == expected
    rig.device.inputs[1] = not level
    status = rig.controller.get_status()
    assert status.ttl_armed is True and status.shutter_state != expected
    with pytest.raises(ShutterError, match="Disarm TTL"):
        rig.controller.open_shutter()
    assert rig.controller.disarm_triggers().ttl_armed is False
    assert rig.device.state == "Closed" and rig.device.mode == "Manual"


@pytest.mark.parametrize("blocked", ["key", "interlock", "no-input", "fault"])
def test_arm_refusals_do_not_enable_or_write_output(rig, blocked):
    rig.controller.connect()
    if blocked == "key":
        rig.device.Status.KeyEnabled = False
    elif blocked == "interlock":
        rig.device.interlock = False
    elif blocked == "no-input":
        rig.controller.configure_triggers(TriggerConfig("output", "high", "disabled", "low"))
    else:
        rig.device.CommsStatus = "Timeout"
    before = list(rig.device.calls)
    with pytest.raises(ShutterError):
        rig.controller.arm_triggers()
    assert not any(
        c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls[len(before) :]
    )


@pytest.mark.parametrize("armed", [False, True])
def test_configuration_requires_closed_inactive_manual(rig, armed):
    rig.controller.connect()
    if armed:
        rig.controller.arm_triggers()
    else:
        rig.controller.open_shutter()
    before = list(rig.device.calls)
    with pytest.raises(ShutterError, match="Disarm/Close"):
        rig.controller.configure_triggers(TriggerConfig())
    assert not any(c[0] == "set_triggers" for c in rig.device.calls[len(before) :])


def test_setting_readback_mismatch_faults_and_prevents_arm(rig, monkeypatch):
    rig.controller.connect()
    monkeypatch.setattr(rig.device, "SetTriggerConfigParams", lambda config: None)
    with pytest.raises(ShutterError, match="readback mismatch"):
        rig.controller.configure_triggers(TriggerConfig(trig1_polarity="low"))
    status = rig.controller.get_status()
    assert status.trigger_config is None and status.ttl_armed is None
    with pytest.raises(ShutterError, match="readback mismatch"):
        rig.controller.arm_triggers()
    rig.controller.safe_shutdown()


@pytest.mark.parametrize("failure", ["request_triggers", "get_triggers", "set_triggers"])
def test_trigger_communication_errors_are_faults_and_cleanup_remains_available(rig, failure):
    rig.controller.connect()
    rig.device.fail.add(failure)
    with pytest.raises(ShutterError):
        rig.controller.configure_triggers(TriggerConfig(trig1_polarity="low"))
    assert rig.controller.get_status().ttl_armed is None
    try:
        rig.controller.safe_shutdown()
    except ShutterError:
        pass
    assert ("set_state", "Inactive") in rig.device.calls
    if failure == "set_triggers":
        assert ("set_mode", "Manual") in rig.device.calls
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_unsupported_vendor_enum_is_not_reported_as_valid_config(rig):
    rig.controller.connect()
    rig.device.trigger_config.Trigger1Mode = "UnexpectedFirmwareMode"
    status = rig.controller.get_status()
    assert status.connection == "fault" and status.trigger_config is None
    assert status.ttl_armed is None


@pytest.mark.parametrize(
    "failure", ["enable", "set-mode", "set-state", "feedback", "interlock", "interrupt"]
)
def test_failed_arm_attempts_disarm_and_latches_fault(rig, monkeypatch, failure):
    rig.controller.connect()
    original_mode = rig.device.SetOperatingMode
    original_state = rig.device.SetOperatingState

    def set_mode(mode):
        if mode == "Triggered" and failure in ("set-mode", "interrupt"):
            if failure == "interrupt":
                raise KeyboardInterrupt("TTL interrupted")
            raise RuntimeError("Triggered write failed")
        original_mode(mode)

    def set_state(state):
        original_state(state)
        if state == "Active":
            if failure == "set-state":
                raise RuntimeError("Active write failed after actuation")
            if failure == "feedback":
                rig.device.operation = "Inactive"
            if failure == "interlock":
                rig.device.interlock = False

    monkeypatch.setattr(rig.device, "SetOperatingMode", set_mode)
    monkeypatch.setattr(rig.device, "SetOperatingState", set_state)
    if failure == "enable":
        rig.device.fail.add("enable")
    with pytest.raises(KeyboardInterrupt if failure == "interrupt" else ShutterError):
        rig.controller.arm_triggers()
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert rig.controller.get_status().connection == "fault"
    assert rig.controller.get_status().ttl_armed is None


def test_shutdown_refuses_manual_after_failed_inactive_and_still_cleans_all_slots(rig):
    rig.serials[:] = list(rig.devices)
    hub = ShutterHub(list(rig.devices))
    for shutter in hub.controllers:
        shutter.connect()
        shutter.arm_triggers()
    for device in rig.devices.values():
        device.calls.clear()
    rig.device.fail.add("set_state")
    with pytest.raises(ShutterError, match="Shutter 1"):
        hub.safe_shutdown()
    for device in rig.devices.values():
        assert device.calls[0] == ("set_state", "Inactive")
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
        assert not device.IsConnected
    assert ("set_mode", "Manual") not in rig.device.calls
    assert rig.device.mode == "Triggered"  # Unverified disarm, never force Manual/Active.
    assert all(d.mode == "Manual" for d in list(rig.devices.values())[1:])
    assert all(device.state == "Closed" for device in list(rig.devices.values())[1:])


def test_disarm_reports_failed_inactive_and_does_not_attempt_mode_transition(rig):
    rig.controller.connect()
    rig.device.calls.clear()
    rig.device.fail.update(("set_state", "set_mode"))
    with pytest.raises(ShutterError, match="set_state"):
        rig.controller.disarm_triggers()
    assert ("set_mode", "Manual") not in rig.device.calls


def test_repeat_arm_is_read_only_and_close_disarms_with_active_low_input(rig):
    rig.controller.connect()
    rig.controller.configure_triggers(TriggerConfig(trig1_polarity="low"))
    assert rig.controller.arm_triggers().shutter_state == "open"
    rig.device.calls.clear()
    assert rig.controller.arm_triggers().ttl_armed is True
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)
    assert rig.controller.close_shutter().ttl_armed is False
    assert rig.device.mode == "Manual" and rig.device.state == "Closed"


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


def test_unacknowledged_inactive_cannot_switch_primed_closed_cube_to_manual(rig, monkeypatch):
    rig.controller.connect()
    assert rig.controller.arm_triggers().shutter_state == "closed"
    monkeypatch.setattr(rig.device, "SetOperatingState", lambda state: None)
    rig.device.calls.clear()
    with pytest.raises(ShutterError, match="Closed/Inactive"):
        rig.controller.disarm_triggers()
    assert ("set_mode", "Manual") not in rig.device.calls
    assert rig.device.operation == "Active" and rig.device.mode == "Triggered"
    assert rig.device.state == "Closed"


@pytest.mark.parametrize("failure", ["request_triggers", "get_triggers", "unknown-enum"])
def test_disarm_operating_feedback_does_not_depend_on_trigger_settings(rig, failure):
    rig.controller.connect()
    rig.controller.configure_triggers(TriggerConfig(trig1_polarity="low"))
    assert rig.controller.arm_triggers().shutter_state == "open"
    if failure == "unknown-enum":
        rig.device.trigger_config.Trigger1Mode = "Unknown"
    else:
        rig.device.fail.add(failure)
    assert rig.controller.get_status().connection == "fault"
    status = rig.controller.disarm_triggers()
    assert status.shutter_state == "closed" and status.ttl_armed is False
    assert status.trigger_config is None  # This command samples operating feedback only.
    assert rig.device.mode == "Manual" and rig.device.operation == "Inactive"
    assert rig.controller.get_status().connection == "fault"  # Prior read fault stays latched.
    rig.controller.safe_shutdown()
    assert not rig.device.IsConnected
