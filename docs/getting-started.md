# Getting started

[README](../README.md) · [GUI](gui.md) · [Python API](python-api.md) · [Hardware](hardware.md)

Start with simulation. It runs the real controller and GUI against the repository's
test fixture, so no Kinesis installation, USB device or optical setup is needed.

## Install the tools

The verified setup is **Windows x64, Python 3.12.14 and uv 0.11.2**, with a modern
browser. The package declares Python `>=3.11,<3.14`; other Python versions and
non-Windows simulation are not validated here. The real backend requires Windows.

1. Install [Git](https://git-scm.com/downloads).
2. Install [uv using the official instructions](https://docs.astral.sh/uv/getting-started/installation/).
   One documented Windows option is `winget install --id=astral-sh.uv -e`.
3. Open a new PowerShell window so the tools are on `PATH`.

```powershell
git --version
uv --version
git clone https://github.com/cct1123/thorlabs-shutter-control.git
cd thorlabs-shutter-control
uv sync --locked
```

`uv sync` creates `.venv`, installs the package and default dev dependencies
(including pytest and Ruff), and uses Python 3.12 from `.python-version`.
The first run may download Python and packages. You do not need to activate
`.venv`: `uv run` selects it for each command. Keep `uv.lock` unchanged when
reproducing the documented setup.

If you already have this checkout, start with `uv sync --locked` in its root.

## Try simulation

Run the command-line API walkthrough:

```powershell
uv run --locked python docs/examples/simulated_demo.py --api
```

Expected output:

```text
SIMULATION ONLY — test fixture; no hardware access.
Discovered: ['68000001']
Identity: {'serial_number': '68000001', 'description': 'TEST DOUBLE, NOT HARDWARE'}
Initial: closed
Open: open
Close: closed
After cleanup: disconnected
```

`68000001` is deliberately fictional. The demo uses the existing pytest rig and
its virtual clock; it does not load Kinesis or fall back to hardware. The
[helper source](examples/simulated_demo.py) is documentation support, not a
production backend or installed console command. It requires this source checkout,
including `tests/`, and the default dev dependencies.

Start the actual Dash GUI with that same fixture:

```powershell
uv run --locked python docs/examples/simulated_demo.py
```

Keep the terminal open and visit [http://127.0.0.1:8050](http://127.0.0.1:8050).
Initially the screen says **Disconnected** and **Unknown**, and Open/Close are
disabled. Click **Discover**, then **Connect**. Identity should read
**TEST DOUBLE, NOT HARDWARE / 68000001** and the shutter should report **Closed**.
Try Open, Close and Close & disconnect. See the [illustrated GUI guide](gui.md).

Stop the demo with **Ctrl+C** in the terminal. Closing a browser tab leaves the
server running. A new demo process starts with a new fixture; it does not preserve
simulated device state.

To explore the no-device case after stopping the first demo:

```powershell
uv run --locked python docs/examples/simulated_demo.py --empty
```

Discover reports `Found 0 device(s).`; Connect reports `Expected one KSC101; found 0.`
No hardware is queried. There is no `shutter-control --simulate` option.

## Run software checks

In a second terminal at the repository root:

```powershell
uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
uv run --locked ruff check src tests docs/examples
uv run --locked ruff format --check src tests docs/examples
uv build
```

Expect **44 passed**, successful Ruff checks, and a wheel plus source distribution
under `dist/`. The ignored SDK test can enumerate real USB when `KINESIS_TEST_DIR`
is set, so the explicit exclusion matters even on a development computer.

These checks cover software behavior, including faults and GUI callbacks, not
physical operation. [E007](../records/RECORDS.md#e007) records the tested environment
and verification limits.

For an already populated cache, `uv sync --locked --offline` and `uv build --offline`
work without downloads. A fresh machine needs network access. The lock covers
runtime/dev packages; the build tool has a version range and the vendor SDK is
installed separately.

## Move to real hardware

**Physical validation is pending.** Follow [the hardware guide](hardware.md) and
the [approved validation procedure](HARDWARE_VALIDATION.md) before device access.

After approval, stop the demo, select the verified Kinesis folder, then enumerate:

```powershell
$env:KINESIS_DIR = Read-Host 'Verified Kinesis installation folder'
uv run --locked shutter-control --list
```

Compare the returned identity with the physical controller label. Do not use the
fictional test serial. Then launch the hardware GUI:

```powershell
uv run --locked shutter-control
```

The GUI does not auto-connect. Discover accesses the real SDK/USB interface;
Connect discovers again and requires either a selected serial or exactly one
discovered device. Open and Close request physical operation.

Inspect available options without hardware access:

```powershell
uv run --locked shutter-control --help
```

| Option | Meaning |
| --- | --- |
| `--serial` | Actual eight-digit KSC101 serial beginning with `68`; preselects the identity, does not auto-connect |
| `--kinesis-dir` | SDK folder; overrides `KINESIS_DIR`, then the default `C:\Program Files\Thorlabs\Kinesis` |
| `--list` | Load SDK and enumerate USB identities; no connection or output command |
| `--port` | Local GUI port, default `8050`, accepted range `1..65535` |

The hardware application always binds to `127.0.0.1`, runs one process without
debug/reloading, and attempts shutdown on normal server exit or Ctrl+C.

## Troubleshooting

Software messages and conditions below come from the implementation/tests.
Hardware checks are expected diagnostics, not physically validated remedies.

| Symptom | Next step |
| --- | --- |
| `uv` or `git` is not recognized | Reopen PowerShell after installation; confirm the installation directory is on `PATH`. Follow the official installer instructions. |
| Cannot write the uv cache | In this checkout, try `uv --cache-dir .uv-cache sync --locked` and use the same prefix for subsequent commands. |
| `No module named pytest`, or demo fixture file missing | Use a source checkout with `tests/` and run `uv sync --locked` without `--no-dev`. A wheel alone does not include this demo. |
| Lockfile or download failure | Use the repository's matching `pyproject.toml` and `uv.lock`; allow network access for uncached packages. `--offline` needs an existing cache. |
| Address/port already in use | Stop the earlier server, or launch the demo with `--port 8051` and visit port 8051. The hardware CLI also accepts `--port`. |
| GUI is disconnected; Open/Close disabled | Expected before connection. In the demo, Discover then Connect. In hardware mode, complete the approval/setup gates before either button. |
| GUI loads without Kinesis, but Discover fails | Expected: SDK loading is lazy. Use the simulation helper to explore without Kinesis. |
| `Kinesis SDK not found` / `Cannot load Kinesis` | Check the installed folder, matching Python/SDK bitness, .NET Framework and vendor runtime dependencies. Restart Python after correcting the installation or changing SDK versions. |
| `The Kinesis hardware backend requires Windows` | Use Windows for real hardware. A GUI page can render elsewhere without making the backend supported. |
| `Expected one KSC101; found 0` | In the empty demo this is intentional. On hardware, confirm device availability, the documented power/cabling arrangement and vendor USB-driver installation. |
| More than one device, or selected serial not discovered | Compare actual discovery with the controller label; explicitly select the intended identity. Do not substitute a sample serial. |
| Settings initialization/polling/connect failure | Read the full message and any cleanup error. Check the verified SDK/driver setup and competing controller processes before retrying under the hardware procedure. |
| Open disabled while connected | The GUI requires both key and interlock reports to be enabled. Preserve the bench safeguards; do not bypass them to enable a button. |
| Connection says Fault, shutter Unknown | Open is blocked. Read the error; Close/cleanup remain available while a device handle exists. Physically establish a safe state and resolve the cause before disconnect/reconnect. |
| Close or shutdown reports an error | Release is still attempted. Physical closure is unverified; follow the approved physical shutdown/recovery method. A repeated cleanup call cannot prove closure. |

For a useful issue report, include the command, full non-sensitive error, software
versions, simulation vs hardware mode, and the last successful step. Do not infer
physical motion from a successful Python return value.
