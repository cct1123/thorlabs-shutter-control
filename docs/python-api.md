# Python API

Current fault reset: safe_state(target) is explicit Stop/OFF and clears a prior
fault only after verified electrical OFF and preserved interlock. Automatic
cleanup/shutdown and reads retain faults. Failed reset keeps the journal; a
poisoned session needs Release/Connect before another explicit Stop. This reset
records no optical observation. recover() remains an optional passive procedure
requiring independent closure evidence. Hardware disconnect alone still requires
its explicit source_inhibited=True assertion. Native Start/settings do not.

Import configuration and owner classes from `thorlabs_shutter_control`:
`ControllerConfig`, `Policy`, `Route`, `CycleParameters`, `ShutterHub`,
`ShutterStatus` and `load_config` remain available there.
The internal config/device/discovery modules were consolidated into controller
and transport; their old import paths have no compatibility wrappers. Existing
TOML keys remain supported. KEH3 requires host/bay; hub_serial/hub_firmware may
be omitted when unknown and do not establish verified hub identity. Supplied
known metadata must agree across routes to the same host.

```python
from thorlabs_shutter_control import ShutterHub

with ShutterHub("shutters.local.toml") as hub:  # construction is passive
    connection = hub.connect("shutter")     # exact identity only, no enable
    print(connection.identity)              # model/serial/firmware/hardware/channels
    sample = hub.get_status("shutter")      # fresh electrical feedback
    print(sample.electrical_state)
```

The context closes communication on success or error. It preserves the original
exception and adds any cleanup failure; retain the owner if release fails. Closing
does not actuate OFF. Explicit connect/get_status/release is also supported.

The additional documented Issue42.1 operations use the same owner:

| Method | Result and effect |
| --- | --- |
| get_channel_enabled(target) | Boolean from 0x0211/0212; not blade position |
| get_hub_bay_reply(target) | Raw legacy bay byte on other routes; KEH3 is unqualified and raises UnsupportedRoute before I/O |
| get_led_modes(target) | Raw LED indication-mode word; not display brightness |
| set_led_modes(target, modes, source_inhibited=False) | Write/read back documented LED bits 1=Identify, 2=limit switch, 8=moving; does not infer their shutter meaning |
| require_interlock(target, source_inhibited=False) | Ensure interlock is required, verify Manual/OFF; already-required readback sends no write. No disable API |
| start_updates(target), stop_updates(target) | Explicit 0x0011/0012 requests; no ACK confirms streaming started/stopped |
| get_events(target) | Fresh identity query collects arrivals, then returns/consumes buffered raw Frame objects; no motor payload decoded |
| disconnect_hardware(target, source_inhibited=False) | Explicit 0x0002 followed by release; requires protected Manual/OFF and no active request |

LED/interlock settings use the existing allow_device_settings permission;
the source_inhibited boolean is now compatibility-only for settings/native Start; the tracked live profile keeps settings disabled.
LED writes require Manual/OFF/interlock and exact RAM readback, send no EEPROM
command and create no output-cleanup obligation. Interlock repair may start with
the requirement disabled, but cannot disable it; failures retain uncertainty and
use the existing bounded output cleanup. No new firmware qualification is implied.

Stop updates explicitly before releasing. Events are held in the existing bounded
64-frame queue and collected during queries, without a receiver thread or a
lossless-acquisition claim. Status-update payloads remain bytes, because Issue42.1
does not establish a KSC101-specific motor-status layout. Use get_status for the
usual fresh electrical readback. Issue42.1 p52 describes legacy T-Cube bay
identifiers, not a verified KEH3 contract. The actual KSC10168800777 / firmware1.0.7
middle-bay query timed out in TEST-252; the shared owner now refuses it on KEH3
before I/O without faulting the connection. Configured routing is unchanged.
The LED request uses the consistent 0x04B4 model-table/section identifier; p93's
request diagram prints an inconsistent 0x0411. No such motor query is sent.

The low-level KSC101.set_channel_enabled encoder implements the documented
0x0210 output alias. Application ON/OFF stays on the canonical 0x04CB owner path;
There is no owner-level channel-enable setup alias. Ordinary disconnect()/close()
send neither hardware-disconnect nor automatic-update commands.

| Method | Effect |
| --- | --- |
| connect(target) | Open exact route, claim serial/endpoint, verify identity |
| identify_device(target) | Request and verify identity again; no flashing/identify command |
| blink_identify(target) | APT identify LED-flash request only; no flash acknowledgement or shutter output |
| get_status(target) | Request identity, mode, interlock requirement and fresh status bits |
| get_cycle_parameters(target) | Explicit APT cycle read; returns dated cycle_parameters in ShutterStatus |
| get_solenoid_state_reply(target) | Explicit raw 0x04CD byte, without output/operating-state interpretation |
| connection_snapshot(target) | Host metadata only; no hardware polling |
| disconnect(target=None, require_stopped=False), close() | Release communication; no output command. The WebUI passes require_stopped=True to refuse pending ON/Start under the same lock as release |

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
For an explicit Trigger->Manual transition, use `manual`. The legacy
`--source-inhibited` option is accepted but is no longer required or used.

