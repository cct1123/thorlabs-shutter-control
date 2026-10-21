# Thorlabs shutter control

A local Dash GUI and reusable Python API for a configurable number of **KSC101** solenoid
controllers. Control an **SH05R** optical shutter through the official Kinesis
SDK, directly by USB, through a **KEH3/KEH6** USB hub, or over **KEH3 Ethernet LAN**.
Each panel has explicit device
selection, four operating modes, state controls, trigger settings and cleanup.
Startup is passive.

![KSC101 solenoid controller and SH05R optical shutter](docs/assets/ksc101-sh05r.webp)

Manufacturer product photo: [Thorlabs optical shutters](https://www.thorlabs.com/optical-shutters).
It illustrates the supported device pair; it is not a photograph of the test bench.

## GUI

![Modern shutter panels in software simulation](docs/assets/gui-modern-simulation.png)

Compact neutral panels retain the Kinesis control layout: four mode selectors,
flat action controls and status lamps. This capture uses fictional software devices, not real hardware.
Trigger settings expand within each card; see the [GUI guide](docs/gui.md).

## Install

From a local checkout, use Windows x64, Python 3.12 x64, [uv](https://docs.astral.sh/uv/)
and the official [Thorlabs Kinesis SDK/USB drivers](https://www.thorlabs.com/software-pages/Motion_Control).
The vendor runtime is installed separately from Python dependencies.

```powershell
uv sync --locked
uv run --locked python -B -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
```

Edit hardware settings directly in [config.py](src/thorlabs_shutter_control/config.py):
SDK folder, panel count, optional serial preselection and local port. No command-line
options or environment parameters are needed. See [setup](docs/getting-started.md).

## Launch and operate

Keep the source independently disabled or blocked, preserve the normal physical
interlock, and close Kinesis/other controller owners. Match the physical shutter
to the serial found locally.

```powershell
uv run shutter-control
```

Click **Discover** to find USB and Ethernet controllers together, then choose a
device and **Connect**. Results show serial and detected route; no manual USB/LAN
choice or exact IP entry is needed. Full LAN scanning requires released handles.
Set the default LAN range (192.168.1.0–192.168.1.255), timeout and scan-size limit
with `LAN_SCAN_*` in [config.py](src/thorlabs_shutter_control/config.py).
Users set and verify the physical interlock externally. GUI interlock feedback is
informational and does not gate Open or Arm; connection, key, operating feedback
and TTL prerequisites still apply.

Open [localhost:8050](http://127.0.0.1:8050/):

1. Discover/select the intended controller and Connect. Read identity and status.
2. Establish Inactive/Closed, select Manual, Single, Auto or Trigger, and use
   Open/Close (Manual) or Start/Stop (other modes) within approved limits.
   Controls assume an enabled channel; see the [GUI guide](docs/gui.md#main-controls)
   for explicit setup and stored cycle settings.
3. Expand Trigger settings only when needed. Draft edits do not apply or arm.
4. Finish with **Shut down GUI & devices** to release all devices and exit the server.
   **Close & disconnect all** releases devices while keeping the GUI running.

Set `SLOTS = 6` in `config.py` for six panels, or any positive count.
See the [current six-panel preview](docs/gui.md#six-panel-layout).
`SERIAL_NUMBERS` preselects distinct devices in panel order. With `SLOTS = None`,
the USB default is three panels, growing to fit the configured serials. With
`ETHERNET_ENDPOINTS` configured, the default fits the endpoint/serial lists.
For optional one-panel LAN startup defaults, use this in `config.py`
(replace the fictional values):

```python
SERIAL_NUMBERS = (68000001,)
ETHERNET_ENDPOINTS = ("192.0.2.10:40304",)  # KEH3 left bay; None selects USB.
SLOTS = None
```

Each result displays its detected connection route. Connect automatically applies
the selected route to a released panel; it never falls back to another transport.
See [GUI discovery](docs/gui.md#ethernet-lan-configuration). No per-panel endpoint
or connection-type controls are needed. Restart after config.py edits. Unused panels
stay disconnected. Closing the browser does not shut down hardware. Cleanup is
best effort and cannot bound a hung SDK call; use independent bench recovery on
uncertainty. Reported states and software holds are not optical/timing measurements.

## Python API

```python
from thorlabs_shutter_control import KCubeShutter, config

serial = config.SERIAL_NUMBERS[0]  # Set the intended serial in config.py first.
shutter = KCubeShutter(serial)
verified = False
try:
    shutter.connect()
    verified = True
    shutter.close_shutter()  # Send commands, returns None.
    print(shutter.get_shutter_state())  # Explicit feedback read.
finally:
    shutter.disconnect(close_shutter=verified)
```

[Hardware tutorials](docs/examples/README.md) cover discovery, passive reads,
Open/Close, three shutters and TTL. Read the [API](docs/python-api.md),
[interface contract](docs/INTERFACE.md) and [architecture](docs/architecture.md).

Setters send commands and return `None`; getters request feedback separately.
Direct API callers own readiness and verification. The GUI performs explicit
reads. Current command paths have software validation; historical hardware
evidence below does not qualify the changed paths.

## Hub support and scale

The USB driver selects individual KSC101 identities and does not depend on a
three-bay hub. Thorlabs lists [KEH6](https://www.thorlabs.com/item/KEH6) as a six-bay
hub; the same addressing path is expected to work through KEH3/KEH6 USB or linked
USB hubs. KEH6 hardware has not been qualified here. Hub/power/USB limits still
apply; an arbitrary software count does not imply unlimited physical capacity or
simultaneous operation. Refresh and cleanup run sequentially, so latency grows
with the connected count. Ethernet remains experimental and belongs to
`ShutterHub`; `KCubeShutter` is USB-only. The launcher starts with USB defaults
and supports automatic USB/Ethernet discovery, detected routes and mixed panels.

## What has been tested

Qualified bench: computer -> USB -> KEH3 -> KSC101 -> SH05R; Windows x64,
Python 3.12.7, Kinesis 1.14.60.27990 and cube firmware 1.0.7. USB uses Kinesis/FTDI,
with no COM-port dependency. Published records use device aliases.

| Check | Evidence |
| --- | --- |
| Historical USB identity, status, reconnect, Open/Close and shutdown | Controller readback passed; user confirmed the five-cycle physical sequence |
| Historical GUI controls, refresh, reconnect and cleanup | Actual browser and USB readback passed for the recorded revision |
| TTL, both ports disconnected | Configuration/Arm/Disarm passed; active-low Open expectation failed on both ports |
| One KEH3/KSC101 explicit-endpoint LAN discovery, identity, Connect and passive release | E128 / TEST-138 passed; user also reports successful LAN notebook execution |
| LAN range scanning, current GUI hardware paths, Ethernet actuation/timing, multiple real pairs, external TTL, physical fault recovery, calibration | Not qualified on the current software |

Current modern GUI, mode selection and launcher shutdown have software-only
validation; historical bench results do not qualify these changed paths.

[Results](records/hardware-validation.json), [TTL observations](records/ttl-summary.json)
and the [short hardware test procedure](docs/HARDWARE_VALIDATION.md) preserve these
limits. TTL Arm can open immediately; active-low remains a potential opening
condition with an unplugged input, despite the unresolved no-cable test result.

## Development

```powershell
.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
uv run --locked python tests/simulated_demo.py --api
uv run --locked ruff check --no-cache src tests docs/examples docs/hardware_tests
uv build --wheel
```

Tests are grouped into controller, hub/routing, GUI, launcher, triggers,
tutorials and representative diagnostic workflows. Exhaustive historical stage
matrices have been replaced by smaller contract and integration checks. `-B` and
`-p no:cacheprovider` keep test runs from recreating bytecode and pytest caches.

The developer simulator never reaches the real SDK. The default test command
excludes opt-in real-SDK enumeration. See the [evidence index](records/RECORDS.md),
[current checkpoint](STATE.md) and [report](outputs/REPORT.md) for project status.

## Documentation

| Topic | Guide |
| --- | --- |
| Install, configure and troubleshoot | [Setup](docs/getting-started.md) |
| Modes, lamps, TTL and shutdown | [GUI guide](docs/gui.md) |
| Driver and hub calls | [Python API](docs/python-api.md), [interface contract](docs/INTERFACE.md) |
| USB and Ethernet tutorials | [Examples](docs/examples/README.md) |
| Hardware and qualification limits | [Hardware](docs/hardware.md), [commissioning](docs/HARDWARE_VALIDATION.md), [Ethernet](docs/ethernet-assessment.md) |
| Software structure and validation | [Architecture](docs/architecture.md), [evidence](records/RECORDS.md), [report](outputs/REPORT.md) |

Current screenshots and historical capture provenance are indexed in
[documentation assets](docs/assets/README.md). All current connected previews
use fictional software devices.
