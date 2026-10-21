# Setup and troubleshooting

[README](../README.md) | [GUI](gui.md) | [API](python-api.md)

## Environment

Use Windows x64 and Python 3.12 x64 for the qualified configuration. Install the
official Thorlabs Kinesis x64 distribution, its vendor dependencies and USB driver.
Python.NET loads the .NET Framework assemblies; installing Python dependencies
alone does not install Kinesis or a USB driver.

```powershell
uv sync --locked
uv run --locked python -B -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
```

These commands do not contact hardware.

## Project configuration and launch

Edit [config.py](../src/thorlabs_shutter_control/config.py), then launch:

```powershell
uv run shutter-control
```

| Setting | Meaning |
| --- | --- |
| `KINESIS_DIR` | SDK folder; default `C:\Program Files\Thorlabs\Kinesis` |
| `SERIAL_NUMBERS` | Tuple of distinct serial strings or integers in panel order; empty means select in GUI |
| `ETHERNET_ENDPOINTS` | Per-panel KEH3 IPv4 cube endpoints (`IP:40304`..`IP:40307`); `None` selects USB; empty tuple defaults to USB |
| `LAN_SCAN_START_IP` / `LAN_SCAN_END_IP` | Inclusive default discovery range; `192.168.1.0` through `192.168.1.255`; used by the shared Discover action |
| `LAN_SCAN_MAX_ADDRESSES` | Maximum addresses per scan, integer 1..256; default 256 |
| `LAN_SCAN_OPEN_TIMEOUT_MS` | Vendor per-address connection timeout, integer 50..1000 ms; default 100 ms |
| `SLOTS` | Positive panel count; `None` fits endpoint/serial lists when endpoints are supplied, otherwise at least three |
| `PORT` | Localhost port, integer 1..65535; default 8050 |

For six empty panels, set `SLOTS = 6`. To preselect a controller, put its actual
serial in `SERIAL_NUMBERS = ("your serial",)`; keep live identities out of shared
commits. No launcher argument parsing or environment configuration is used.
The Python API still accepts explicit constructor settings.
For LAN-only or mixed operation, follow [GUI Ethernet configuration](gui.md#ethernet-lan-configuration).
Startup stays passive; entering an endpoint never discovers or connects a device.
Discover finds USB and Ethernet automatically using the configured LAN range.
Choose a result and Connect; the detected endpoint is applied automatically.
There are no per-panel transport controls or separate LAN scan form. File settings
are optional startup defaults. Release all controllers and close competing owners
for a fresh full scan; skipped/failed transports report a warning while successful
results remain selectable.

Preserve manufacturer-approved power, docking and shutter wiring. Keep the source
independently blocked and only one application owning each controller. Startup is
passive: use GUI Discover/select and Connect, then verify identity and status.

Users set and verify the physical interlock externally. GUI interlock feedback is
informational and does not gate Open or Arm. Connection, key, operating feedback
and TTL prerequisites still apply. Explicit session confirmation remains available
through the Python API as informational metadata; it is optional and project
procedures do not gate on it.
See [current hardware evidence](../records/hardware-validation.json).

## Troubleshooting

| Symptom | Action |
| --- | --- |
| SDK missing/load failure | Check x64 alignment, SDK folder, .NET Framework and vendor dependencies; restart Python after fixing installation |
| No controllers discovered | Read the USB/LAN discovery warning. For USB, inspect power/cabling and FTDI drivers; no COM port is needed. For LAN, check the config.py scan range, release process handles and follow the [Ethernet guide](ethernet-assessment.md) |
| Identity mismatch | Stop; preserve both selected and reported serials. Firmware1.0.7 repaired the historical mismatch onCONTROLLER_A; never alias serials in code |
| Already owned | Release the existing panel/process. A failed SDK disconnect retains its ownership claim |
| Open/Start disabled | Read the readiness hint. Manual needs healthy known feedback and key enabled; Single/Auto/Trigger need Inactive/Closed, with an actual input configured for Trigger. No software interlock gate |
| Mode selector disabled | Establish fresh Inactive/Closed feedback with Stop/Close; mode selection does not Stop or Enable implicitly |
| Start uses unexpected duration/count | Single/Auto use stored controller settings; this GUI does not edit or read cycle timing/counts |
| Unknown operating state0 | Do not interpret it as Inactive. Preserve the report and diagnose; Close/Manual commands require separate output authority |
| Close/shutdown fails | Use independent bench recovery. Release alone does not establish closure |
| Port occupied | Use the existing GUI, stop its owning terminal normally, or edit `PORT` in `config.py` |
| Ethernet hub only | Follow the [separate Ethernet assessment](ethernet-assessment.md); hub discovery is not cube communication |

Do not run two GUIs against the same serial. Browser closure is not hardware
shutdown. The launcher provides **Shut down GUI & devices**; **Close & disconnect
all** keeps the server running, and normal terminal Ctrl+C also attempts cleanup.
See [GUI ownership and finish](gui.md#ownership-and-finish).

## Optional developer simulation

```powershell
uv run --locked python tests/simulated_demo.py --port 8051
uv run --locked python tests/simulated_demo.py --api
```

This helper embeds the GUI and has no server-shutdown button; finish with normal
terminal Ctrl+C. Documentation screenshots use a separately labelled isolated
software preview with an owner-provided shutdown callback.

The source-checkout helper reuses the fake SDK fixture. Its identities and states
are fictional. It establishes software behavior, not physical performance.
