# Engineering state

Checkpoint: consistency review **VALIDATED (SOFTWARE ONLY), READY TO PUBLISH**, 2026-10-20.
Intent: [PROJECT.md](PROJECT.md), review/fix/commit/push request.
Current evidence: E024 / TEST-035; prior TTL evidence E023 is historical after
these changes. **AWAITING_HUMAN_REVIEW** remains the hardware status. No SDK load,
device discovery/connection, actuation, electrical test or firmware change is authorized.
Physical acceptance remains **BLOCKED**; software success is not overall completion.

## Requirements

Full criteria and sources are in PROJECT.md. REQ-019–031 track the successive
three-shutter, naming/simplification, Ethernet research and TTL requests;
REQ-032–033 track the latest consistency review and publication request.
Earlier scoped evidence remains historical. Current regressions revalidate
unchanged behavior; physical criteria remain blocked under B001.

| ID | Short criterion | Validation / evidence | Status |
| --- | --- | --- | --- |
| REQ-001 | Python, uv, packaging and lock | TEST-001/025; locked setup, build/package checks, E024 | PASS |
| REQ-002 | Reusable controller, separate GUI | TEST-002/022–024; current software tests, E024 | PASS |
| REQ-003 | Physical discovery/identity/connect/reconnect | TEST-003; historical E002 empty enumeration only; new three-cube bench pending | BLOCKED |
| REQ-004 | Physical opening/closure/repetition | TEST-004; no independent physical observations | BLOCKED |
| REQ-005 | Feedback agrees with physical state | TEST-005; real sensor/cache behavior unknown | BLOCKED |
| REQ-006 | Physical error handling/recovery | TEST-006; real USB/hub/device loss pending | BLOCKED |
| REQ-007 | Physical safe shutdown | TEST-007; per-shutter closure/latency unverified | BLOCKED |
| REQ-008 | GUI on physical hardware | TEST-008; only simulated GUI validated | BLOCKED |
| REQ-009 | Setup/troubleshooting documentation | TEST-009/025; updated guides and references, E024 | PASS |
| REQ-010 | Accurate API/architecture/integration/simulation | TEST-010/025; examples/demo/review, E024 | PASS |
| REQ-011 | Actual simulated screenshot, editable diagrams | Historical E016/E023 screenshots; unchanged GUI/diagrams, TEST-035 E024 | PASS |
| REQ-012 | Reproducible documentation workflow | TEST-012/025; demo, references, E024 | PASS |
| REQ-013 | Honest prior documentation delivery | TEST-013; historical scoped E007/E008 | PASS |
| REQ-014 | Focused prior simplification (derived) | TEST-014; historical scoped E009 | PASS |
| REQ-015 | Validate current package (derived) | TEST-015/025; software suite/build, E024 supersedes E009 for changed source | PASS |
| REQ-016 | Explain architecture and retained complexity (derived) | TEST-016/025; current report E024, historical E009 | PASS |
| REQ-017 | Simple hardware-focused visual README (derived) | TEST-018/020/025; updated README E024, diagram E014 | PASS |
| REQ-018 | Multiple-controller/KEH3 compatibility review (derived) | TEST-021; source assessment E015 only | PASS |
| REQ-019 | Three independent GUI panels (derived) | TEST-022; distinct fake devices, HTTP/browser lifecycle, E024 | PASS (software) |
| REQ-020 | Exclusive ownership and cleanup all slots (derived) | TEST-023; duplicate/race/failure/interrupt tests, E024 | PASS (software) |
| REQ-021 | Passive startup, CLI serials, hardware hold (derived) | TEST-024; fake launch/argument tests, E024 | PASS (software) |
| REQ-022 | Reproducible package and operating docs (derived) | TEST-025; tests/lint/build/examples/visual review, E024 | PASS (software) |
| REQ-023 | Three KSC101s through actual KEH3 USB (derived physical scope) | TEST-026 / physical TEST-003–008; prepared procedure stage 9 | BLOCKED |
| REQ-024 | Rename driver, merge hub module and prune (derived) | TEST-027; 99 tests, package, docs and layout parity, E017 | PASS (software) |
| REQ-025 | Rename ShutterHub, centralize construction and prune (derived) | TEST-029; 107 source/package tests, examples and layout parity, E019 | PASS (software) |
| REQ-026 | Simplify GUI construction, preserve independent controls (derived) | TEST-030 historical E020; current TEST-035 regression E024 | PASS (software) |
| REQ-027 | Assess KEH3 Ethernet SDK support and changes (derived) | TEST-032; official documentation/static SDK/source review, E022 | PASS (research only) |
| REQ-028 | TTL configuration/readback and explicit arm/disarm (derived) | TEST-033; static official contract, distinct software devices, E024 | PASS (software) |
| REQ-029 | Independent TTL GUI controls and draft/readback separation (derived) | TEST-033; HTTP/browser checks, E024 | PASS (software) |
| REQ-030 | TTL shutdown and package regression (derived) | TEST-033; failure/interrupt/all-slot tests and wheel, E024 | PASS (software) |
| REQ-031 | Physical TTL configuration/priming/disarm across three shutters (derived) | TEST-034; stage 10, no SDK/physical execution | BLOCKED |
| REQ-032 | Consistency review, focused fixes and pruning (derived) | TEST-035; 211 source/wheel tests, E024 | PASS (software) |
| REQ-033 | Commit and push reviewed changes | TEST-036; verified commit and remote reference required | PENDING |

