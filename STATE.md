# Engineering state

Project: `thorlabs-shutter-control`. Checkpoint: 2026-09-09, 23:38 UTC.
Intent: [PROJECT.md](PROJECT.md). Evidence: [E005/E006](records/RECORDS.md#e005).
Current fingerprints: [readiness manifest](records/hardware-readiness-manifest.json).

## Status

**AWAITING_HUMAN_REVIEW** — software candidate and staged procedure passed readiness
review. This is not physical acceptance or permission to communicate with hardware.
Recorded transitions on 2026-09-09: BLOCKED -> HARDWARE_READY after E005/E006,
then HARDWARE_READY -> AWAITING_HUMAN_REVIEW at the user's explicit review hold.
No device access is authorized by either readiness label. Wait for the launch prompt.

## Objective and requirements

Reliable KSC101 shutter control through a reusable Python controller and simple
Dash GUI, with independent physical validation. Full criteria remain in PROJECT.md.

| ID | Criterion | Test / current evidence | Status |
| --- | --- | --- | --- |
| REQ-001 | Python, uv, pyproject and lock | TEST-001; fresh locked offline sync, wheel install, build; E006 | PASS |
| REQ-002 | Small supported controller; separate GUI | TEST-002; source review, E001 historical SDK contract, E005/E006 current software | PASS |
| REQ-003 | Physical discovery/identity/connect/reconnect | TEST-003; E002 historical empty enumeration; physical setup not rechecked | BLOCKED |
| REQ-004 | Physical open/close and repetition | TEST-004; fake cycles pass E006; no independent physical observations | BLOCKED |
| REQ-005 | Status agrees with physical state | TEST-005; software fault/feedback tests E006; actual cache/sensor behavior unknown | BLOCKED |
| REQ-006 | Physical communication errors/recovery | TEST-006; injected failures E006; real loss/recovery untested | BLOCKED |
| REQ-007 | Physical safe shutdown | TEST-007; software cleanup/failure tests E006; closure unverified | BLOCKED |
| REQ-008 | GUI through controller on hardware | TEST-008; fake HTTP lifecycle E006, historical zero-device browser E004; hardware pending | BLOCKED |

All criteria map to the controller, GUI, validation and constraints in PROJECT.md.
No readiness designation changes the physical acceptance standard.

## Architecture and audited change

Dash GUI / CLI -> KSC101Controller -> official Kinesis .NET through Python.NET -> USB.
The controller owns lazy SDK loading, selection, polling, commands, status, faults
and cleanup. Public API: discover, connect, identify_device, get_status, open_shutter,
close_shutter, disconnect, safe_shutdown; immutable ShutterStatus and ShutterError.
One owner per device; per-instance locking. Test fake lives in tests/conftest.py;
there is no separate production simulation backend or extra driver framework.

Only production change: Open now requires reported Closed/Inactive/Manual before
Enable/Active. Two regression cases demonstrated the prior false preparation
success. GUI/CLI, dependencies and public API are unchanged. The procedure now
uses explicit passive disconnect before the first output-changing Close.

## Current validation and configuration

- E006: 44 software tests PASS, including two new regressions. Fresh locked offline
  environment, lint, format, sdist/wheel build, installed-wheel suite, CLI help,
  dependency compatibility, and passive GUI/packaged CSS checks PASS.
- E003's 43 tests included a real SDK enumeration check; that test was explicitly
  excluded here. E004's zero-device browser observations are historical.
- Windows x64, CPython 3.12.14, uv 0.11.2; Dash 4.4.1, Plotly 7.0.0,
  Python.NET 3.1.0. .python-version selects 3.12; other supported versions untested.
- Prior verified SDK: Kinesis 1.14.60.27990 x64, administratively extracted to
  tmp/kinesis-sdk/Program Files 64/Thorlabs/Kinesis. Not a USB-driver installation;
  it is ignored/local and absent from a fresh clone. No SDK was loaded this audit.
- Reproduction commands and environment/build limits: E006 and README.md.
- No device communication/actuation during this audit, no hardware handles opened,
  and no GUI server started. No physical operation is pending in this task.

## Hardware-dependent assumptions / B001

Physical REQ-003..008 require the actual bench and independent observation:

- Actual serial, exact compatible shutter model, firmware and initial physical/
  operating state; current device availability. Last discovery was empty (E002),
  not a present-day recheck or proof of a specific hardware/driver fault.
- Supply model/rating/polarity, shutter/USB cabling, power-up procedure; existing
  key/interlock and trigger wiring/state; independent beam block/source disable,
  observation method/operator, and approved physical shutdown method.
- Installed Kinesis path/version/bitness, vendor runtime and USB-driver readiness;
  actual settings initialization, passive connect/polling and channel-enable behavior.
- Whether reported solenoid position comes from useful feedback on this shutter,
  status/key/interlock meanings and freshness, USB-loss detection latency and vendor
  call blocking, including whether preparation feedback is available before Enable.
- Physical Close/Open mapping, travel/settling time, duty cycle/thermal limits and
  approved dwell; repeated operation and deliberate reconnect behavior.
- Behavior of key/interlock transitions, external triggers, mode persistence/startup,
  normal close-on-shutdown/Ctrl+C and USB/power-loss/forced-exit residual state.
  No automatic closure guarantee is made for communication or process failure.

## Human review and next action

Review [report](outputs/REPORT.md), audited changes, and the exact
[ordered hardware procedure](docs/HARDWARE_VALIDATION.md). Supply/confirm the bench
facts and safeguards above; unknowns block dependent stages. After explicit launch
approval, start at stage 0, then discovery, passive connection/identity/status/
release, first Close, one Open/Close, shutdown/reconnect, GUI/Ctrl+C, 20 approved-dwell
cycles, and closed-state USB-loss/recovery last. Every physical transition requires
independent observation; stop on discrepancy and update records/state after each gate.

Exact postapproval launch prompt:

> Human review approved. Read PROJECT.md, AGENTS.md, STATE.md and docs/HARDWARE_VALIDATION.md. Begin hardware validation in the documented order, verifying the bench conditions before device access and requiring independent observations for every actuation. Stop on any failed gate or missing prerequisite; record evidence and update state.

## Completion

Hardware readiness review is complete; physical project acceptance is not.
The current user instruction prohibits device communication/actuation until approval.
No firmware changes or interlock bypass are authorized. [D004](records/RECORDS.md#d004)
records the readiness-state override of the template; do not auto-resume from a
readiness label. Preserve user edits in prompt log.txt, which was not edited by
this audit. Consult Git history for the readiness audit's commit and publication status.
