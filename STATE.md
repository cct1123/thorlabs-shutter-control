# Engineering state

## Current checkpoint - review and publication (REQ-082)

Software review PASS; final publication in progress. User confirmed state-only
Open/Close and removal of all software interlock gates. Users manage the physical
circuit. Optional Python interlock readings/confirmation remain informational;
GUI, tutorials and diagnostic helpers do not gate on them.

TEST-122 / E114: current source suite186 passed,1 skipped. Initial failures after
the concurrent edit were reconciled to the user's confirmed contract, preserving
the state-only change. Lint/format and simulation PASS; publication follows. No hardware command or server launch during this review.

Current architecture: KCubeShutter is USB-only; ShutterHub owns explicit per-slot
Ethernet endpoints and dispatch. Setters write/return None; getters request
feedback. Connect verifies identity without requesting operating feedback. Zero
state is unknown. Writes clear cached observations; Close/release remain available
after faults. Open/Close send Active/Inactive only. Explicit enable_device()
provides channel setup; Disarm selects Inactive/Manual. Arm remains the compound
Enable/Triggered/Active operation. GUI manual Open requires Manual and assumes an
enabled controller. Native calls may block; successful writes do not prove closure.

Launch: edit src/thorlabs_shutter_control/config.py, then uv run shutter-control.
Published SERIAL_NUMBERS is empty; choose actual identities locally. Default is
three passive panels. Notebook outputs are cleared and optional repeat is false.
No CLI/environment hardware configuration or interlock confirmation flag.

Tests retain eight modules with representative contracts, error/interrupt/cleanup,
routing, GUI, examples and diagnostic workflows. E108 documents the substantial
reduction and cache cleanup; older exhaustive counts are historical. Source and
wheel validation apply to the current reduced suite.

## Bench state and remaining qualification

Historical topology: Windows USB -> KEH3 -> KSC101 firmware1.0.7 -> SH05R;
Kinesis1.14.60.27990, Python3.12.7 x64/pythonnet3.1. E110 observed passive current-GUI
USB connection. E111 later observed all GUIs stopped and no port8050 listener;
that is the last process observation, not a current ownership/closure guarantee.
Recheck transient hardware state before any authorized bench work.

Changed direct command/GUI paths require physical revalidation. Cube Ethernet,
actual KEH6/multiple real pairs, physical communication-loss recovery, calibrated
shutdown/exposure and electrical TTL remain unqualified. E082 preserves the
unresolved active-low no-cable expectation failure. Stage7 was removed, not passed.
The project is not physically COMPLETE. No hardware test is required for this
software publication request. Human action required: none.

## Evidence and next action

Current review: records/review-publication-validation.json and records/RECORDS.md
E114. Historical bench indexes: records/hardware-validation.json,
records/current-hardware-tests.json and records/ttl-summary.json. Private raw
archive retention: records/archive/README.md. The illustrated supervisor notebook
summarizes historical bench results; its launch examples now match current config.

