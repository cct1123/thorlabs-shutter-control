"""Explicit host inventory only. Importing this module performs no hardware I/O."""

from .errors import ShutterError


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
