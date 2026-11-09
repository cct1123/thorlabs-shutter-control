# Direct KSC101 shutter control

One shared Python owner for the library, CLI, WebUI and six
[Ethernet notebooks](docs/examples/README.md). Device actions use documented APT
messages directly. No Kinesis, pythonnet or Thorlabs SDK runtime is used;
Ethernet needs only the Python standard library.

The control core has three modules: controller (configuration, KSC101 commands,
ownership and policy), protocol (APT messages/deadlines) and transport (TCP/USB
routes and explicit inventory). Use package-level imports; the former config,
device and discovery modules are removed. Hub serial/firmware metadata is
optional when unknown; exact controller identity is still verified on connection.

Additional documented Python operations cover channel/bay/LED queries, guarded
LED settings, interlock enforcement, explicit update start/stop with raw events,
and explicit hardware disconnect. They use the same owner and deadlines; ordinary
connect/status/ON/OFF/release remains the normal path. Motor/MMI/trigger layouts
remain excluded. See the [API contracts](docs/python-api.md).

The reviewed setup is **shutter**, **SH05R**, KSC101 **68800777**, firmware
**1.0.7**, KEH3 middle bay **192.168.1.19:40305**. Application channel 0 is separate
from APT channel 1. Its tracked [configuration](config/shutter.ethernet.toml)
allows protected selection of Manual, Single, Auto and Triggered. Output activation
permits all four modes through `qualified_modes`. Native Start retains OFF/interlock
readback and cycle/load limits; continuous Triggered priming, cycle-setting
and EEPROM writes retain their separate restrictions.

From the repository root, install the GUI once with `uv sync --locked --extra gui`,
then run:

```powershell
uv run shutter-control gui
```

Open http://127.0.0.1:9860. The GUI defaults to
[config/shutter.ethernet.toml](config/shutter.ethernet.toml) and port 9860.
Use `--config PATH` before `gui`, or `gui --port PORT`, to override them.
Other CLI commands retain `shutters.local.toml` as their default configuration.
Startup is passive and localhost-only. Select an exact target, then Connect.
Stop/release the previous owner before restarting an updated WebUI and reload
the browser. There is no automatic port takeover, scan, fallback or ON replay.

WebUI Release refuses pending ON/Start under the same owner lock as communication
release. Queries reject stale replies across all queued receive chunks before
sending a request; a busy event stream consumes the existing deadline. APT still
cannot prove freshness for arbitrary delayed same-type replies.

Standalone launches show **Shutdown GUI server** in the heading. It exits through
normal output cleanup and communication release after accepted requests finish;
imported `create_app()` instances do not expose this button. Use Stop / OFF for
immediate output control. Restart the launcher to serve the GUI again.

## Operation

Connect verifies exact identity/firmware and the WebUI reads actual mode,
interlock requirement and electrical output. Read state gets fresh replies;
Live readback is opt-in. The modern flat panel provides mode selectors,
Open/Close or qualified Start/Stop, timing/count readout, Settings and Identify.
Healthy polling preserves operator messages. Persistent faults remain visible in
the main and Settings notices. Confirmed Stop/OFF and dated electrical feedback
stay visible alongside a retained fault. An explicit verified Stop/OFF now clears
the fault; reads and automatic failure cleanup do not.
Disconnected or undated feedback stays Unknown; electrical OFF does not prove
physical blade closure or clear a fault. A healthy refused command preserves the
last same-connection dated feedback with its original timestamp and an explicit
historical-reading notice; a fault, disconnect or different connection clears it.

