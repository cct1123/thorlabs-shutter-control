"""TEST-203 and TEST-205: manufacturer frames, alignment, faults and freshness."""

import struct
import time
from threading import Event

import pytest
from conftest import FakeTransport

from thorlabs_shutter_control.device import KSC101
from thorlabs_shutter_control.errors import ControllerFault, DeadlineExceeded, ProtocolError
from thorlabs_shutter_control.protocol import Deadline, Decoder, Frame, Session


def test_status_bits_decode_actual_firmware_107_capture():
    # Real 68800777/1.0.7 TCP capture; no simulated transport or device response.
    raw = bytes.fromhex("2a0406008150010000200000")
    (frame,) = Decoder(destination=1, source=0x50).feed(raw)
    assert KSC101.decode_status_bits(frame) == 0x2000


@pytest.mark.parametrize(
    "frame",
    [
        Frame(0x042A, payload=b"\x02\x00\x00\x20\x00\x00"),
        Frame(0x042A, payload=bytes(5)),
        Frame(0x042A, payload=bytes(7)),
        Frame(0x042A),
        Frame(0x0481, payload=bytes(6)),
    ],
)
def test_status_bits_reject_wrong_channel_form_or_length(frame):
    with pytest.raises(ProtocolError):
        KSC101.decode_status_bits(frame)


def test_reference_frames_and_all_split_boundaries():
    assert Frame(0x04CB, 1, 1).encode() == bytes.fromhex("cb 04 01 01 50 01")
    assert Frame(0x04C1, 1).encode() == bytes.fromhex("c1 04 01 00 50 01")
    raw = bytes.fromhex("cd 04 01 02 01 50")
    identity = Frame(6, destination=1, source=0x50, payload=bytes(84)).encode()
    stream = identity + raw + raw
    for cut in range(len(stream) + 1):
        decoder = Decoder()
        frames = decoder.feed(stream[:cut]) + decoder.feed(stream[cut:])
        assert [f.message_id for f in frames] == [6, 0x04CD, 0x04CD]
        assert frames[-1].param2 == 2
        assert not decoder.buffer


def test_commands_use_protocol_values_and_validate_before_io(config):
    transport = FakeTransport(config)
    driver = KSC101(Session(transport, Event()), config)
    for mode in (None, True, 1, "MANUAL"):
        with pytest.raises(ValueError):
            driver.set_operating_mode(mode, Deadline(1))
    for on in (None, 1, "off"):
        with pytest.raises(ValueError):
            driver.set_output(on, Deadline(1))
    assert not transport.history
    driver.set_operating_mode("manual", Deadline(1))
    driver.set_output(True, Deadline(1))
    driver.set_output(False, Deadline(1))
    assert [f.encode().hex() for _, f in transport.history] == [
        "c00401015001",
        "cb0401015001",
        "cb0401025001",
    ]


@pytest.mark.parametrize(
    "method,request_hex,reply_hex,expected",
    [
        ("operating_mode", "c10401005001", "c20401040150", "triggered"),
        ("interlock_required", "c70401005001", "c80401010150", True),
        ("interlock_required", "c70401005001", "c80401020150", False),
        ("solenoid_state_reply", "cc0401005001", "cd0401000150", 0),
        ("output_state", "290401005001", "2a0406008150010000200000", "off"),
        ("output_state", "290401005001", "2a0406008150010001200000", "on"),
    ],
)
def test_driver_queries_against_literal_reference_frames(
    config, method, request_hex, reply_hex, expected
):
    """Independent fixed bytes: APT tables and recorded firmware-1.0.7 status replies."""

    class Exchange:
        pending = b""

        def read_nowait(self):
            return b""

        def write(self, raw, deadline):
            assert raw == bytes.fromhex(request_hex)
            self.pending = bytes.fromhex(reply_hex)
            return len(raw)

        def read(self, seconds):
            raw, self.pending = self.pending, b""
            return raw

    driver = KSC101(Session(Exchange(), Event()), config)
    assert getattr(driver, method)(Deadline(1)) == expected


