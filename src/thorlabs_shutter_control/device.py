"""KSC101 documented messages only; no operating-policy or optical interpretation."""

import struct
import time
from dataclasses import dataclass

from .errors import IdentityMismatch, ProtocolError
from .protocol import Frame

MODES = {1: "manual", 2: "single", 3: "auto", 4: "triggered"}


@dataclass(frozen=True)
class CycleParameters:
    """Rev F section6.3.2 bounds; APT0x04C3/5 uses integer milliseconds."""

    on_ms: int
    off_ms: int
    cycles: int

    def __post_init__(self):
        for name in ("on_ms", "off_ms"):
            value = getattr(self, name)
            if type(value) is not int or not 100 <= value <= 10000:
                raise ValueError(f"{name} must be an integer in 100..10000 ms")
        if type(self.cycles) is not int or not 0 <= self.cycles <= 1000000:
            raise ValueError("cycles must be an integer in 0..1000000; 0 means continuous")

    def encode(self):
        return struct.pack("<HIII", 1, self.on_ms, self.off_ms, self.cycles)

    @classmethod
    def decode(cls, payload):
        channel, on_ms, off_ms, cycles = struct.unpack("<HIII", payload)
        if channel != 1:
            raise ValueError("Wrong cycle-parameter response channel")
        return cls(on_ms, off_ms, cycles)


@dataclass(frozen=True)
class Identity:
    serial_number: str
    model: str
    firmware: str
    hardware_version: int
    channels: int

    @classmethod
    def decode(cls, payload):
        """Use one identity layout for operational replies and offline captures."""
        if not isinstance(payload, bytes) or len(payload) != 84:
            raise ProtocolError("Hardware identity requires an 84-byte payload")
        try:
            return cls(
                str(struct.unpack_from("<I", payload)[0]),
                payload[4:12].decode("ascii").rstrip("\0 "),
                f"{payload[16]}.{payload[15]}.{payload[14]}",
                struct.unpack_from("<H", payload, 78)[0],
                struct.unpack_from("<H", payload, 82)[0],
            )
        except UnicodeDecodeError as exc:
            raise ProtocolError("Malformed hardware identity") from exc

    def verify(self, config):
        if (
            self.serial_number != config.serial_number
            or self.model != "KSC101"
            or self.channels != 1
            or self.firmware not in config.firmware
        ):
            raise IdentityMismatch(f"Identity/model/firmware mismatch on exact route: {self}")
        return self


class KSC101:
    def __init__(self, session, config):
        self.session = session
        self.config = config

    def identity(self, deadline, *, protective=False):
        reply = self.session.query(Frame(0x0005), 0x0006, deadline, protective=protective)
        return Identity.decode(reply.payload).verify(self.config)

    def _scalar(self, request, reply, allowed, deadline, *, protective=False):
        frame = self.session.query(Frame(request, 1), reply, deadline, protective=protective)
        if frame.param2 not in allowed:
            self.session.poisoned = True
            error = ProtocolError(f"Unsupported scalar value {frame.param2} in 0x{reply:04x}")
            error.add_note(f"Raw controller reply: {frame.encode().hex()}")
            raise error
        return frame.param2

    def operating_mode(self, deadline, *, protective=False):
        return MODES[self._scalar(0x04C1, 0x04C2, MODES, deadline, protective=protective)]

    def solenoid_state_reply(self, deadline):
        """Uninterpreted 0x04CD byte; legacy APT and current feedback enums differ."""
        return self.session.query(Frame(0x04CC, 1), 0x04CD, deadline).param2

    def output_state(self, deadline, *, protective=False):
        """Electrical output from fresh KSC101 status bit0, never optical position."""
        return "on" if self.status_bits(deadline, protective=protective) & 1 else "off"

    def wait_output(self, on, deadline, *, protective=False):
        """Observe transition within the caller's budget; never resend the command."""
        while True:
            bits = self.status_bits(deadline, protective=protective)
            if bool(bits & 1) == on:
                return bits
            time.sleep(min(0.01, deadline.remaining()))

    def interlock_required(self, deadline, *, protective=False):
        return self._scalar(0x04C7, 0x04C8, (1, 2), deadline, protective=protective) == 1

    @staticmethod
    def decode_status_bits(frame):
        """APT 0x042A: exact channel word followed by a 32-bit status field."""
        if frame.message_id != 0x042A or frame.payload is None or len(frame.payload) != 6:
            raise ProtocolError("Status bits require a 0x042A frame with a 6-byte payload")
        channel, bits = struct.unpack("<HI", frame.payload)
        if channel != 1:
            raise ProtocolError("Wrong status-bits response channel")
        return bits

    def status_bits(self, deadline, *, protective=False):
        frame = self.session.query(Frame(0x0429, 1), 0x042A, deadline, protective=protective)
        try:
            return self.decode_status_bits(frame)
        except ProtocolError:
            self.session.poisoned = True
            raise

    def set_operating_mode(self, mode, deadline):
        if mode not in MODES.values():
            raise ValueError("mode must be manual, single, auto or triggered")
        code = next(code for code, name in MODES.items() if name == mode)
        self.session.send(Frame(0x04C0, 1, code), deadline)

    def set_output(self, on, deadline, *, protective=False):
        if type(on) is not bool:
            raise ValueError("on must be boolean")
        self.session.send(Frame(0x04CB, 1, 1 if on else 2), deadline, protective=protective)

    def cycle_parameters(self, deadline):
        reply = self.session.query(Frame(0x04C4, 1), 0x04C5, deadline)
        try:
            return CycleParameters.decode(reply.payload)
        except (struct.error, TypeError, ValueError) as exc:
            self.session.poisoned = True
            raise ProtocolError(f"Invalid cycle parameters: {exc}") from exc

    def set_cycle_parameters(self, parameters, deadline):
        if not isinstance(parameters, CycleParameters):
            raise ValueError("parameters must be validated CycleParameters")
        self.session.send(Frame(0x04C3, payload=parameters.encode()), deadline)

    def persist_cycle_parameters(self, deadline):
        """APT p99: request storage of cycle parameters only; no persistence ACK exists."""
        self.session.send(Frame(0x04B9, payload=struct.pack("<HH", 1, 0x04C3)), deadline)

    def blink_identify(self, deadline):
        self.session.send(Frame(0x0223, 1), deadline)
