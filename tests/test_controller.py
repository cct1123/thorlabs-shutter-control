import pytest

from thorlabs_shutter_control import KSC101Controller, ShutterError


@pytest.mark.parametrize("serial", ["123", "27000001", "68abcdef", "68000001\n", "68１２３４５６"])
def test_rejects_invalid_serial_before_hardware_access(serial):
    with pytest.raises(ValueError):
        KSC101Controller(serial)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), 61])
def test_rejects_invalid_timeouts(timeout):
    with pytest.raises(ValueError):
        KSC101Controller(timeout=timeout)


def test_initial_status_and_discovery_do_not_connect_or_actuate(rig):
    assert rig.controller.get_status().shutter_state == "unknown"
    assert rig.controller.discover() == ["68000001"]
    assert rig.device.calls == []


def test_connect_and_read_identity_without_output_writes(rig):
    assert rig.controller.connect().connection == "connected"
    assert rig.controller.identify_device()["serial_number"] == "68000001"
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_discovery_requires_unique_or_explicit_device(rig):
    rig.serials.extend(["68000002"])
    with pytest.raises(ShutterError, match="found 2"):
        rig.controller.connect()
    assert rig.device.calls == []
    assert rig.controller.connect("68000002").serial_number == "68000002"
    with pytest.raises(ShutterError, match="Disconnect before"):
        rig.controller.connect("68000001")


def test_no_device_is_actionable_error(rig):
    rig.serials.clear()
    with pytest.raises(ShutterError, match="found 0"):
        rig.controller.connect()


@pytest.mark.parametrize("failure", ["connect", "poll", "identity", "status"])
def test_partial_connection_failure_releases_without_actuation(rig, failure):
    rig.device.fail.add(failure)
    with pytest.raises(ShutterError, match="Connect failed"):
        rig.controller.connect()
    assert ("disconnect",) in rig.device.calls
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)
    assert rig.controller.get_status().has_device is False


def test_settings_timeout_is_not_treated_as_connected(rig):
    rig.device.initialized = False
    with pytest.raises(ShutterError, match="settings did not initialize"):
        rig.controller.connect()
    assert ("disconnect",) in rig.device.calls


def test_repeat_open_close_and_reconnect(rig):
    rig.controller.connect()
    for _ in range(20):
        assert rig.controller.open_shutter().shutter_state == "open"
        assert rig.controller.close_shutter().shutter_state == "closed"
    rig.controller.disconnect()
    assert rig.controller.get_status().connection == "disconnected"
    rig.controller.connect()
    assert rig.controller.get_status().connection == "connected"


def test_open_disarms_auto_mode_before_enabling(rig):
    rig.device.mode = "AutoToggle"
    rig.controller.connect()
    rig.controller.open_shutter()
    commands = [c for c in rig.device.calls if c[0] in {"set_state", "set_mode", "enable"}]
    assert commands == [
        ("set_state", "Inactive"),
        ("set_mode", "Manual"),
        ("enable",),
        ("set_state", "Active"),
    ]


@pytest.mark.parametrize("unchanged", ["operation", "position"])
def test_open_does_not_enable_when_preparation_feedback_disagrees(rig, monkeypatch, unchanged):
    rig.device.mode = "AutoToggle"
    rig.device.state = "Open"
    rig.device.operation = "Active"
    rig.controller.connect()
    set_state = rig.device.SetOperatingState

    def incomplete_close(state):
        if state == "Inactive":
            rig.device.record("set_state", state)
            if unchanged != "operation":
                rig.device.operation = "Inactive"
            if unchanged != "position":
                rig.device.state = "Closed"
        else:
            set_state(state)

    monkeypatch.setattr(rig.device, "SetOperatingState", incomplete_close)
    with pytest.raises(ShutterError, match="reported Closed/Inactive in Manual mode"):
        rig.controller.open_shutter()
    assert ("enable",) not in rig.device.calls
    assert ("set_state", "Active") not in rig.device.calls
    assert rig.device.calls[-1] == ("set_state", "Inactive")
    assert rig.controller.get_status().shutter_state == "unknown"


