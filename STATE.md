# Engineering state

## Review validation PASS; publication pending - E084/E085

Latest user authorizes review/fix/prune/commit/push, then removal of the README
privacy section and KEH6/configurable shutter support. README section removed.
Added --slots N/ShutterHub(slots=N); default remains three and grows to fit more
serials. Six/nine fake-device lifecycle tests and actual empty three/six-panel
GUI captures PASS. KEH6 USB expected, not physically qualified; Ethernet unchanged.

TEST-093/094 PASS:487 source +487 extracted-wheel regression cases, Ruff/format,
18 Markdown files/92 local links/6 compiled Python examples, current-file/wheel
privacy and image metadata checks.70 private-original hashes and136 archived
payload hashes verified (137 ZIP entries including manifest).22 temporary capture/
build files removed; redundant handoff widgets and report prose pruned. Existing
physical TTL low-position FAIL remains unchanged. No new hardware operation.

Pending: reviewed allowlist commit, normal push and exact remote verification,
recorded as E086. No force push/history rewrite. Human action required: none.

## Bench and ownership

USB computer -> KEH3 left bay -> KSC101 (alias CONTROLLER_A)/firmware1.0.7 -> SH05R. SDK
Kinesis1.14.60.27990, Python3.12.7 x64/pythonnet3.1, FTDI without a COM assignment.
Actual USB identity/reconnect/Open/Close/shutdown and browser actions have readback
evidence; the user confirmed the earlier five-cycle physical sequence. SDK
interlock clear-bit is unknown; explicit object/serial session confirmation records
normal physical circuit/protection without an interlock write. Known negative,
key, identity and communication checks remain intact. Undefined operating0 is
not relabeled Inactive. Ethernet pre-update discovery found only the hub; no
post-update cube Ethernet PASS is claimed.

Last observed E082 handoff: GUI server running on localhost8050,
all slots disconnected after the test owner released. Last actual
controller feedback Closed/Inactive/Manual with original trigger settings restored.
Recheck transient state before outputs. Historical E078 connected-GUI evidence is
preserved but no longer describes ownership. No pending hardware test/loop.

## Evidence and remaining work

records/hardware-validation.json is the compact bench result index.
records/current-hardware-tests.json captures stage scope/last observation.
records/archive/README.md explains private retention of the raw evidence archive;
private original PROJECT/STATE/REPORT and E001-E078 records preserve detailed lineage.
records/RECORDS.md holds consequential summaries and E079-E084 evidence.
records/ttl-summary.json indexes current no-cable TTL observations and raw hashes.

Remaining: independent physical shutdown observation/calibration as required,
Closed-state physical communication loss/recovery, three real pairs, external-signal
TTL acceptance/active-low response diagnosis and post-update passive Ethernet
cube qualification. Stage7 stays removed by user, not passed. These limits are not administrative hardware holds.

Human action required: none. Preserve .venv, installed Kinesis, Git and the
existing GUI owner. E082 trigger settings were restored; no firmware/wiring/
network changes or hardware reads are required for this review.

## Requirements

Full current criteria: PROJECT.md; historical detailed criteria/evidence: archive.
Earlier IDs are retained; scope labels distinguish software, readback and physical
acceptance. No broader electrical/physical completion is inferred from no-cable readback.

