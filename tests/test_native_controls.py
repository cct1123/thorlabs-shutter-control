"""REQ-225 software-only contracts. These checks establish no physical behavior."""

import struct
from dataclasses import replace

import pytest
from conftest import FakeTransport
from ui_helpers import post_callback

from thorlabs_shutter_control import CycleParameters, ShutterError, ShutterHub
from thorlabs_shutter_control.device import KSC101
from thorlabs_shutter_control.errors import ProtocolError
from thorlabs_shutter_control.protocol import Deadline, Decoder, Frame


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


def test_current_profile_stays_manual_only_and_settings_disabled(config):
    assert config.policy.qualified_modes == ("manual",)
    assert not config.policy.allow_device_settings
    assert not config.policy.allow_persistent_settings
    hub = ShutterHub([config])
    for mode in ("single", "auto", "triggered"):
        with pytest.raises(ShutterError, match="qualified_modes"):
            hub.set_operating_mode("beam", mode, source_inhibited=True)
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
        result = hub.start("beam", source_inhibited=True)
        assert result.requested_state == "start"
        assert result.feedback.operating_state == "unknown" and not result.transition_confirmed
        result = hub.safe_state("beam")
        assert result.feedback.operating_mode == mode and result.feedback.electrical_state == "off"
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
        assert result.feedback.electrical_state == "off"
        assert not device.output_frames
        writes = [f for _, f in device.history if f.message_id in (0x04C3, 0x04B9)]
        assert [f.message_id for f in writes] == [0x04C3, 0x04B9]


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
    sample, _ = execute_action(hub, "release", "beam")
    assert not sample.has_device


def test_webui_renderer_keeps_unavailable_feedback_unknown(bench):
    from dataclasses import asdict

    from thorlabs_shutter_control.gui import create_app

    hub, _, _, _ = bench
    hub.connect("beam")
    sample = asdict(hub.get_status("beam"))
    app = create_app(hub)
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    rendered = post_callback(app, key, {"sample": sample, "target": "beam"}, "sample.data")
    assert rendered["on"]["disabled"] is False
    assert rendered["auto"]["disabled"] is True
    assert rendered["apply-settings"]["disabled"] is True
    assert rendered["key-lamp-value"]["children"] == "Unknown"
    assert rendered["ready-lamp-value"]["children"] == "Unknown"
    assert rendered["output-lamp-value"]["children"] == "Off"
    assert rendered["active-lamp-value"]["children"] == "Unknown"
