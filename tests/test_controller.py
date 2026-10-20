from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import KCubeShutter, ShutterError


@pytest.fixture
def independent_rig(rig, monkeypatch):
    """Provide distinct fake handles rather than reusing one fake for all serials."""
    rig.controller.discover()
    rig.serials[:] = list(rig.devices)
    factory_calls = []

    def create(serial):
        factory_calls.append(serial)
        return rig.devices[serial]

    monkeypatch.setattr(rig.controller._sdk.device_type, "CreateKCubeSolenoid", create)
    rig.factory_calls = factory_calls
    rig.controllers = [KCubeShutter(serial, timeout=0.5) for serial in rig.serials]
    return rig


@pytest.mark.parametrize(
    "serial", ["123", "27000001", "68abcdef", "68000001\n", "68１２３４５６", 68000001, [], False]
)
def test_rejects_invalid_serial_before_hardware_access(serial):
    with pytest.raises(ValueError):
        KCubeShutter(serial)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan"), 61])
def test_rejects_invalid_timeouts(timeout):
    with pytest.raises(ValueError):
        KCubeShutter(timeout=timeout)


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


@pytest.mark.parametrize(
    "getter, value",
    [
        ("GetOperatingState", "Active"),
        ("GetSolenoidState", "Open"),
        ("GetOperatingMode", "AutoToggle"),
    ],
    ids=["operation", "position", "mode"],
)
def test_open_does_not_enable_when_preparation_feedback_disagrees(rig, monkeypatch, getter, value):
    rig.device.mode = "AutoToggle"
    rig.device.state = "Open"
    rig.device.operation = "Active"
    rig.controller.connect()
    monkeypatch.setattr(rig.device, getter, lambda: value)
    with pytest.raises(ShutterError, match="reported Closed/Inactive"):
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


@pytest.mark.parametrize(
    "attribute, value",
    [
        ("state", "Closed"),
        ("operation", "Inactive"),
        ("mode", "AutoToggle"),
        ("KeyEnabled", False),
        ("interlock", False),
    ],
)
def test_missing_feedback_does_not_turn_successful_write_into_success(
    rig, monkeypatch, attribute, value
):
    rig.controller.connect()
    set_state = rig.device.SetOperatingState

    def disagree_after_open(state):
        set_state(state)
        if state == "Active":
            target = rig.device.Status if attribute == "KeyEnabled" else rig.device
            setattr(target, attribute, value)

    monkeypatch.setattr(rig.device, "SetOperatingState", disagree_after_open)
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


def test_connect_rejects_mismatched_identity_without_output_writes(rig, monkeypatch):
    identity = rig.device.GetDeviceInfo
    monkeypatch.setattr(
        rig.device,
        "GetDeviceInfo",
        lambda: SimpleNamespace(Description="WRONG TEST DEVICE", SerialNumberText="68000002"),
    )
    with pytest.raises(ShutterError, match="identity mismatch.*68000001.*68000002"):
        rig.controller.connect()
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    assert not any(
        c[0] in {"enable", "set_state", "set_mode", "set_triggers"} for c in rig.device.calls
    )
    monkeypatch.setattr(rig.device, "GetDeviceInfo", identity)
    replacement = KCubeShutter("68000001", timeout=0.5)
    assert replacement.connect().connection == "connected"
    replacement.safe_shutdown()


def test_status_samples_operating_feedback_after_trigger_read_wait(rig, monkeypatch):
    rig.controller.connect()
    rig.controller.open_shutter()
    read = rig.device.GetTriggerConfigParams

    def changed_during_settings_read():
        rig.device.Status.KeyEnabled = False
        rig.device.interlock = False
        rig.device.state = "Closed"
        rig.device.operation = "Inactive"
        return read()

    monkeypatch.setattr(rig.device, "GetTriggerConfigParams", changed_during_settings_read)
    status = rig.controller.get_status()
    assert status.key_enabled is False and status.interlock_enabled is False
    assert status.shutter_state == "closed" and status.operating_state == "inactive"


