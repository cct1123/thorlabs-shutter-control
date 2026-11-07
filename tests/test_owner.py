"""TEST-202/204/206/207: ownership, policy, ambiguity and priority cleanup."""

import json
import math
import subprocess
import sys
import time
from dataclasses import asdict, replace
from threading import Event, Thread

import pytest
from conftest import FakeTransport

from thorlabs_shutter_control import Policy, Route, ShutterError, ShutterHub
from thorlabs_shutter_control.errors import Cancelled, IdentityMismatch, ProtocolError


def test_connect_read_manual_on_off_and_passive_release(bench):
    hub, devices, _, _ = bench
    assert not devices
    assert not hub.connection_snapshot("beam").has_device
    assert hub.connect(0).identity_verified
    device = devices[0]
    assert not device.output_frames
    assert hub.get_status("beam").feedback.electrical_state == "off"
    hub.set_manual_mode("beam")
    result = hub.open_shutter("beam")
    assert result.requested_state == "on"
    assert result.feedback.electrical_state == "on"
    assert result.feedback.shutter_state == "unknown"
    assert not result.transition_confirmed
    hub.close_shutter("beam")
    count = len(device.output_frames)
    hub.close()
    assert device.closed and len(device.output_frames) == count


@pytest.mark.parametrize("qualified", [False, True])
@pytest.mark.parametrize("faulted", [False, True])
def test_readonly_shutdown_does_not_send_incidental_off(config, tmp_path, qualified, faulted):
    config = config if qualified else replace(config, policy=None)
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        assert hub.get_status("beam").feedback.electrical_state == "off"
        if faulted:
            device.serial = "68000002"
            with pytest.raises(IdentityMismatch):
                hub.get_status("beam")
            with pytest.raises(ShutterError, match="Read-only fault"):
                hub.shutdown_outputs()
        else:
            hub.shutdown_outputs()
        assert not device.output_frames
    assert device.closed


def test_context_release_retains_original_error_and_failed_handle(bench):
    hub, devices, _, _ = bench
    with pytest.raises(ValueError, match="original") as caught:
        with hub:
            hub.connect("beam")
            devices[0].close_fails = True
            raise ValueError("original")
    assert any("release failed" in note for note in caught.value.__notes__)
    assert hub.connection_snapshot("beam").has_device
    devices[0].close_fails = False
    hub.close()


@pytest.mark.parametrize(
    "attribute,value",
    [
        ("serial", "68000002"),
        ("model", "TSC001"),
        ("firmware", (8, 0, 1)),
    ],
)
def test_identity_mismatch_cannot_write(config, tmp_path, attribute, value):
    device = FakeTransport(config)
    setattr(device, attribute, value)
    hub = ShutterHub([config], transport_factory=lambda c, d: device, lock_directory=tmp_path)
    with pytest.raises(IdentityMismatch):
        hub.connect("beam")
    assert device.closed and not device.output_frames


def test_changed_identity_after_connect_never_receives_cleanup_output(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].serial = "68000002"
    with pytest.raises(IdentityMismatch):
        hub.open_shutter("beam")
    assert not hub.connection_snapshot("beam").identity_verified
    with pytest.raises(ShutterError):
        hub.safe_state("beam")
    assert not devices[0].output_frames


@pytest.mark.parametrize(
    "field,value", [("name", "beam"), ("channel", 0), ("serial_number", "68000001")]
)
def test_duplicate_mapping_rejected(config, second, field, value):
    with pytest.raises(ValueError, match="Duplicate"):
        ShutterHub([config, replace(second, **{field: value})])


def test_duplicate_vcp_route_rejected(config, second):
    with pytest.raises(ValueError, match="Duplicate"):
        ShutterHub(
            [
                replace(config, route=Route("vcp", port="COM9")),
                replace(second, route=Route("vcp", port="COM9")),
            ]
        )


@pytest.mark.parametrize("field", ["hub_serial", "host", "bay", "hub_firmware"])
def test_usb_routes_reject_even_empty_hub_fields(field):
    with pytest.raises(ValueError, match="hub fields"):
        Route("d2xx", **{field: ""})


def test_noncanonical_com_aliases_rejected_before_io():
    for alias in ("com9", "COM09", r"\\.\COM9", "COM9 "):
        with pytest.raises(ValueError):
            Route("vcp", port=alias)


def test_external_keh3_and_vcp_control_remain_blocked(config):
    from thorlabs_shutter_control.transport import require_control_route

    lan = replace(
        config,
        route=Route(
            "keh3",
            hub_serial="120000001",
            host="192.0.2.1",
            bay="external",
            hub_firmware="unqualified",
        ),
    )
    for candidate in (lan, replace(config, route=Route("vcp", port="COM9"))):
        with pytest.raises(ShutterError):
            require_control_route(candidate)


