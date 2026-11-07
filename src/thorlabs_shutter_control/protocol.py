"""APT framing and one receive path. Sources: docs/sources.md, SRC-001.

APT has no transaction ID. A timeout, cancellation, duplicate or unexpected
same-family reply poisons the session; no retry can turn it into fresh evidence.
Reconnection is explicit. APT cannot prove arbitrary delayed unsolicited data
fresh; observation provenance states this limitation instead of inventing an ACK.
"""

import math
import struct
import time
from collections import deque
from dataclasses import dataclass
from threading import Event

from .errors import Cancelled, ControllerFault, DeadlineExceeded, ProtocolError

MAX_PAYLOAD = 255  # SRC-001 p34: documented bound for this supported protocol revision.
REPLIES = {
    0x0006: 84,
    0x042A: 6,
    0x04C2: None,
    0x04C5: 14,
    0x04C8: None,
    0x04CD: None,
    0x0212: None,
}
MESSAGE_LENGTHS = {**REPLIES, 0x0002: None, 0x0080: None, 0x0081: 68}


def clock():
    """High-resolution monotonic seconds, including Windows Python 3.12."""
    return time.perf_counter()


class Deadline:
    def __init__(self, seconds):
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
            raise ValueError("timeout must be a finite positive number of seconds")
        if not math.isfinite(seconds) or not 0 < seconds <= 60:
            raise ValueError("timeout must be in (0, 60] seconds")
        self.end = clock() + seconds

    def remaining(self):
        left = self.end - clock()
        if left <= 0:
            raise DeadlineExceeded("End-to-end deadline expired; result is unconfirmed")
        return left


@dataclass(frozen=True)
class Frame:
    message_id: int
    param1: int = 0
    param2: int = 0
    destination: int = 0x50
    source: int = 1
    payload: bytes | None = None

    def encode(self):
        if type(self.message_id) is not int or not 0 <= self.message_id <= 65535:
            raise ValueError("message ID must be a word")
        for value in (self.param1, self.param2):
            if type(value) is not int or not 0 <= value <= 255:
                raise ValueError("parameters must be bytes")
        for value in (self.destination, self.source):
            if type(value) is not int or not 0 <= value <= 127:
                raise ValueError("addresses must be 7-bit integers")
        if self.payload is None:
            return struct.pack(
                "<HBBBB", self.message_id, self.param1, self.param2, self.destination, self.source
            )
        if not isinstance(self.payload, bytes) or not 1 <= len(self.payload) <= MAX_PAYLOAD:
            raise ValueError(f"payload must contain 1..{MAX_PAYLOAD} bytes")
        return (
            struct.pack(
                "<HHBB", self.message_id, len(self.payload), self.destination | 0x80, self.source
            )
            + self.payload
        )


class Decoder:
    """Incremental, terminal-on-error framing; validate headers before awaiting data."""

    def __init__(self, *, destination=None, source=None):
        self.buffer = bytearray()
        self.destination = destination
        self.source = source
        self.failure = None

    def feed(self, data):
        if self.failure is not None:
            raise ProtocolError(f"Decoder desynchronized: {self.failure}")
        self.buffer.extend(data)
        result = []
        try:
            while len(self.buffer) >= 6:
                ident, p1, p2, dest, src = struct.unpack_from("<HBBBB", self.buffer)
                long_form = bool(dest & 0x80)
                length = p1 + (p2 << 8) if long_form else 0
                if length > MAX_PAYLOAD or (long_form and length == 0):
                    raise ProtocolError(f"Invalid APT payload length {length}")
                if src & 0x80:
                    raise ProtocolError("Invalid source address")
                if (self.destination is not None and dest & 0x7F != self.destination) or (
                    self.source is not None and src != self.source
                ):
                    raise ProtocolError("Reply from wrong address; no route fallback")
                if ident in MESSAGE_LENGTHS:
                    expected = MESSAGE_LENGTHS[ident]
                    if (long_form and length != expected) or (
                        not long_form and expected is not None
                    ):
                        raise ProtocolError(f"Invalid form/length for APT message 0x{ident:04x}")
                if len(self.buffer) < 6 + length:
                    break
                payload = bytes(self.buffer[6 : 6 + length]) if long_form else None
                result.append(
                    Frame(
                        ident,
                        0 if payload is not None else p1,
                        0 if payload is not None else p2,
                        dest & 0x7F,
                        src,
                        payload,
                    )
                )
                del self.buffer[: 6 + length]
        except ProtocolError as exc:
            self.failure = str(exc)
            # Preserve already decoded diagnostics and the malformed tail for callers.
            exc.decoded_frames = tuple(result)
            exc.raw_tail = bytes(self.buffer)
            raise
        return result