@pytest.mark.parametrize("blocked", ["key", "interlock"])
def test_open_respects_existing_safeguards(rig, blocked):
    rig.controller.connect()
    if blocked == "key":
        rig.device.Status.KeyEnabled = False
    else:
        rig.device.interlock = False
    with pytest.raises(ShutterError, match="Open refused"):
        rig.controller.open_shutter()
    assert not any(c[0] == "enable" for c in rig.device.calls)
    assert rig.controller.close_shutter().shutter_state == "closed"


def test_missing_feedback_does_not_turn_successful_write_into_success(rig):
    rig.controller.connect()
    rig.device.stuck = True
    with pytest.raises(ShutterError, match="Timed out waiting for reported Open"):
        rig.controller.open_shutter()
    assert rig.device.calls[-1] == ("set_state", "Inactive")
    assert rig.controller.get_status().shutter_state == "unknown"
    with pytest.raises(ShutterError, match="Open failed"):
        rig.controller.open_shutter()


@pytest.mark.parametrize("loss", ["usb", "comms", "status"])
def test_communication_fault_invalidates_feedback_and_requires_reconnect(rig, loss):
    rig.controller.connect()
    rig.controller.open_shutter()
    if loss == "usb":
        rig.device.USBConnected = "Disconnected"
    elif loss == "comms":
        rig.device.CommsStatus = "Timeout"
    else:
        rig.device.fail.add("status")
    status = rig.controller.get_status()
    assert status.connection == "fault"
    assert status.shutter_state == "unknown"
    rig.device.CommsStatus = "OK"
    rig.device.USBConnected = "Connected"
    rig.device.fail.clear()
    with pytest.raises(ShutterError):
        rig.controller.open_shutter()
    rig.controller.disconnect()
    assert rig.controller.connect().connection == "connected"


def test_shutdown_closes_before_releasing(rig):
    rig.controller.connect()
    rig.controller.open_shutter()
    rig.controller.safe_shutdown()
    assert rig.device.state == "Closed"
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    rig.controller.safe_shutdown()  # Idempotent after success.


def test_close_failure_does_not_skip_cleanup_or_hide_failure(rig):
    rig.controller.connect()
    rig.device.fail.add("set_state")
    with pytest.raises(ShutterError, match="Shutdown incomplete"):
        rig.controller.safe_shutdown()
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert rig.controller.get_status().error
    assert not rig.controller.get_status().has_device
    rig.controller.safe_shutdown()
    assert rig.controller.get_status().error  # A second cleanup cannot erase the failed close.


def test_shutdown_still_disconnects_if_stopping_polling_fails(rig):
    rig.controller.connect()
    rig.device.fail.add("stop_poll")
    with pytest.raises(ShutterError, match="stop polling"):
        rig.controller.safe_shutdown()
    assert rig.device.calls[-1] == ("disconnect",)


def test_disconnect_failure_retains_handle_for_retry(rig):
    rig.controller.connect()
    rig.device.fail.add("disconnect")
    with pytest.raises(ShutterError):
        rig.controller.safe_shutdown()
    assert rig.controller.get_status().has_device
    rig.device.fail.clear()
    rig.controller.safe_shutdown()
    assert not rig.controller.get_status().has_device


def test_explicit_passive_disconnect_does_not_write_output(rig):
    rig.controller.connect()
    rig.controller.disconnect(close_shutter=False)
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_context_keeps_original_exception_and_attaches_shutdown_error(rig):
    with pytest.raises(ValueError, match="application failure") as caught:
        with rig.controller:
            rig.device.fail.add("set_state")
            raise ValueError("application failure")
    assert "Shutdown incomplete" in caught.value.__notes__[0]


def test_interrupt_during_close_still_releases_device(rig, monkeypatch):
    rig.controller.connect()

    def interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr(rig.controller, "close_shutter", interrupt)
    with pytest.raises(KeyboardInterrupt):
        rig.controller.safe_shutdown()
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


def test_connection_loss_during_status_read_cannot_return_healthy_snapshot(rig, monkeypatch):
    rig.controller.connect()

    def lost_during_request():
        rig.device.CommsStatus = "Timeout"

    monkeypatch.setattr(rig.device, "RequestStatus", lost_during_request)
    status = rig.controller.get_status()
    assert status.connection == "fault"
    assert status.shutter_state == "unknown"
