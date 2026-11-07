# Local GUI

```powershell
uv sync --locked --extra gui
uv run --locked shutter-control --config config/shutter.ethernet.toml gui --port 9857
```

Open http://127.0.0.1:9857. The default port remains 8050; use `gui --port PORT`
to select a free port explicitly. The app never takes over an existing listener
or silently switches ports. Startup is passive and local-only. Select an exact configured
name, then explicitly Connect. Connect verifies identity and reads fresh mode,
interlock configuration and output feedback. Every control, including Release, requires that
exact selection; an empty selection never releases all routes. Read state obtains controller replies; no background
polling is started until **Live readback** is explicitly enabled. Mode selection,
Open/Start, priority Close/Stop and passive Release are separate controls. An omitted
qualification policy blocks output/mode/settings writes. Identify flashes LEDs only.
The Manual control states that mode changes are remembered at power-up. A real
transition requires separate `allow_persistent_mode_changes` policy permission;
an already Manual/OFF state is queried without a mode write.
Every real mode transition also requires the **Source independently blocked;
external triggers isolated** assertion. It is an operator condition, not a sensor.
An already selected mode can be queried without a write. Qualified D2XX and docked KEH3
output commands otherwise share the same owner; VCP/external USB OUT remain unavailable.

The page displays the full structured result, including requested electrical
state, dated controller feedback, fault/cleanup details and human optical evidence.
Unknown optical state stays unknown. Buttons are explicit commands; no toggle is
computed from a cached state. OFF can interrupt an active query/hold through the
same shared owner. Native driver blocking still requires independent protection.
After a partial/unknown-count write, the owner refuses further frames, including
OFF, because transmit alignment is unknown. The GUI reports the failed cleanup;
use independent source protection and the explicit protected recovery procedure.

Fresh OFF readback starts the configured minimum OFF interval. An ON request
before it expires is refused with the remaining wait and an explicit message
that ON was not dispatched. An observed ON invalidates the previous OFF interval.
Wait the full interval after OFF; no automatic delay or repeated ON command occurs.
The explicit **1-second ON, then OFF** button uses the existing owner pulse with
a 1 s host hold after ON readback and automatic priority OFF/readback. It requires
the same Manual/load/interlock/OFF-rest prerequisites; the browser does not time
the hold. Use it only within the approved physical window and cycle count.

## Repeating the protected user-flow check

Use only the exact approved controller/load and present source/trigger/interlock
conditions. The tracked configuration is not authorization for a new physical run.

1. Select shutter and click Connect. Expect serial 68800777, firmware 1.0.7,
   endpoint 192.168.1.19:40305 and actual mode/output. Establish Manual/OFF within
   the approved procedure before continuing; checking a UI box is not physical authority.
2. Wait at least the configured 2 s OFF rest, then click Open / ON once. Inspect
   fresh electrical ON and status bit 0 set. Click Close / OFF promptly
   within the approved hold window; inspect fresh electrical OFF and bit 0 clear.
3. An immediate ON during the OFF interval must be refused. Read state must still
   show OFF without a new fault. Do not repeat cycles to obtain missing observations.
4. After confirmed OFF, Release communication. A subsequent Read state reports
   disconnected/has_device=false, with no claim of continuing electrical feedback.
5. Stop this test server after releasing. Browser-tab closure alone does not stop it.

## Actual browser evidence, 6 November 2026

The user confirmed the unchanged protected SH05R setup. E188/E189 record actual
visible browser controls, production ShutterHub/TCP, two short ON/OFF cycles total
(one baseline, one after fixes), and final Manual/OFF followed by release. The
baseline exposed occupied port 8050 and a first-ON rest-timer bug. The corrected
Connect/read/rest/first-ON/OFF path passed, as did immediate-ON refusal with
"wait 1.66 s; ON was not dispatched" and fresh OFF readback afterward.
No simulator, injected transport or direct callback substitute was used.
Controller output readback does not establish independent blade motion or optics.
In the separately requested single1s cycle E191, the user subsequently confirmed
"Yes, it opened and returned closed" (E192). This establishes qualitative human
observation for that exact cycle, not calibrated optical timing or extinction.

See [baseline browser observations](../records/webui-baseline-live.json),
[corrected browser observations](../records/webui-final-live.json) and
[final OFF screenshot](../records/webui-final-off.jpg). The saved-evidence checker:

```powershell
uv run --locked python scripts/verify_webui_evidence.py
```

It checks the saved record's consistency without connecting, clicking or creating
new physical evidence. Ordinary source verification also checks the passive
`gui --help` interface, including the explicit port option.