def test_open_recovery_interrupt_cannot_leave_healthy_status(rig, monkeypatch):
    rig.controller.connect()
    set_state = rig.device.SetOperatingState
    failed_open = False

    def fail_open_and_interrupt_recovery(state):
        nonlocal failed_open
        if state == "Inactive" and failed_open:
            raise KeyboardInterrupt("Recovery interrupted")
        set_state(state)
        if state == "Active":
            failed_open = True
            raise RuntimeError("Active failed after actuation")

    monkeypatch.setattr(rig.device, "SetOperatingState", fail_open_and_interrupt_recovery)
    with pytest.raises(KeyboardInterrupt, match="Recovery interrupted") as caught:
        rig.controller.open_shutter()
    status = rig.controller.get_status()
    assert status.connection == "fault" and status.shutter_state == "unknown"
    assert "Active failed" in status.error and "Recovery interrupted" in status.error
    assert status.error in caught.value.__notes__


@pytest.mark.parametrize("serial", [68000001, [], False])
def test_connect_rejects_non_string_serial_without_sdk_access(rig, serial):
    with pytest.raises(ShutterError, match="serial"):
        rig.controller.connect(serial)
    assert not rig.manager_calls and not rig.device.calls


@pytest.mark.parametrize("method", ["StopPolling", "Disconnect"])
@pytest.mark.parametrize("during_connect", [False, True])
@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, SystemExit])
def test_release_interrupt_still_attempts_disconnect_and_preserves_fault_and_ownership(
    rig, monkeypatch, method, during_connect, exception_type
):
    if not during_connect:
        rig.controller.connect()
    else:
        rig.device.fail.add("poll")
    interrupt = exception_type("Injected release interrupt")
    original = getattr(rig.device, method)

    def interrupted():
        rig.device.record("stop_poll" if method == "StopPolling" else "disconnect")
        raise interrupt

    monkeypatch.setattr(rig.device, method, interrupted)
    with pytest.raises(exception_type) as caught:
        if during_connect:
            rig.controller.connect()
        else:
            rig.controller.safe_shutdown()
    assert caught.value is interrupt
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]
    status = rig.controller.get_status()
    assert status.connection == "fault"
    assert status.has_device is (method == "Disconnect")
    assert any("release interrupt" in note for note in interrupt.__notes__)
    if during_connect:
        assert "Connect failed" in status.error and "poll" in status.error
    replacement = KCubeShutter("68000001", timeout=0.5)
    if status.has_device:
        with pytest.raises(ShutterError, match="already owned"):
            replacement.connect()
    monkeypatch.setattr(rig.device, method, original)
    rig.device.fail.clear()
    if status.has_device:
        rig.controller.safe_shutdown()
    assert replacement.connect().connection == "connected"
    replacement.safe_shutdown()


def test_duplicate_serial_is_refused_before_creating_a_second_handle(independent_rig):
    rig = independent_rig
    first = rig.controllers[0]
    duplicate = KCubeShutter(first.serial_number, timeout=0.5)
    first.connect()
    first.connect()  # Connecting the current owner again remains idempotent.
    with pytest.raises(ShutterError, match="already owned by another controller"):
        duplicate.connect()
    assert rig.factory_calls == [first.serial_number]
    assert not duplicate.get_status().has_device
    first.disconnect(close_shutter=False)
    assert duplicate.connect().connection == "connected"
    assert rig.factory_calls == [first.serial_number, first.serial_number]


