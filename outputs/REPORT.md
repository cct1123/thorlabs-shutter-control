# Hardware-readiness engineering review

Status: **AWAITING_HUMAN_REVIEW**, following **HARDWARE_READY** on 2026-09-09.
The candidate is ready for staged hardware integration after human approval and
verification of the bench conditions. Physical acceptance remains BLOCKED.
No physical KSC101 communication or actuation occurred during this review.

## Architecture and audit conclusions

Dash / CLI -> KSC101Controller -> official Kinesis .NET via Python.NET -> USB KSC101.
The public class provides discover, connect, identify_device, get_status,
open_shutter, close_shutter, disconnect and safe_shutdown, plus context cleanup.
ShutterStatus is an immutable snapshot; ShutterError carries failures. Methods on
one instance are serialized. Hardware-specific calls remain in controller.py;
GUI callbacks only use the public controller interface. Import/GUI startup is passive.
The test fake replaces the SDK boundary; there is no production simulator or
additional driver abstraction to configure.

| Requested audit | Conclusion |
| --- | --- |
| 1. Small coherent API | PASS: eight operations, status/error types, explicit passive release option. |
| 2. GUI/device separation | PASS: Dash orchestration calls controller; no vendor enums or SDK calls in GUI. |
| 3. Real backend implemented from official sources | PASS for software readiness: official KSC101 Python/C# examples, native header and previously reflected 1.14.60.27990 SDK contract; no stubbed hardware operations. Actual device behavior pending. |
| 4. Assumptions explicit | PASS: unresolved bench, feedback, timing and shutdown facts below and in STATE.md. |
| 5. Failure/shutdown policy | PASS in software; fault snapshots invalidate state, faults block Open, Close/cleanup remain possible. Physical guarantees not inferred. |
| 6. Meaningful simulation tests | PASS: lifecycle, faults, feedback disagreement, cleanup and actual Dash HTTP callbacks. Mock timing/mechanics are not hardware evidence. |
| 7. Reproducible uv setup | PASS on Windows/Python 3.12 x64: fresh locked environment and installed wheel tested. Vendor runtime/drivers remain external prerequisites. |
| 8. Ordered physical procedure | PASS after correction: passive checks, first Close, singles, shutdown, GUI, repetition, closed-state faults. |
| 9. Exact first actions | PASS: explicit commands and vendor sequence in stages 1–3 of the procedure. |
| 10. Clean resumption | PASS: canonical checkpoint, artifact hashes, authority hold, stage gates, evidence fields and launch prompt recorded. |

