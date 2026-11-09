# Setup and diagnosis

Use a 64-bit Python 3.12 deployment through uv. All setup, tests and execution
use uv; Windows device bindings and native libraries remain separate.

## Install and launch

From the repository root, install the GUI dependencies:

```powershell
uv sync --locked --extra gui
```

Launch the GUI from the repository root:

```powershell
uv run shutter-control gui
```

The GUI defaults to the tracked Ethernet profile
and http://127.0.0.1:9860; it opens no device until you select an exact target and
click Connect. Override with `--config PATH` before `gui` or `gui --port PORT`.
Other CLI commands continue to default to `shutters.local.toml`.

```powershell
uv run shutter-control --config shutters.local.toml gui --port 9861
```

Startup neither connects nor changes output. Stop and Release an existing owner
before replacing it. **Shutdown GUI server** is available in standalone launches;
it waits for accepted callbacks, runs output cleanup and releases communication.
Use Stop / OFF for immediate output control. Embedded `create_app(hub)` instances
omit shutdown; see [the GUI guide](gui.md#standalone-server-shutdown).

## Transport dependencies

The default package has no Python runtime dependencies. Optional `d2xx` uses
ftd2xx 1.3.8 and the installed FTDI D2XX native library; it never uses a Thorlabs
DLL. Optional `vcp` uses pyserial 3.5 and an exact configured port. The VCP bridge
reset equivalence is unresolved, so VCP connections are read-only commissioning.
Do not change USB bindings as part of installation; follow [cutover](cutover.md).

To explicitly list host metadata without opening a controller or loading config:

```powershell
uv run --locked --extra d2xx shutter-control discover
uv run --locked --extra vcp shutter-control discover --vcp
```

The first command enumerates all FTDI D2XX descriptors, including unrelated
devices; the second enumerates OS serial ports. Neither identifies a controller
over APT, selects a target, changes configuration or falls back to another route.
An empty list does not prove absence on the other transport. Copy reviewed
identity/route information into local configuration; connection verifies the
configured model, serial and allowed firmware before control. Imports and help
never run this inventory. Native enumeration duration depends on the OS driver.

## Configure and check

Configuration is strict TOML, loaded without discovery or I/O. Start from
`config/shutters.example.toml`; local configuration is ignored by Git. Each entry
requires name, application channel, physical role, exact KSC101 serial, firmware
allowlist and an explicit route. Model must read back KSC101, with one channel.
Duplicate serials/names/channels/routes fail before connecting.

The tracked Ethernet profile is already configured for `shutter`, KSC101
`68800777`, firmware `1.0.7`, KEH3 middle bay `192.168.1.19:40305`, application
channel 0 / APT channel 1. For another setup, copy the example to a new
`shutters.local.toml`, then edit its exact identity and route before connecting.
Preserve any existing local configuration. Check either file without device I/O:

```powershell
uv run --locked shutter-control --config shutters.local.toml check-config
uv run --locked shutter-control --config config/shutter.ethernet.toml check-config
```

For KEH3, supply host and bay. Omit hub_serial/hub_firmware when unknown;
do not insert placeholder identities. The controller reply does not identify
the hub. Optional known metadata is checked for consistency across its routes.

`policy` is omitted by default. Writes require an operator-reviewed qualification
record covering shutter model, wiring, OFF -> optical closed mapping, interlocks,
continuous-duty permission and minimum OFF interval. The current implementation
only activates continuous-duty loads in permitted modes: finite exposure/duty policies fail
closed until an independent cutoff and applicable limits are qualified.
Changing a policy requires revalidation; setting a boolean is not qualification.
`allow_persistent_mode_changes` is a legacy compatibility field and does not gate
mode selection; electrical OFF and interlock/readback checks remain. KSC101 mode changes
persist automatically (SRC-002 p20) even without an explicit EEPROM command.

The tracked profile permits all four modes and sets `min_off_s = 0.0`. Native
Start still checks load/cycles/OFF/interlock; continuous-cycle and settings/storage
permissions remain disabled. These flags do not establish physical qualification.

## CLI commands

Put global `--config` and `--target` options before the command. For example,
this command **opens the configured controller**, reads feedback, then releases
communication without an output command:

```powershell
uv run --locked shutter-control --config config/shutter.ethernet.toml --target shutter status
```

| Command | Effect |
| --- | --- |
| `check-config` | Parse/validate TOML and print it; no device I/O or target needed |
| `discover` / `discover --vcp` | Explicit host inventory using the corresponding optional extra; no controller selection or config load |
| `identify` | Connect and print verified identity; does not flash LEDs |
| `status` | Connect and request fresh controller feedback |
| `manual` | Explicit persistent Manual selection with OFF/interlock checks; an already selected mode requires no write |
| `safe-off` | Explicit qualified Stop/OFF and readback; clears faults only after verification |
| `pulse --seconds N` | Validate duration, connect, prepare OFF/rest, then Manual ON/host hold/OFF |
| `gui [--port PORT]` | Start the passive localhost WebUI |

Except for `check-config`, inventory and GUI startup, commands require an exact
`--target`. Mode/output commands are physical operations and require the reviewed
load policy and applicable protected operating window. CLI `manual --source-inhibited`
is a legacy compatibility option; it is no longer required. Electrical feedback
and a host hold do not measure optical state or exposure; see [the API](python-api.md).

## Troubleshooting

| Symptom | Meaning / response |
| --- | --- |
| Missing ftd2xx/native DLL | Install optional Python extra and matching official FTDI native package; no Thorlabs application required |
| Already owned | Release the active owner; a failed release retains claims; do not delete lock files to bypass ownership |
| Identity mismatch | Check exact controller/route with source protected; no fallback or output cleanup to a mismatched device |
| Fault lockout | Keep independent optical protection; explicit Stop/OFF resets after verified OFF/interlock. A poisoned session needs Release/Connect first; passive protected recovery is another option. Never repeat ON |
| Control route unavailable | VCP and KEH3 external USB OUT writes are refused; docked KEH3 writes require the reviewed load policy and mode/interlock checks |
| Trigger->Manual refused | Check electrical OFF and enabled interlock requirement; no source confirmation is required for mode selection |
| OFF unconfirmed | Physical state remains unknown; use independent source protection and inspect the shutter |
| Write framing unknown | No more frames, including OFF, are sent on that connection; independently inhibit the source and perform protected recovery |

Defaults cover complete operations: connection/identity 5 s, ordinary query or
command 3 s, separate cleanup 5 s. Driver/native calls can exceed their requested
timeouts; a late return is rejected, but hard dispatch/closure bounds require
physical validation and independent protection.

## Software verification

Install the development group and GUI extra, then verify without instruments:

```powershell
uv sync --locked --group dev --extra gui
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix docs-refresh-
```

The offline command requires cached locked dependencies. It runs source and
isolated-wheel tests, lint/format, passive import/help/config and static notebook
checks. It never executes notebook hardware cells. For just the tutorial checks:

```powershell
uv run --locked --group dev pytest tests/test_tutorial_notebooks.py
```

Use [the notebook guide](examples/README.md) for interactive execution and
[physical acceptance](HARDWARE_VALIDATION.md) for unresolved bench requirements.