## Current architecture and configuration

GUI/CLI -> ShutterHub -> up to three independent KCubeShutter objects -> lazy
Kinesis .NET/Python.NET -> KEH3 USB serial identities. Default GUI has three
passive slots. No new dependency or lockfile change. One serialized GUI callback
keeps per-panel settings drafts, Apply/Read/Arm/Disarm and readback independent.
Connect/refresh never configure or arm. Manual Open refuses Triggered mode.

Connection verifies the returned serial. Full status samples operating feedback
after requesting TTL settings; Open/Close/Disarm waits read operating feedback
alone, allowing disarm after settings errors. Faults stay latched until successful
disconnect/reconnect. Command snapshots may omit trigger_config; use get_status()
for full readback. Apply requires Closed/Inactive/Manual and matching settings.
Arm requires healthy feedback, key/interlock and an input; uses reported settings.

Close requires Closed/Inactive before Manual, then Closed/Inactive/Manual. Release
attempts Disconnect after StopPolling errors or interruptions; failed release
retains its handle/serial claim. Hub/CLI attempts every slot, preserves faults and
interrupts. Open recovery interruption also leaves a fault. No persistent-settings
or firmware commands. Port settings remain; prior Triggered mode is not restored.

Default polling 250 ms, GUI interval 1 s. Full three-slot status adds at least
750 ms of settings waits plus SDK latency. Feedback timeout is 5 s per stage:
two for Close/Disarm, three for Open/Arm including preparation. SDK calls and
sequential shutdown have no total latency bound. No calibrated pin-level or
precise exposure timing API is provided.

Current source and rebuilt wheel: 211 tests PASS each; 14 selected regressions
FAIL against the prior E023 wheel and PASS with the fixes. Lint/format/build,
39-package dependency check, simulated API and documentation checks PASS. Current
hashes: records/review-validation.json; prior manifests are historical. Current
GUI is unchanged visually; historical simulated captures E016/E023 remain labeled.
Environment: Windows x64, CPython 3.12.7, Dash 4.4.1, Python.NET 3.1.0, unchanged uv.lock.

Ethernet assessment [E022](records/RECORDS.md#e022) remains research only; Kinesis
KEH3 Ethernet is documented, XA Python discovery details unresolved, no backend
implemented. See [assessment](docs/ethernet-assessment.md). Actual installed SDK,
physical topology, feedback/cache age, electrical behavior, persistence and
closure/latency remain unvalidated. No simulator or hardware handle is pending.

## Next action

Commit/push the validated reviewed tree to
origin/main (explicitly authorized by the latest request). Use a normal push;
no history rewrite is authorized. Keep physical work on hold. Forced termination,
power/USB loss or a hung SDK call can prevent closure and later cleanup attempts.

## Human action required for future hardware validation / B001

1. Known: software regressions pass; physical REQ-003–008/023/031 remain BLOCKED.
   The user kept hardware access on hold; no new bench action is requested now.
2. Blocker: software cannot establish actual bench identity, limits, authority or
   independent physical observations.
3. Before resumption, approve [HARDWARE_VALIDATION.md](docs/HARDWARE_VALIDATION.md),
   including three-cube stage 9 and TTL stage 10. Establish independent source
   disable/beam block, safe observation and physical shutdown, with per-shutter
   and combined dwell/duty-cycle limits.
4. Return three actual serials/models/firmware, KEH3 supply/USB mapping, SDK
   path/version/bitness, initial physical states, key/interlock arrangement,
   approved dwell in seconds and TTL source/wiring/levels/polarities with limits.
5. After explicit launch approval, recheck transient state and run ordered gates
   with independent observations; failed or unknown criteria remain blockers.
