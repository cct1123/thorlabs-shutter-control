# Direct KSC101 shutter control

One Python owner for the library, CLI, GUI and six [Ethernet notebooks](docs/examples/README.md).
The runtime sends documented APT messages directly; it needs no Kinesis,
pythonnet or Thorlabs SDK DLLs. Ethernet uses the Python standard library.

The notebooks select **shutter**, KSC101 **68800777**, firmware **1.0.7**, at
**192.168.1.19:40305** (KEH3 middle bay). They perform actual identity/status
queries with no simulator, scan or USB fallback. Docked KEH3 bays use the same
qualified Manual ON/OFF commands as D2XX; VCP and external USB OUT control remain
unavailable. Notebooks 5 and 6 contain physical commands, as described in their
instructions. The selected middle-bay SH05R passed real ON/OFF controller
readback. The user independently observed the blade open and return closed in
the later single-cycle WebUI test (E191/E192); optical timing and broader
qualification remain unverified. The test left Manual/OFF and released ownership.
That is dated evidence for its recorded revision; this software review does not
repeat the cycle or establish the controller's present state.

```powershell
uv sync --locked --group dev --group notebooks --extra gui
uv run --locked python scripts/verify.py
uv run --locked --group notebooks jupyter lab docs/examples
```

Imports, construction, configuration checks and software verification open no
instrument. Start with the notebooks for the fixed Ethernet setup, or load an
explicit TOML configuration with the [Python API](docs/python-api.md):

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("shutters.local.toml") as hub:
    hub.connect("shutter")
    status = hub.get_status("shutter")
    print(status.feedback.operating_mode, status.feedback.electrical_state)
```

`get_status()` requests fresh identity, mode, interlock requirement and status
bits. Output bit0 means enabled=1/disabled=0. It never infers Active/Inactive or
optical blade position from that bit. The ambiguous legacy scalar reply is an
explicit separate diagnostic, `get_solenoid_state_reply()`.

For the CLI, copy [the fictional config](config/shutters.example.toml) to ignored
shutters.local.toml and supply the exact identities/routes. Omit policy for reads.

```powershell
uv run --locked shutter-control --config shutters.local.toml check-config
uv run --locked shutter-control --config shutters.local.toml --target shutter identify
uv run --locked shutter-control --config shutters.local.toml --target shutter status
uv run --locked shutter-control --config shutters.local.toml gui --port 9857
```

The GUI binds only localhost; the example selects port 9857 (default 8050).
Use an explicit free port when another application is running; there is no
automatic fallback or takeover. Connect verifies identity and reads fresh mode,
interlock configuration and electrical output. Fresh OFF starts the configured
rest interval, so ON does not need a preliminary failed click. Qualified D2XX and docked
KEH3 Manual ON/OFF and host holds use the same owner and reviewed load policy.
The [modern minimalist panel](docs/gui.md) provides four mode selectors,
Open/Close or Start/Stop, timing readout, cycle settings and Identify through our
APT driver/shared owner. Kinesis is a visual reference only: no SDK is used.
White surfaces, slate typography, a restrained teal accent and flat controls
provide a consistent desktop/phone layout with clearly separated control groups.
Real mode transitions require the explicit source-protection assertion and
separate persistent-mode permission. The selected SH05R configuration stays
Manual-only, with device settings and EEPROM writes disabled by default.
Display/trigger-I/O settings remain visibly unavailable pending a verified
KSC101 wire contract; Key/Ready feedback stays Unknown.
Context exit/close release communication; explicit output cleanup is separate.
GUI shutdown sends OFF only for targets with prior output or mode attempts;
read-only faults remain visible without incidental actuation. Every GUI control
requires an exact selected target.

The separate DiamondGUI checkout currently fails its page integration tests
because its shutter page is commented out and its route metadata is stale.
See [the integration findings](docs/diamondgui.md) before deploying there.

Optional USB extras are `--extra d2xx` or `--extra vcp`; both retain FTDI driver
dependence. `shutter-control discover` lists D2XX metadata; `discover --vcp` lists
COM metadata. Neither selects a controller. Replacing Kinesis does not establish
a fix for Windows driver crashes. No driver/security changes are part of this package.

See [API and commands](docs/python-api.md), [protocol traceability](docs/INTERFACE.md),
[manufacturer sources](docs/sources.md), [local manuals and APT protocol PDFs](docs/manuals/README.md),
[architecture](docs/architecture.md),
[setup](docs/getting-started.md), [routes](docs/hardware.md),
[physical acceptance](docs/HARDWARE_VALIDATION.md), [cutover](docs/cutover.md),
[DiamondGUI integration](docs/diamondgui.md), [state](STATE.md) and [report](outputs/REPORT.md).

For the real SH05R at192.168.1.19:40305, use the reviewed
[Ethernet configuration](config/shutter.ethernet.toml). With the source protected,
triggers isolated and Manual already selected:

```powershell
uv run --locked shutter-control --config config/shutter.ethernet.toml --target shutter status
uv run --locked shutter-control --config config/shutter.ethernet.toml --target shutter pulse --seconds 1
uv run --locked shutter-control --config config/shutter.ethernet.toml --target shutter safe-off
```

The pulse command explicitly prepares OFF, waits the configured2s pause, then
runs ON/hold/OFF. For a protected Trigger->Manual transition use
manual --source-inhibited; this sends OFF before selecting remembered Manual.
Minimum OFF rest starts with electrical OFF readback. Host holds and rest periods
are not calibrated optical timings.
See [the real ON/OFF notebook](docs/examples/06_on_off.ipynb) and
[actual hardware result](records/ethernet-control-live.json). The test left Manual/OFF.

The revised panel's browser review was disconnected and issued no device command.
Native mode/settings behavior has software-only coverage; earlier physical
Manual-cycle evidence does not qualify the new functions. See the
[feature/validation matrix](docs/gui.md#manufacturer-reference-and-implemented-functions).

The [migration guide](docs/cutover.md) lists retired entry points and their
replacements. The verification command checks source and an isolated installed
wheel without lab access, removes its successful temporary environment and keeps
failed-run diagnostics under ignored tmp/. Static notebook verification is
separate and never executes device cells:

```powershell
uv run --locked --group notebooks python scripts/verify_notebooks.py
```

Actual browser testing on the selected SH05R verified ON/OFF, OFF-rest refusal and
release using the production TCP owner, with no simulator. See the
[WebUI procedure and evidence](docs/gui.md). To check the saved observations
without operating hardware:

```powershell
uv run --locked python scripts/verify_webui_evidence.py
```