def test_ambiguous_session_cannot_send_an_ordinary_command(config):
    transport = FakeTransport(config)
    session = Session(transport, Event())
    session.poisoned = True
    with pytest.raises(ProtocolError, match="ambiguous"):
        KSC101(session, config).set_output(True, Deadline(1))
    assert not transport.history


def test_delayed_output_transition_polls_readback_without_replaying_on(config):
    transport = FakeTransport(config)
    states = iter((0x2000, 0x2000, 0x2001))
    transport.rewrite = lambda raw: (
        bytes.fromhex("2a04060081500100") + struct.pack("<I", next(states))
    )
    driver = KSC101(Session(transport, Event()), config)
    driver.set_output(True, Deadline(1))
    assert driver.wait_output(True, Deadline(1)) == 0x2001
    assert [frame.message_id for _, frame in transport.history] == [
        0x04CB,
        0x0429,
        0x0429,
        0x0429,
    ]
    assert len(transport.output_frames) == 1


def test_output_that_never_transitions_expires_without_replaying_on(config):
    transport = FakeTransport(config)
    transport.rewrite = lambda raw: bytes.fromhex("2a0406008150010000200000")
    driver = KSC101(Session(transport, Event()), config)
    driver.set_output(True, Deadline(1))
    with pytest.raises(DeadlineExceeded):
        driver.wait_output(True, Deadline(0.03))
    assert len(transport.output_frames) == 1


@pytest.mark.parametrize("raw", ["06 00 ff ff 81 50", "06 00 00 00 81 50", "cd 04 01 02 01 d0"])
def test_malformed_headers_fail(raw):
    with pytest.raises(ProtocolError):
        Decoder().feed(bytes.fromhex(raw))


@pytest.mark.parametrize(
    "raw",
    [
        "06 00 53 00 81 50",  # Identity must declare 84 payload bytes, not 83.
        "06 00 00 00 01 50",  # Identity cannot arrive in short form.
        "c2 04 01 00 81 50",  # Mode must be short, not a one-byte long frame.
        "81 00 00 00 01 50",  # Rich fault must be long, even before its body arrives.
        "80 00 44 00 81 50",  # Basic fault must be short.
        "77 77 00 01 81 50",  # Unknown messages still obey the 255-byte bound.
    ],
)
def test_invalid_schema_rejected_from_header_without_waiting_for_body(raw):
    decoder = Decoder()
    with pytest.raises(ProtocolError):
        decoder.feed(bytes.fromhex(raw))
    with pytest.raises(ProtocolError, match="desynchronized"):
        decoder.feed(bytes.fromhex("cd 04 01 02 01 50"))


def test_high_resolution_deadline_expires_inside_a_coarse_monotonic_tick(monkeypatch):
    from thorlabs_shutter_control import protocol

    ticks = iter((100.0, 100.002))
    monkeypatch.setattr(protocol.time, "perf_counter", lambda: next(ticks))
    monkeypatch.setattr(protocol.time, "monotonic", lambda: 100.0)
    deadline = Deadline(0.001)
    with pytest.raises(DeadlineExceeded):
        deadline.remaining()


def test_fragmented_identity_and_interleaved_event(config):
    transport = FakeTransport(config)
    transport.split = 1
    # An asynchronous, unrelated complete frame remains diagnostic evidence.
    transport.prefix = Frame(0x0464, 1, destination=1, source=0x50).encode()
    session = Session(transport, Event())
    result = KSC101(session, config).identity(Deadline(1))
    assert (result.model, result.serial_number, result.firmware) == ("KSC101", "68000001", "1.0.7")
    assert session.events[0].message_id == 0x0464


@pytest.mark.parametrize(
    "change",
    [
        lambda raw: raw[:4] + bytes([2]) + raw[5:],
        lambda raw: raw[:5] + bytes([0x51]) + raw[6:],
        lambda raw: raw[:2] + bytes([2]) + raw[3:],
        lambda raw: raw + raw,
        lambda raw: raw[:3] + bytes([99]) + raw[4:],
    ],
)
def test_wrong_addresses_channels_duplicate_values_poison(config, change):
    transport = FakeTransport(config)
    transport.rewrite = change
    session = Session(transport, Event())
    with pytest.raises(ProtocolError):
        KSC101(session, config).operating_mode(Deadline(0.1))
    assert session.poisoned


