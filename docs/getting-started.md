# Setup and troubleshooting

[README](../README.md) | [GUI](gui.md) | [API](python-api.md)

## Environment

Use Windows x64 and Python 3.12 x64 for the qualified configuration. Install the
official Thorlabs Kinesis x64 distribution, its vendor dependencies and USB driver.
Python.NET loads the .NET Framework assemblies; installing Python dependencies
alone does not install Kinesis or a USB driver.

```powershell
uv sync --locked
uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
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
| `SLOTS` | Positive panel count; `None` means at least three, growing to fit serials |
| `PORT` | Localhost port, integer 1..65535; default 8050 |

For six empty panels, set `SLOTS = 6`. To preselect a controller, put its actual
serial in `SERIAL_NUMBERS = ("your serial",)`; keep live identities out of shared
commits. No launcher argument parsing or environment configuration is used.
The Python API still accepts explicit constructor settings.

Preserve manufacturer-approved power, docking and shutter wiring. Keep the source
independently blocked and only one application owning each controller. Startup is
passive: use GUI Discover/select and Connect, then verify identity and status.

Users set and verify the physical interlock externally. GUI interlock feedback is
informational and does not gate Open or Arm. Connection, key, operating feedback
and TTL prerequisites still apply. Explicit session confirmation remains available
through the Python API as informational metadata; project procedures do not
gate on it.
See [current hardware evidence](../records/hardware-validation.json).

## Troubleshooting

| Symptom | Action |
| --- | --- |
| SDK missing/load failure | Check x64 alignment, SDK folder, .NET Framework and vendor dependencies; restart Python after fixing installation |
| No controllers discovered | Inspect the approved USB/power arrangement and driver installation; this FTDI device need not have a COM port |
| Identity mismatch | Stop; preserve both selected and reported serials. Firmware1.0.7 repaired the historical mismatch onCONTROLLER_A; never alias serials in code |
| Already owned | Release the existing panel/process. A failed SDK disconnect retains its ownership claim |
| Open disabled | Read the readiness hint: connection fault, key, unknown operating feedback or Triggered mode. Disarm/Close before manual Open |
| Unknown operating state0 | Do not interpret it as Inactive. Preserve the report and diagnose; Close/Manual commands require separate output authority |
| Close/shutdown fails | Use independent bench recovery. Release alone does not establish closure |
| Port occupied | Use the existing GUI, stop its owning terminal normally, or edit `PORT` in `config.py` |
| Ethernet hub only | Follow the [separate Ethernet assessment](ethernet-assessment.md); hub discovery is not cube communication |

Do not run two GUIs against the same serial. Browser closure is not hardware
shutdown; use Close & disconnect all and normal terminal Ctrl+C.

## Optional developer simulation

```powershell
uv run --locked python tests/simulated_demo.py --port 8051
uv run --locked python tests/simulated_demo.py --api
```

The source-checkout helper reuses the fake SDK fixture. Its identities and states
are fictional. It establishes software behavior, not physical performance.
