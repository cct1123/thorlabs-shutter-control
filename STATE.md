# Engineering state

Project: `thorlabs-shutter-control`. Checkpoint recorded: 2026-09-09, 23:20 UTC.
Intent: [PROJECT.md](PROJECT.md). Evidence: [records](records/RECORDS.md).
Validated software fingerprints: [manifest](records/validation-manifest.json).

## Status

BLOCKED — software implementation and available software/SDK checks are complete.
The real Kinesis discovery API returns no KSC101 devices. Physical acceptance
cannot proceed without an accessible controller/shutter and known test conditions.

## Objective

Reliable KSC101 shutter control through a reusable Python controller and simple
Dash GUI, with independent physical validation of the shutter's operation.

## Requirements status

Full criteria remain in PROJECT.md. PASS below is limited to the stated criterion;
passing software checks do not clear any physical requirement.

| ID / source | Short criterion | Validation / current evidence | Status |
| --- | --- | --- | --- |
| REQ-001 / [constraints](PROJECT.md#constraints) | Python, uv, pyproject.toml, uv.lock | TEST-001: locked sync, offline sync, wheel/sdist build; [E003](records/RECORDS.md#e003) | PASS |
| REQ-002 / [objective](PROJECT.md#engineering-objective), [constraints](PROJECT.md#constraints) | Reusable minimal controller and supported API; separate GUI | TEST-002: official SDK contract, source review and callback tests; [E001](records/RECORDS.md#e001), [E003](records/RECORDS.md#e003) | PASS |
| REQ-003 / [controller](PROJECT.md#controller), [validation](PROJECT.md#validation) | Physical discovery/identity/connect/reconnect | TEST-003: real discovery returns []; mock lifecycle passes; [E002](records/RECORDS.md#e002), [E003](records/RECORDS.md#e003); B001 | BLOCKED |
| REQ-004 / [validation](PROJECT.md#validation) | Physical open/close and repetition | TEST-004: 20 software-double cycles pass; no physical observations; E003, B001 | BLOCKED |
| REQ-005 / [controller](PROJECT.md#controller) | Available state/status agrees with hardware | TEST-005: real getters verified; fault/unknown behavior tested with double; E001, E003, B001 | BLOCKED |
| REQ-006 / [validation](PROJECT.md#validation) | Hardware communication-error handling | TEST-006: injected failures pass; real loss/recovery untested; E003, B001 | BLOCKED |
| REQ-007 / [validation](PROJECT.md#validation) | Defined safe shutdown demonstrated physically | TEST-007: close/release/error paths tested with double; physical shutdown untested; E003, B001 | BLOCKED |
| REQ-008 / [GUI](PROJECT.md#gui), [validation](PROJECT.md#validation) | GUI through controller on real hardware | TEST-008: callback lifecycle passes; real browser no-device behavior checked; [E004](records/RECORDS.md#e004), E003, B001 | BLOCKED |

## Current system

`src/thorlabs_shutter_control/controller.py`: KSC101Controller, ShutterStatus,
ShutterError. Official Kinesis .NET SDK loaded lazily through Python.NET.
`gui.py`: local Dash callbacks; `__main__.py`: CLI and server shutdown.
No other driver abstraction, database, firmware, or deployment service.
See [README](README.md) for usage and [interface notes](docs/INTERFACE.md).

Connect starts communication/polling without explicit output/mode commands.
Open/Close select Manual. Default disconnect and safe_shutdown attempt close
before stopping polling/releasing. Faults invalidate state and prevent Open
until reconnect; Close/release remain available. SDK state is vendor-polled
feedback, not independent optical proof.

## Working / validated

- 43 tests PASS, including the opt-in real-SDK contract/discovery check.
- Lint/format checks, locked/offline environment sync and package build PASS.
- Browser: correct initial state, discovery of zero devices, visible connect error,
  disabled actuation buttons. Test server has been stopped.
- No physical controller connection or actuation was performed.

## Current configuration

- Windows x64; uv 0.11.2; CPython 3.12.14 in .venv.
- Locked packages: Dash 4.4.1, Plotly 7.0.0, Python.NET 3.1.0, pytest 9.1.1.
- No Kinesis in usual system locations; existing Thorlabs folder contains OPM.
- Official Kinesis 1.14.60.27990 x64 SDK administratively extracted under
  `tmp/kinesis-sdk/Program Files 64/Thorlabs/Kinesis` (ignored, local only).
  This was an administrative image extraction, not a system driver installation.
- Kinesis DLL load and .NET Framework load succeeded; discovery returns [].
- Unknown: actual serial, exact shutter model, supply/configuration, firmware,
  key/interlock/trigger configuration, driver readiness and physical shutter state.
- User launched autonomous engineering on 2026-09-09, superseding initialization-only
  scope. Routine reversible engineering authorized. Firmware changes require
  explicit approval; no bypass of hardware safety mechanisms.

## Current priority and next action

Resolve B001. After the operator response, repeat discovery, validate the supplied
hardware configuration against official documentation, and perform the staged
[physical acceptance procedure](docs/HARDWARE_VALIDATION.md) within established
authority. Record observations and fix any hardware/interface mismatch. Rerun
affected software tests after changes; then perform final integrated validation.

## Blockers

B001 affects REQ-003..008: no KSC101 is discoverable and physical setup/observation
are unavailable. Further mock testing cannot prove physical motion, wiring,
interlock operation, or USB-loss/shutdown behavior. No independent required software
work remains. This is not validated project completion.

## Human action required

Make the KSC101/shutter available on this USB control computer. Return the actual
controller serial, shutter model, supply model/rating, existing key/interlock and
trigger state, and confirm a safe test configuration with the beam source disabled
or independently blocked and a means to observe shutter motion. Preserve existing
safety mechanisms; do not change powered shutter/interlock cabling. If Kinesis is
installed elsewhere, provide its path. An asynchronous question requesting device
availability/model/power was sent during this session; no answer was received.

The [procedure](docs/HARDWARE_VALIDATION.md) specifies single transitions before
20 cycles and shutdown/error/GUI checks. Confirm applicable conditions before the
first physical operation. The next action is discovery and configuration review,
not automatic actuation merely because a device appears.

## Completion status

Software ready for hardware acceptance; project BLOCKED, not COMPLETE.
See [outputs/REPORT.md](outputs/REPORT.md). All physical tests remain unexecuted.