def test_rich_fault_retains_entire_frame(config):
    transport = FakeTransport(config)
    payload = struct.pack("<HH", 0x04CC, 42) + b"diagnostic".ljust(64, b"\0")
    fault = Frame(0x81, destination=1, source=0x50, payload=payload)
    transport.prefix = fault.encode()
    session = Session(transport, Event())
    with pytest.raises(ControllerFault) as caught:
        KSC101(session, config).output_state(Deadline(1))
    assert caught.value.raw == fault.encode().hex()


def test_timeout_then_delayed_same_type_never_reused(config):
    transport = FakeTransport(config)
    transport.silent.add(0x0429)
    session = Session(transport, Event())
    with pytest.raises(DeadlineExceeded):
        KSC101(session, config).output_state(Deadline(0.02))
    transport.rx.append(bytes.fromhex("cd 04 01 01 01 50"))
    count = len(transport.history)
    with pytest.raises(ProtocolError, match="ambiguous"):
        KSC101(session, config).output_state(Deadline(1))
    assert len(transport.history) == count


def test_pending_stale_response_cannot_satisfy_new_query(config):
    transport = FakeTransport(config)
    transport.rx.append(bytes.fromhex("cd 04 01 01 01 50"))
    session = Session(transport, Event())
    with pytest.raises(ProtocolError, match="late"):
        KSC101(session, config).output_state(Deadline(1))
    assert not transport.history


def test_late_read_is_not_success(config):
    transport = FakeTransport(config)
    transport.delay = 0.03
    with pytest.raises(DeadlineExceeded):
        KSC101(Session(transport, Event()), config).output_state(Deadline(0.01))


def test_failed_write_never_appends_a_cleanup_frame_to_unknown_transmit_alignment(config):
    transport = FakeTransport(config)
    original = transport.write

    def fail_after_possible_application(raw, deadline):
        original(raw, deadline)
        raise OSError("Write failed with unknown byte count")

    transport.write = fail_after_possible_application
    session = Session(transport, Event())
    with pytest.raises(OSError, match="unknown byte count"):
        session.send(Frame(0x04CB, 1, 1), Deadline(1))
    with pytest.raises(ProtocolError, match="Write framing unknown"):
        session.send(Frame(0x04CB, 1, 2), Deadline(1), protective=True)
    assert len(transport.history) == 1


def test_complete_but_late_write_keeps_qualified_cleanup_dispatch_reachable(config):
    transport = FakeTransport(config)
    original = transport.write

    def late_complete(raw, deadline):
        count = original(raw, deadline)
        time.sleep(0.02)
        return count

    transport.write = late_complete
    session = Session(transport, Event())
    with pytest.raises(DeadlineExceeded):
        session.send(Frame(0x04CB, 1, 1), Deadline(0.005))
    transport.write = original
    session.send(Frame(0x04CB, 1, 2), Deadline(1), protective=True)
    assert [frame.param2 for frame in transport.output_frames] == [1, 2]


def test_total_deadline_is_not_restarted_between_preflight_queries(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].delay = 0.015
    hub.query_timeout = 0.025
    started = time.perf_counter()
    with pytest.raises(DeadlineExceeded):
        hub.get_status("beam")
    assert time.perf_counter() - started < 0.15
    assert not devices[0].output_frames


def test_cancelled_query_does_not_touch_transport(config):
    transport = FakeTransport(config)

    def forbidden():
        pytest.fail("Cancelled query touched the receive path")

    transport.read_nowait = forbidden
    cancel = Event()
    cancel.set()
    session = Session(transport, cancel)
    from thorlabs_shutter_control.errors import Cancelled

    with pytest.raises(Cancelled):
        KSC101(session, config).output_state(Deadline(1))
    assert session.poisoned and not transport.history
