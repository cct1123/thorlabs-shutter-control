"""Bounded TCP bytes; APT framing and complete/partial-write handling stay in Session."""

import select
import socket

from .errors import ShutterError


class TCPTransport:
    def __init__(self, host, port, deadline):
        self.socket = socket.create_connection((host, port), timeout=deadline.remaining())
        try:
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            deadline.remaining()
        except BaseException:
            self.socket.close()
            raise

    def write(self, data, deadline):
        # Exactly one send. A partial result is surfaced, never replayed.
        self.socket.settimeout(deadline.remaining())
        return self.socket.send(data)  # Session checks lateness after learning the exact count.

    def read(self, seconds):
        self.socket.settimeout(seconds)
        try:
            data = self.socket.recv(4096)
        except (TimeoutError, BlockingIOError):
            return b""
        if not data:
            raise ShutterError("TCP peer disconnected; shutter state is unknown")
        return data

    def read_nowait(self):
        """Drain only arrived bytes so Session can reject unsolicited replies."""
        if not select.select([self.socket], [], [], 0)[0]:
            return b""
        return self.read(0)

    def close(self):
        self.socket.close()
