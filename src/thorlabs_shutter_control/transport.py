"""Optional FTDI transports. Importing this module performs no enumeration.

SRC-001 section 2.1: 115200 baud, 8N1, RTS/CTS and asserted RTS. Its USB
initialization includes 50 ms before/after purge and a bridge reset. These
documented waits apply to connection only, and consume the identity deadline.
No Thorlabs DLL is loaded. Native driver call latency still needs qualification.
"""

import time

from .errors import ShutterError, UnsupportedRoute
from .ethernet import TCPTransport


def dwell(deadline, seconds):
    if deadline.remaining() < seconds:
        raise ShutterError("Insufficient connection budget for documented USB initialization")
    time.sleep(seconds)
    deadline.remaining()


class VCPTransport:
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
        return self.device.read(max(1, min(self.device.in_waiting, 4096)))

    def read_nowait(self):
        self.device.timeout = 0
        return self.device.read(min(self.device.in_waiting, 4096))

    def close(self):
        self.device.close()


class D2XXTransport:
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
        return self.device.read(max(1, min(self.device.getQueueStatus(), 4096)))

    def read_nowait(self):
        count = min(self.device.getQueueStatus(), 4096)
        return self.device.read(count) if count else b""

    def close(self):
        self.device.close()


def require_control_route(config):
    """Connection/readback is separate from qualification for physical output."""
    if config.route.kind == "keh3" and config.route.bay == "external":
        raise UnsupportedRoute(
            "KEH3 external USB control unavailable; select a documented docked cube bay"
        )
    if config.route.kind == "vcp":
        raise UnsupportedRoute("VCP bridge reset/binding unqualified: read-only commissioning")


def open_transport(config, deadline):
    if config.route.kind == "keh3":
        host, port = config.route.endpoint.split(":")
        return TCPTransport(host, int(port), deadline)
    if config.route.kind == "vcp":
        return VCPTransport(config.route.port, deadline)
    return D2XXTransport(config.serial_number, deadline)
