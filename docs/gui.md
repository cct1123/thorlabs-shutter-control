# Local GUI

The current panel uses a modern minimalist style: white surfaces, slate text,
a restrained teal accent, flat controls, subtle borders and consistent spacing.
Operating mode, Output control and Controller status have explicit section
headings. The manufacturer GUI defines functional references, not the current
visual skin. Supported APT controls are retained. The controller-status rows use literal
Interlock flag/Channel flag (Set/Clear), Software fault, Output ON and Native
request labels. Key/Ready and actual native activity remain explicitly undecoded;
the documented flags must not be relabelled as physical switch/readiness states.
Connected controls delegate route, qualification and settings permissions to
ShutterHub; a disallowed request reports its refusal in the notice. Button
availability does not indicate permission or physical qualification. Display and
trigger-configuration placeholders have been removed; neither function has a
verified KSC101 APT layout. Cycle inputs use the shared CycleParameters validator.

```powershell
uv sync --locked --extra gui
uv run shutter-control gui
```

Run from the repository root and open http://127.0.0.1:9860. The GUI loads
`config/shutter.ethernet.toml` by default; use `--config PATH` before `gui` to
select another file, or `gui --port PORT` for another port. Other CLI commands
keep `shutters.local.toml` as their default. The app never takes over an existing listener
or silently switches ports. Startup is passive and local-only. Select an exact configured
name, then explicitly Connect. Connect verifies identity and reads fresh mode,
interlock configuration and output feedback. Every control, including Release, requires that
exact selection; an empty selection never releases all routes. Read state obtains controller replies; no background
polling is started until **Live readback** is explicitly enabled. Mode selection,
Open/Start, priority Close/Stop and passive Release are separate controls. An omitted
qualification policy blocks output/mode/settings writes. Identify flashes LEDs only.
Release checks pending ON/Start requests under the owner's lock, so a concurrent
callback cannot start output between this check and communication release.
Successful background polls refresh data without erasing the last command or
refusal message. An explicit Read state still displays its own result.
An explicit **Stop / OFF** clears a retained software fault after identity,
OFF command/readback and preserved-interlock verification. Automatic cleanup
and ordinary polling retain faults. A failed OFF/readback keeps the fault and
journal; no optical closure is inferred. If the old session cannot communicate,
Release, Connect, then Stop / OFF using the new owner. Startup never clears faults.
Connected, dated electrical feedback remains visible even when a fault is latched.
Disconnect or a new connection clears settings drafts, persistence opt-in and
polling selection; ordinary polling preserves edits on the same connection.
Mode changes are remembered at power-up. Selection needs no separate
persistent-mode permission or source-confirmation checkbox. An already selected
mode is read without a write. Actual transitions still require fresh OFF and an
enabled interlock requirement, send OFF/deactivate and verify it, then verify the
requested mode/OFF/interlock. `allow_persistent_mode_changes` is legacy-only.
The source checkbox has been removed. Native Start and settings writes no longer
require that software assertion; their load, interlock/OFF, settings and EEPROM
permissions remain. Legacy boolean source_inhibited arguments are accepted.
Triggered priming still requires its separate continuous-cycle permission/count.
Hardware disconnect is API-only and retains its separate source assertion.
Ordinary Release remains available and does not send a bus command.
Restart a released GUI owner and reload the browser to load this change; opening
the GUI or restarting it does not connect or select a device mode.

The page displays the full structured result, including requested electrical
state, dated controller feedback, fault/cleanup details and human optical evidence.
Unknown optical state stays unknown. A healthy pre-dispatch refusal retains the
previous same-connection dated feedback and its original timestamp, explicitly
labelled as historical; faults, disconnects and new connections do not reuse it.
Buttons are explicit commands; no toggle is
computed from a cached state. OFF can interrupt an active query/hold through the
same shared owner. Native driver blocking still requires independent protection.
After a partial/unknown-count write, the owner refuses further frames, including
OFF, because transmit alignment is unknown. The GUI reports the failed cleanup;
use independent source protection and the explicit protected recovery procedure.

