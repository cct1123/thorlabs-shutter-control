"""REQ-225 software-only contracts. These checks establish no physical behavior."""

import struct
from dataclasses import replace

import pytest
from conftest import FakeTransport
from ui_helpers import post_callback

from thorlabs_shutter_control import CycleParameters, ShutterError, ShutterHub
from thorlabs_shutter_control.controller import KSC101
from thorlabs_shutter_control.protocol import Deadline, Decoder, Frame, ProtocolError


def test_cycle_bytes_match_apt_page186_literal():
    parameters = CycleParameters(1000, 1000, 20)
    literal = bytes.fromhex("0100e8030000e803000014000000")
    assert parameters.encode() == literal
    assert CycleParameters.decode(literal) == parameters
    assert Frame(0x04C3, payload=parameters.encode()).encode() == bytes.fromhex(
        "c3040e00d0010100e8030000e803000014000000"
    )
    raw = bytes.fromhex("c5040e008150") + literal
    for cut in range(len(raw) + 1):
        decoder = Decoder(destination=1, source=0x50)
        frames = decoder.feed(raw[:cut]) + decoder.feed(raw[cut:])
        assert len(frames) == 1 and CycleParameters.decode(frames[0].payload) == parameters


@pytest.mark.parametrize(
    "values",
    [
        (99, 1000, 1),
        (10001, 1000, 1),
        (1000, True, 1),
        (1000, 1000, -1),
        (1000, 1000, 1000001),
        (1000.5, 1000, 1),
    ],
)
def test_invalid_cycle_values_rejected(values):
    with pytest.raises(ValueError):
        CycleParameters(*values)


def test_wrong_cycle_channel_and_frame_length_are_rejected():
    with pytest.raises(ValueError, match="channel"):
        CycleParameters.decode(struct.pack("<HIII", 2, 1000, 1000, 1))
    with pytest.raises(ProtocolError):
        Decoder().feed(bytes.fromhex("c5040c008150"))


def test_identify_and_persistence_literal_commands():
    """Outbound frame sink only, not a device or an acknowledgement generator."""
    sent = []

    class Sink:
        def send(self, frame, deadline):
            sent.append(frame.encode())

    driver = KSC101(Sink(), None)
    driver.blink_identify(Deadline(1))
    driver.persist_cycle_parameters(Deadline(1))
    assert sent == [bytes.fromhex("230201005001"), bytes.fromhex("b9040400d0010100c304")]


def test_default_policy_stays_manual_only_and_settings_disabled(config):
    assert config.policy.qualified_modes == ("manual",)
    assert not config.policy.allow_device_settings
    assert not config.policy.allow_persistent_settings
    hub = ShutterHub([config])
    with pytest.raises(ShutterError, match="allow_device_settings"):
        hub.set_cycle_parameters("beam", CycleParameters(1000, 2000, 1), source_inhibited=True)
    assert not hub.connection_snapshot("beam").has_device


@pytest.mark.parametrize(
    "modes", [("single",), ("manual", "manual"), ("manual", "unknown"), ("manual", [])]
)
def test_invalid_qualification_lists_fail(config, modes):
    with pytest.raises(ValueError, match="qualified_modes"):
        replace(config.policy, qualified_modes=modes)


@pytest.mark.parametrize("mode", ["single", "auto", "triggered"])
def test_mode_selection_without_confirmation_does_not_qualify_native_start(config, tmp_path, mode):
    from thorlabs_shutter_control.gui import execute_action

    config = replace(config, policy=replace(config.policy, allow_persistent_mode_changes=True))
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        execute_action(hub, "connect", "beam")
        from thorlabs_shutter_control.gui import create_app

        app = create_app(hub)
        key = next(key for key in app.callback_map if "notice.children" in key)
        rendered = post_callback(
            app, key, {"target": "beam", mode: 1, "source-inhibited": []}, f"{mode}.n_clicks"
        )
        assert "Mode selected and read back" in rendered["notice"]["children"]
        assert rendered["sample"]["data"]["operating_mode"] == mode
        selected = hub.get_status("beam")
        assert selected.operating_mode == mode
        assert selected.electrical_state == "off"
        with pytest.raises(ShutterError, match="qualified_modes"):
            execute_action(hub, "on", "beam", source_inhibited=True)
        # Enabled GUI controls still use the owner's qualification checks.
        from thorlabs_shutter_control.gui import create_app

        app = create_app(hub)
        key = next(key for key in app.callback_map if "notice.children" in key)
        rendered = post_callback(
            app,
            key,
            {"target": "beam", "on": 1, "source-inhibited": ["protected"]},
            "on.n_clicks",
        )
        assert "qualified_modes" in rendered["notice"]["children"]
        assert not rendered["sample"]["data"]["error"]
        assert not any(f.message_id == 0x04CB and f.param2 == 1 for f in device.output_frames)
        stopped, _, _ = execute_action(hub, "off", "beam")
        assert stopped.electrical_state == "off" and not stopped.error
        selected, _, _ = execute_action(hub, "manual", "beam", source_inhibited=True)
        assert selected.operating_mode == "manual"
        assert selected.interlock_required
        released, _, _ = execute_action(hub, "release", "beam")
        assert not released.has_device