Sources and interface details: [INTERFACE.md](../docs/INTERFACE.md).
Audit/reproduction evidence: [E005/E006](../records/RECORDS.md#e005).

## Concrete changes and automated validation

Fixed one production defect: Open previously proceeded to Enable/Active when its
preparatory Inactive request still reported Active or Open, provided Manual mode
was reported. Two injected regression cases reproduced that failure. Preparation
now requires **Closed AND Inactive AND Manual** before enabling/requesting Active.
Both cases then passed. No public API, GUI, dependency, feature or abstraction changed.

Corrected the procedure's first disconnect to `disconnect(close_shutter=False)`;
default disconnect writes Close. Added first-close-before-open ordering, explicit
actuation labels, observation/stop gates, and exact first calls. Clarified mode
persistence and the difference between historical SDK evidence and current tests.
PROJECT.md's scope now reflects the user's explicit human-review pause.

- **44 software-only tests PASS**, including the two regressions, repeated in a fresh
  locked environment and against the installed wheel.
- Ruff lint/format PASS; fresh offline uv sync installed 39 locked packages.
- Source distribution and wheel build PASS; installed CLI --help, dependency
  compatibility, GUI page/layout/CSS and packaged-asset checks PASS.
- Verified wheel import from site-packages and no Python.NET/Kinesis modules loaded
  during passive GUI smoke checks. Real USB enumeration test explicitly excluded.
- Previous 43-test result included one opt-in SDK enumeration test. That and the
  zero-device browser result remain historical E003/E004 evidence, not new hardware
  validation. There are now 44 software cases plus one opt-in SDK case.

Current source/document/build hashes: [readiness manifest](../records/hardware-readiness-manifest.json).
The old manifest is preserved as historical evidence. Builds are usable artifacts;
byte-identical builds across all toolchain versions are not claimed. uv.lock covers
Python runtime/dev packages, not the separately installed vendor SDK or USB driver.
The build-system requirement permits a Hatchling version range. Other declared
Python versions have not been validated; the hardware candidate targets 3.12 x64.

## Remaining hardware-dependent assumptions

All of these require discovery, supplied bench facts or physical observation:

- Actual serial, shutter model/compatibility, firmware, initial mode/state and
  availability. Last real enumeration found zero devices; it was not rerun here.
- Actual supply model/rating/polarity, shutter/USB cabling and power sequence;
  key/interlock/trigger configuration; independently blocked/disabled beam,
  qualified observer/measurement arrangement and approved physical shutdown method.
- Installed Kinesis version/path/bitness, .NET/vendor dependencies and USB driver;
  settings initialization, passive connection/polling and channel-enable behavior.
- Whether this shutter supplies meaningful position feedback; state/key/interlock
  semantics and cache freshness; feedback availability before Enable; actual USB
  fault detection latency and native-call blocking behavior.
- Physical open/close mapping and settling, thermal/duty-cycle limits and approved
  dwell, repeated-operation reliability, ownership release and reconnect behavior.
- Key/interlock and external-trigger behavior, startup/mode persistence, closure
  during normal shutdown/Ctrl+C, and residual state under USB/power/process failure.
  Abrupt failures cannot be assumed to close the shutter and are not all injected
  by this bounded plan; normal-mode and closed-state USB-loss checks are required.

The official SDK administrative image under tmp/ is local/ignored and not a USB
installation. Its prior successful load cannot settle any of these unknowns.

## Ordered hardware validation and shutdown

The exact commands, vendor calls, expectations, evidence and stop rules are in
[HARDWARE_VALIDATION.md](../docs/HARDWARE_VALIDATION.md). Execute only after approval:

| Order | Action | Actuation classification |
| --- | --- | --- |
| 0 | Confirm hardware/configuration, supported software, independent protection/observation, shutdown method and dwell limits. | Operator setup/power changes may cause motion; manufacturer procedure required. |
| 1 | Locked environment checks, then CLI --list; compare physical label/serial. | SDK discovery only; no explicit output commands. |
| 2 | Connect, identify, sample status, passive disconnect; review and repeat twice. | No explicit output commands; observe any SDK/startup side effects. |
| 3 | Connect and first Close; verify Closed/Inactive/Manual and independent position. | First intentional output-changing command. |
| 4 | One Open, approved dwell, Close; correlate physical observations and status. | Actuates. |
| 5 | Shutdown from closed, then from open; reconnect/identity/cleanup. | Actuates; proves normal closing path before further tests. |
| 6 | Dash discovery/connect, Close/Open/Close, Close & disconnect; reconnect/Open/Ctrl+C. | Actuates; independently verify cleanup. |
| 7 | Twenty numbered Open/Close pairs at approved dwell; observe every transition; shutdown. | Repeated actuation. |
| 8 | Closed-state USB loss, Fault/Unknown timing, Open refusal only after fault, failed-shutdown reporting, reconnect/cleanup; repeat through GUI. | No intended opening; loss/restoration and cleanup may affect output. |

Stop at any failed gate, ambiguous state or missing prerequisite. Do not interpret
successful calls as proof of movement. Record TEST-003..008 against the exact
configuration; repeat affected gates and final GUI open/close/shutdown after changes.

Normal `safe_shutdown()`, default `disconnect()`, context exit, GUI Close &
disconnect and server Ctrl+C request Inactive then Manual, wait for reported
Closed/Inactive/Manual, stop polling and disconnect. Closure failure does not skip
release; errors remain visible. Failed release retains the handle for retry.
Successful shutdown does not restore auto/trigger mode. Failed Open attempts a
recovery Inactive write and latches a fault, without claiming physical closure.
Browser-tab closure does nothing to the controller. Force-kill, USB/power loss,
stale feedback or a hung native call cannot guarantee closure; maintain independent
protection and use the approved bench shutdown method when software cannot verify it.

## Human handoff

REQ-001/002 PASS within software scope; REQ-003..008 remain BLOCKED. Review is
complete, project acceptance is not. [STATE.md](../STATE.md) is canonical and records
HARDWARE_READY -> AWAITING_HUMAN_REVIEW. No hardware command or server is pending.
User changes to prompt log.txt were preserved outside this audit. Consult Git
history for commit/publication status. After approval, use exactly:

> Human review approved. Read PROJECT.md, AGENTS.md, STATE.md and docs/HARDWARE_VALIDATION.md. Begin hardware validation in the documented order, verifying the bench conditions before device access and requiring independent observations for every actuation. Stop on any failed gate or missing prerequisite; record evidence and update state.
