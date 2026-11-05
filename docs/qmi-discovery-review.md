# QMI discovery and communication investigation

Inspected 5 November 2026 for the user's QMI source link. GitHub commits/main
resolved to `7b02875043985abd6366d902c1cf32af240a6881`, matching SRC-005.
Source inspection only; no QMI import, hardware enumeration, connection or output.
Downloaded references: ignored `inputs/reference/qmi-investigation/`.

## Discovery and selection

| Family | Device selection | Communication |
| --- | --- | --- |
| KDC101, K10CR1/2, MPC320 | Caller supplies serial:COM3 or serial:/dev/ttyUSB1; no controller port scan | pyserial VCP, default 115200 baud, 8N1, RTS/CTS; binary APT |
| MFF101/102 | Caller supplies serial descriptor | Same serial defaults; separate APT packing/parser |
| PM100D and compatible meters | list_instruments enumerates USBTMC descriptors, filters VID 0x1313 and supported product IDs | USBTMC carrying SCPI, including *IDN? |
| Original TSP01 | USBTMC enumeration filtered by VID 0x1313 / PID 0x80f8 | USBTMC carrying SCPI |
| TSP01B | PyUSB enumeration by VID 0x1313 / PID 0x80fa, manufacturer/product string checks; explicit serial selection on open | USB HID, 32-byte binary packets, interrupt endpoints and feature reports |
| TC200 | Caller supplies serial descriptor | 115200 baud, 8N1, no flow control; CR-terminated text commands, echo/prompt parsing |

USBTMC enumeration uses PyVISA on Windows and bundled python-usbtmc/PyUSB
otherwise. The Windows module also checks a libusb backend using LIBUSBPATH.
TSP01B explicitly expects Linux and can detach a kernel driver before claiming
the HID interface. These are different device families, not KSC101 recipes.

## APT path

QMI_SerialTransport opens serial.Serial; it does not use FTDI D2XX. Its fixed
40 ms native read timeout avoids repeatedly reprogramming serial parameters;
the source cites Windows FTDI data loss as its rationale. This is not bench proof.

KDC101 opens the configured port, waits 50 ms, discards incoming data, sends
HW_REQ_INFO (0x0005), receives HW_GET_INFO (0x0006), and rejects a model other
than KDC101. K10CR subclasses likewise check their model. get_idn returns model,
serial and firmware, but opening does not match an operator-configured expected
serial. MPC320/MFF10X open without this same automatic model verification.

apt_packets uses packed little-endian ctypes structures. Common AptProtocol
uses a six-byte header, default device 0x50 and host 0x01. Destination bit 7 marks
a payload, with its length in the header. ask writes a request and waits for a
reply class. MFF10X has its own implementation and uses 0x11 in its identity
request; do not generalize that address to KEH3.

## Project implications and limitations

- Complete Thorlabs directory inventory has no KSC101/KEH3 driver or hub
  discovery, identity, bay mapping or Ethernet wire contract.
- Generic TCP transport is not hub support: shared AptProtocol directly uses
  _safe_serial.in_waiting/out_waiting; KDC101/K10CR/MPC320 require serial transport.
- send_message clears pending input; wait_message discards unexpected valid
  types. Matching is by Python message class, without transaction IDs.
- Fixed sleeps, separate payload waits and an optional indefinite timeout do
  not provide strict total deadlines or guaranteed response freshness.
- K10CR base explicitly skips an additional documented wait/RTS step because
  its transport cannot explicitly set/clear RTS. KSC101 initialization equivalence
  is not established by this reference.

Use the transport/protocol/driver separation, explicit descriptors and identity
queries as references. Retain our exact serial/firmware/route checks, deadlines,
fault preservation and quarantine. Physical and Ethernet acceptance stay open.

## Pinned upstream evidence

- [Package inventory](https://github.com/QuTech-Delft/QMI/tree/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs)
- [KDC101](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs/kdc101.py)
- [APT protocol](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs/apt_protocol.py)
- [APT packets](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs/apt_packets.py)
- [Transports](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/core/transport.py)
- [Power meters](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs/pm100d.py)
- [TSP01B](https://github.com/QuTech-Delft/QMI/blob/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs/tsp01b.py)
