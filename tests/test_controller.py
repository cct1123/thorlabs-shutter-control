from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import KCubeShutter, ShutterError, TriggerConfig
from thorlabs_shutter_control import controller as driver


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
    "serial",
    ["123", "27000001", "68abcdef", "68000001\n", "68１２３４５６", 68000001.0, [], False, True],
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


@pytest.mark.parametrize("serial", [None, "68000002"])
def test_owned_handle_cannot_be_relabelled_even_after_failed_release(rig, serial):
    rig.controller.connect()
    rig.device.fail.add("disconnect")
    with pytest.raises(ShutterError, match="Shutdown incomplete"):
        rig.controller.disconnect(close_shutter=False)
    calls = list(rig.device.calls)
    with pytest.raises(ShutterError, match="Disconnect before"):
        rig.controller.serial_number = serial
    assert rig.controller.serial_number == "68000001"
    assert rig.device.calls == calls
    rig.device.fail.clear()
    rig.controller.disconnect(close_shutter=False)
    rig.controller.serial_number = serial
    assert rig.controller.serial_number == serial


def test_settings_timeout_is_not_treated_as_connected(rig):
    rig.device.initialized = False
    with pytest.raises(ShutterError, match="settings did not initialize"):
        rig.controller.connect()
    assert ("disconnect",) in rig.device.calls


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


def test_disconnect_failure_retains_handle_for_retry(rig):
    rig.controller.connect()
    rig.device.fail.add("disconnect")
    with pytest.raises(ShutterError):
        rig.controller.safe_shutdown()
    assert rig.controller.get_status().has_device
    rig.device.fail.clear()
    rig.controller.safe_shutdown()
    assert not rig.controller.get_status().has_device


def test_context_keeps_original_exception_and_attaches_shutdown_error(rig):
    with pytest.raises(ValueError, match="application failure") as caught:
        with rig.controller:
            rig.device.fail.add("set_state")
            raise ValueError("application failure")
    assert "Shutdown incomplete" in caught.value.__notes__[0]


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


@pytest.mark.parametrize("serial", ["68000001", 68000001])
def test_serial_input_normalizes_for_selection_confirmation_and_connection(rig, serial):
    controller = KCubeShutter(serial)
    assert controller.serial_number == "68000001"
    assert not rig.manager_calls and not rig.device.calls
    rig.controller.serial_number = serial
    rig.controller.confirm_interlock(serial)
    assert rig.controller.connect(serial).operator_interlock_confirmed
    # Reassigning the same identity in another representation preserves confirmation.
    rig.controller.serial_number = 68000001
    assert rig.controller.connect("68000001").operator_interlock_confirmed
    assert not any(call[0] == "set_state" for call in rig.device.calls)


@pytest.mark.parametrize("method", ["StopPolling", "Disconnect"])
@pytest.mark.parametrize("during_connect", [True])
@pytest.mark.parametrize("exception_type", [KeyboardInterrupt])
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


@pytest.mark.parametrize(
    "method, expected_requests",
    [
        ("get_status", ["status", "request_mode", "request_operation", "request_triggers"]),
        ("get_operating_status", ["status", "request_mode", "request_operation"]),
        ("get_trigger_config", ["request_triggers"]),
        ("get_cached_status", []),
    ],
)
def test_read_methods_only_request_their_own_data(rig, method, expected_requests):
    rig.controller.connect()
    rig.device.calls.clear()
    getattr(rig.controller, method)()
    assert [c[0] for c in rig.device.calls if c[0] != "get_triggers"] == expected_requests
    rig.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize(
    "method,args,writes",
    [
        ("enable_device", (), ["enable"]),
        ("open_shutter", (), ["set_state"]),
        ("close_shutter", (), ["set_state"]),
        ("arm_triggers", (), ["enable", "set_mode", "set_state"]),
        ("disarm_triggers", (), ["set_state", "set_mode"]),
        ("configure_triggers", (TriggerConfig(),), ["set_triggers"]),
        ("set_operating_state", ("active",), ["set_state"]),
        ("set_operating_state", ("inactive",), ["set_state"]),
        ("set_operating_mode", ("manual",), ["set_mode"]),
        ("set_operating_mode", ("single",), ["set_mode"]),
        ("set_operating_mode", ("auto",), ["set_mode"]),
        ("set_operating_mode", ("triggered",), ["set_mode"]),
    ],
)
def test_setters_never_request_or_read_feedback_or_wait(rig, monkeypatch, method, args, writes):
    rig.controller.connect()
    rig.device.calls.clear()

    def forbidden(*args, **kwargs):
        pytest.fail("Setter requested/read feedback or waited")

    for name in dir(rig.device):
        if name.startswith(("Request", "Get")):
            monkeypatch.setattr(rig.device, name, forbidden)
    monkeypatch.setattr(rig.controller, "_check_connection", forbidden)
    monkeypatch.setattr(driver.time, "sleep", forbidden)
    assert getattr(rig.controller, method)(*args) is None
    assert [c[0] for c in rig.device.calls] == writes


