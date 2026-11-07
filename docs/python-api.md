# Python API

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("shutters.local.toml") as hub:  # construction is passive
    connection = hub.connect("shutter")     # exact identity only, no enable
    print(connection.identity)              # model/serial/firmware/hardware/channels
    sample = hub.get_status("shutter")      # fresh electrical feedback
    print(sample.feedback.electrical_state)
```

The context closes communication on success or error. It preserves the original
exception and adds any cleanup failure; retain the owner if release fails. Closing
does not actuate OFF. Explicit connect/get_status/release is also supported.

| Method | Effect |
| --- | --- |
| connect(target) | Open exact route, claim serial/endpoint, verify identity |
| identify_device(target) | Request and verify identity again; no flashing/identify command |
| blink_identify(target) | APT identify LED-flash request only; no flash acknowledgement or shutter output |
| get_status(target) | Request identity, mode, interlock requirement and fresh status bits |
| get_cycle_parameters(target) | Explicit APT cycle read; returns dated cycle_parameters in ShutterStatus |
| get_solenoid_state_reply(target) | Explicit raw 0x04CD byte, without output/operating-state interpretation |
| connection_snapshot(target) | Host metadata only; no hardware polling |
| disconnect(target=None), close() | Release communication; no output command |

Names or configured integer application channels are accepted. APT channel is
always1. KEH3 and VCP connections support queries. Docked KEH3 and D2XX writes
use the same load policy and controller checks; VCP and KEH3 external USB OUT
control are refused before command dispatch, even with an injected transport.
Hub identity is unverified by a child-controller reply. SDK caches/polling are not used.
The former candidate-probe/analyzer module and CLI commands were removed; use
connect/identify/status for the same exact target through this owner.

Run scripts with uv run --locked python your_script.py. The CLI commands are
check-config, discover [--vcp], identify, status, manual, safe-off, pulse --seconds,
and gui. Reads accept a configured Ethernet route; manual/safe-off/pulse require
the reviewed D2XX or docked-KEH3 load policy below. Imports/help/check-config are passive.
For a protected Trigger->Manual transition, use manual --source-inhibited; this
is an operator assertion of established source/trigger isolation, not a sensor reading.

After physical qualification and within the approved operating window, a balanced
host hold on a continuous-duty load looks like this (not executed by verification):

```python
import time

with ShutterHub("qualified.local.toml") as hub:
    hub.connect("beam")
    # True only after independently blocking the source and isolating trigger control.
    hub.set_manual_mode("beam", source_inhibited=True)
    hub.safe_state("beam")
    time.sleep(hub.configs[0].policy.min_off_s)  # Single-target example configuration.
    hub.pulse("beam", 0.5)       # electrical ON, host hold, priority OFF/readback