def test_failed_mode_selection_retains_fault_and_can_confirm_off(config, tmp_path):
    config = replace(config, policy=replace(config.policy, allow_persistent_mode_changes=True))
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        driver = hub._channels["beam"].driver
        change_mode = driver.set_operating_mode

        def wrong_mode(mode, deadline):
            change_mode(mode, deadline)
            device.mode = 3  # Wrong readback must fault, even though output stayed OFF.

        driver.set_operating_mode = wrong_mode
        with pytest.raises(ShutterError, match="unconfirmed"):
            hub.set_operating_mode("beam", "single", source_inhibited=True)
        snapshot = hub.connection_snapshot("beam")
        assert snapshot.error and "unconfirmed" in snapshot.error
        assert snapshot.cleanup.startswith("Electrical OFF readback")
        assert hub._channels["beam"].claim.journal.exists()
        assert not any(f.message_id == 0x04CB and f.param2 == 1 for f in device.output_frames)


@pytest.mark.parametrize("mode", ["single", "auto", "triggered"])
def test_native_start_stop_uses_one_output_request_and_preserves_mode(config, tmp_path, mode):
    policy = replace(
        config.policy,
        qualified_modes=("manual", mode),
        allow_persistent_mode_changes=True,
        allow_continuous_cycles=mode == "triggered",
    )
    config = replace(config, policy=policy)
    device = FakeTransport(config)
    if mode == "triggered":
        device.cycle = (1000, 2000, 0)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        hub.set_operating_mode("beam", mode, source_inhibited=True)
        result = hub.start("beam")
        assert result.requested_state == "start" and result.optical_closed_at is None
        result = hub.safe_state("beam")
        assert result.operating_mode == mode and result.electrical_state == "off"
        assert not result.error
        assert [f.param2 for f in device.output_frames if f.message_id == 0x04CB] == [2, 1, 2]


@pytest.mark.parametrize("cycles", [0, 3])
def test_native_auto_limits_reject_before_output(config, tmp_path, cycles):
    config = replace(config, policy=replace(config.policy, qualified_modes=("manual", "auto")))
    device = FakeTransport(config)
    device.mode, device.cycle = 3, (1000, 2000, cycles)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises((ShutterError, ValueError)):
            hub.start("beam", source_inhibited=True)
        assert not device.output_frames


def test_cycle_write_readback_and_explicit_storage_request(config, tmp_path):
    config = replace(
        config,
        policy=replace(config.policy, allow_device_settings=True, allow_persistent_settings=True),
    )
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        parameters = CycleParameters(2500, 2000, 1)
        result = hub.set_cycle_parameters("beam", parameters, source_inhibited=True, persist=True)
        assert result.cycle_parameters == parameters
        assert "restart verification required" in result.settings_persistence
        assert result.electrical_state == "off"
        assert not device.output_frames
        writes = [f for _, f in device.history if f.message_id in (0x04C3, 0x04B9)]
        assert [f.message_id for f in writes] == [0x04C3, 0x04B9]
        frames = [f.message_id for _, f in device.history]
        # One fresh OFF read before the settings write, one after; no duplicate poll.
        assert frames[: frames.index(0x04C3)].count(0x0429) == 1
        assert frames.count(0x0429) == 2


@pytest.mark.parametrize(
    "mode,state,interlock,message",
    [(1, 1, 1, "electrical OFF"), (2, 2, 1, "Manual mode"), (1, 2, 2, "interlock requirement")],
)
def test_settings_preflight_refuses_active_or_unqualified_state(
    config, tmp_path, mode, state, interlock, message
):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    device.mode, device.state, device.interlock = mode, state, interlock
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ShutterError, match=message):
            hub.set_cycle_parameters("beam", CycleParameters(1000, 2000, 1), source_inhibited=True)
        assert not device.output_frames
        assert not any(f.message_id in (0x04C3, 0x04B9) for _, f in device.history)