After physical qualification and within the approved operating window, a balanced
host hold on a continuous-duty load looks like this (not executed by verification):

```python
import time

with ShutterHub("qualified.local.toml") as hub:
    hub.connect("beam")
    # Establish the approved source/trigger protection physically before this procedure.
    hub.set_operating_mode("beam", "manual")
    hub.safe_state("beam")
    time.sleep(hub.configs[0].policy.min_off_s)  # Single-target example configuration.
    hub.pulse("beam", 0.5)       # electrical ON, host hold, priority OFF/readback
```

| Command | Effect / limit |
| --- | --- |
| set_operating_mode(target, mode, source_inhibited=False) | Mode selection requires OFF/interlock readback; no separate permission; source_inhibited is compatibility-only |
| start(target, source_inhibited=False) | Manual ON or one qualified native Start/prime; native modes require a qualified continuous-duty load; source flag is compatibility-only |
| set_cycle_parameters(target, parameters, source_inhibited=False, persist=False) | Validated CycleParameters, Manual/OFF and separate write/storage permissions; fresh RAM readback |
| set_solenoid(target, True) | Qualified continuous-duty Manual ON with fresh electrical readback |
| set_solenoid(target, False), safe_state(target) | Priority qualified OFF with electrical readback; cancels active work |
| pulse(target, seconds) | ON/host hold/OFF; not calibrated optical exposure |
| shutdown_outputs() | Attempt OFF for current/unresolved output work; a confirmed-safe released session cannot authorize output in a later reader; aggregate failures and retained faults, even after successful OFF |

For direct Manual calls, first establish Manual/OFF and any configured positive OFF pause;
then set_solenoid(name, True) requests ON and set_solenoid(name, False) requests OFF.
The CLI pulse command performs explicit OFF preparation and that pause. The
tracked Ethernet profile uses min_off_s=0.0; no extra pause is added there.
The minimum OFF interval begins after electrical OFF readback, so transition
latency cannot consume the required rest time. This is an electrical observation,
not a measured optical closure time.
Fresh OFF from get_status also starts that interval; an ON click is not required
to start it. Any observed ON invalidates the previous OFF interval. Library
connect remains identity-only; the WebUI Connect additionally reads fresh status.
An ON attempt itself also invalidates prior rest, even if no subsequent poll
sees ON. A later externally imposed OFF therefore starts a new interval.
Mode-write failures share the output ambiguity/cleanup guard. ON and pulse also
preserve the original failure and any separate cleanup outcome. Output methods
remain unavailable on VCP, KEH3 external USB OUT and without the reviewed load policy.

Output operations are requests using the reviewed load mapping; they
do not report independently measured blade motion. The selected SH05R commissioning
policy uses its manufacturer closed-on-deenergization design and user-protected setup. `set_solenoid(target, bool)` uses the same policy boundary. No public
output method bypasses it. Invalid arguments/modes fail before output writes;
nonfinite durations fail before any I/O. Native modes are separately gated and
unqualified on the current physical profile; trigger-I/O configuration is unavailable.
The protocol aliases channel enable to solenoid output; no owner-level enable
setup method is provided. The low-level encoder can actuate the load.
`validate_pulse(target, duration)` checks the same duration/load constraints as
`pulse()` without connecting or accessing hardware; the CLI uses it before opening
a transport. Finite exposure/duty loads remain unavailable for both ON and pulse.

SRC-002 p20 specifies that the last used mode is remembered across power cycles.
Mode selection requires electrical OFF and the preserved interlock requirement,
without a separate permission flag. `allow_persistent_mode_changes` is accepted
as a legacy configuration field and no longer gates selection. Mode selection requires no software
source confirmation; source_inhibited remains an accepted compatibility argument. A changed mode
first sends OFF/deactivate and verifies output clear, then selects the requested mode.
An already selected/OFF controller is
queried without a mode write. A refused precondition is not an ambiguous write and does
not itself latch a fault. No separate EEPROM command is sent.
The GUI has no source-protection assertion. Only hardware disconnect and passive
protected recovery retain their explicit API source assertions.

