# Direct KSC101 shutter control

Python library, CLI, localhost WebUI and six [Ethernet notebooks](docs/examples/README.md)
for Thorlabs KSC101 controllers. All clients use one shared owner and documented
APT messages. The runtime requires no Kinesis, pythonnet or Thorlabs SDK DLLs.
Ethernet transport uses the Python standard library; the WebUI adds Dash.

## Quick start

Use Python 3.12 and uv. From the repository root:

```powershell
uv sync --locked --extra gui
uv run shutter-control gui
```

Open [http://127.0.0.1:9860](http://127.0.0.1:9860). The GUI loads
[config/shutter.ethernet.toml](config/shutter.ethernet.toml). Startup opens no
device: select the exact configured target, then click **Connect**.

To use another configuration or localhost port:

```powershell
uv run shutter-control --config shutters.local.toml gui --port 9861
```

The GUI defaults above apply when launched from the repository root. Other CLI
commands default to `shutters.local.toml`. There is no automatic discovery,
port takeover, route fallback, reconnect or ON replay. See
[setup and diagnostics](docs/getting-started.md) for custom configurations and USB extras.

## Daily operation

Connect verifies the configured controller identity and reads mode, interlock
requirement and electrical output. **Read state** requests fresh feedback;
**Live readback** enables optional polling. Readings include their observation
time, and disconnected or undated feedback stays **Unknown**.

| Control | Effect |
| --- | --- |
| Manual / Single / Auto / Triggered | Explicit mode selection with OFF/interlock checks and readback; changed modes persist at power-up |
| Open / ON or Start | Manual ON or qualified native Start through the shared owner; ordinary Manual ON has no automatic shutoff |
| 1-second ON, then OFF | Manual ON, a 1 s host hold after ON readback, then OFF/readback |
| Close / OFF or Stop / OFF | Priority output stop; a retained fault clears only after verified OFF and preserved interlock |
| Settings | Read timing/count and LED modes; applying changes requires the configured settings permissions |
| Readback and diagnostics | Explicit channel/bay queries, device-message start/stop and raw event collection |
| Release | Close communication; refuses a pending ON/Start request and sends no output command |
| Shutdown GUI server | Standalone launcher only: drain accepted callbacks, clean up output work and release communication, then return to the terminal |

Use Stop / OFF for output control; server shutdown can wait for pending callbacks.
Cleanup failures are reported in the terminal. Embedded `create_app(hub)` instances
omit the shutdown control. To load updated code/configuration, Stop and Release
the existing owner, shut down the server, restart the launcher and reload the browser.

An explicit Stop / OFF can reset a fault after successful verification. Reads and
automatic cleanup retain faults. If the old session cannot communicate, Release,
Connect, then Stop / OFF. Failed verification retains the diagnostic journal;
never delete ownership state to imitate recovery. See the
[GUI procedure](docs/gui.md) and [API/recovery contract](docs/python-api.md).

## Tracked hardware profile

The repository profile selects this exact setup; it does not establish the
present connection or physical state.

| Item | Configured value |
| --- | --- |
| Logical target / load | `shutter` / SH05R |
| Controller / firmware | KSC101 `68800777` / `1.0.7` |
| Route | KEH3 middle bay, `192.168.1.19:40305` |
| Channels | Application 0; APT 1 |
| Hub identity | Unknown; not inferred from the controller reply |

The profile permits selection and software activation of all four modes, subject
to load, cycle, OFF/interlock, fault and ownership checks. `min_off_s = 0.0` adds
no extra software OFF pause; custom positive intervals remain enforced. Native
cycles are limited to one by default, continuous Triggered priming is blocked,
and settings/EEPROM write permissions are disabled. No source-confirmation
checkbox or separate mode-selection permission is required. These software
permissions do not qualify native modes or settings for physical use.

Qualified output is implemented for D2XX and docked KEH3 routes. VCP supports
read-only commissioning; KEH3 external USB OUT is unavailable. USB retains its
FTDI driver dependencies. The legacy bay query is refused on KEH3 before I/O;
use the configured bay/endpoint. Hardware disconnect is a protected Python API
operation, separate from ordinary Release. See the [route matrix](docs/hardware.md).

## Python and CLI

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("config/shutter.ethernet.toml") as hub:
    hub.connect("shutter")
    status = hub.get_status("shutter")
    print(status.operating_mode, status.electrical_state)
```

Construction is passive; `connect()` opens the exact route and verifies identity.
Context exit and `close()` release communication without sending OFF. This example
only queries the controller. Scripts that actuate output need explicit output
cleanup under the [API contract](docs/python-api.md).

Check the tracked configuration without opening a device:

```powershell
uv run --locked shutter-control --config config/shutter.ethernet.toml check-config
uv run --locked shutter-control --help
```

The CLI also provides `discover`, `identify`, `status`, `manual`, `safe-off` and
`pulse --seconds`. Device commands require an explicit `--target`; configuration
and target options go before the subcommand. Inventory never selects a device.
See [setup](docs/getting-started.md) for command effects and examples.

The three core modules are `controller.py`, `protocol.py` and `transport.py`.
Use package-level imports. Version 2 replaces the former config/device/discovery
modules and nested status schema; external consumers need the
[API/status migration](docs/python-api.md#status-schema-migration).

## Validation and limits

Run software verification with cached locked dependencies:

```powershell
uv sync --locked --group dev --extra gui
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix docs-refresh-
```

The verifier checks source and an isolated installed wheel, locked dependencies,
lint/format, Python/CSS parity, passive startup and static notebook checks. Tests
use simulated transports and localhost; notebook hardware cells are not executed.
`--record-prefix` preserves earlier campaigns; `--test-path` selects a subset.
Latest results: [verification record](records/docs-refresh-direct-validation.json).

Electrical OFF does not prove blade closure. The status panel's Interlock flag
and Channel flag are literal status bits, not verified key position, readiness
or contact continuity. Native request tracks host Start requests, not measured
activity. Key/Ready/actual native activity and trigger/MMI configuration still
need verified KSC101 mappings; see [status readback](docs/status-readback.md).
APT also cannot prove freshness for arbitrary delayed same-type replies.

The [8 November bounded WebUI run](records/webui-redo-bounded-validation.json)
completed one approved Manual pulse and ended with electrical OFF and release
on its recorded revision. Independent blade motion was unobserved; the cycle
allowance is consumed. Optical timing/extinction, native modes/settings, wider
hub/USB deployment and external DiamondGUI migration remain open. Host hold
times are not calibrated optical exposures. The broader project remains
**BLOCKED** on those acceptance gaps; software verification does not close them.

## Documentation

| Guide | Contents |
| --- | --- |
| [Setup and diagnosis](docs/getting-started.md) | Installation, configuration, CLI and troubleshooting |
| [GUI](docs/gui.md) | Controls, shutdown, diagnostics and dated browser evidence |
| [Python API](docs/python-api.md) | Shared owner, status schema, output/cleanup and recovery |
| [Ethernet notebooks](docs/examples/README.md) | Six standalone tutorials using the real interface |
| [Architecture](docs/architecture.md) / [APT interface](docs/INTERFACE.md) | Layers, messages, ownership and deadlines |
| [Hardware](docs/hardware.md) / [physical acceptance](docs/HARDWARE_VALIDATION.md) | Routes, drivers and remaining measurements |
| [Manuals](docs/manuals/README.md) / [source register](docs/sources.md) | Manufacturer references and provenance |
| [Cutover](docs/cutover.md) / [DiamondGUI](docs/diamondgui.md) | Migration, deployment and external integration |
| [Current state](STATE.md) / [report](outputs/REPORT.md) / [records](records/RECORDS.md) | Requirement status, results and historical evidence |