def test_cycle_read_and_identify_do_not_acquire_an_output_cleanup_obligation(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    assert hub.get_cycle_parameters("beam").cycle_parameters == CycleParameters(1000, 2000, 1)
    hub.blink_identify("beam")
    hub.shutdown_outputs()
    assert not devices[0].output_frames


def test_policy_rest_applies_to_native_settings_before_io(config):
    config = replace(config, policy=replace(config.policy, min_off_s=2, allow_device_settings=True))
    hub = ShutterHub([config])
    with pytest.raises(ValueError, match="OFF rest"):
        hub.set_cycle_parameters("beam", CycleParameters(1000, 1000, 1), source_inhibited=True)
    assert not hub.connection_snapshot("beam").has_device


def test_settings_readback_mismatch_latches_fault_and_attempts_off(config, tmp_path, monkeypatch):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        driver = hub._channels["beam"].driver
        monkeypatch.setattr(driver, "cycle_parameters", lambda d: CycleParameters(1000, 2000, 1))
        with pytest.raises(ShutterError, match="readback differs"):
            hub.set_cycle_parameters("beam", CycleParameters(2500, 2000, 1), source_inhibited=True)
        snapshot = hub.connection_snapshot("beam")
        assert snapshot.error and "readback differs" in snapshot.error
        assert hub._channels["beam"].claim.journal.exists()
        assert [f.param2 for f in device.output_frames] == [2]


def test_webui_start_requires_stop_before_release(bench):
    from thorlabs_shutter_control.gui import execute_action

    hub, devices, _, _ = bench
    execute_action(hub, "connect", "beam")
    execute_action(hub, "on", "beam")
    with pytest.raises(ShutterError, match="Stop / OFF"):
        execute_action(hub, "release", "beam")
    assert not devices[0].closed
    execute_action(hub, "off", "beam")
    sample, _, _ = execute_action(hub, "release", "beam")
    assert not sample.has_device


def test_webui_renderer_shows_documented_flags_and_host_request(bench):
    from dataclasses import asdict

    from thorlabs_shutter_control.gui import create_app

    hub, _, _, _ = bench
    hub.connect("beam")
    sample = asdict(hub.get_status("beam"))
    app = create_app(hub)
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    rendered = post_callback(app, key, {"sample": sample, "target": "beam"}, "sample.data")
    assert rendered["on"]["disabled"] is False
    assert rendered["auto"]["disabled"] is False
    assert rendered["apply-settings"]["disabled"] is False
    assert rendered["interlock-lamp-value"]["children"] == "Clear"
    assert rendered["channel-lamp-value"]["children"] == "Clear"
    assert rendered["output-lamp-value"]["children"] == "Off"
    assert rendered["active-lamp-value"]["children"] == "No pending request"


def test_webui_enabled_settings_still_refuse_unpermitted_write(bench):
    from thorlabs_shutter_control.gui import create_app

    hub, devices, _, _ = bench
    hub.connect("beam")
    before = len(devices[0].history)
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    rendered = post_callback(
        app,
        key,
        {
            "target": "beam",
            "apply-settings": 1,
            "cycle-on": 1000,
            "cycle-off": 2000,
            "cycles": 1,
            "source-inhibited": ["protected"],
        },
        "apply-settings.n_clicks",
    )
    assert "allow_device_settings" in rendered["notice"]["children"]
    assert len(devices[0].history) == before


@pytest.mark.parametrize("mode", ["single", "auto", "triggered"])
def test_tracked_profile_allows_native_mode_activation_gate(tmp_path, mode):
    from pathlib import Path

    from thorlabs_shutter_control import load_config

    (tracked,) = load_config(Path(__file__).resolve().parents[1] / "config/shutter.ethernet.toml")
    device = FakeTransport(tracked)
    with ShutterHub(
        [tracked], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect(tracked.name)
        hub.set_operating_mode(tracked.name, mode)
        if mode == "triggered":
            with pytest.raises(ShutterError, match="priming requires"):
                hub.start(tracked.name, source_inhibited=True)
        else:
            assert hub.start(tracked.name, source_inhibited=True).requested_state == "start"
        assert hub.safe_state(tracked.name).electrical_state == "off"
