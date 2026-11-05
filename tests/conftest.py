"""Byte-level simulated KSC101. No SDK, native library, device or network access."""

import struct
import time
from collections import deque
from dataclasses import replace

import pytest

from thorlabs_shutter_control import ControllerConfig, Policy, Route, ShutterHub
from thorlabs_shutter_control.protocol import Decoder, Frame


class FakeTransport:
    def __init__(self, config):
        self.serial = config.serial_number
        self.model = "KSC101"
        self.firmware = (7, 0, 1)
        self.mode, self.state, self.interlock = 1, 2, 1
        self.rx = deque()
        self.history = []
        self.closed = False
        self.split = 4096
        self.delay = 0
        self.silent = set()
        self.partial = False
        self.close_fails = False
        self.rewrite = lambda raw: raw
        self.prefix = b""

    def write(self, raw, deadline):
        frame = Decoder().feed(raw)[0]
        self.history.append((time.perf_counter(), frame))
        if frame.message_id == 0x04CB:
            self.state = frame.param2
            if self.partial:
                return 3  # Possibly applied, even though transport reports short write.
        elif frame.message_id == 0x04C0:
            self.mode = frame.param2
        if frame.message_id in self.silent:
            return len(raw)
        reply = None
        if frame.message_id == 5:
            p = bytearray(84)
            struct.pack_into("<I", p, 0, int(self.serial))
            p[4:12] = self.model.encode().ljust(8, b"\0")
            p[14:17] = bytes(self.firmware)
            struct.pack_into("<H", p, 78, 1)
            struct.pack_into("<H", p, 82, 1)
            reply = Frame(6, destination=1, source=0x50, payload=bytes(p))
        elif frame.message_id in (0x04C1, 0x04CC, 0x04C7):
            ident, value = {
                0x04C1: (0x04C2, self.mode),
                0x04CC: (0x04CD, self.state),
                0x04C7: (0x04C8, self.interlock),
            }[frame.message_id]
            reply = Frame(ident, 1, value, 1, 0x50)
        if reply:
            self.rx.append(self.prefix + self.rewrite(reply.encode()))
        return len(raw)

    def read(self, seconds):
        if self.delay:
            time.sleep(self.delay)
        if not self.rx:
            time.sleep(seconds)
            return b""
        data = self.rx.popleft()
        if len(data) > self.split:
            self.rx.appendleft(data[self.split :])
            data = data[: self.split]
        return data

    def read_nowait(self):
        return b"".join(self.rx.popleft() for _ in range(len(self.rx)))

    def close(self):
        if self.close_fails:
            raise OSError("simulated release failure")
        self.closed = True

    @property
    def output_frames(self):
        return [f for _, f in self.history if f.message_id in (0x04CB, 0x04C0, 0x0210)]


@pytest.fixture
def config():
    return ControllerConfig(
        "beam",
        0,
        "fictional beam role",
        "68000001",
        ("1.0.7",),
        Route("d2xx"),
        Policy("simulated qualification only", "fake load", "closed", 0, True),
    )


@pytest.fixture
def bench(config, tmp_path):
    devices = []

    def factory(c, d):
        device = FakeTransport(c)
        devices.append(device)
        return device

    hub = ShutterHub([config], transport_factory=factory, lock_directory=tmp_path)
    yield hub, devices, factory, tmp_path
    for device in devices:
        device.close_fails = False
    hub.close()


@pytest.fixture
def second(config):
    return replace(config, name="second", channel=1, serial_number="68000002")