@pytest.mark.parametrize(
    "method,expected",
    [
        ("open_shutter", [("set_state", "Active")]),
        ("close_shutter", [("set_state", "Inactive")]),
        ("arm_triggers", [("enable",), ("set_mode", "Triggered"), ("set_state", "Active")]),
        ("disarm_triggers", [("set_state", "Inactive"), ("set_mode", "Manual")]),
    ],
)
def test_command_order_and_repeated_calls_are_explicit(rig, method, expected):
    rig.controller.connect()
    rig.device.mode = "AutoToggle"
    rig.device.calls.clear()
    for _ in range(2):
        assert getattr(rig.controller, method)() is None
    assert rig.device.calls == expected * 2
    if method in ("open_shutter", "close_shutter"):
        assert rig.device.mode == "AutoToggle"


@pytest.mark.parametrize(
    "method,expected_request,value",
    [
        ("get_shutter_state", "status", "closed"),
        ("get_operating_state", "request_operation", "inactive"),
        ("get_operating_mode", "request_mode", "manual"),
        ("get_status_bits", "status", 0x1000),
    ],
)
def test_specific_getters_request_only_the_selected_feedback(rig, method, expected_request, value):
    rig.controller.connect()
    rig.device.calls.clear()
    start = driver.time.monotonic()
    assert getattr(rig.controller, method)() == value
    assert rig.device.calls == [(expected_request,)]
    assert driver.time.monotonic() - start == pytest.approx(rig.controller.polling_ms / 1000)


def test_connect_does_not_request_operating_feedback_or_wait_for_zero(rig):
    rig.device.operation = "0"
    start = driver.time.monotonic()
    status = rig.controller.connect()
    assert driver.time.monotonic() == start
    assert status.connection == "connected" and status.operating_state == "unknown"
    assert [c[0] for c in rig.device.calls] == ["connect", "poll", "identity"]
    assert rig.controller.get_operating_state() == "unknown"
    assert rig.controller.get_status().operating_state == "unknown"


def test_write_completion_does_not_claim_readback_or_leave_stale_snapshot(rig, monkeypatch):
    rig.controller.connect()
    assert rig.controller.get_status().is_closed_manual
    monkeypatch.setattr(rig.device, "SetOperatingState", lambda value: None)
    assert rig.controller.open_shutter() is None  # No acknowledgment implied.
    assert rig.controller.get_cached_status().shutter_state == "unknown"
    assert rig.controller.get_shutter_state() == "closed"  # Separate read shows disagreement.


def test_trigger_write_and_readback_are_separate(rig, monkeypatch):
    rig.controller.connect()
    config = TriggerConfig(trig1_polarity="low")
    monkeypatch.setattr(rig.device, "SetTriggerConfigParams", lambda value: None)
    assert rig.controller.configure_triggers(config) is None
    assert rig.controller.get_trigger_config() != config


@pytest.mark.parametrize("exception", [RuntimeError, KeyboardInterrupt])
def test_write_errors_preserve_fault_without_hidden_recovery(rig, monkeypatch, exception):
    rig.controller.connect()
    rig.device.calls.clear()

    def fail(value):
        raise exception("write failed")

    monkeypatch.setattr(rig.device, "SetOperatingState", fail)
    with pytest.raises(KeyboardInterrupt if exception is KeyboardInterrupt else ShutterError):
        rig.controller.open_shutter()
    assert rig.device.calls == []
    assert "write failed" in rig.controller.get_cached_status().error
    rig.controller.disconnect(close_shutter=False)
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


@pytest.mark.parametrize(
    "method,args",
    [
        ("set_operating_state", ("bad",)),
        ("set_operating_mode", ("bad",)),
        ("configure_triggers", (None,)),
    ],
)
def test_invalid_setter_inputs_fail_without_io(rig, method, args):
    with pytest.raises(ValueError):
        getattr(rig.controller, method)(*args)
    assert not rig.device.calls and not rig.manager_calls


@pytest.mark.parametrize(
    "method", ["get_shutter_state", "get_operating_state", "get_operating_mode", "get_status_bits"]
)
def test_disconnected_specific_getters_do_not_load_sdk(rig, method):
    with pytest.raises(ShutterError, match="No device connected"):
        getattr(rig.controller, method)()
    assert not rig.device.calls and not rig.manager_calls


def test_confirmation_does_not_cross_serial_or_instance(rig):
    c = rig.controller
    c.serial_number = "68000001"
    c.confirm_interlock("68000001")
    rig.device.interlock = False
    other = KCubeShutter("68000001")
    assert not other.connect().operator_interlock_confirmed
    other.disconnect(close_shutter=False)
    c.serial_number = "68000002"
    c.serial_number = "68000001"
    assert not c.connect().interlock_ready
    c.disconnect(close_shutter=False)


def test_confirmation_requires_explicit_selected_disconnected_controller(rig):
    with pytest.raises(ValueError):
        rig.controller.confirm_interlock("68000001")
    rig.controller.serial_number = "68000001"
    with pytest.raises(ValueError):
        rig.controller.confirm_interlock("68000002")
    rig.controller.connect()
    with pytest.raises(ShutterError):
        rig.controller.confirm_interlock("68000001")
    rig.controller.disconnect(close_shutter=False)
