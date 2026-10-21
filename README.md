# Thorlabs shutter control

Control up to three KSC101 shutters from a local Dash GUI or a reusable Python
API. Each panel owns its own serial, connection, Open/Close controls and trigger
settings. Import and startup are passive; hardware access starts explicitly.

## Validated configuration

Computer -> USB -> KEH3 left bay -> **KSC101 68800777 -> SH05R**.
Windows x64, Python 3.12.7, Kinesis 1.14.60.27990, controller firmware **1.0.7**.
This USB device uses the Kinesis/FTDI interface; no COM port is assigned.

| Evidence | Result |
| --- | --- |
| USB identity, status, reconnect and normal shutdown | Controller readback passed |
| Five Open/Close cycles with 2-second added holds | SDK readback passed; user confirmed physical sequence |
| Production GUI discovery, Open/Close, trigger read, reconnect and cleanup | Actual browser and USB readback passed |
| Three real controllers, TTL electrical behavior, fault injection, calibrated timing | Not validated |
| KEH3 Ethernet cube communication | Unvalidated; historical hub-only discovery before firmware update |

See [hardware results](records/hardware-validation.json) and the
[remaining acceptance procedure](docs/HARDWARE_VALIDATION.md).

![Actual USB controller reporting Closed in the GUI](records/gui-ux-final-2026-10-20.png)

## Install

Use Windows x64, Python 3.12 x64, [uv](https://docs.astral.sh/uv/), and the official
[Thorlabs Kinesis x64 SDK/USB drivers](https://www.thorlabs.com/software-pages/Motion_Control).
The vendor runtime is separate from Python dependencies.

```powershell
git clone https://github.com/cct1123/thorlabs-shutter-control.git
cd thorlabs-shutter-control
uv sync --locked
uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
```

The default SDK folder is `C:\Program Files\Thorlabs\Kinesis`. Override it with
`KINESIS_DIR` or `--kinesis-dir`. See [setup and troubleshooting](docs/getting-started.md).

## Launch and operate

Keep the light source independently disabled or blocked, preserve the normal
physical interlock, and close Kinesis/other controller owners. Match the actual
serial and shutter wiring before operation.

```powershell
uv run --locked shutter-control --list
uv run --locked shutter-control --serial 68800777 --verified-interlock 68800777
```

Use `--verified-interlock` only after verifying the normal interlock and independent
protection. The SDK interlock indication is unknown on this bench; this records
operator evidence for this selected serial/session without changing hardware
interlock settings. Key, identity and communication checks still apply.
Retargeting clears confirmation. Omit the flag where readiness is independently
reported by the controller or when only passive reads are intended.

Open [localhost:8050](http://127.0.0.1:8050/), then:

1. Discover/select the intended serial and Connect. Check identity and state.
2. Establish Closed, then use Open/Close within the bench's approved limits.
3. Inspect feedback beside the controls. Expand **Trigger settings** only as needed.
4. Finish with **Close & disconnect all**, then normal terminal **Ctrl+C**.

Repeat `--serial` for up to three distinct controllers in panel order. Unused slots
stay disconnected. The GUI does not auto-connect. The actual current single-pair
hardware authorization is recorded in [STATE.md](STATE.md).

Reported state is not independent optical proof. Shutdown is best effort, runs
sequentially, and cannot bound a hung vendor call. Closing the browser tab does
not shut down the controllers. Open/Close selects Manual mode; previous timed or
triggered operation is not restored. Software holds are not calibrated exposure
times. Use the bench's independent shutdown procedure on uncertainty or failure.

## Python API and examples

```python
from thorlabs_shutter_control import KCubeShutter

shutter = KCubeShutter("68800777")
# Only after physical interlock/source protection have been verified:
shutter.confirm_interlock("68800777")
try:
    shutter.connect()
    print(shutter.identify_device())
    print(shutter.close_shutter())
finally:
    shutter.safe_shutdown()
```

[Five hardware tutorials](docs/examples/README.md) cover discovery, passive reads,
manual Open/Close, three shutters and TTL. [API reference](docs/python-api.md),
[GUI guide](docs/gui.md), [architecture](docs/architecture.md) and
[interface contract](docs/INTERFACE.md) explain ownership, feedback and cleanup.

TTL Arm can open immediately. An active-low input can activate with no cable
because the documented disconnected input is LOW. Draft edits do not apply or
arm; Close disarms. Physical TTL acceptance remains separate from software tests.

## Development and evidence

```powershell
uv run --locked python tests/simulated_demo.py --api
uv run --locked ruff check --no-cache src tests docs/examples docs/hardware_tests
uv build --wheel
```

The simulator uses fictional software devices and never reaches the SDK. The
normal test command excludes the opt-in real-SDK enumeration test. No simulator
or raw diagnostic runner is shipped as a production backend.

[Records](records/RECORDS.md) summarize durable results. Historical logs, acquisition
scripts and superseded plans are consolidated in a checksum-verified
[evidence archive](records/archive/README.md). [Project intent](PROJECT.md),
[current checkpoint](STATE.md) and [report](outputs/REPORT.md) describe current scope.
