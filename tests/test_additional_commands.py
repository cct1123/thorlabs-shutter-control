"""Issue42.1 literal-wire and owner regressions; no instruments or motor-layout guesses."""

import struct
from dataclasses import replace

import pytest
from conftest import FakeTransport

from thorlabs_shutter_control import ShutterError, ShutterHub
from thorlabs_shutter_control.controller import KSC101, IdentityMismatch
from thorlabs_shutter_control.protocol import Deadline, Decoder, Frame, ProtocolError


def test_documented_outbound_frames_match_manual_literals():
    sent = []

    class Sink:
        def send(self, frame, deadline):
            sent.append(frame.encode().hex())

    driver = KSC101(Sink(), None)
    driver.require_interlock(Deadline(1))
    driver.set_channel_enabled(True, Deadline(1))
    driver.set_channel_enabled(False, Deadline(1))
    driver.set_led_modes(0x0B, Deadline(1))
    driver.start_updates(Deadline(1))
    driver.stop_updates(Deadline(1))
    driver.disconnect_hardware(Deadline(1))
    assert sent == [
        "c60401015001",  # Issue42.1 p188, only require interlock.
        "100201015001",  # p44, output alias ON.
        "100201025001",  # p44, output alias OFF.
        "b3040400d00101000b00",  # p92, channel and LED bits.
        "110000005001",  # p48, start updates.
        "120000005001",  # p48, stop updates.
        "020000005001",  # p46, hardware disconnect.
    ]


@pytest.mark.parametrize("modes", [True, -1, 4, 0x10, 65536, 1.5, "1"])
def test_invalid_led_bits_fail_before_device_access(config, modes):
    hub = ShutterHub([config])
    with pytest.raises(ValueError, match="LED modes"):
        hub.set_led_modes("beam", modes, source_inhibited=True)
    assert not hub.connection_snapshot("beam").has_device


@pytest.mark.parametrize("enabled", [True, False])
def test_channel_query_is_separate_from_output(bench, enabled):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.state, device.split = (1 if enabled else 2), 1
    assert hub.get_channel_enabled("beam") is enabled
    assert device.history[-1][1].encode().hex() == "110201005001"
    assert not device.output_frames
    hub.shutdown_outputs()
    assert not device.output_frames


@pytest.mark.parametrize("bay", [0, 1, 3, 255])
def test_bay_query_returns_raw_byte_without_channel_or_route_inference(bench, bay):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.bay, device.split = bay, 1
    assert hub.get_hub_bay_reply("beam") == bay
    assert device.history[-1][1].encode().hex() == "650000005001"
    assert hub.configs[0].route.kind == "d2xx"


def test_led_read_preserves_unknown_bits_and_has_no_output_obligation(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.led_modes = 0x8001
    assert hub.get_led_modes("beam") == 0x8001
    assert device.history[-1][1].encode().hex() == "b40401005001"
    hub.shutdown_outputs()
    assert not device.output_frames


@pytest.mark.parametrize("operation", ["led", "interlock"])
@pytest.mark.parametrize("permission,protection", [(False, True), (True, False)])
def test_settings_permissions_are_checked_before_io(config, operation, permission, protection):
    config = replace(config, policy=replace(config.policy, allow_device_settings=permission))
    hub = ShutterHub([config])
    with pytest.raises(ShutterError):
        if operation == "led":
            hub.set_led_modes("beam", 1, source_inhibited=protection)
        else:
            hub.require_interlock("beam", source_inhibited=protection)
    assert not hub.connection_snapshot("beam").has_device


def test_require_interlock_can_repair_disabled_requirement(config, tmp_path):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    device.interlock = 2
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        sample = hub.require_interlock("beam", source_inhibited=True)
        assert sample.interlock_required and sample.electrical_state == "off"
        assert not hub._channels["beam"].claim.journal.exists()
        commands = [f for _, f in device.history if f.message_id == 0x04C6]
        assert len(commands) == 1 and commands[0].param2 == 1
        hub.require_interlock("beam", source_inhibited=True)
        assert sum(f.message_id == 0x04C6 for _, f in device.history) == 1
        assert not device.output_frames


@pytest.mark.parametrize("mode,state", [(2, 2), (1, 1)])
def test_interlock_write_requires_manual_off(config, tmp_path, mode, state):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    device.mode, device.state = mode, state
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ShutterError, match="Manual/OFF"):
            hub.require_interlock("beam", source_inhibited=True)
        assert not any(f.message_id == 0x04C6 for _, f in device.history)
        assert not device.output_frames


def test_led_write_has_exact_readback_without_incidental_off(config, tmp_path):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        assert hub.set_led_modes("beam", 9, source_inhibited=True) == 9
        hub.shutdown_outputs()
        assert not device.output_frames
        assert [f.payload.hex() for _, f in device.history if f.message_id == 0x04B3] == [
            "01000900"
        ]
        assert not any(f.message_id == 0x04B9 for _, f in device.history)


