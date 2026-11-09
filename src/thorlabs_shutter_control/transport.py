"""Connection routes, TCP/USB bytes and explicit informational discovery.

Importing and route construction perform no enumeration or device I/O.
Routes and backend selection come first, followed by byte transports and explicit
inventory. Each backend supplies write(data, deadline), read(seconds),
read_nowait() and close(); Session owns APT framing and partial-write checks.

SRC-001 section 2.1: 115200 baud, 8N1, RTS/CTS and asserted RTS. Its USB
initialization includes 50 ms before/after purge and a bridge reset. These
documented waits apply to connection only, and consume the identity deadline.
No Thorlabs DLL is loaded. Native driver call latency still needs qualification.
"""

import re
import socket
import time
from dataclasses import dataclass
from ipaddress import IPv4Address

from .protocol import ShutterError

_KEH3_BAY_PORTS = {"left": 40304, "middle": 40305, "right": 40306, "external": 40307}
_READ_SIZE = 4096


# Route configuration and backend selection.


@dataclass(frozen=True)
class Route:
    """Validated connection coordinates; optional hub metadata is descriptive."""

    kind: str
    port: str | None = None
    hub_serial: str | None = None
    host: str | None = None
    bay: str | None = None
    hub_firmware: str | None = None

    def __post_init__(self):
        if self.kind not in ("vcp", "d2xx", "keh3"):
            raise ValueError("route kind must be vcp, d2xx or keh3")
        if self.kind == "vcp":
            if not isinstance(self.port, str) or not re.fullmatch(r"COM[1-9][0-9]*", self.port):
                raise ValueError("VCP route must be a canonical Windows COM number, e.g. COM9")
        elif self.port is not None:
            raise ValueError("port is only valid for vcp")
        if self.kind == "keh3":
            if not isinstance(self.host, str) or str(IPv4Address(self.host)) != self.host:
                raise ValueError("hub host must be a canonical IPv4 address")
            if self.bay not in tuple(_KEH3_BAY_PORTS):
                raise ValueError("unknown KEH3 route")
            for name in ("hub_serial", "hub_firmware"):
                value = getattr(self, name)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    raise ValueError(f"{name} must be nonempty text when supplied")
        elif any(v is not None for v in (self.hub_serial, self.host, self.bay, self.hub_firmware)):
            raise ValueError("hub fields apply only to keh3 routes")

    @property
    def endpoint(self):
        if self.kind == "keh3":
            port = _KEH3_BAY_PORTS[self.bay]
            return f"{self.host}:{port}"
        return self.port


class UnsupportedRoute(ShutterError):
    """A documented and qualified route contract is missing."""


def open_transport(config, deadline):
    """Open only the selected backend within the caller's connection budget."""
    if config.route.kind == "keh3":
        return TCPTransport(config.route.host, _KEH3_BAY_PORTS[config.route.bay], deadline)
    if config.route.kind == "vcp":
        return VCPTransport(config.route.port, deadline)
    return D2XXTransport(config.serial_number, deadline)


# Byte transports. Optional USB dependencies are imported only when opened.


class TCPTransport:
    """Bounded TCP bytes; APT framing and partial-write handling stay in Session."""

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
            data = self.socket.recv(_READ_SIZE)
        except (TimeoutError, BlockingIOError):
            return b""
        if not data:
            raise ShutterError("TCP peer disconnected; shutter state is unknown")
        return data

    def read_nowait(self):
        """Drain only arrived bytes so Session can reject unsolicited replies."""
        return self.read(0)

    def close(self):
        self.socket.close()


def dwell(deadline, seconds):
    """Wait for USB initialization without exceeding the connection deadline."""
    if deadline.remaining() < seconds:
        raise ShutterError("Insufficient connection budget for documented USB initialization")
    time.sleep(seconds)
    deadline.remaining()


class VCPTransport:
    """Pyserial USB bytes; bridge reset remains unqualified for output control."""

    def __init__(self, port, deadline):
        deadline.remaining()
        import serial

        self.device = serial.Serial(
            port=None,
            baudrate=115200,
            bytesize=8,
            parity="N",
            stopbits=1,
            rtscts=True,
            timeout=0,
            write_timeout=0.1,
        )
        try:
            self.device.port = port
            self.device.rts = True
            self.device.open()
            deadline.remaining()
            dwell(deadline, 0.05)
            self.device.reset_input_buffer()
            self.device.reset_output_buffer()
            dwell(deadline, 0.05)
            # pyserial has no FT_ResetDevice equivalent. VCP remains commissioning-only.
        except BaseException:
            self.device.close()
            raise

    def write(self, data, deadline):
        self.device.write_timeout = min(0.05, deadline.remaining())
        return self.device.write(data)

    def read(self, seconds):
        self.device.timeout = seconds
        return self.device.read(max(1, min(self.device.in_waiting, _READ_SIZE)))

    def read_nowait(self):
        return self.read(0)

    def close(self):
        self.device.close()


class D2XXTransport:
    """FTDI USB bytes opened by exact serial, with documented bridge setup."""

    def __init__(self, serial_number, deadline):
        deadline.remaining()
        import ftd2xx

        self.device = ftd2xx.openEx(serial_number.encode("ascii"), 1, update=False)
        try:
            deadline.remaining()
            self.device.setTimeouts(20, 50)
            self.device.setBaudRate(115200)
            self.device.setDataCharacteristics(8, 0, 0)
            dwell(deadline, 0.05)
            self.device.purge(3)
            dwell(deadline, 0.05)
            self.device.resetDevice()
            self.device.setFlowControl(0x0100, 0, 0)
            self.device.setRts()
            deadline.remaining()
        except BaseException:
            self.device.close()
            raise

    def write(self, data, deadline):
        self.device.setTimeouts(20, max(1, min(50, int(deadline.remaining() * 1000))))
        return self.device.write(data)

    def read(self, seconds):
        self.device.setTimeouts(max(1, int(seconds * 1000)), 50)
        return self.device.read(max(1, min(self.device.getQueueStatus(), _READ_SIZE)))

    def read_nowait(self):
        count = min(self.device.getQueueStatus(), _READ_SIZE)
        return self.device.read(count) if count else b""

    def close(self):
        self.device.close()


# Explicit informational inventory; never opens or selects a controller.


def list_d2xx_devices():
    """List FTDI descriptor metadata without opening or selecting a controller."""
    try:
        import ftd2xx
    except (ImportError, OSError) as exc:
        raise ShutterError(
            "D2XX inventory requires the d2xx extra and FTDI native library/driver"
        ) from exc

    count = ftd2xx.createDeviceInfoList()
    rows = []
    for index in range(count):
        info = ftd2xx.getDeviceInfoDetail(index, update=False)
        serial = info["serial"].decode("ascii", errors="replace")
        description = info["description"].decode("ascii", errors="replace")
        device_id = info["id"]
        state = "OPEN" if info["flags"] & 1 else "closed"
        rows.append(
            f"{serial}\tVID:PID={device_id >> 16:04X}:{device_id & 0xFFFF:04X}"
            f"\t{description}\t{state}"
        )
    return rows


def list_vcp_ports():
    """List OS serial-port metadata; entries are candidates, not verified KSC101s."""
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise ShutterError("VCP inventory requires the vcp extra (pyserial)") from exc

    return [
        f"{port.device}\t{port.hwid}\t{port.description}"
        for port in sorted(list_ports.comports(), key=lambda port: port.device)
    ]
