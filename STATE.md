# Engineering state

## Cleanup checkpoint - E079 / TEST-088, 2026-10-20

Latest user requests holistic review, pruning, consistency fixes, commit and push.
Historical evidence was preserved in a verified136-file ZIP before pruning.
Current docs now distinguish one-pair USB results from untested three-pair/TTL/
fault/calibration and post-update Ethernet scope. Fixed stale hardware holds,
contradictory status, old screenshots and encoding artifacts.

Tutorials now support explicit serial-scoped interlock confirmation like the GUI.
Their ExitStack cleanup registers passive release before Connect and Close only
after verified identity/feedback; all callbacks are attempted and Python preserves
chained failures. Added regressions cover unknown SDK indication, wrong confirmation
serial and identity mismatch plus failed release.449 source software tests PASS.
Driver/GUI/CLI unchanged; previous bench qualification remains scoped to those paths.

Cleanup/validation PASS:100 inventoried files/directories removed, including
scratch SDK extraction/installer copies, caches, old build outputs and obsolete
active logs/assets. Source449 tests and wheel449 tests PASS; wheel9 entries,
no vendor binaries/records/tests. Archive136 members verified;17 Markdown files/
67 local targets checked, Ruff/format/diff checks PASS. Active text normalized LF.
Next: reviewed allowlist commit and push origin/main, then remote identity check.
No new hardware operation. Installed vendor runtime/.venv/GUI owner preserved.

## Bench and ownership

USB computer -> KEH3 left bay -> KSC10168800777/firmware1.0.7 -> SH05R. SDK
Kinesis1.14.60.27990, Python3.12.7 x64/pythonnet3.1, FTDI without a COM assignment.
Actual USB identity/reconnect/Open/Close/shutdown and browser actions have readback
evidence; the user confirmed the earlier five-cycle physical sequence. SDK
interlock clear-bit is unknown; explicit object/serial session confirmation records
normal physical circuit/protection without an interlock write. Known negative,
key, identity and communication checks remain intact. Undefined operating0 is
not relabeled Inactive. Ethernet pre-update discovery found only the hub; no
post-update cube Ethernet PASS is claimed.

Last observed GUI handoff E078: localhost8050/session8424, normal production CLI
--serial 68800777 --verified-interlock 68800777, Connected/Closed/manual/inactive,
other slots disconnected. This is timestamped history; recheck before outputs.
Cleanup preserves this intentional owner and performs no new read or actuation.
No pending hardware test/loop. Broad physical acceptance remains PARTIAL.

## Evidence and remaining work

records/hardware-validation.json is the compact bench result index.
records/current-hardware-tests.json captures stage scope/last observation.
records/archive/README.md explains the checksum-verified raw evidence archive;
its original PROJECT/STATE/REPORT and E001-E078 records preserve detailed lineage.
records/RECORDS.md holds consequential summaries and new E079 evidence.

Remaining: independent physical shutdown observation/calibration as required,
Closed-state physical communication loss/recovery, three real pairs, electrical
TTL acceptance and post-update passive Ethernet cube qualification. Stage7 stays
removed by user, not passed. These limits are not administrative hardware holds.

Human action required for this cleanup: none. Preserve .venv, installed Kinesis,
Git and the live GUI owner. No firmware, wiring, network or trigger changes.

## Requirements

Full current criteria: PROJECT.md; historical detailed criteria/evidence: archive.
Earlier IDs are retained; scope labels distinguish software, readback and physical
acceptance. No broader completion is inferred from this cleanup.