@pytest.mark.parametrize("bay,port", [("left", 40304), ("middle", 40305), ("right", 40306)])
def test_docked_keh3_uses_same_qualified_manual_control(config, tmp_path, bay, port):
    """Software route regression, not evidence of physical hub/load qualification."""
    config = replace(
        config,
        route=Route(
            "keh3",
            host="192.0.2.1",
            bay=bay,
            hub_serial="UNKNOWN",
            hub_firmware="UNKNOWN",
        ),
    )
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        connected = hub.connect("beam")
        assert connected.endpoint == f"192.0.2.1:{port}"
        assert not device.output_frames
        hub.set_manual_mode("beam")
        assert hub.set_solenoid("beam", True).feedback.electrical_state == "on"
        assert hub.set_solenoid("beam", False).feedback.electrical_state == "off"
        assert [f.encode().hex() for f in device.output_frames] == [
            "cb0401015001",
            "cb0401025001",
        ]
    assert device.closed


def test_docked_keh3_without_load_policy_cannot_actuate(config, tmp_path):
    config = replace(
        config,
        policy=None,
        route=Route(
            "keh3",
            host="192.0.2.1",
            bay="middle",
            hub_serial="UNKNOWN",
            hub_firmware="UNKNOWN",
        ),
    )
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        for operation in (hub.open_shutter, hub.safe_state, hub.set_manual_mode):
            with pytest.raises(ShutterError, match="unqualified"):
                operation("beam")
        hub.shutdown_outputs()
        assert not device.output_frames


def test_external_keh3_readback_cannot_become_output_by_injection(config, tmp_path):
    lan = replace(
        config,
        route=Route(
            "keh3",
            hub_serial="120000001",
            host="192.0.2.1",
            bay="external",
            hub_firmware="unqualified",
        ),
    )
    device = FakeTransport(lan)
    device.mode, device.state = 4, 0  # Actual firmware1.0.7 Trigger/OFF scalar reply.
    with ShutterHub([lan], transport_factory=lambda c, d: device, lock_directory=tmp_path) as hub:
        assert hub.connect("beam").identity.serial_number == lan.serial_number
        feedback = hub.get_status("beam").feedback
        assert feedback.electrical_state == "off" and feedback.status_bits == 0x2000
        assert feedback.operating_state == "unknown"  # OFF does not prove unprimed/inactive.
        assert not any(f.message_id == 0x04CC for _, f in device.history)
        assert hub.get_solenoid_state_reply("beam") == 0
        for action in (hub.open_shutter, hub.safe_state, hub.set_manual_mode):
            with pytest.raises(ShutterError, match="unavailable"):
                action("beam")
        assert not device.output_frames
    assert device.closed


@pytest.mark.parametrize("mode", [2, 3, 4])
def test_nonmanual_on_refused_without_incidental_off(bench, mode):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].mode = mode
    with pytest.raises(ShutterError, match="Manual"):
        hub.open_shutter("beam")
    assert not devices[0].output_frames


def test_disabled_interlock_requirement_refuses_on(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].interlock = 2
    with pytest.raises(ShutterError, match="interlock"):
        hub.open_shutter("beam")
    assert not devices[0].output_frames