The tracked SH05R Ethernet profile uses `min_off_s = 0.0`: no extra software
OFF pause. Fresh OFF/interlock readback remains required. For profiles with a
positive minimum, fresh OFF readback starts the configured minimum OFF interval. An ON request
before it expires is refused with the remaining wait and an explicit message
that ON was not dispatched. An observed ON invalidates the previous OFF interval.
Wait the full interval after OFF; no automatic delay or repeated ON command occurs.
The explicit **1-second ON, then OFF** button uses the existing owner pulse with
a 1 s host hold after ON readback and automatic priority OFF/readback. It requires
the same Manual/load/interlock/OFF-rest prerequisites; the browser does not time
the hold. Use it only within the approved physical window and cycle count.
The timed button is disabled when the displayed electrical output is ON;
the owner independently checks fresh Manual/OFF before dispatch.

## Standalone server shutdown

The standalone launchers (`uv run shutter-control gui` and
`uv run python -m thorlabs_shutter_control gui`) show **Shutdown GUI server** in the
heading. Clicking it stops the localhost listener after accepted requests finish,
then runs output cleanup and releases communication before returning to the
terminal. Pending commands can delay exit; this button is not an emergency Stop.
Cleanup failures are reported in the terminal and cause an unsuccessful exit.
The browser tab stays open with its shutdown acknowledgement; it is not proof of
optical closure. Restart the launcher to serve the GUI again.

Imported `create_app(hub)` instances have no shutdown button or callback. `run(hub)`
explicitly owns a standalone listener and supplies the shutdown callback; it never
kills another server/process or uses a forced process exit. The launcher stays
bound to 127.0.0.1 with threaded callbacks and no development reloader.

## Additional shutter commands

The main output controls are unchanged. Open **Settings** for LED indications
and interlock configuration; expand **Readback and diagnostics** for the less
frequent commands. Opening either section or editing fields makes no device request.

| Control | Shared ShutterHub API | Result / use |
| --- | --- | --- |
| Read LED modes | get_led_modes | Shows the raw mask and fills the three documented indication checkboxes |
| Apply LED modes | set_led_modes | Replaces the mask with the selected flags; checks RAM readback, without an EEPROM request |
| Require interlock | require_interlock | Confirms or enables the requirement; never disables it or measures contact continuity |
| Read channel enable | get_channel_enabled | Last explicit enable read; separate from electrical output and blade position |
| Read raw bay | get_hub_bay_reply | Raw legacy byte on other routes; KEH3 is refused before I/O, without faulting the owner; configured routing stays unchanged |
| Start / Stop device messages | start_updates / stop_updates | Explicit requests without acknowledgement; separate from Live readback |
| Collect raw events | get_events | Consumes the bounded raw event queue; shows message IDs and complete frame hex without decoding motor payloads |

LED Apply and Require interlock use the existing device-settings permission and
Manual/OFF/interlock checks. No software source confirmation is required. The tracked Ethernet
profile keeps device-settings writes disabled. Settings results and refusals are
visible inside the dialog as well as on the main panel.

Read LED modes before editing the flags. An unfamiliar returned bit is reported;
Apply replaces the entire mask with the three documented selections. Polling and
other diagnostics preserve LED drafts. Extra readouts and drafts are scoped to
the selected target and owner connection, and clear when that scope becomes
invalid. Readouts are labelled as last explicit reads, not continuous measurements.

Stop device messages before Release. They do not create a background reader or
prove native activity. **Release** closes communication without a hardware
disconnect request. Protected hardware disconnect is available through the Python API only.
Normal ON/OFF uses the existing output buttons, with no second enable alias.
Key/Ready, optical position and ambiguous trigger/MMI layouts remain unavailable.

TEST-250 checks these callbacks against the shared owner with software transport
fixtures. A passive localhost preview was inspected disconnected at 1280 x 720
and 390 x 844, including scrolling Settings and Diagnostics; no browser warnings,
errors or horizontal overflow were observed. No hardware command was clicked.
[Settings preview](../records/gui-commands-settings-desktop.jpg),
[diagnostics preview](../records/gui-commands-diagnostics-desktop.jpg),
[phone settings](../records/gui-commands-settings-phone.jpg),
[phone diagnostics](../records/gui-commands-diagnostics-phone.jpg).
This is layout/software evidence, not physical command qualification.

## Bounded actual redo, 8 November 2026

E239 / TEST-255 completed the current visible-browser procedure after fresh
user confirmation of source protection, trigger isolation, intact key/interlock
and initially closed blade. Passive protected recovery cleared the prior fault
without an output command. Exactly one approved1s Manual pulse completed, followed
by final protective OFF and healthy Manual/OFF/interlock readback at
2026-11-09T03:34:39.878424 UTC. Communication was released and the test server
stopped; no active connection or journal remained. The allowance is consumed.