@pytest.mark.parametrize("operation", ["led", "interlock"])
def test_settings_readback_mismatch_retains_fault(config, tmp_path, operation):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)

    def rewrite(raw):
        if operation == "led" and raw[:2] == b"\xb5\x04":
            return Frame(
                0x04B5, destination=1, source=0x50, payload=struct.pack("<HH", 1, 0)
            ).encode()
        if operation == "interlock" and raw[:2] == b"\xc8\x04":
            return Frame(0x04C8, 1, 2, 1, 0x50).encode()
        return raw

    device.rewrite = rewrite
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ShutterError, match="readback|interlock"):
            if operation == "led":
                hub.set_led_modes("beam", 1, source_inhibited=True)
            else:
                hub.require_interlock("beam", source_inhibited=True)
        assert hub.connection_snapshot("beam").error
        assert hub._channels["beam"].claim.journal.exists()
        assert [f.param2 for f in device.output_frames] == ([] if operation == "led" else [2])


def test_updates_are_raw_events_with_explicit_start_stop(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    device = devices[0]
    device.split = 1
    hub.start_updates("beam")
    events = hub.get_events("beam")
    assert events and all(f.message_id == 0x0481 for f in events)
    assert all(f.payload == device.update_payload for f in events)
    assert hub.get_status("beam").electrical_state == "off"
    hub.stop_updates("beam")
    assert not device.updates
    hub.get_events("beam")  # Drain arrivals preceding Stop; no ACK implies no empty-buffer claim.
    assert hub.get_events("beam") == ()
    assert not device.output_frames


@pytest.mark.parametrize("mode,state,requested", [(2, 2, None), (1, 1, None), (1, 2, "start")])
def test_hardware_disconnect_refuses_active_or_native_state(bench, mode, state, requested):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].mode, devices[0].state = mode, state
    hub._channels["beam"].requested_state = requested
    with pytest.raises(ShutterError):
        hub.disconnect_hardware("beam", source_inhibited=True)
    assert not devices[0].bus_disconnected


def test_hardware_disconnect_is_explicit_and_ordinary_close_stays_passive(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    before = len(devices[0].history)
    with pytest.raises(ShutterError, match="source_inhibited"):
        hub.disconnect_hardware("beam")
    assert len(devices[0].history) == before
    sample = hub.disconnect_hardware("beam", source_inhibited=True)
    assert devices[0].bus_disconnected and devices[0].closed
    assert not sample.has_device and sample.identity is None
    assert not devices[0].output_frames


@pytest.mark.parametrize(
    "query,reply", [("get_channel_enabled", 0x0212), ("get_led_modes", 0x04B5)]
)
def test_new_queries_reject_wrong_channels(bench, query, reply):
    hub, devices, _, _ = bench
    hub.connect("beam")

    def rewrite(raw):
        if raw[:2] != struct.pack("<H", reply):
            return raw
        return (
            Frame(reply, 2, 1, 1, 0x50)
            if reply == 0x0212
            else Frame(reply, destination=1, source=0x50, payload=struct.pack("<HH", 2, 1))
        ).encode()

    devices[0].rewrite = rewrite
    with pytest.raises(ProtocolError, match="channel"):
        getattr(hub, query)("beam")
    assert hub._channels["beam"].driver.session.poisoned


def test_led_reply_length_rejected_before_reading_a_payload():
    with pytest.raises(ProtocolError, match="form/length"):
        Decoder().feed(bytes.fromhex("b50402008150"))


def test_new_query_still_verifies_controller_identity(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].serial = "68000002"
    with pytest.raises(IdentityMismatch):
        hub.get_channel_enabled("beam")
    assert not any(f.message_id == 0x0211 for _, f in devices[0].history)


def test_bay_reply_rejects_nonzero_reserved_byte(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].rewrite = lambda raw: (
        Frame(0x0066, 2, 1, 1, 0x50).encode() if raw[:2] == b"\x66\x00" else raw
    )
    with pytest.raises(ProtocolError, match="reserved byte"):
        hub.get_hub_bay_reply("beam")
    assert hub._channels["beam"].driver.session.poisoned


def test_channel_query_rejects_unknown_enable_enum(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].rewrite = lambda raw: (
        Frame(0x0212, 1, 0, 1, 0x50).encode() if raw[:2] == b"\x12\x02" else raw
    )
    with pytest.raises(ProtocolError, match="Unsupported scalar"):
        hub.get_channel_enabled("beam")


@pytest.mark.parametrize("operation,message", [("led", 0x04B3), ("interlock", 0x04C6)])
def test_partial_settings_write_is_not_replayed_or_followed_by_cleanup_bytes(
    config, tmp_path, operation, message
):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    if operation == "interlock":
        device.interlock = 2
    original = device.write

    def partial(raw, deadline):
        count = original(raw, deadline)
        return 3 if raw[:2] == struct.pack("<H", message) else count

    device.write = partial
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        with pytest.raises(ProtocolError, match="Partial write"):
            if operation == "led":
                hub.set_led_modes("beam", 1, source_inhibited=True)
            else:
                hub.require_interlock("beam", source_inhibited=True)
        assert device.history[-1][1].message_id == message
        assert sum(f.message_id == message for _, f in device.history) == 1
        assert not device.output_frames
        assert hub._channels["beam"].driver.session.write_desynchronized
        assert hub._channels["beam"].claim.journal.exists()
