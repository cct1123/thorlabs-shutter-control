"""Bounded TCP bytes for explicit commissioning, not a KEH3 wire-contract claim."""

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
        count = self.socket.send(data)
        deadline.remaining()
        return count

    def read(self, seconds):
        self.socket.settimeout(seconds)
        try:
            data = self.socket.recv(4096)
        except TimeoutError:
            return b""
        if not data:
            raise ShutterError("TCP peer disconnected; shutter state is unknown")
        return data

    def close(self):
        self.socket.close()
