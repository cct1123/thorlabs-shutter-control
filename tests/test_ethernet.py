"""Real TCP loopback checks only; no lab host or simulated notebook execution."""

import socket
import time
from dataclasses import replace
from threading import Thread

import pytest

from thorlabs_shutter_control import Route, ShutterError
from thorlabs_shutter_control.protocol import Deadline
from thorlabs_shutter_control.transport import TCPTransport


@pytest.mark.parametrize("bay,port", [("left", 40304), ("middle", 40305), ("right", 40306)])
def test_default_route_selects_exact_tcp_bay_without_usb(config, monkeypatch, bay, port):
    from thorlabs_shutter_control import transport

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
    expected = object()
    deadline = Deadline(1)

    def tcp(host, selected_port, budget):
        assert (host, selected_port, budget) == ("192.0.2.1", port, deadline)
        return expected

    monkeypatch.setattr(transport, "TCPTransport", tcp)
    monkeypatch.setattr(transport, "D2XXTransport", lambda *a: pytest.fail("Ethernet opened USB"))
    assert transport.open_transport(config, deadline) is expected


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
        assert transport.read_nowait() == b""  # Peer awaits our request; never blocks.
        assert transport.write(b"123456", Deadline(1)) == 6
        raw = b""
        receive_budget = Deadline(2)
        while len(raw) < 6:
            receive_budget.remaining()
            raw += transport.read_nowait()
            time.sleep(0.001)
        assert raw == b"abcdef"
        worker.join(1)
        with pytest.raises(ShutterError, match="disconnected"):
            transport.read_nowait()
    finally:
        transport.close()
        worker.join(1)
    assert received == [b"123456"]
