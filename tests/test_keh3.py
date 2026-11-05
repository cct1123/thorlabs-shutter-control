"""TEST-217: candidate diagnostics only; no lab network or device access."""

import socket
import struct
import time
from dataclasses import replace
from threading import Thread

import pytest
from conftest import FakeTransport

from thorlabs_shutter_control import Route, ShutterError, ShutterHub
from thorlabs_shutter_control.ethernet import TCPTransport
from thorlabs_shutter_control.keh3 import KEH3Probe, analyze_capture
from thorlabs_shutter_control.protocol import Deadline, Frame


@pytest.fixture
def lan(config):
    return replace(
        config,
        route=Route(
            "keh3", hub_serial="120000001", host="192.0.2.1", bay="left", hub_firmware="unqualified"
        ),
    )


def identity(serial=68000001, source=0x50, model=b"KSC101\0\0", firmware=(7, 0, 1), channels=1):
    data = bytearray(84)
    struct.pack_into("<I", data, 0, serial)
    data[4:12] = model
    data[14:17] = bytes(firmware)
    struct.pack_into("<H", data, 82, channels)
    return Frame(6, destination=1, source=source, payload=bytes(data)).encode()


@pytest.mark.parametrize(
    "raw,verdict",
    [
        (b"", "no-identity"),
        (identity(), "candidate-controller-match-hub-unverified"),
        (identity(68000002), "identity-mismatch"),
        (identity(model=b"TSC001\0\0"), "identity-mismatch"),
        (identity(firmware=(8, 0, 1)), "identity-mismatch"),
        (identity(channels=2), "identity-mismatch"),
        (identity(source=0x21), "invalid-candidate-stream"),
        (identity() + identity(), "ambiguous-identities"),
        (identity()[:20], "incomplete-frame"),
        (identity() + bytes.fromhex("80 00 00 00 01 50"), "controller-fault-or-disconnect"),
        (bytes.fromhex("06 00 ff ff 81 50"), "invalid-candidate-stream"),
    ],
)
def test_capture_verdicts_never_qualify_a_hub(lan, raw, verdict):
    report = analyze_capture(lan, raw, destination=0x50)
    assert report.verdict == verdict
    assert not report.hub_identity_verified and not report.operational_route_available
    assert report.raw_hex == raw.hex()


def test_all_identity_split_boundaries_single_query(lan, tmp_path):
    for split in range(1, 91):
        fake = FakeTransport(lan)
        fake.split = split
        probe = KEH3Probe(
            lan,
            destination=0x50,
            authorized=True,
            lock_directory=tmp_path,
            transport_factory=lambda h, p, d, device=fake: device,
        )
        report = probe.run()
        assert report.verdict == "candidate-controller-match-hub-unverified"
        assert [f.message_id for _, f in fake.history] == [5]
        assert fake.closed


def test_no_authorization_or_bad_address_performs_no_io(lan, tmp_path):
    def forbidden(*args):
        pytest.fail("Unexpected socket/transport access")

    with pytest.raises(ShutterError, match="authorization"):
        KEH3Probe(lan, destination=0x50, transport_factory=forbidden).run()
    for bad in (True, 0, 0x80, 0x22 + 0.5):
        with pytest.raises(ValueError):
            KEH3Probe(lan, destination=bad, transport_factory=forbidden)
    with pytest.raises(ShutterError):
        ShutterHub([lan], transport_factory=forbidden, lock_directory=tmp_path).connect("beam")


def test_partial_query_is_not_retried(lan, tmp_path):
    fake = FakeTransport(lan)
    fake.write = lambda raw, d: 3
    report = KEH3Probe(
        lan,
        destination=0x50,
        authorized=True,
        lock_directory=tmp_path,
        transport_factory=lambda *a: fake,
    ).run()
    assert report.verdict == "probe-unconfirmed" and "Partial" in report.error
    assert fake.closed


def test_late_reply_retained_without_success(lan, tmp_path):
    fake = FakeTransport(lan)
    fake.delay = 0.03
    report = KEH3Probe(
        lan,
        destination=0x50,
        timeout=0.01,
        authorized=True,
        lock_directory=tmp_path,
        transport_factory=lambda *a: fake,
    ).run()
    assert report.verdict == "probe-unconfirmed" and report.raw_hex


def test_failed_release_retains_claim_and_cleanup_error(lan, tmp_path):
    fake = FakeTransport(lan)
    fake.close_fails = True
    p = KEH3Probe(
        lan,
        destination=0x50,
        authorized=True,
        lock_directory=tmp_path,
        transport_factory=lambda *a: fake,
    )
    report = p.run()
    assert report.cleanup_error and p.claim is not None
    with pytest.raises(ShutterError, match="owned"):
        KEH3Probe(
            lan,
            destination=0x50,
            authorized=True,
            lock_directory=tmp_path,
            transport_factory=lambda *a: fake,
        ).run()
    fake.close_fails = False
    p.close()


def test_real_tcp_loopback_fragments_and_disconnect():
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(6)
    received = []

    def peer():
        conn, _ = server.accept()
        with conn:
            received.append(conn.recv(6))
            for part in (b"abc", b"def"):
                conn.sendall(part)
                time.sleep(0.002)
        server.close()

    worker = Thread(target=peer, daemon=True)
    worker.start()
    transport = TCPTransport("127.0.0.1", server.getsockname()[1], Deadline(5))
    try:
        assert transport.write(b"123456", Deadline(1)) == 6
        raw = b""
        while len(raw) < 6:
            raw += transport.read(0.2)
        assert raw == b"abcdef"
        with pytest.raises(ShutterError, match="disconnected"):
            transport.read(0.2)
    finally:
        transport.close()
        worker.join(1)
    assert received == [b"123456"]


def test_capture_limit_and_cli_are_offline(lan, tmp_path, monkeypatch, capsys):
    from thorlabs_shutter_control.__main__ import main

    config = tmp_path / "lan.toml"
    config.write_text("""[[shutters]]
name="beam"
channel=0
role="simulated"
serial_number="68000001"
firmware=["1.0.7"]
[shutters.route]
kind="keh3"
hub_serial="120000001"
hub_firmware="unqualified"
host="192.0.2.1"
bay="left"
""")
    capture = tmp_path / "rx.bin"
    capture.write_bytes(identity())
    monkeypatch.setattr(
        socket, "create_connection", lambda *a, **kw: pytest.fail("Lab connection attempted")
    )
    args = ["--config", str(config), "--target", "beam"]
    assert main([*args, "keh3-analyze", "--destination", "0x50", "--capture", str(capture)]) == 0
    assert "candidate-controller-match-hub-unverified" in capsys.readouterr().out
    assert main([*args, "keh3-probe", "--destination", "0x50"]) == 1
    assert "authorization" in capsys.readouterr().err
    capture.write_bytes(bytes(4097))
    assert main([*args, "keh3-analyze", "--destination", "0x50", "--capture", str(capture)]) == 1
    assert "4096" in capsys.readouterr().err
    with pytest.raises(ValueError, match="4096"):
        analyze_capture(lan, bytes(4097), destination=0x50)