Terminal Ctrl+C attempts each applicable qualified target's OFF separately, then
releases communication even if cleanup fails. A session with no prior output or
mode attempt receives no incidental OFF, even when a write policy is configured.
A read-only fault is reported and retained without sending an output command.
Browser-tab closure
does not terminate the server or establish closure. Process failure cannot run
cleanup reliably; the persistent uncertainty marker prevents a new process from
silently restoring ON.

## Manufacturer reference and implemented functions

The user's supplied ETN017648-D03 URL returned the unchanged
[HA0368T Rev F September 2026 manual](manuals/KSC101_Kinesis_UI_Manual_HA0368T_Rev_F.pdf),
41 pages. Sections 6.2-6.3 (printed pp28-33) and the supplied screenshot define
the visual/function reference. They do not authorize running Kinesis. Every
device action routes WebUI -> ShutterHub -> KSC101 -> APT Session -> transport.
Opening Settings, selecting a configured target and editing draft fields are local.

| Panel function | Implementation and limit | New validation |
| --- | --- | --- |
| Four named modes | APT 0x04C0/C1/C2; Manual=1, Single=2, Auto=3, Triggered=4. Only policy-qualified modes selectable; changes persist at power-up | Software frame/owner checks; native modes not bench-qualified |
| Open/Close, Start/Stop | 0x04CB ON=1/OFF=2; labels follow actual mode. Manual retains its existing owner checks. Native Start reads cycle parameters and sends ON once; Stop sends OFF without changing mode | Software guard/dispatch/stop checks; no new actuation |
| On/Off duration, cycles | Explicit Read device settings, 0x04C4/C5; no guessed device defaults | Software literal payload and callback checks |
| Cycle settings | 0x04C3, channel1 + uint32 On ms/Off ms/count; 100..10000 ms, count0..1000000. Count0 requires explicit Continuous permission; load rest/count limits also apply | Software validation/readback mismatch/cleanup checks |
| Store cycle settings | Separately permitted 0x04B9 with channel1/message0x04C3. Fresh RAM readback is checked; there is no EEPROM ACK | Software frames only; persistence requires protected restart/readback qualification |
| Identify | 0x0223 channel1, flash request; no output command or flash ACK | Literal frame and no-output-cleanup software checks |
| Key Enabled / Is Ready | Unknown; no verified KSC101 wire mapping. Interlock requirement is configuration, not continuity | Unknown-state renderer checks |
| Error / Output ON / Activity | Fault report, electrical bit0, and explicitly labelled Start requested. Never infer blade position or native activity/completion from OFF | Software renderer checks; earlier physical evidence only for its original Manual revision |
| Display intensity/dimming/timeout | Visible disabled controls; no device read/write | Blocked on KSC101-specific APT layout |
| Trigger1/2 I/O mode/polarity | Visible disabled controls; no device read/write. Triggered start is only level-mode priming with count0 and separate permission | Configuration blocked on KSC101-specific APT layout; priming software-only |

APT Issue42.1 lists 0x0520 MMI / 0x0523 trigger messages for KSC101 in its model
table, but the detailed sections describe motor controllers, motor positions and
conflicting lengths. Those layouts are not safe evidence for KSC101 settings.
See [SRC-010 and the protocol gaps](sources.md#src-010---ksc101-kinesis-ui-manual-6-november-2026).
KSC-specific level-trigger behavior takes precedence over generic solenoid-cycle
prose. There is no guessed trigger implementation or hidden SDK fallback.

New optional Policy fields default to `qualified_modes=("manual",)`,
`allow_device_settings=False`, `allow_persistent_settings=False`,
`allow_continuous_cycles=False`, `max_cycle_count=1`. These are conservative
software permissions, not load ratings. TOML uses `qualified_modes=["manual"]`.
Adding modes or write permissions requires separate deployment qualification;
the real Ethernet configuration was not broadened. Finite exposure/duty loads
still require an independently qualified cutoff and remain unavailable for Start.
Settings apply requires Manual/OFF, preserved interlock requirement, source
assertion, explicit permissions and exact readback. Opening the panel writes nothing.

Native Single can finish before a status reply. Native Auto may be in its OFF
interval while active. Start therefore remains a request requiring explicit Stop
before Release or another Start, even when the latest output sample is OFF.
Activity remains Unknown, with an amber request indicator; Stop's electrical
OFF is not a measured optical state or independent native-inactivity signal.

The new panel was reviewed disconnected at 1100px desktop and 390px phone widths;
the selector grid and scrolling Settings header were corrected. No browser
warning/error was observed and no hardware Connect/Identify/write was clicked.
[Desktop panel](../records/webui-apt-panel-desktop.png),
[settings](../records/webui-apt-settings-desktop.png),
[phone panel](../records/webui-apt-panel-phone.png).
TEST-225 software/packaging evidence is separate from TEST-224's earlier actual
hardware runs. The new panel and native operations have no new physical PASS.
