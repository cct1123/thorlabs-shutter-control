# Setup and troubleshooting

[README](../README.md) | [GUI](gui.md) | [API](python-api.md)

Use Windows x64 and Python 3.12 x64. Install the official Kinesis .NET Framework
runtime and vendor drivers separately from project dependencies.

```powershell
uv sync --locked
uv run --locked python -B -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
uv run shutter-control
```

Dependency setup and the excluded-SDK test suite do not contact hardware. GUI
startup is passive. Visit [localhost:8050](http://127.0.0.1:8050/).

## Project configuration

Edit [config.py](../src/thorlabs_shutter_control/config.py), then restart the server.
SERIAL_NUMBERS and ETHERNET_ENDPOINTS are optional panel defaults; keep actual
identities/address details out of shared commits. None endpoints mean USB.
SLOTS is a positive count; None means at least three USB panels, or enough for
supplied endpoint/serial lists. Set SLOTS=6 for six panels; actual hub/power/USB
limits still apply. PORT selects a localhost port, default8050.

LAN_SCAN_START_IP/END_IP default to192.168.1.0..192.168.1.255 inclusive.
LAN_SCAN_MAX_ADDRESSES is an integer1..256; LAN_SCAN_OPEN_TIMEOUT_MS is an
integer50..1000ms per address, default100. Native SDK calls can block.

Discover combines USB, configured routes and the shared LAN scan. Select a result
and Connect; the detected route is applied automatically. Startup never discovers,
connects or writes outputs. Release process handles for a fresh broad scan and
close competing GUI/notebook/Kinesis owners.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| SDK missing/load error | Match Python/Kinesis bitness and runtime dependencies; inspect KINESIS_DIR; restart after correction |
| No device discovered | Read the USB/LAN warning; inspect USB power/FTDI drivers or LAN_SCAN range and [Ethernet setup](ethernet-assessment.md) |
| Wrong identity/route | Stop and resolve physical serial/bay mapping; do not bypass validation |
| Already owned | Release the owning panel/process; failed release retains its handle and claim |
| Open/Start disabled | Read the hint; establish healthy known feedback/key and the mode's prerequisites |
| Mode disabled | Stop/Close and read Inactive/Closed before changing mode |
| Unknown operating state0 | Preserve unknown; do not interpret it as Inactive or enable implicitly |
| Unexpected cycle timing | Single/Auto use the controller's stored settings; the GUI does not edit cycle timing/counts |
| Close/release fails | Preserve the object/error, use independent source protection and verify physical state |
| Port occupied | Stop its owning server normally or edit PORT; browser closure does not stop it |

Users manage the physical interlock externally. GUI interlock feedback is
informational. Restart the server after source/config edits; reloading the browser
alone does not load new Python code. See [commissioning](HARDWARE_VALIDATION.md).
