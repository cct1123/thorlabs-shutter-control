# thorlabs-shutter-control

A reusable Python controller for the Thorlabs KSC101 and a local Plotly Dash GUI.
Hardware commands live entirely in `KSC101Controller`; the GUI calls that class.

**Hardware validation pending.** Software tests pass and the official Kinesis SDK
loads, but discovery on the development computer returns no KSC101 devices.
See [STATE.md](STATE.md) and the [engineering report](outputs/REPORT.md).

## Setup

Use 64-bit Windows, Python 3.12, [uv](https://docs.astral.sh/uv/getting-started/installation/),
and the official [Thorlabs Kinesis package](https://www.thorlabs.com/software-pages/Motion_Control)
matching Python's bitness. Kinesis provides vendor DLLs and USB drivers; those
are not distributed in this repository. Python.NET also requires .NET Framework.
Development checks used Python 3.12.14 and the 64-bit Kinesis 1.14.60 SDK.

```powershell
uv sync --locked
uv run --locked shutter-control --list
uv run --locked shutter-control
```

Open <http://127.0.0.1:8050>. Discover devices, select a serial number if needed,
and Connect. Open and Close request manual operation. The GUI reports connection,
identity, controller-reported shutter state, key/interlock status, and errors.

For a nonstandard SDK location:

```powershell
$env:KINESIS_DIR = 'C:\path\to\Kinesis'
uv run --locked shutter-control --list
```

Alternatively pass `--kinesis-dir` directly. `--serial` selects a known device;
without a selection, connection requires exactly one discovered KSC101.
`--port` changes the default 8050 port. The server binds only to `127.0.0.1` and
runs as a single process without debug/reloading. Use one operator and one owner
per device; do not run Kinesis GUI or another control process on the same device.

On this development computer, `uv` is at
`C:\Users\ctcheung\.local\bin\uv.exe`. If it is not on PATH, invoke that path with
PowerShell's `&`. This sandbox requires `--cache-dir .uv-cache` before the command:

```powershell
& "$env:USERPROFILE\.local\bin\uv.exe" --cache-dir .uv-cache run --locked shutter-control
```

An ignored SDK administrative image is available locally at
`tmp\kinesis-sdk\Program Files 64\Thorlabs\Kinesis`; select it with `--kinesis-dir`
for SDK checks. It is not a system installation or evidence of USB driver readiness.

## Python use

Run only on the agreed safe hardware setup described in the
[hardware validation procedure](docs/HARDWARE_VALIDATION.md).

```python
from thorlabs_shutter_control import KSC101Controller

controller = KSC101Controller()  # Or supply the actual discovered serial_number.
print(controller.discover())
with controller:  # Connects; exits with close attempt and disconnect.
    print(controller.identify_device())
    print(controller.get_status())
    print(controller.open_shutter())
    print(controller.close_shutter())
```

Methods: `discover`, `connect`, `identify_device`, `get_status`, `open_shutter`,
`close_shutter`, `disconnect`, and `safe_shutdown`. Failures raise `ShutterError`;
`get_status()` instead returns an explicit fault snapshot with unknown shutter
state. Communication/operation faults block further Open commands until a
disconnect/reconnect. Close and cleanup remain available while a handle exists.

`connect()` issues no explicit output, enable, or mode commands. Open clears prior
activity, selects Manual, enables the device, and requests Active. Close requests
Inactive, then Manual. Commands wait for matching Kinesis feedback with a default
5-second wait per stage; vendor calls have their own timeouts. Polling is 250 ms;
GUI refresh is 1 second. These are not real-time guarantees or exposure controls.

## Shutdown and recovery

- **Close & disconnect**, `disconnect()`, and `safe_shutdown()` attempt closure,
  then stop polling and release the device, including when closure fails.
- Ctrl+C in the server terminal runs the same shutdown attempt. Closing a browser
  tab does not stop the server or close the shutter. Forced termination, lost
  USB, power failure, or a hung vendor call cannot guarantee closure.
- A shutdown error must be investigated physically. A repeated cleanup call does
  not erase a failed-close message. If release fails, the handle is retained so
  cleanup can be retried.
- `disconnect(close_shutter=False)` is an explicit communication-only release:
  it leaves the output unchanged and is not safe shutdown.
- Preserve existing interlocks and key safeguards. Do not bypass them or modify
  firmware. Software feedback is not independent proof of physical closure.

If discovery is empty, check device availability, supported power/cabling, and
the vendor USB driver. If SDK loading fails, check path, bitness, .NET Framework,
and the Kinesis runtime dependencies. Restart Python after changing SDK versions.

## Validation and project files

```powershell
uv run --locked pytest -q -p no:cacheprovider
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv build
```

The ordinary suite uses a software test double. To additionally check the actual
SDK signatures and USB enumeration, set `KINESIS_TEST_DIR` to the Kinesis folder
before running pytest. That test never connects or actuates a device. No automatic
test in this repository moves real hardware.

- `src/thorlabs_shutter_control/`: controller, GUI, CLI, packaged CSS.
- `tests/`: failure, lifecycle, GUI callback, CLI, and optional real-SDK checks.
- [docs/INTERFACE.md](docs/INTERFACE.md): official sources and API semantics.
- [docs/HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md): pending physical tests.
- [PROJECT.md](PROJECT.md): human intent; [AGENTS.md](AGENTS.md): operating rules.
- [STATE.md](STATE.md): checkpoint; [records/RECORDS.md](records/RECORDS.md): evidence.

To resume engineering, read PROJECT.md, AGENTS.md, and STATE.md, reconcile the
hardware configuration, then continue from the recorded blocker and next action.