Settings also offers LED indication reads/applies and **Require interlock**.
Readback and diagnostics contains channel/bay queries, device-message start/stop,
raw event collection. Protected hardware disconnect remains API-only. All use the shared owner;
settings permissions still apply. See the [GUI command guide](docs/gui.md#additional-shutter-commands).
The legacy bay query is refused on KEH3 before I/O; the actual route timed out
on that request. Use the explicitly configured bay and endpoint.

The tracked SH05R Ethernet profile sets `min_off_s = 0.0`, removing the extra
software OFF pause. Fresh OFF and enabled-interlock readback remain required.
Profiles with a positive `min_off_s` retain their configured interval.
Every ON attempt invalidates the previous OFF-rest interval. New rest starts
with fresh OFF readback; it cannot be reused after an intervening ON. The 1 s
timed button is a host hold after ON readback, followed by OFF. Neither host
hold nor electrical timestamps are calibrated optical exposure.

Mode changes persist at power-up; selection has no separate permission flag or
source-confirmation requirement. OFF/interlock/readback checks remain.
The source-confirmation checkbox is removed for native activation and settings;
their separate policy, OFF/interlock and readback checks remain. Display
and trigger-I/O configuration remains unavailable pending a verified KSC101 wire layout.
The status panel reads the documented interlock/channel flags as Set/Clear;
these are not verified key position or readiness. Native request shows host
Start tracking, not measured activity. See the
[function and qualification matrix](docs/gui.md#manufacturer-reference-and-implemented-functions).

Settings drafts, persistence opt-in and polling are
scoped to a target/connection generation. Disconnect or reconnect clears old
state; ordinary polling preserves active edits. Settings writes check timing,
count/duty limits, exact readback and retained interlock configuration.
Read LED modes fills the indication checkboxes; other reads preserve local edits.
Editing a draft writes nothing until Apply is explicitly requested and permitted.

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("config/shutter.ethernet.toml") as hub:
    hub.connect("shutter")
    status = hub.get_status("shutter")
    print(status.operating_mode, status.electrical_state)
```

Construction/configuration checks open no device; `connect()` above does.
Context exit and `close()` release communication without output commands.
Explicit OFF is separate. Shutdown cleanup follows unresolved/current output
work, while a successfully closed output session cannot authorize an OFF in a
later read-only connection. Uncertain output retains its journal across release;
protected recovery checks Manual/OFF/interlock and clears stale requests without
replaying commands. Recovery requires independent source protection and a closed
blade observation. Empty-text exceptions retain their exception name and lockout
until verified explicit Stop/OFF or protected recovery. Neither reset establishes
optical closure. See the [API/recovery contract](docs/python-api.md).

An omitted load policy permits reads only. Qualified output is supported on
D2XX and docked KEH3 routes; VCP and KEH3 external USB OUT output control remain
unavailable. Optional USB extras retain FTDI driver dependencies. Informational
`discover`/`discover --vcp` never selects an instrument. No driver/security
change or Windows crash fix is implied by this package.

## Validation and migration

```powershell
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix review-
uv run --locked python scripts/verify_webui_evidence.py records/webui-modern-hardware-live.json
```

Verification checks source and an isolated installed wheel, locked dependencies,
exact Python/CSS parity and zero failed/skipped/uncollected required tests.
Frozen real-observation fixtures participate in input hashes. `--test-path`
selects an explicit subset; `--record-prefix` preserves previous campaigns.
Software tests include protocol fixtures and localhost loopback; they establish
no new bench result. The same suite checks notebook schema, syntax, links and
passive setup without executing hardware cells. To run just those checks, use
`uv run --locked --group dev pytest tests/test_tutorial_notebooks.py`. Successful
disposable verification environments are removed; inspect failed-run diagnostics
before pruning. Environments, manuals, actual records, backups and ownership
state are retained.

Latest software results: [source and isolated-wheel verification](records/repo-review-final-direct-validation.json).
The [8 November bounded actual WebUI redo](records/webui-redo-bounded-validation.json)
completed one approved 1 s host-held pulse, LED/cycle/channel reads, draft checks
and safe KEH3 bay-query refusal. Final readback was Manual/OFF, interlock required,
no fault; communication was released and the server stopped with no journal left.
Its [browser record](records/webui-redo-bounded-live.json) and
[final OFF screenshot](records/webui-redo-bounded-final-off.jpg) apply to that exact
recorded runtime. Independent blade motion was unobserved, and optical timing,
extinction, native modes/settings and wider deployment remain unqualified.
That one-cycle allowance is consumed; the record does not authorize another run.

No SDK backend or retired probe/notebook wrapper remains. Owner method names
have been narrowed; version 2 intentionally replaces nested feedback and redundant
status fields with a flat ShutterStatus. External consumers need the
[status migration](docs/python-api.md#status-schema-migration) before upgrading. The last recorded
external DiamondGUI check (E185) failed its commented-out page/stale mapping;
its restoration and live deployment are separate. Use the
[migration guide](docs/cutover.md), [current state](STATE.md) and
[review report](outputs/REPORT.md) before deploying.

Reference: [GUI procedure](docs/gui.md), [protocol](docs/INTERFACE.md),
[sources/manuals](docs/manuals/README.md), [architecture](docs/architecture.md),
[setup](docs/getting-started.md), [routes](docs/hardware.md),
[physical acceptance](docs/HARDWARE_VALIDATION.md),
[external integration](docs/diamondgui.md).