class Session:
    """Called only under the shared owner lock. No receiver thread or cache getter."""

    def __init__(self, transport, cancel: Event):
        self.transport = transport
        self.cancel = cancel
        self.decoder = Decoder(destination=1, source=0x50)
        self.events = deque(maxlen=64)
        self.poisoned = False
        self.write_desynchronized = False

    def _check(self, deadline, protective):
        deadline.remaining()
        if self.cancel.is_set() and not protective:
            raise Cancelled("Request cancelled; session requires explicit recovery")

    def send(self, frame, deadline, *, protective=False):
        if self.poisoned and not protective:
            raise ProtocolError("Session ambiguous; release and explicitly recover")
        if self.write_desynchronized:
            raise ProtocolError(
                "Write framing unknown; no further commands allowed on this session. "
                "Independently protect the source and recover explicitly."
            )
        self._check(deadline, protective)
        raw = frame.encode()
        try:
            count = self.transport.write(raw, deadline)
        except BaseException:
            self.write_desynchronized = True
            self.poisoned = True
            raise
        if count != len(raw):
            self.write_desynchronized = True
            self.poisoned = True
            raise ProtocolError(f"Partial write: {count}/{len(raw)} bytes; possibly applied")
        try:
            # A complete but late write is ambiguous electrically, with intact
            # transmit alignment. A qualified protective OFF remains reachable.
            self._check(deadline, protective)
        except BaseException:
            self.poisoned = True
            raise

    def _accept(self, frame):
        # Decoder has already validated addresses and known message forms/lengths.
        if frame.message_id in (0x0080, 0x0081):
            raise ControllerFault(frame)
        if frame.message_id == 0x0002:
            raise ProtocolError("Controller disconnected")
        if frame.message_id in REPLIES and REPLIES[frame.message_id] is None and frame.param1 != 1:
            raise ProtocolError("Wrong response channel")

    def query(self, request, reply_id, deadline, *, protective=False):
        if self.poisoned:
            raise ProtocolError("Session ambiguous; release and explicitly recover")
        try:
            self._check(deadline, protective)
            # Drain only already-arrived traffic. Never reuse it to satisfy a query.
            for old in self.decoder.feed(self.transport.read_nowait()):
                self._accept(old)
                if old.message_id in REPLIES:
                    raise ProtocolError("Unsolicited/late reply before request")
                self.events.append(old)
            if self.decoder.buffer:
                raise ProtocolError("Unsolicited partial frame before request")
            self.send(request, deadline, protective=protective)
            while True:
                self._check(deadline, protective)
                data = self.transport.read(min(0.02, deadline.remaining()))
                self._check(deadline, protective)
                found = None
                for frame in self.decoder.feed(data):
                    self._accept(frame)
                    if frame.message_id == reply_id:
                        if found is not None:
                            raise ProtocolError("Duplicate response; freshness is ambiguous")
                        found = frame
                    elif frame.message_id in REPLIES:
                        raise ProtocolError("Unsolicited/late reply during another query")
                    else:
                        self.events.append(frame)
                if found is not None:
                    if self.decoder.buffer:
                        raise ProtocolError("Trailing partial frame; response is ambiguous")
                    return found
        except BaseException:
            self.poisoned = True
            raise