LED0x0001 correctly selected Identify; an unapplied local draft survived another
read, and explicit LED read restored the actual flags. Cycle settings remained
2000/2000ms/count5, channel read Disabled and raw events returned0. The legacy
bay query was refused without latching a fault; a subsequent Read state worked.
Live readback preserved the OFF confirmation. Release cleared old feedback/drafts,
and post-release Read state reported that no device feedback was requested.
No mode/timing/LED/EEPROM settings changes or extra pulse were sent.

The exact runtime matches354 source +354 installed-wheel passing tests. Camera
view was No/unsure and unused; independent blade motion/timing is unobserved.
[Actual browser record](../records/webui-redo-bounded-live.json),
[validation](../records/webui-redo-bounded-validation.json),
[healthy final OFF](../records/webui-redo-bounded-final-off.jpg).
Earlier observations below describe their own revisions and outcomes.

## Actual command debugging, 8 November 2026

TEST-252 used visible browser controls with the production owner and actual
KSC10168800777 / firmware1.0.7 / SH05R /192.168.1.19:40305. The user confirmed
independent beam blocking, trigger isolation, intact key/interlock and initially
closed blade, and approved protected passive recovery plus exactly one1s pulse.
The prior killed owner had left a persistent cleanup lockout. Documented recovery
verified Manual/OFF/interlock without an output command, then a fresh GUI owner
connected normally. The one pulse completed with electrical OFF readback. Its
routine checks electrical ON before the1s host hold and OFF afterward; this is
not a calibrated optical timing measurement. No additional ON was requested.

Cycle reads returned2000ms ON /2000ms OFF /count5; LED mask0x0001 and channel
enable Disabled were read. No mode, timing, LED or EEPROM settings were changed.
The actual raw bay query timed out and latched a fault. After releasing that
receive session, the GUI reconnected, sent final protective OFF and verified
Manual/OFF/interlock at2026-11-09T00:07:18.604417 UTC, then released. The fault
journal remains; the test server is stopped. Update start/stop, hardware
disconnect and settings writes were not exercised in this bounded run.

The run found three software issues: faulted samples could display generic
success messages; simultaneous status/detail updates left the LED checklist
stale; and the legacy bay query was exposed on an unqualified KEH3 route.
The historical fixes retained fault notices even during polling, inspect all changed callback
inputs when updating LED drafts, and reject the KEH3 bay query in ShutterHub
before any I/O. Regressions cover each; the final LED/route changes have software
validation, with no repeated hardware pulse or post-fix live recovery.

The user did not observe the pulse. No independent blade-position/optical signal
is exposed through this owner, so actual blade motion remains unobserved. Do not
clear the retained fault from electrical OFF alone in that revision: protected recovery then
requires an independently confirmed closed blade and source protection.
[Raw browser observations](../records/webui-command-hardware-live.json),
[passive recovery](../records/webui-command-hardware-recovery.json),
[released fault screenshot](../records/webui-command-hardware-final-released.jpg).

## Repeating the protected user-flow check

Use only the exact approved controller/load and present source/trigger/interlock
conditions. The tracked configuration is not authorization for a new physical run.

1. Select shutter and click Connect. Expect serial 68800777, firmware 1.0.7,
   endpoint 192.168.1.19:40305 and actual mode/output. Establish Manual/OFF within
   the approved procedure before continuing; checking a UI box is not physical authority.
2. After fresh Manual/OFF/interlock readback, click Open / ON once. The current
   profile adds no software OFF pause. Inspect
   fresh electrical ON and status bit 0 set. Click Close / OFF promptly
   within the approved hold window; inspect fresh electrical OFF and bit 0 clear.