| ID | Short criterion | Validation / evidence | Status |
| --- | --- | --- | --- |
| REQ-044 | Firmware update procedure preparation | E048 / TEST-058, update later completed E050 | PASS (preparation) |
| REQ-043 | Resolve KSC101 through KEH3 Ethernet with minimal code and passive tests (derived, latest PROJECT.md request) | TEST-055 / E045 software path PASS; TEST-056 / E046 hub PASS, confirmed left cube bay silent; human vendor-GUI comparison also hub only | BLOCKED (physical communication) |
| REQ-042 | Revise actual-hardware acceptance procedure (derived, latest PROJECT.md request) | TEST-054 / E044; current evidence reconciliation, snippet compilation and 8 software-device cases | PASS (plan only) |
| REQ-041 | Minimal controller hardware-handling revision (derived, latest PROJECT.md request) | TEST-053 / E043; 346 offline tests and scoped lint/format; actual SDK/bench revalidation pending | PASS (software only) |
| REQ-040 | Holistic review and comprehensive package development plan (derived, latest review request in PROJECT.md) | TEST-045 / E035; source/docs review, two software reproductions, 279-test baseline and prioritized roadmap | PASS (review/planning only) |
| REQ-001 | Python, uv, packaging and lock | TEST-001/025; locked setup, build/package checks, E024 | PASS |
| REQ-002 | Reusable controller, separate GUI | TEST-002/022–024; current software tests, E024 | PASS |
| REQ-003 | USB discovery/identity/connect/reconnect | E050/E053/E077 / TEST-086, serial68800777 | PASS (single USB pair; Ethernet separate) |
| REQ-004 | Physical opening/closure | E075 / TEST-084 five cycles, human confirmed; E077 production readbacks | PASS (requested single-pair sequence) |
| REQ-005 | Feedback vs physical state | E075 human sequence agrees; E077 electronic only | PARTIAL (new shutdown observation/timing absent) |
| REQ-006 | Physical error handling/recovery | TEST-006; real USB/hub/device loss pending | BLOCKED |
| REQ-007 | Physical safe shutdown | E077 / TEST-086 Close/readback/release PASS | PARTIAL (independent closure timing unmeasured) |
| REQ-008 | GUI on hardware | E077 / TEST-086 actual USB callbacks/browser and Ctrl+C cleanup | PASS (single-pair electronic scope) |
| REQ-009 | Setup/troubleshooting documentation | TEST-009/025; updated guides and references, E026 | PASS |
| REQ-010 | Accurate API/architecture/integration/simulation | TEST-010/025; examples/demo/review, E026 | PASS |
| REQ-011 | Actual simulated screenshot, editable diagrams | Historical E016/E023 screenshots; unchanged GUI/diagrams, TEST-035 E024 | PASS |
| REQ-012 | Reproducible documentation workflow | TEST-012/025; demo, references, E026 | PASS |
| REQ-013 | Honest prior documentation delivery | TEST-013; historical scoped E007/E008 | PASS |
| REQ-014 | Focused prior simplification (derived) | TEST-014; historical scoped E009 | PASS |
| REQ-015 | Validate current package (derived) | TEST-015/025; software suite/build, E024 supersedes E009 for changed source | PASS |
| REQ-016 | Explain architecture and retained complexity (derived) | TEST-016/025; current report E024, historical E009 | PASS |
| REQ-017 | Simple hardware-focused visual README (derived) | TEST-018/020/025; updated README E024, diagram E014 | PASS |
| REQ-018 | Multiple-controller/KEH3 compatibility review (derived) | TEST-021; source assessment E015 only | PASS |
| REQ-019 | Three independent GUI panels (derived) | TEST-022; distinct fake devices, HTTP/browser lifecycle, E024 | PASS (software) |
| REQ-020 | Exclusive ownership and cleanup all slots (derived) | TEST-023; duplicate/race/failure/interrupt tests, E024 | PASS (software) |
| REQ-021 | Passive startup and explicit selection | TEST-024 / E077; holds removed by user, default startup still passive | PASS (software and one-pair GUI) |
| REQ-022 | Reproducible package and operating docs (derived) | TEST-025; tests/lint/build/examples/visual review, E026 | PASS (software) |
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
| REQ-033 | Commit and push reviewed changes | TEST-036; implementation 2bce513 pushed and remote verified, E025 | PASS |
| REQ-034 | Five beginner hardware-only tutorial scripts (derived) | TEST-037; five hardware scripts/guide, 243 source/wheel tests, E026 | PASS (software) |
| REQ-035 | Reviewed staged hardware plan (derived, final-plan request in PROJECT.md) | TEST-038; source/procedure review, syntax and six software-device cases, E028 | PASS (documentation only) |
| REQ-036 | Staged implementation with scoped authority | E075/E077; latest user permits autonomous Stage5/6; Stage7 removed | IN PROGRESS (later stages unexecuted) |
| REQ-045 | Newest compatible KSC101 firmware | E050 / TEST-060,1.0.7 and identity repaired | PASS |
| REQ-046 | Implement Stage3/4 | E051 / TEST-062; latest437-test regression | PASS (software) |
| REQ-047 | USB health correction | E053 / TEST-064 and E077 actual USB | PASS |
| REQ-048 | Holistic command/manual interpretation review | E070 / TEST-079; raw interlock remains unknown | PASS (review/correction) |
| REQ-049 | Remove Stage7 | E072 / TEST-081, user scope change | PASS (removed, not tested) |
| REQ-050 | Implement/test Stage5/6 autonomously (derived, PROJECT.md) | E076/E077 / TEST-085/086;437 offline tests, actual USB shutdown/GUI/Ctrl+C | PASS (electronic scope; physical criteria REQ-007 separate) |
| REQ-051 | Enable GUI/hardware; remove holds (derived, PROJECT.md request) | E076/E077; session serial-specific confirmation, live flags/GUI tested | PASS |
| REQ-052 | Actual GUI/hardware user experience and focused GUI design (derived, latest PROJECT.md request) | E078 / TEST-087;440 software tests, real browser actions and USB readback, final layout/reload proof | PASS (electronic/browser scope) |
| REQ-053 | Holistic review, prune, consistency, commit/push (derived, latest PROJECT.md request) | E079 / TEST-088;449 source +449 wheel tests, archive/link/lint checks PASS; publication pending | VALIDATED; COMMIT/PUSH PENDING |
