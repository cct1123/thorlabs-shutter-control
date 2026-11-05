"""KSC101 documented messages only; no operating-policy or optical interpretation."""

import struct
from dataclasses import dataclass

from .errors import IdentityMismatch, ProtocolError
from .protocol import Frame

MODES = {1: "manual", 2: "single", 3: "auto", 4: "triggered"}


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

    def scalar(self, request, reply, allowed, deadline, *, protective=False):
        frame = self.session.query(Frame(request, 1), reply, deadline, protective=protective)
        if frame.param2 not in allowed:
            self.session.poisoned = True
            raise ProtocolError(f"Unsupported scalar value {frame.param2} in 0x{reply:04x}")
        return frame.param2

    def mode(self, deadline, *, protective=False):
        return MODES[self.scalar(0x04C1, 0x04C2, MODES, deadline, protective=protective)]

    def state(self, deadline, *, protective=False):
        return (
            "on"
            if self.scalar(0x04CC, 0x04CD, (1, 2), deadline, protective=protective) == 1
            else "off"
        )

    def interlock_required(self, deadline, *, protective=False):
        return self.scalar(0x04C7, 0x04C8, (1, 2), deadline, protective=protective) == 1

    def set_manual(self, deadline):
        self.session.send(Frame(0x04C0, 1, 1), deadline)

    def set_solenoid(self, on, deadline, *, protective=False):
        self.session.send(Frame(0x04CB, 1, 1 if on else 2), deadline, protective=protective)