3. No extra wait is required by the current profile after confirmed OFF. A custom
   profile with positive min_off_s still refuses premature ON. Do not add cycles
   outside the approved procedure to obtain missing observations.
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
Shutdown also reports a retained output fault after successful OFF; only an
explicit verified Stop/OFF or protected recovery clears that fault.
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
| Four named modes | APT 0x04C0/C1/C2; Manual=1, Single=2, Auto=3, Triggered=4. Selection of all four needs no separate mode permission; changes persist at power-up. Output qualification is separate | Software frame/owner checks; native modes not bench-qualified |
| Open/Close, Start/Stop | 0x04CB ON=1/OFF=2; labels follow actual mode. Manual retains its existing owner checks. Native Start reads cycle parameters and sends ON once; Stop sends OFF without changing mode | Software guard/dispatch/stop checks; no new actuation |
| On/Off duration, cycles | Explicit Read device settings, 0x04C4/C5; no guessed device defaults | Software literal payload and callback checks |
| Cycle settings | 0x04C3, channel1 + uint32 On ms/Off ms/count; 100..10000 ms, count0..1000000. Count0 requires explicit Continuous permission; load rest/count limits also apply | Software validation/readback mismatch/cleanup checks |
| Store cycle settings | Separately permitted 0x04B9 with channel1/message0x04C3. Fresh RAM readback is checked; there is no EEPROM ACK | Software frames only; persistence requires protected restart/readback qualification |
| Identify | 0x0223 channel1, flash request; no output command or flash ACK | Literal frame and no-output-cleanup software checks |
| Interlock flag / Channel flag | Decoded from fresh status0x042A masks0x1000/0x80000000 (SRC-008); Set/Clear with the sample timestamp. Neither is labelled key position/readiness | Literal-mask/readback/GUI software checks; physical flag semantics unvalidated |
| Software fault / Output ON / Native request | Owner fault report, electrical bit0, and host Start requested/No pending request. No native activity/completion or blade inference | Software renderer checks; prior physical evidence only for its recorded Manual revision |
| Vendor Key Enabled / Is Ready / actual Active | Not reproduced: public API/manual names exist, but verified raw mappings are missing/conflicting. Panel explicitly states these are not decoded | Manufacturer raw-wire mapping or independent passive trace required |
| Display intensity/dimming/timeout | Unimplemented; no placeholder controls or device read/write | Blocked on KSC101-specific APT layout |
| Trigger1/2 I/O mode/polarity | Unimplemented; no placeholder controls or device read/write. Triggered start is only level-mode priming with count0 and separate permission | Configuration blocked on KSC101-specific APT layout; priming software-only |