| ID | Short criterion | Validation / evidence | Status |
| --- | --- | --- | --- |
| REQ-044 | Firmware update procedure preparation | E048 / TEST-058, update later completed E050 | PASS (preparation) |
| REQ-043 | Resolve KSC101 through KEH3 Ethernet with minimal code and passive tests (derived, latest PROJECT.md request) | TEST-055 / E045 software path PASS; TEST-056 / E046 hub PASS, confirmed left cube bay silent; human vendor-GUI comparison also hub only | BLOCKED (physical communication) |
| REQ-042 | Revise actual-hardware acceptance procedure (derived, latest PROJECT.md request) | TEST-054 / E044; current evidence reconciliation, snippet compilation and 8 software-device cases | PASS (plan only) |
| REQ-041 | Minimal controller hardware-handling revision (derived, latest PROJECT.md request) | TEST-053 / E043; 346 offline tests and scoped lint/format; actual SDK/bench revalidation pending | PASS (software only) |
| REQ-040 | Holistic review and comprehensive package development plan (derived, latest review request in PROJECT.md) | TEST-045 / E035; source/docs review, two software reproductions, 279-test baseline and prioritized roadmap | PASS (review/planning only) |
| REQ-001 | Python, uv, packaging and lock | TEST-001/025; locked setup, build/package checks, E024 | PASS |
| REQ-002 | Reusable controller, separate GUI | TEST-002/022–024; current software tests, E024 | PASS |
| REQ-003 | USB discovery/identity/connect/reconnect | E050/E053/E077 / TEST-086, controller alias CONTROLLER_A | PASS (single USB pair; Ethernet separate) |
| REQ-004 | Physical opening/closure | E075 / TEST-084 five cycles, human confirmed; E077 production readbacks | PASS (requested single-pair sequence) |
| REQ-005 | Feedback vs physical state | E075 human sequence agrees; E077 electronic only | PARTIAL (new shutdown observation/timing absent) |
| REQ-006 | Physical error handling/recovery | TEST-006; real USB/hub/device loss pending | BLOCKED |
| REQ-007 | Physical safe shutdown | E077 / TEST-086 Close/readback/release PASS | PARTIAL (independent closure timing unmeasured) |
| REQ-008 | GUI on hardware | E077 / TEST-086 actual USB callbacks/browser and Ctrl+C cleanup | PASS (single-pair electronic scope) |
| REQ-009 | Setup/troubleshooting documentation | TEST-009/025; updated guides and references, E026 | PASS |
| REQ-010 | Accurate API/architecture/integration/simulation | TEST-010/025; examples/demo/review, E026 | PASS |
| REQ-011 | Actual simulated screenshot, editable diagrams | Historical E016/E023; E083 unconfigured public captures, private originals retained | PASS |
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
| REQ-023 | Three KSC101s through actual KEH3 USB (derived physical scope) | TEST-026 / physical TEST-003–008; separate three-controller acceptance | BLOCKED |
| REQ-024 | Rename driver, merge hub module and prune (derived) | TEST-027; 99 tests, package, docs and layout parity, E017 | PASS (software) |
| REQ-025 | Rename ShutterHub, centralize construction and prune (derived) | TEST-029; 107 source/package tests, examples and layout parity, E019 | PASS (software) |
| REQ-026 | Simplify GUI construction, preserve independent controls (derived) | TEST-030 historical E020; current TEST-035 regression E024 | PASS (software) |
| REQ-027 | Assess KEH3 Ethernet SDK support and changes (derived) | TEST-032; official documentation/static SDK/source review, E022 | PASS (research only) |
| REQ-028 | TTL configuration/readback and explicit arm/disarm (derived) | TEST-033; static official contract, distinct software devices, E024 | PASS (software) |
| REQ-029 | Independent TTL GUI controls and draft/readback separation (derived) | TEST-033; HTTP/browser checks, E024 | PASS (software) |
| REQ-030 | TTL shutdown and package regression (derived) | TEST-033; failure/interrupt/all-slot tests and wheel, E024 | PASS (software) |
| REQ-031 | Physical TTL configuration/priming/disarm across three shutters (derived) | TEST-034 remains unexecuted; E082 single-pair no-cable subset partial, low-position FAIL | BLOCKED |
| REQ-032 | Consistency review, focused fixes and pruning (derived) | TEST-035; 211 source/wheel tests, E024 | PASS (software) |
| REQ-033 | Commit and push reviewed changes | TEST-036; implementation 2bce513 pushed and remote verified, E025 | PASS |
| REQ-034 | Five beginner hardware-only tutorial scripts (derived) | TEST-037; five hardware scripts/guide, 243 source/wheel tests, E026 | PASS (software) |
| REQ-035 | Reviewed staged hardware plan (derived, final-plan request in PROJECT.md) | TEST-038; source/procedure review, syntax and six software-device cases, E028 | PASS (documentation only) |
| REQ-036 | Historical staged implementation with scoped authority | E075/E077; E080 replaces the ordered workflow; physical criteria remain separate | SUPERSEDED (workflow only) |
| REQ-045 | Newest compatible KSC101 firmware | E050 / TEST-060,1.0.7 and identity repaired | PASS |
| REQ-046 | Implement Stage3/4 | E051 / TEST-062 implementation; current review regressions E084 | PASS (software) |
| REQ-047 | USB health correction | E053 / TEST-064 and E077 actual USB | PASS |
| REQ-048 | Holistic command/manual interpretation review | E070 / TEST-079; raw interlock remains unknown | PASS (review/correction) |
| REQ-049 | Remove Stage7 | E072 / TEST-081, user scope change | PASS (removed, not tested) |
| REQ-050 | Implement/test Stage5/6 autonomously (derived, PROJECT.md) | E076/E077 / TEST-085/086;437 offline tests, actual USB shutdown/GUI/Ctrl+C | PASS (electronic scope; physical criteria REQ-007 separate) |
| REQ-051 | Enable GUI/hardware; remove holds (derived, PROJECT.md request) | E076/E077; session serial-specific confirmation, live flags/GUI tested | PASS |
| REQ-052 | Actual GUI/hardware user experience and focused GUI design (derived, latest PROJECT.md request) | E078 / TEST-087;440 software tests, real browser actions and USB readback, final layout/reload proof | PASS (electronic/browser scope) |
| REQ-053 | Holistic review, prune, consistency, commit/push (derived, latest PROJECT.md request) | E079 / TEST-088;449 source +449 wheel tests, archive/link/lint checks PASS; implementation5445fec pushed/remote verified | PASS (cleanup/publication) |
| REQ-054 | Summarize hardware lessons and simplify future test procedure (derived, latest PROJECT.md request) | E080 / TEST-089; three-stage reference, routine shortcut, aligned links and preserved evidence scope | PASS (reference only) |
| REQ-055 | Autonomous actual single-pair TTL tests with IO1/IO2 disconnected (derived, latest PROJECT.md request) | E081/TEST-090;457 software cases PASS; E082/TEST-091 configuration/priming/cleanup PASS, low-position FAIL | PARTIAL (actual tests executed) |
| REQ-056 | Illustrated docs and removal of real identifiers/credentials (derived, latest PROJECT.md request) | E083 / TEST-092; clean screenshots/photo, current-tree and wheel privacy,93 links,457 software cases | PASS (current shareable files; history excluded) |
| REQ-057 | Review/fix/prune and publish accumulated changes (derived, latest PROJECT.md request) | E084 / TEST-093 validation, E086 publication | IN PROGRESS |
| REQ-058 | KEH6 USB compatibility and configurable shutter count (derived, latest PROJECT.md steering) | E085/TEST-094;487 software regressions, six/nine lifecycle and passive GUI captures; physical scope separate | PASS (software; KEH6 hardware untested) |
