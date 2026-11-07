# Direct KSC101 shutter control

One shared Python owner for the library, CLI, WebUI and six
[Ethernet notebooks](docs/examples/README.md). Device actions use documented APT
messages directly. No Kinesis, pythonnet or Thorlabs SDK runtime is used;
Ethernet needs only the Python standard library.

The reviewed setup is **shutter**, **SH05R**, KSC101 **68800777**, firmware
**1.0.7**, KEH3 middle bay **192.168.1.19:40305**. Application channel0 is separate
from APT channel1. Its tracked [configuration](config/shutter.ethernet.toml)
remains Manual-only with cycle-setting and EEPROM writes disabled.

```powershell
uv sync --locked --group dev --group notebooks --extra gui
uv run --locked shutter-control --config config/shutter.ethernet.toml check-config
uv run --locked shutter-control --config config/shutter.ethernet.toml gui --port 9860
```

Startup is passive and localhost-only. Select an exact target, then Connect.
Use a free port explicitly; default8050 may belong to another application.
Stop/release the previous owner before restarting an updated WebUI and reload
the browser. There is no automatic port takeover, scan, fallback or ON replay.

## Operation

Connect verifies exact identity/firmware and the WebUI reads actual mode,
interlock requirement and electrical output. Read state gets fresh replies;
Live readback is opt-in. The modern flat panel provides mode selectors,
Open/Close or qualified Start/Stop, timing/count readout, Settings and Identify.
Successful polling preserves operator messages. Disconnected feedback stays Unknown.

Every ON attempt invalidates the previous OFF-rest interval. New rest starts
with fresh OFF readback; it cannot be reused after an intervening ON. The1s
timed button is a host hold after ON readback, followed by OFF. Neither host
hold nor electrical timestamps are calibrated optical exposure.

Mode changes persist at power-up and need explicit qualification and source
protection. Native modes/settings have separate default-off permissions. Display
and trigger-I/O settings remain disabled pending a verified KSC101 wire layout;
Key/Ready and native activity are not inferred from the output bit. See the
[function and qualification matrix](docs/gui.md#manufacturer-reference-and-implemented-functions).

Settings drafts, protection assertions, persistence opt-in and polling are
scoped to a target/connection generation. Disconnect or reconnect clears old
state; ordinary polling preserves active edits. Settings writes check timing,
count/duty limits, exact readback and retained interlock configuration.

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("config/shutter.ethernet.toml") as hub:
    hub.connect("shutter")
    status = hub.get_status("shutter")
    print(status.feedback.operating_mode, status.feedback.electrical_state)
```

Construction/configuration checks open no device; `connect()` above does.
Context exit and `close()` release communication without output commands.
Explicit OFF is separate. Shutdown cleanup follows unresolved/current output
work, while a successfully closed output session cannot authorize an OFF in a
later read-only connection. Uncertain output retains its journal across release;
protected recovery checks Manual/OFF/interlock and clears stale requests without
replaying commands. See the [API/recovery contract](docs/python-api.md).

An omitted load policy permits reads only. Qualified output is supported on
D2XX and docked KEH3 routes; VCP and KEH3 external USB OUT output control remain
unavailable. Optional USB extras retain FTDI driver dependencies. Informational
`discover`/`discover --vcp` never selects an instrument. No driver/security
change or Windows crash fix is implied by this package.

## Validation and migration

```powershell
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix review-
uv run --locked --group notebooks python -B scripts/verify_notebooks.py
uv run --locked python scripts/verify_webui_evidence.py records/webui-modern-hardware-live.json
```

Verification checks source and an isolated installed wheel, locked dependencies,
exact Python/CSS parity and zero failed/skipped/uncollected required tests.
Frozen real-observation fixtures participate in input hashes. `--test-path`
selects an explicit subset; `--record-prefix` preserves previous campaigns.
Software tests include protocol fixtures and localhost loopback; they establish
no new bench result. Notebook checks never execute hardware cells. Successful
disposable verification environments are removed; inspect failed-run diagnostics
before pruning. Environments, manuals, actual records, backups and ownership
state are retained.

E200 records two real WebUI/controller cycles, active-release refusal and final
Manual/OFF followed by release. E202 reports that the user did not observe both
cycles, so complete two-cycle blade motion remains unverified. E191/E192 records
an earlier individually observed blade cycle. These are dated results on their
exact revisions; current software review does not repeat or extend them.

No SDK backend or retired probe/notebook wrapper remains. Existing DiamondGUI
owner method/status names are intentional public contracts. The last recorded
external DiamondGUI check (E185) failed its commented-out page/stale mapping;
its restoration and live deployment are separate. Use the
[migration guide](docs/cutover.md), [current state](STATE.md) and
[review report](outputs/REPORT.md) before deploying.

Reference: [GUI procedure](docs/gui.md), [protocol](docs/INTERFACE.md),
[sources/manuals](docs/manuals/README.md), [architecture](docs/architecture.md),
[setup](docs/getting-started.md), [routes](docs/hardware.md),
[physical acceptance](docs/HARDWARE_VALIDATION.md),
[external integration](docs/diamondgui.md).