Next: inspect staged files, commit and push normally to origin/main, then verify
remote hash and clean checkout. Preserve .venv, .git, private inputs and raw data.

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
| REQ-002 | Reusable controller, separate GUI | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-003 | USB discovery/identity/connect/reconnect | E050/E053/E077 historical single USB pair; E104 changes Connect feedback contract | UNTESTED (current path; historical identity evidence retained) |
| REQ-004 | Physical opening/closure | E075/E077 historical sequence; E093 changes Manual action path, bench revalidation pending | UNTESTED (current path; historical sequence PASS) |
| REQ-005 | Feedback vs physical state | E075 human sequence agrees; E077 electronic only | PARTIAL (new shutdown observation/timing absent) |
| REQ-006 | Physical error handling/recovery | TEST-006; real USB/hub/device loss pending | BLOCKED |
| REQ-007 | Physical safe shutdown | E077 historical Close/readback/release; E104 removes implicit Close verification | UNTESTED (current shutdown path) |
| REQ-008 | GUI on hardware | E077 historical USB/browser evidence; E093 changes action/refresh path, bench revalidation pending | UNTESTED (current path; historical GUI PASS) |
| REQ-009 | Setup/troubleshooting documentation | TEST-009/025; updated guides and references, E026 | PASS |
| REQ-010 | Accurate API/architecture/integration/simulation | E104 / TEST-113; updated API/interface/architecture/tutorials and simulation | PASS (current software/docs) |
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
| REQ-028 | TTL configuration/readback and explicit arm/disarm (derived) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-029 | Independent TTL GUI controls and draft/readback separation (derived) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-030 | TTL shutdown and package regression (derived) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
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
| REQ-057 | Review/fix/prune and publish accumulated changes (derived, latest PROJECT.md request) | E084/TEST-093, E085/TEST-094 PASS; E086/TEST-095 implementation a6b9e68 pushed/remote verified | PASS (review and publication) |
| REQ-058 | KEH6 USB compatibility and configurable shutter count (derived, latest PROJECT.md steering) | E085/TEST-094;487 software regressions, six/nine lifecycle and passive GUI captures; physical scope separate | PASS (software; KEH6 hardware untested) |
| REQ-059 | Follow-up consistency review, focused cleanup and publication (latest PROJECT.md request) | E087/TEST-096 software PASS; E088/TEST-097 implementation 25bbe8e pushed and remote verified | PASS (review and publication) |
| REQ-060 | Illustrated Notion HTML supervisor notebook and future reference (latest PROJECT.md request) | E089/TEST-098; rendered reference, private Notion embed/readback and exact attachment match | PASS (documentation) |
| REQ-061 | Remove hashes and revise existing notebook as practical tutorial (latest PROJECT.md steering) | E090/TEST-099; local and Notion tutorial/readback checks | PASS (documentation) |
| REQ-062 | Simple project-configured launch without parser/environment parameters (derived, current PROJECT.md request) | E091 / TEST-100; 489 software tests and lint/format | PASS (software) |
| REQ-063 | Identify GUI Open/Close communication overhead (derived, current PROJECT.md request) | E092 / TEST-101; source inspection and fake callback trace at 1/3/6 connected devices | PASS (software diagnosis) |
| REQ-064 | Faster GUI actions with safety checks preserved (derived, current PROJECT.md request) | E104 / REQ-075 replaces implicit driver safeguards with caller checks | SUPERSEDED (driver contract) |
| REQ-065 | Single-purpose controller reads and removal of repeated checking (derived, current PROJECT.md request) | E104 / TEST-113; specific getters and zero-read setters | PASS (software) |
| REQ-066 | Simple shorter shutter command handling (derived, current PROJECT.md request) | E104 / TEST-113; direct write sequences replace preparation/readback workflows | PASS (software; supersedes old behavior) |
| REQ-067 | Simple shutter Open/Close API notebook (derived, current PROJECT.md request) | E104 / TEST-113; notebook uses explicit getters, five fake cleanup scenarios | PASS (software/notebook) |
| REQ-068 | Explain current Open/Close latency difference | E097 / TEST-106; source inspection and isolated fake API trace | PASS (diagnosis only) |
| REQ-069 | Conditional Close preparation before Open (derived, current PROJECT.md request) | E104 / REQ-075 removes automatic Close preparation | SUPERSEDED (explicit user contract) |
| REQ-070 | Reconcile controller/GUI APIs and fix remaining tests (derived, current PROJECT.md request) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-071 | Update notebook for reconciled API and separate call timings (derived, current PROJECT.md request) | E104 / TEST-113; fake notebook setter timings exclude explicit readback/hold | PASS (notebook/software only) |
| REQ-072 | Earlier serial type diagnostic | E101, string-only expectation replaced by E102 | SUPERSEDED (input contract) |
| REQ-073 | Accept string/int serials | E104 / TEST-113 revalidates normalized identity/confirmation | PASS (software) |
| REQ-074 | Startup zero-feedback retry | E103 retained historically; E104 removes feedback dependency from Connect | SUPERSEDED (explicit user contract) |
| REQ-075 | Direct setters and explicit specific getters (derived, PROJECT.md current request) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-076 | Split, sequential tutorial with local optional-repeat settings | E114 / TEST-122; eight fake control-flow scenarios, published outputs cleared | PASS (software) |
| REQ-077 | USB-only KCubeShutter; hub-owned Ethernet and slot dispatch (derived, PROJECT.md current request) | E108 / TEST-117; 183 reduced contract/integration regressions, GUI/tutorials and software simulation | PASS (representative software suite; physical paths untested) |
| REQ-078 | Remove generated temp/cache and substantially simplify tests (derived, PROJECT.md current request) | E108 / TEST-117; 16->8 modules, 4002->2014 lines; 183 passed/1 skipped; zero generated leftovers | PASS (software cleanup/test delivery) |

| REQ-079 | GUI/controller readiness and retry consistency | E113/E114; real Dash callbacks with software devices | PASS (software; E110 historical passive USB connection) |
| REQ-080 | Remove launcher interlock confirmation setting | E112/E114; passive launch and config tests | PASS |
| REQ-081 | No software interlock gating anywhere | E114 / TEST-122; GUI None/False/True cases; tutorial/diagnostic metadata trap; source audit | PASS (software) |
| REQ-082 | Review, fix, prune, commit and push | E114 / TEST-122; source/wheel PASS; publication pending | IN PROGRESS |