def test_manual_selection_does_not_rewrite_an_already_manual_controller(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    assert hub.set_manual_mode("beam").feedback.operating_mode == "manual"
    assert not devices[0].output_frames


@pytest.mark.parametrize("allowed", [False, True])
def test_mode_transition_requires_separate_persistent_permission(config, tmp_path, allowed):
    config = replace(config, policy=replace(config.policy, allow_persistent_mode_changes=allowed))
    device = FakeTransport(config)
    device.mode = 2
    hub = ShutterHub([config], transport_factory=lambda c, d: device, lock_directory=tmp_path)
    try:
        hub.connect("beam")
        if allowed:
            assert (
                hub.set_manual_mode("beam", source_inhibited=True).feedback.operating_mode
                == "manual"
            )
            assert [f.message_id for f in device.output_frames] == [0x04CB, 0x04C0]
        else:
            with pytest.raises(ShutterError, match="persistent"):
                hub.set_manual_mode("beam", source_inhibited=True)
            assert not device.output_frames
            assert not hub.connection_snapshot("beam").error
    finally:
        hub.close()


def test_mode_permission_is_boolean(config):
    with pytest.raises(ValueError, match="boolean"):
        replace(config.policy, allow_persistent_mode_changes=1)


@pytest.mark.parametrize("source_inhibited", [False, True])
def test_trigger_manual_requires_explicit_protection(config, tmp_path, source_inhibited):
    config = replace(config, policy=replace(config.policy, allow_persistent_mode_changes=True))
    device = FakeTransport(config)
    device.mode = 4
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        if source_inhibited:
            result = hub.set_manual_mode("beam", source_inhibited=True)
            assert result.feedback.operating_mode == "manual"
            assert [(f.message_id, f.param2) for f in device.output_frames] == [
                (0x04CB, 2),
                (0x04C0, 1),
            ]
        else:
            with pytest.raises(ShutterError, match="source_inhibited"):
                hub.set_manual_mode("beam")
            assert not device.output_frames


def test_failed_mode_transition_uses_the_output_cleanup_guard(config, tmp_path):
    config = replace(config, policy=replace(config.policy, allow_persistent_mode_changes=True))
    device = FakeTransport(config)
    device.mode = 2
    original = device.write

    def write(raw, deadline):
        count = original(raw, deadline)
        if raw[:2] == bytes.fromhex("c0 04"):
            device.state = 1  # Independent operating state can affect output after mode change.
        return count

    device.write = write
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ShutterError, match="changed output"):
            hub.set_manual_mode("beam", source_inhibited=True)
        assert [(f.message_id, f.param2) for f in device.output_frames] == [
            (0x04CB, 2),
            (0x04C0, 1),
            (0x04CB, 2),
        ]
        status = hub.connection_snapshot("beam")
        assert status.error and "Electrical OFF readback" in status.cleanup


@pytest.mark.parametrize("value", [math.nan, math.inf, -1, 0, True, "1", 51])
def test_invalid_exposure_before_io(bench, value):
    hub, devices, _, _ = bench
    with pytest.raises((ValueError, ShutterError)):
        hub.pulse("beam", value)
    assert not devices


def test_unqualified_or_finite_load_cannot_write(config, tmp_path):
    for policy in (None, Policy("test", "finite load", "closed", 0, max_on_s=0.1)):
        hub = ShutterHub([replace(config, policy=policy)], lock_directory=tmp_path)
        with pytest.raises(ShutterError):
            hub.pulse("beam", 0.05)


def test_pulse_validation_is_passive_and_shared_with_execution(bench):
    hub, devices, _, _ = bench
    assert hub.validate_pulse("beam", 0.5) == 0.5
    assert not devices


def test_invalid_mode_and_on_value_before_io(bench):
    hub, devices, _, _ = bench
    with pytest.raises(ShutterError, match="qualified_modes"):
        hub.set_operating_mode("beam", "triggered")
    with pytest.raises(ValueError):
        hub.set_solenoid("beam", 1)
    assert not devices


def test_off_interval_is_not_silently_waited_or_bypassed(config, tmp_path):
    policy = replace(config.policy, min_off_s=0.1)
    device = FakeTransport(config)
    hub = ShutterHub(
        [replace(config, policy=policy)],
        transport_factory=lambda c, d: device,
        lock_directory=tmp_path,
    )
    hub.connect("beam")
    with pytest.raises(ShutterError, match="interval"):
        hub.open_shutter("beam")
    assert not device.output_frames
    time.sleep(0.11)
    hub.open_shutter("beam")
    hub.safe_state("beam")
    with pytest.raises(ShutterError, match="interval"):
        hub.open_shutter("beam")
    hub.close()


def test_off_interval_begins_after_output_readback(config, tmp_path, monkeypatch):
    """A slow OFF transition must not consume the required electrical rest time."""
    now = [100.0]
    monkeypatch.setattr("thorlabs_shutter_control.controller.clock", lambda: now[0])
    config = replace(config, policy=replace(config.policy, min_off_s=1.0))
    device = FakeTransport(config)
    device.state = 1
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        driver = hub._channel("beam").driver
        wait_output = driver.wait_output

        def delayed_off(on, deadline, **kwargs):
            if not on:
                now[0] += 0.75
            return wait_output(on, deadline, **kwargs)

        monkeypatch.setattr(driver, "wait_output", delayed_off)
        hub.safe_state("beam")
        now[0] = 101.1  # Only 0.35 s after confirmed OFF, despite 1.1 s since dispatch.
        with pytest.raises(ShutterError, match="interval"):
            hub.set_solenoid("beam", True)
        assert [f.param2 for f in device.output_frames] == [2]
        now[0] = 101.8
        assert hub.set_solenoid("beam", True).feedback.electrical_state == "on"
        hub.safe_state("beam")


