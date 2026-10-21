"""Project settings. Edit here, then run: uv run shutter-control.

Serials only preselect panels; startup never discovers or connects hardware.
Keep actual local serials out of shared commits.
"""

KINESIS_DIR = r"C:\Program Files\Thorlabs\Kinesis"
SERIAL_NUMBERS: tuple[str | int, ...] = ()
ETHERNET_ENDPOINTS: tuple[str | None, ...] = ()  # Per panel: "IPv4:bay-port", None for USB.
# LAN discovery defaults used by GUI Discover and the Python API.
LAN_SCAN_START_IP = "192.168.1.0"
LAN_SCAN_END_IP = "192.168.1.255"
LAN_SCAN_MAX_ADDRESSES = 256  # Integer 1..256; may narrow the scan limit.
LAN_SCAN_OPEN_TIMEOUT_MS = 100  # Per-address vendor connection timeout, integer 50..1000 ms.
SLOTS: int | None = None  # USB default: at least three; with endpoints: fit routes/serials.
PORT = 8050
