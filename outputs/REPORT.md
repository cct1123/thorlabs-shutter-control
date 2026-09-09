# Engineering report

Status: **BLOCKED — physical acceptance pending**. Recorded 2026-09-09, 23:20 UTC.

## Objective and outcome

Implemented a reusable Python controller and lightweight Plotly Dash GUI for the
Thorlabs KSC101. Software verification and real SDK loading/discovery are complete;
no KSC101 is currently discoverable, so no physical operation has been validated.

## Resulting system

- [KSC101Controller](../src/thorlabs_shutter_control/controller.py): discovery,
  connection/identity, explicit Open/Close, reported status, error handling,
  safe_shutdown and context-manager cleanup. Calls serialized with a lock.
- [Dash GUI](../src/thorlabs_shutter_control/gui.py): discovery/selection,
  connection/identity/state, Open/Close, close-and-disconnect, status/errors.
  All hardware operations go through the controller class.
- [CLI](../src/thorlabs_shutter_control/__main__.py): localhost server and passive
  `--list` command. No automatic device connection or actuation on GUI startup.
- [pyproject.toml](../pyproject.toml), [uv.lock](../uv.lock), packaged CSS and tests.
  Architecture: Dash -> Python controller -> official Kinesis .NET -> USB KSC101.
  No additional driver framework or persistence service.

## Requirements and evidence

| Requirement | Status | Demonstrated scope |
| --- | --- | --- |
| REQ-001 Python/uv environment | PASS | Locked/offline sync and package builds |
| REQ-002 Controller/GUI separation and supported interface | PASS | Source/API review, actual SDK contract, software callback tests |
| REQ-003 Discovery/connection/identity/reconnect | BLOCKED | Real enumeration returns []; lifecycle tested only with double |
| REQ-004 Physical open/close/repetition | BLOCKED | 20 software-double cycles; no physical observation |
| REQ-005 Physical state/status handling | BLOCKED | Vendor getters inspected, software faults tested; actual feedback unverified |
| REQ-006 Hardware errors/recovery | BLOCKED | Injected software failures pass; hardware failure cases unexecuted |
| REQ-007 Physical safe shutdown | BLOCKED | Cleanup/failure/interruption code tested; physical closure unverified |
| REQ-008 Integrated GUI on hardware | BLOCKED | Real browser no-device checks and software callback lifecycle pass |

Evidence: [E001-E004](../records/RECORDS.md), [source/build fingerprints](../records/validation-manifest.json).
Final software run: **43 tests passed**, including the opt-in real SDK contract
test, with no physical connection/actuation. Lint/format, lock consistency, offline
sync, sdist/wheel build and packaged-asset inspection passed.

## Working configuration

Windows x64; CPython 3.12.14; uv 0.11.2; Dash 4.4.1; Plotly 7.0.0;
Python.NET 3.1.0; official Kinesis SDK 1.14.60.27990 x64.
The SDK is a local administrative image under
`tmp/kinesis-sdk/Program Files 64/Thorlabs/Kinesis`, selected explicitly for tests.
No system Kinesis driver installation or firmware modification was performed.
The GUI test server has been stopped.

Actual serial, shutter model, power setup, firmware, interlock/key/trigger
configuration and current physical state remain unknown. There is no physical
calibration/measurement result. Timing metrology is not currently an acceptance
criterion; no exposure-timing accuracy is claimed.

## Operation, limits, and shutdown

See [README.md](../README.md) for installation, CLI and Python usage.
Default: `uv run --locked shutter-control`, then open http://127.0.0.1:8050.
Use `--kinesis-dir` or KINESIS_DIR for a nonstandard SDK directory.

Connection issues no explicit enable/output/mode command. Open/Close select Manual;
default disconnect attempts close before releasing. Failed closure is reported,
even if resource release succeeds. No browser-tab-close or forced-exit closure
guarantee exists. SDK feedback is polled and does not independently prove optical
operation. Vendor-call and communication-loss latency remain to be measured.

Use one operator/process per device. This local manual GUI is not a safety interlock,
real-time exposure controller, or shared multiuser hardware service. Preserve
hardware safeguards; firmware changes require explicit approval.

## Blocker and resumption

B001: no KSC101 discovered and no physical setup available for independent observation.
The operator needs to make the controller/shutter available on this computer and
provide actual serial, shutter model, power supply/rating, existing key/interlock/
trigger configuration, and safe test conditions with the beam independently
blocked/disabled. If Kinesis is installed elsewhere, provide its path.

Next: repeat discovery; verify setup against official documentation; perform the
[staged physical tests](../docs/HARDWARE_VALIDATION.md) and record evidence.
Resolve any resulting software or hardware failures, then run final integrated
acceptance on the recorded configuration. These tests are not yet executed and
the project must not be treated as complete.

## Decisions and references

[D001-D003](../records/RECORDS.md#d001) record launch authority, Kinesis selection,
and shutdown policy. [Interface notes](../docs/INTERFACE.md) link official Thorlabs
examples/manual/software and document verified API members.