```

| Command | Effect / limit |
| --- | --- |
| set_operating_mode(target, mode, source_inhibited=False), set_manual_mode(target, source_inhibited=False) | Policy-qualified mode selection; every changed mode requires True and persistent-mode permission |
| start(target, source_inhibited=False) | Manual ON or one qualified native Start/prime; native modes require True and a qualified continuous-duty load |
| set_cycle_parameters(target, parameters, source_inhibited=False, persist=False) | Validated CycleParameters, Manual/OFF, source assertion and separate write/storage permissions; fresh RAM readback |
| set_solenoid(target, True), open_shutter(target) | Qualified continuous-duty Manual ON with fresh electrical readback |
| set_solenoid(target, False), close_shutter(target), safe_state(target) | Priority qualified OFF with electrical readback |
| pulse(target, seconds) | ON/host hold/OFF; not calibrated optical exposure |
| cancel(target) | Cancel active work and attempt qualified OFF |
| shutdown_outputs() | Attempt OFF for targets with prior output/mode attempts; report read-only faults without actuating those targets; aggregate failures |

For direct calls, first establish Manual/OFF and the configured minimum OFF pause;
then set_solenoid(name, True) requests ON and set_solenoid(name, False) requests OFF.
The CLI pulse command performs explicit OFF preparation and that pause.
The minimum OFF interval begins after electrical OFF readback, so transition
latency cannot consume the required rest time. This is an electrical observation,
not a measured optical closure time.
Fresh OFF from get_status also starts that interval; an ON click is not required
to start it. Any observed ON invalidates the previous OFF interval. Library
connect remains identity-only; the WebUI Connect additionally reads fresh status.
Mode-write failures share the output ambiguity/cleanup guard. ON and pulse also
preserve the original failure and any separate cleanup outcome. Output methods
remain unavailable on VCP, KEH3 external USB OUT and without the reviewed load policy.

Optical open/close names are requests using the reviewed load mapping; they
do not report independently measured blade motion. The selected SH05R commissioning
policy uses its manufacturer closed-on-deenergization design and user-protected setup. `set_solenoid(target, bool)` uses the same policy boundary. No public
output method bypasses it. Invalid arguments/modes fail before output writes;
nonfinite durations fail before any I/O. Native modes are separately gated and
unqualified on the current physical profile; trigger-I/O configuration is unavailable.
`enable_device()` rejects explicitly because the protocol aliases channel enable
to solenoid output. It must not act as a harmless setup call.
`validate_pulse(target, duration)` checks the same duration/load constraints as
`pulse()` without connecting or accessing hardware; the CLI uses it before opening
a transport. Finite exposure/duty loads remain unavailable for both ON and pulse.

SRC-002 p20 specifies that the last used mode is remembered across power cycles.
Changing any mode therefore requires `allow_persistent_mode_changes = true` in
the reviewed qualification policy, in addition to electrical OFF and the preserved
interlock requirement. The default is false. Every actual transition requires source_inhibited=True
after independently blocking the source and isolating triggers. A changed mode
first sends OFF/deactivate and verifies output clear, then selects the requested mode.
An already selected/OFF controller is
queried without a mode write. A refused opt-in is not an ambiguous write and does
not itself latch a fault. No separate EEPROM command is sent.
The GUI has an explicit source-protection assertion; the controller cannot measure it.

`CycleParameters(on_ms, off_ms, cycles)` is exported from the package. Durations
are integer 100..10000 ms; count is 0..1000000, with 0 meaning continuous.
Read settings are dated separately from electrical feedback and cleared on release.
`settings_persistence` reports an EEPROM request, never confirmed persistence;
that requires separately authorized restart/readback verification. Optional policy
fields and native Start/Stop semantics are in the [WebUI guide](gui.md#manufacturer-reference-and-implemented-functions).
The live SH05R profile remains Manual-only with settings writes disabled. A native
Start remains pending until Stop even if output reads OFF; operating_state and
transition_confirmed never become inferred success. Existing Manual methods retain
their contracts; native control does not route through set_solenoid(True).

`ShutterStatus` retains the DiamondGUI owner schema. Requested state,
`feedback.electrical_state`, and timestamped human optical observations are
separate. `feedback.shutter_state` stays unknown without a live independent
sensor. `transition_confirmed` is false. Interlock mode is the controller's
configuration, not proof of contact continuity. status_bits is the fresh raw
32-bit field; electrical_state uses the exact KSC101 output mask0x1.
operating_state remains unknown: an OFF output does not establish Inactive or
an unprimed trigger. key_enabled/channel_enabled remain unknown in the normalized
application schema; no readiness or output permission is inferred from them.
The .NET Closed0/Open1 feedback enum differs from the legacy C/APT1/2 representation;
the optional raw scalar never controls normal feedback or output confirmation.

APT has no transaction identifiers. Freshness says
`response_after_request_no_transaction_id`, which describes receive provenance,
not a write acknowledgement or arbitrary network-delay immunity. No SDK cache
is involved. A query timeout/cancellation, duplicate reply or conflicting frame
poisons the session; it is never retried or reused for successful results.
After a short or unknown-count write, transmit alignment is also unknown. That
connection refuses every subsequent frame, including OFF, so a cleanup frame
cannot become part of the incomplete command. Independently protect the source
and restore the controller under the documented recovery procedure. Receive-only
failures and complete-but-late writes still allow a qualified OFF attempt; their
uncertain readback cannot confirm optical closure.

After any ambiguous output, ON remains locked out even after release/reconnect
or a new process. Normal successful OFF does not clear an existing fault. With
the source independently inhibited, optical closure independently observed and
the controller locally restored to Manual/OFF with interlocks intact:

```python
hub.recover("beam", source_inhibited=True, optical_closed=True,
            evidence="operator observation record with setup and timestamp")
```

Recovery reopens only the exact route, verifies identity/firmware and fresh
OFF/Manual/interlock replies, records the human observation and clears the
persistent uncertainty marker. It never sends ON or replays a trigger cycle.
The physical observation remains a dated record, not a continuing optical sensor.

The driver command values remain APT ON=1/OFF=2 and Manual=1. They are never
replaced by .NET feedback Closed=0. See [command traceability](INTERFACE.md) and
[manufacturer sources](sources.md). Qualified cycle settings and an explicitly
permitted cycle-only EEPROM request are supported in the owner/WebUI, not new
CLI subcommands. Trigger-I/O settings and interlock-bypass commands remain unavailable.
