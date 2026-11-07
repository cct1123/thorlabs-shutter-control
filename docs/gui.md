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
polling is started. Manual selection, ON, priority OFF and passive Release are
separate controls. An omitted qualification policy blocks every write.
The Manual control states that mode changes are remembered at power-up. A real
transition requires separate `allow_persistent_mode_changes` policy permission;
an already Manual/OFF state is queried without a mode write.
Trigger->Manual also requires explicit source-protection confirmation, which this
GUI does not supply. Establish protection and use the Python API or CLI
`manual --source-inhibited` for that transition. Qualified D2XX and docked KEH3
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
   the approved procedure before continuing; the GUI cannot authorize Trigger exit.
2. Wait at least the configured 2 s OFF rest, then click Solenoid ON once. Inspect
   fresh electrical ON and status bit 0 set. Click Cancel / qualified OFF promptly
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