def test_serial_is_owned_while_first_connection_is_initializing(independent_rig, monkeypatch):
    rig = independent_rig
    first = rig.controllers[0]
    duplicate = KCubeShutter(first.serial_number, timeout=0.5)
    device = rig.devices[first.serial_number]
    connect = device.Connect
    initializing = Event()
    finish = Event()

    def paused_connect(serial):
        initializing.set()
        if not finish.wait(2):
            raise TimeoutError("Test did not release the paused fake connection")
        connect(serial)

    monkeypatch.setattr(device, "Connect", paused_connect)
    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(first.connect)
        try:
            assert initializing.wait(2)
            with pytest.raises(ShutterError, match="already owned"):
                duplicate.connect()
            assert rig.factory_calls == [first.serial_number]
        finally:
            finish.set()
        assert pending.result(timeout=2).connection == "connected"


@pytest.mark.parametrize("failure", ["connect", "poll", "identity", "status"])
def test_failed_connection_releases_ownership_after_successful_cleanup(independent_rig, failure):
    rig = independent_rig
    first = rig.controllers[0]
    device = rig.devices[first.serial_number]
    device.fail.add(failure)
    with pytest.raises(ShutterError, match="Connect failed"):
        first.connect()
    device.fail.clear()
    replacement = KCubeShutter(first.serial_number, timeout=0.5)
    assert replacement.connect().connection == "connected"


@pytest.mark.parametrize("factory_result", ["none", "raise"])
def test_failed_factory_releases_ownership(independent_rig, monkeypatch, factory_result):
    rig = independent_rig
    first = rig.controllers[0]
    factory = rig.controller._sdk.device_type.CreateKCubeSolenoid

    def fail_creation(serial):
        if factory_result == "raise":
            raise RuntimeError("Injected factory failure")
        return None

    monkeypatch.setattr(rig.controller._sdk.device_type, "CreateKCubeSolenoid", fail_creation)
    with pytest.raises(ShutterError, match="Connect failed"):
        first.connect()
    monkeypatch.setattr(rig.controller._sdk.device_type, "CreateKCubeSolenoid", factory)
    replacement = KCubeShutter(first.serial_number, timeout=0.5)
    assert replacement.connect().connection == "connected"


@pytest.mark.parametrize("during_connect", [False, True])
def test_failed_disconnect_retains_serial_ownership_until_retry(independent_rig, during_connect):
    rig = independent_rig
    first = rig.controllers[0]
    device = rig.devices[first.serial_number]
    if during_connect:
        device.fail.update({"poll", "disconnect"})
        with pytest.raises(ShutterError, match="Connect failed"):
            first.connect()
    else:
        first.connect()
        device.fail.add("disconnect")
        with pytest.raises(ShutterError, match="Shutdown incomplete"):
            first.safe_shutdown()
    replacement = KCubeShutter(first.serial_number, timeout=0.5)
    with pytest.raises(ShutterError, match="already owned"):
        replacement.connect()
    assert first.get_status().has_device
    device.fail.clear()
    first.safe_shutdown()
    assert replacement.connect().connection == "connected"


@pytest.mark.parametrize("device_count", [2, 3])
def test_distinct_handles_keep_control_status_and_faults_independent(independent_rig, device_count):
    rig = independent_rig
    controllers = rig.controllers[:device_count]
    for controller in controllers:
        status = controller.connect()
        assert status.serial_number == controller.serial_number
        assert controller.identify_device()["serial_number"] == controller.serial_number
    controllers[0].open_shutter()
    assert rig.devices[controllers[0].serial_number].state == "Open"
    for controller in controllers[1:]:
        device = rig.devices[controller.serial_number]
        assert device.state == "Closed"
        assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in device.calls)
    failed_device = rig.devices[controllers[0].serial_number]
    failed_device.fail.add("status")
    assert controllers[0].get_status().connection == "fault"
    for controller in controllers[1:]:
        assert controller.open_shutter().shutter_state == "open"
        assert controller.close_shutter().shutter_state == "closed"
    failed_device.fail.clear()
    for controller in controllers:
        controller.safe_shutdown()
        device = rig.devices[controller.serial_number]
        assert device.state == "Closed"
        assert device.calls[-2:] == [("stop_poll",), ("disconnect",)]