APT Issue42.1 lists 0x0520 MMI / 0x0523 trigger messages for KSC101 in its model
table, but the detailed sections describe motor controllers, motor positions and
conflicting lengths. Those layouts are not safe evidence for KSC101 settings.
See [SRC-010 and the protocol gaps](sources.md#src-010---ksc101-kinesis-ui-manual-6-november-2026).
KSC-specific level-trigger behavior takes precedence over generic solenoid-cycle
prose. There is no guessed trigger implementation or hidden SDK fallback.

New optional Policy fields default to `qualified_modes=("manual",)`,
`allow_device_settings=False`, `allow_persistent_settings=False`,
`allow_continuous_cycles=False`, `max_cycle_count=1`. These are conservative
software permissions, not load ratings. A default custom policy uses
`qualified_modes=["manual"]`; the tracked SH05R profile lists all four modes.
Adding output modes to `qualified_modes` requires separate deployment qualification;
`allow_persistent_mode_changes` is accepted for compatibility but ignored by mode
selection; native Start/priming is checked separately. Device-settings permissions require their own review;
the real Ethernet profile lists all four activation modes. Finite exposure/duty loads
still require an independently qualified cutoff and remain unavailable for Start.
Settings apply requires Manual/OFF, preserved interlock requirement,
explicit permissions and exact readback. Opening the panel writes nothing.

Native Single can finish before a status reply. Native Auto may be in its OFF
interval while active. Start therefore remains a request requiring explicit Stop
before Release or another Start, even when the latest output sample is OFF.
The Native request indicator shows host Start requested (amber) or No pending
request; neither establishes actual native activity. Stop's electrical OFF is
not measured optical closure or an independent native-inactivity signal.

The new panel was reviewed disconnected at 1100px desktop and 390px phone widths;
the selector grid and scrolling Settings header were corrected. No browser
warning/error was observed and no hardware Connect/Identify/write was clicked.
[Desktop panel](../records/webui-apt-panel-desktop.png),
[settings](../records/webui-apt-settings-desktop.png),
[phone panel](../records/webui-apt-panel-phone.png).
TEST-225 software/packaging evidence is separate from TEST-224's earlier actual
hardware runs. The new panel and native operations have no new physical PASS.

## Minimalist visual refinement

REQ-226 / TEST-226 supersedes the original manufacturer appearance. The current
skin removes red chrome, bevels, gradients and circular mechanical buttons;
selection uses a muted teal accent while unknown/error/requested states retain
their distinct text and indicators. System typography requires no external font
or network dependency. Controls include visible keyboard focus, readable disabled
states and reduced-motion support. Settings presents cycle controls in one
column; Stop/OFF remains in its sticky header while the content scrolls. Earlier
screenshots include the removed display/trigger placeholders and are historical
visual evidence.

The real app was reviewed disconnected at1100,768,390 and320px widths, with no
horizontal overflow. Phone Settings scrolling retained visible Stop/OFF and
Close controls. There were no browser console warnings/errors. No Connect,
Identify, output or device-settings action was used. The initial Read state
confirmed has_device=false/generation0 before restarting the owned preview.

[Historical desktop](../records/webui-modern-desktop.png),
[phone](../records/webui-modern-phone.png),
[Settings](../records/webui-modern-settings.png),
[scrolled phone Settings](../records/webui-modern-settings-phone.png).
The original TEST-225 screenshots above remain historical appearance evidence.
That revision's presentation/source/wheel validation is recorded separately in
[webui-modern-validation.json](../records/webui-modern-validation.json).

## Historical modern panel hardware test

REQ-227 / TEST-227, 6 November2026: real WebUI controls on localhost9860 used the
production owner/APT/TCP for SH05R/KSC10168800777, firmware1.0.7,
192.168.1.19:40305. No simulator, SDK or direct callback/API substitute was used
for this live test. Connect/read returned Manual/OFF0x2000, required interlock
configuration and no fault. Read device settings returned2000ms ON/2000ms OFF,
5cycles before and after the fix; no settings were written. Already-Manual
selection was a read-only no-op. Final fresh Manual/OFF was followed by Release
and Read confirming has_device=false and unknown electrical feedback.

The baseline demonstrated that live polling replaced the settings-command
notice with "Readback updated." The fix preserves the notice while electrical
timestamps advance; this passed on the real controller. Source review also
found the timed button remained available during displayed ON; it now requires
displayed OFF. A further actual released-Read check exposed a misleading
"Readback updated" message when no handle existed; it now states that the
controller is disconnected and no device feedback was requested.

The user confirmed the protected setup and up to two Manual cycles. Exactly two
were executed through visible controls on the final source: Open/Close returned
0x2001 ->0x2000 with0.748307s between readbacks, within the5s window. Release
while active was refused without dropping the owner or latching a fault; the
timed button was disabled during ON. After more than2s OFF, the1s timed button
completed and returned Manual/OFF. Final settings remained2000/2000ms/count5.
Final fresh Manual/OFF at2026-11-07T01:10:10.710233UTC was followed by Release
and Read showing disconnected/no handle/unknown feedback and the corrected
message. The protection checkbox was cleared locally after the window ended.
The two-cycle authority is consumed; no third ON, mode/settings/EEPROM or other
device action is authorized by it. This is PASS for the selected real operator
flow, not calibrated optical timing. In E202 the user reports "I did not observe
both cycles"; complete two-cycle independent blade motion remains unverified.

[Actual observations](../records/webui-modern-hardware-live.json),
[final actual OFF screenshot](../records/webui-modern-hardware-final-off.png),
[final released screenshot](../records/webui-modern-hardware-final-released.png).
The updated saved-evidence checker validates identity, unchanged settings,
polling-message preservation, release and (when present) bounded authorized
control cycles. Missing cycles produce PARTIAL and exit2; it never operates hardware.

```powershell
uv run --locked python scripts/verify_webui_evidence.py records/webui-modern-hardware-live.json --output records/webui-modern-hardware-evidence-validation.json
uv run --locked --group dev --extra gui python -B scripts/verify.py --test-path tests/test_webui_live_regressions.py --record-prefix webui-hardware-final-
```

The selected software path uses saved actual samples only, with no emulated
device/transport. The packaging script defaults to the full suite; selection is
explicit in the output's tested_paths. --record-prefix preserves prior campaigns.
Software callback checks are separate from live hardware acceptance.

The follow-up repository review adds stricter OFF-rest/lifecycle/interlock/duty
guards and connection-scoped GUI state. Restart the server and reload the browser
to load it. E200's physical results belong to its recorded pre-review source;
this review performs no new physical actuation or hardware qualification.