`CycleParameters(on_ms, off_ms, cycles)` is exported from the package. Durations
are integer 100..10000 ms; count is 0..1000000, with 0 meaning continuous.
Read settings are dated separately from electrical feedback and cleared on release.
Cycle writes enforce `on_ms / (on_ms + off_ms) <= max_duty_fraction`, alongside
ON/OFF/count limits. Finite-load settings do not qualify finite-load activation.
Mode/settings readback must preserve the interlock requirement; unexpected
disablement faults the owner and retains uncertainty. A mode transition's
explicit Stop/OFF replaces an older native Start request.
`settings_persistence` reports an EEPROM request, never confirmed persistence;
that requires separately authorized restart/readback verification. Optional policy
fields and native Start/Stop semantics are in the [WebUI guide](gui.md#manufacturer-reference-and-implemented-functions).
The live SH05R profile lists all four modes in `qualified_modes`, removing its
Manual-only activation restriction. OFF/interlock readback and cycle/load checks
still apply to native Start; settings writes remain disabled. Stop/OFF is supported in the
selectable modes even when native Start is unqualified. A native
Start remains pending until Stop even if output reads OFF; no native inactivity
or physical completion is inferred. Existing Manual methods retain
their contracts; native control does not route through set_solenoid(True).

## Status schema migration

Version 2 uses one flat `ShutterStatus`; `ShutterFeedback` is removed without an
alias. The current reduction also removes convenience methods and three duplicated
configuration fields. Configuration constructors remain supported.
Update external consumers before deploying this version; the external DiamondGUI
checkout is not migrated by this repository change.

| Previous access | Current access |
| --- | --- |
| `sample.channel`, `.serial_number`, `.endpoint` | Read configured channel/serial/route from `ControllerConfig`; verified serial is `sample.identity.serial_number` when identity is present |
| `sample.feedback.electrical_state`, `.operating_mode`, `.status_bits`, `.electrical_observed_at` | `sample.electrical_state`, `.operating_mode`, `.status_bits`, `.electrical_observed_at` |
| `sample.feedback.interlock_enabled` | `sample.interlock_required`: configuration, not contact continuity |
| `sample.identity_verified` | `sample.identity is not None` |
| `sample.observed_serial_number`, `.description` | Read serial/model/firmware from `sample.identity` when present |
| `sample.connection` | Use `sample.error`, `sample.has_device` and `sample.identity` for distinct fault/handle/verification conditions |
| `sample.optical_observed_state`, `.optical_observed_at`, `.optical_provenance` | `sample.optical_closed_at` and `.optical_evidence`; absent means no independent closed observation |

| Removed method | Replacement |
| --- | --- |
| `open_shutter(target)` | `set_solenoid(target, True)`; remains Manual-only |
| `close_shutter(target)`, `cancel(target)` | `safe_state(target)` |
| `set_manual_mode(target, source_inhibited=...)` | `set_operating_mode(target, "manual", source_inhibited=...)` |
| `enable_device(target)` | No replacement setup call; choose an explicit output operation |
| Low-level `KSC101.output_state(deadline)` | `KSC101.status_bits(deadline)`; bit 0 is electrical ON, not optical position |

Removed: nested `feedback`, redundant `observed_at`/`feedback_freshness`, and
unsupported `shutter_state`, `operating_state`, `key_enabled`, `channel_enabled`
and `transition_confirmed` placeholders. Native activity, key position and blade
motion remain unavailable; field removal supplies no new physical evidence.
Freshness remains response-after-request without APT transaction identifiers.

`ShutterStatus` adds two optional boolean fields: `interlock_status_bit` (0x1000)
and `channel_enabled_bit` (0x80000000), decoded centrally from the exact KSC101
GetStatusBits reference (SRC-008). They share `electrical_observed_at` with
`status_bits`; passive/disconnected snapshots leave them None. No additional
request is made. These are reported bits, not the `interlock_required` setting,
verified interlock continuity, physical key position or hardware readiness.
The GUI renders them as Set/Clear and retains the original date after healthy
refusals; its Native request row is host metadata, not decoded OperatingState.
The .NET KeyEnabled property exists but its raw-wire source remains unverified.

Status snapshots are independent mutable copies; editing one cannot change the
owner. No locks, transports or other private resources are serialized. A
`connection_snapshot()` contains host metadata with unknown electrical readings;
`get_status()` explicitly queries current readings. Requested output, electrical
readback and timestamped human closure evidence remain separate. Output attempts,
release and ambiguity clear the human observation. A closure timestamp records an
observation, not proof of continuing closure or calibrated optical timing.

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
or a new process. Explicit Stop/OFF clears a fault only after fresh OFF/interlock
verification; automatic cleanup and shutdown retain and report it. If framing
is poisoned, Release/Connect before that explicit Stop. Passive protected
recovery is another option, with the source independently inhibited, optical closure independently observed and
the controller locally restored to Manual/OFF with interlocks intact:

```python
hub.recover("beam", source_inhibited=True, optical_closed=True,
            evidence="operator observation record with setup and timestamp")
```

Recovery reopens only the exact route, verifies identity/firmware and fresh
OFF/Manual/interlock replies, records the human observation and clears the
persistent uncertainty marker. It never sends ON or replays a trigger cycle.
Successful protected recovery also clears stale output requests and cleanup
obligations; subsequent read-only shutdown does not send an incidental OFF.
The physical observation remains a dated record, not a continuing optical sensor.

The driver command values remain APT ON=1/OFF=2 and Manual=1. They are never
replaced by .NET feedback Closed=0. See [command traceability](INTERFACE.md) and
[manufacturer sources](sources.md). Qualified cycle settings and an explicitly
permitted cycle-only EEPROM request are supported in the owner/WebUI, not new
CLI subcommands. Trigger-I/O settings and interlock-bypass commands remain unavailable.