def test_partial_output_latches_uncertainty_and_never_replays(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.partial = True
    with pytest.raises(ProtocolError, match="Partial") as caught:
        hub.open_shutter("beam")
    assert [f.param2 for f in device.output_frames] == [1]
    assert caught.value.__notes__
    assert any("Write framing unknown" in note for note in caught.value.__notes__)
    device.partial = False
    with pytest.raises(ProtocolError, match="Write framing unknown"):
        hub.safe_state("beam")
    before = len(device.output_frames)
    with pytest.raises(ShutterError, match="lockout"):
        hub.open_shutter("beam")
    assert len(device.output_frames) == before
    assert hub.connection_snapshot("beam").error


def test_process_reconnect_does_not_clear_active_output_journal(bench):
    hub, devices, factory, path = bench
    hub.connect("beam")
    hub.open_shutter("beam")
    hub.close()
    hub.connect("beam")
    assert hub.connection_snapshot("beam").error
    with pytest.raises(ShutterError, match="lockout"):
        hub.open_shutter("beam")
    with pytest.raises(ShutterError):
        hub.recover("beam")
    result = hub.recover(
        "beam",
        source_inhibited=True,
        optical_closed=True,
        evidence="simulated independent human observation",
    )
    assert not result.error and result.optical_observed_state == "closed"
    assert result.feedback.shutter_state == "unknown"
    assert not devices[-1].output_frames  # Recovery is passive and never restores ON.


def test_cross_process_and_same_process_ownership(bench):
    hub, _, factory, path = bench
    hub.connect("beam")
    other = ShutterHub(hub.configs, transport_factory=factory, lock_directory=path)
    with pytest.raises(ShutterError, match="owned"):
        other.connect("beam")
    code = """
import json, sys
from thorlabs_shutter_control import ControllerConfig, Route
from thorlabs_shutter_control.ownership import Claim
from thorlabs_shutter_control.errors import ShutterError
c = ControllerConfig('beam',0,'fake','68000001',('1.0.7',),Route('d2xx'))
try:
    Claim(c, sys.argv[1]).acquire()
except ShutterError:
    print('owned')
else:
    raise SystemExit(2)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(path)], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    assert "owned" in result.stdout


def test_all_channel_cleanup_survives_one_failed_release(config, second, tmp_path):
    devices = {c.name: FakeTransport(c) for c in (config, second)}
    hub = ShutterHub(
        [config, second], transport_factory=lambda c, d: devices[c.name], lock_directory=tmp_path
    )
    for name in devices:
        hub.connect(name)
    devices["beam"].close_fails = True
    with pytest.raises(ShutterError, match="Release incomplete"):
        hub.close()
    assert devices["second"].closed
    assert hub.connection_snapshot("beam").has_device
    devices["beam"].close_fails = False
    hub.close()


def test_multiple_routes_never_redirect_output(config, second, tmp_path):
    devices = {c.name: FakeTransport(c) for c in (config, second)}
    hub = ShutterHub(
        [config, second], transport_factory=lambda c, d: devices[c.name], lock_directory=tmp_path
    )
    for name in devices:
        hub.connect(name)
    devices["beam"].serial = "68000002"
    with pytest.raises(IdentityMismatch):
        hub.open_shutter("beam")
    hub.open_shutter("second")
    assert not devices["beam"].output_frames
    assert [f.param2 for f in devices["second"].output_frames] == [1]
    with pytest.raises(ShutterError):
        hub.shutdown_outputs()
    assert devices["second"].state == 2
    hub.close()


def test_protective_dispatch_interrupts_long_pulse(bench, record_property):
    hub, devices, _, _ = bench
    hub.connect("beam")
    errors, done = [], Event()

    def pulse():
        try:
            hub.pulse("beam", 5)
        except BaseException as exc:
            errors.append(exc)
        finally:
            done.set()

    worker = Thread(target=pulse)
    worker.start()
    end = time.perf_counter() + 1
    while devices[0].state != 1 and time.perf_counter() < end:
        time.sleep(0.001)
    assert devices[0].state == 1
    started = time.perf_counter()
    hub.safe_state("beam")
    worker.join(1)
    offs = [t for t, f in devices[0].history if f.message_id == 0x04CB and f.param2 == 2]
    dispatch_ms = 1000 * (offs[0] - started)
    record_property("simulated_protective_dispatch_ms", dispatch_ms)
    assert dispatch_ms < 250
    assert done.is_set() and isinstance(errors[0], Cancelled)
    assert devices[0].state == 2
    assert hub.connection_snapshot("beam").error


def test_status_json_keeps_electrical_and_optical_separate(bench):
    hub, _, _, _ = bench
    hub.connect("beam")
    value = json.loads(json.dumps(asdict(hub.get_status("beam"))))
    assert value["feedback"]["electrical_state"] == "off"
    assert value["feedback"]["shutter_state"] == "unknown"
    assert value["optical_observed_state"] == "unknown"


def test_failed_on_readback_uses_separate_cleanup_budget_and_never_replays(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    original_write = device.write

    def write(raw, deadline):
        count = original_write(raw, deadline)
        if raw[:2] == bytes.fromhex("cb 04"):
            device.silent.add(0x0429)
        return count

    device.write = write
    hub.query_timeout = 0.03
    hub.cleanup_timeout = 0.1
    with pytest.raises(ShutterError) as caught:
        hub.open_shutter("beam")
    assert [f.param2 for f in device.output_frames] == [1, 2]
    assert any("Separate cleanup" in note for note in caught.value.__notes__)
    assert hub.connection_snapshot("beam").error
    before = len(device.output_frames)
    with pytest.raises(ShutterError, match="lockout"):
        hub.open_shutter("beam")
    assert len(device.output_frames) == before


def test_query_cancellation_prioritizes_off_and_preserves_original_failure(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.silent.add(0x04C1)
    errors = []

    def read():
        try:
            hub.get_status("beam")
        except BaseException as exc:
            errors.append(exc)

    worker = Thread(target=read)
    worker.start()
    end = time.perf_counter() + 1
    while not any(f.message_id == 0x04C1 for _, f in device.history):
        assert time.perf_counter() < end
        time.sleep(0.001)
    started = time.perf_counter()
    with pytest.raises(ShutterError, match="ambiguous"):
        hub.safe_state("beam")
    worker.join(1)
    off = next(t for t, f in device.history if f.message_id == 0x04CB)
    assert off - started < 0.25
    assert isinstance(errors[0], Cancelled)
    status = hub.connection_snapshot("beam")
    assert "cancel" in status.error.lower()
    assert "unconfirmed" in status.cleanup.lower()


def test_concurrent_shutters_keep_independent_routes(config, second, tmp_path):
    devices = {c.name: FakeTransport(c) for c in (config, second)}
    hub = ShutterHub(
        [config, second], transport_factory=lambda c, d: devices[c.name], lock_directory=tmp_path
    )
    for name in devices:
        hub.connect(name)
    results, errors = [], []

    def pulse(name):
        try:
            results.append(hub.pulse(name, 0.01).name)
        except BaseException as exc:
            errors.append(exc)

    workers = [Thread(target=pulse, args=(name,)) for name in devices]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(1)
    assert not errors and set(results) == set(devices)
    assert all([f.param2 for f in device.output_frames] == [1, 2] for device in devices.values())
    hub.close()


def test_passive_release_does_not_erase_output_cleanup_obligation(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    hub.open_shutter("beam")
    hub.close()
    assert devices[0].state == 1  # Release was passive.
    with pytest.raises(ShutterError, match="unavailable"):
        hub.shutdown_outputs()
    assert len(devices) == 1  # Cleanup must not reconnect or redirect.


def test_new_on_does_not_reuse_a_previous_off_cleanup_result(bench):
    hub, _, _, _ = bench
    hub.connect("beam")
    assert hub.safe_state("beam").cleanup
    assert hub.open_shutter("beam").cleanup is None


def test_failed_pulse_off_reports_current_cleanup_failure(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    hub.safe_state("beam")
    device = devices[0]
    original_write = device.write

    def write(raw, deadline):
        count = original_write(raw, deadline)
        if raw == bytes.fromhex("cb 04 01 02 50 01"):
            device.silent.add(0x0429)
        return count

    device.write = write
    hub.cleanup_timeout = 0.02
    with pytest.raises(ShutterError):
        hub.pulse("beam", 0.001)
    status = hub.connection_snapshot("beam")
    assert "unconfirmed" in status.cleanup.lower()
    assert status.error
    assert [f.param2 for f in device.output_frames] == [2, 1, 2]


def test_recovery_never_clears_a_pending_protective_request(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    channel = hub._channel("beam")
    channel.cancel.set()  # A protective caller has signalled before taking the lock.
    count = len(devices)
    try:
        with pytest.raises(Cancelled):
            hub.recover("beam", source_inhibited=True, optical_closed=True, evidence="simulation")
        assert channel.cancel.is_set()
        assert len(devices) == count and not devices[0].closed
    finally:
        channel.cancel.clear()
