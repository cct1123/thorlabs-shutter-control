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
uv run --locked shutter-control --help
```

These commands do not contact hardware. Default SDK location:
`C:\Program Files\Thorlabs\Kinesis`. If different:

```powershell
$env:KINESIS_DIR = Read-Host 'Kinesis installation folder'
```

## Hardware launch

Preserve the manufacturer-approved power, docking and shutter wiring. Keep the
source independently blocked and only one application owning each controller.
Match discovery to the physical serial before connecting.

```powershell
uv run --locked shutter-control --list
$env:SHUTTER_SERIAL = Read-Host 'Controller serial from local discovery'
uv run --locked shutter-control --serial $env:SHUTTER_SERIAL --verified-interlock $env:SHUTTER_SERIAL
```

The flag records verified normal physical interlock/protection for that exact
preselected serial in this process. It is needed for Open on this bench while
the SDK reading is unknown; it performs no interlock write. GUI startup remains
passive. See [current hardware evidence](../records/hardware-validation.json).

| CLI option | Meaning |
| --- | --- |
| `--slots N` | Positive panel count; default at least three, growing to fit preselected serials |
| `--serial SERIAL` | Preselect a panel; repeat for distinct identities; default panel count grows to fit |
| `--verified-interlock SERIAL` | Confirm normal interlock/protection for the same preselected serial; repeat per device |
| `--kinesis-dir PATH` | Override `KINESIS_DIR` and the default SDK location |
| `--list` | Load the SDK and enumerate USB identities only |
| `--port PORT` | Localhost port, default8050, accepted1..65535 |

## Troubleshooting

| Symptom | Action |
| --- | --- |
| SDK missing/load failure | Check x64 alignment, SDK folder, .NET Framework and vendor dependencies; restart Python after fixing installation |
| No controllers discovered | Inspect the approved USB/power arrangement and driver installation; this FTDI device need not have a COM port |
| Identity mismatch | Stop; preserve both selected and reported serials. Firmware1.0.7 repaired the historical mismatch onCONTROLLER_A; never alias serials in code |
| Already owned | Release the existing panel/process. A failed SDK disconnect retains its ownership claim |
| Open disabled | Read the readiness hint: connection fault, key, unverified interlock or Triggered mode. Disarm/Close before manual Open |
| Unknown operating state0 | Do not interpret it as Inactive. Preserve the report and diagnose; Close/Manual commands require separate output authority |
| Close/shutdown fails | Use independent bench recovery. Release alone does not establish closure |
| Port occupied | Use the existing GUI, stop its owning terminal normally, or choose another `--port` |
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
