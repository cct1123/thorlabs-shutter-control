# Engineering state

## Current checkpoint - REQ-100 COMPLETE (software review/publication)

Source: PROJECT.md latest review/prune/staged commit/push request. E135 / TEST-145:
final source and extracted-wheel suites each **251 passed, 1 optional SDK skip**;
lint/format, package parity, simulation, docs/links/snippets/privacy PASS.
Fixed stale LAN reconnection after failed rescan; its regression failed before
the fix. Preserved the executed LAN notebook byte-for-byte in ignored
inputs/private/notebooks; the shared notebook has blank settings/cleared outputs.
Current evidence: records/lan-publication-review-validation.json. E134 browser evidence
remains applicable to the unchanged layout; the Connect guard has callback tests.
Screenshot: docs/assets/gui-unified-discovery.png. Earlier counts/hashes in records
are historical. REQ-099 supersedes REQ-095's manual GUI form.
Implementation/tests committed as 66ebe49; documentation/evidence/pruning as
5bae2a4. Both pushed to origin/main; exact remote hash verified (E136 / TEST-146).
This final checkpoint records that publication. No remaining software action or
pending helper. No hardware/network discovery or actual GUI restart performed.
Physical project acceptance remains incomplete, as detailed below.

## Architecture and configuration

KCubeShutter is USB-only. ShutterHub owns USB/explicit KEH3 TCPIP routes,
configurable slots, range discovery and command dispatch. One GUI Discover action
returns USB and Ethernet serial/route choices. Connect automatically applies the
selected detected route to a released panel. Per-panel transport/endpoint controls
and the separate global LAN block are removed. Retained/failed-release handles
keep ownership and cleanup available. Broad scan requires all process-owned
handles released; skipped/failed transports warn without hiding other results.
Connect verifies serial and route; output commands remain explicit. Setters write
and return None; getters request feedback. Users manage the physical interlock.

| Setting | Shared default / contract |
| --- | --- |
| KINESIS_DIR | C:/Program Files/Thorlabs/Kinesis |
| SERIAL_NUMBERS / ETHERNET_ENDPOINTS | Empty tuples; no real identities in shared defaults |
| SLOTS | None: USB defaults to at least 3; supplied endpoint/serial lists determine LAN count |
| LAN_SCAN_START_IP / LAN_SCAN_END_IP | 192.168.1.0 through 192.168.1.255, inclusive |
| LAN_SCAN_MAX_ADDRESSES | 256; configurable integer 1..256 |
| LAN_SCAN_OPEN_TIMEOUT_MS | 100 ms; integer 50..1000 |
| PORT | Localhost 8050 |

Launch: `uv run shutter-control`, then Discover -> select device -> Connect.
LAN range/timeout are config.py settings; no on-screen range/transport entry is
needed. Configured explicit routes remain supported by Python and startup config.
SDK scan probes port40303, registers KEH3 ports40304..40307, refreshes asynchronous
type68 identities and validates exact TCPIP endpoints. Native calls may block.


## Evidence and physical limits

E128 / TEST-138 observed one actual KEH3/KSC101 explicit-endpoint LAN discovery,
matching identity, Connect and communication-only release. Discovery took0.844s,
release0.953s outside the restricted sandbox. A restricted run hung in native
Disconnect; its helper exited after interruption. The environment cause is not
established. This evidence does not qualify range scanning or blade motion.

The user reports a successful LAN notebook run; independent timing/optical
observations were not supplied. Its executed copy is preserved byte for byte in
ignored inputs/private/notebooks; shared notebook settings/outputs are cleared.
The Open/Close notebook remains unchanged. Historical USB motion/readback and TTL evidence remain in
records/hardware-validation.json and records/ttl-summary.json. Current GUI bench
operation, LAN range scanning, Ethernet actuation, KEH6/multiple actual pairs,
electrical TTL, physical loss recovery and calibrated timing remain unqualified.
Active-low no-cable expectation E082 remains unresolved. Overall physical project
acceptance is incomplete; this cleanup's software requirements pass.

## Pruning and continuity

Repeated progress/checkpoint/report prose is consolidated here and in
outputs/REPORT.md. Append-only records and historical requirement mappings below
retain the chronology. Removed only the unreferenced generated supervisor HTML
preview image, verified cache files and this review's disposable package scratch.
The HTML report/renderer, historical bench/GUI images, validation records, private
inputs and .venv remain. E135 also removed verified generated Ruff/bytecode caches
and its wheel-validation scratch. No pending helper/process or physical action.

Human action required: none for software delivery. Next operator step: restart the
GUI to load changed source, release competing owners and use the documented
USB/LAN flow. Bench qualification remains a separate authorized activity.

## Requirements

Full criteria remain in PROJECT.md. E135 revalidates current software paths;
older rows below retain historical task evidence and its original scope, not a
claim that old test totals or physical measurements describe this revision.

| ID | Short criterion | Validation / evidence | Status |
| --- | --- | --- | --- |
| REQ-100 | Full review, consistency/pruning, staged commits and push | E135 / TEST-145 software PASS; E136 / TEST-146 exact remote hash | PASS (software publication) |
| REQ-099 | Unified USB/Ethernet Discover; remove manual GUI forms | E134 / TEST-144; software/browser PASS | PASS (software) |
| REQ-098 | Repository consistency and pruning | E133 / TEST-143; source/wheel 249 PASS, 1 SDK skip; docs/package/pruning checks | PASS (software) |
| REQ-097 | LAN defaults in config.py | E132; E133 current config/GUI/API regression | PASS (software) |
| REQ-096 | LAN discovery without exact IP | E131; E133 range/identity/ownership/GUI regression | PASS (software; live range scan UNTESTED) |
| REQ-095 | USB/Ethernet choice in GUI | E130 historical form; REQ-099 replaces manual selection with automatic detected routes | SUPERSEDED (GUI controls) |
| REQ-094 | Launcher/GUI LAN routing and notebook result (derived) | E129 / TEST-139; 213 software PASS; human notebook success reported | PASS (GUI software scope) |
| REQ-093 | Match working Kinesis Ethernet connection (derived) | E128 / TEST-137/138; 207 software PASS; actual passive LAN PASS | PASS (connection only) |
| REQ-092 | Vendor-example Ethernet correction | E128 / TEST-137/138; register/build plus connection-change refresh | PASS (passive connection scope) |
| REQ-091 | Diagnose empty LAN cube list | E128; missing asynchronous SDK refresh reproduced and corrected | PASS (discovery defect; earlier transient timeouts not fully explained) |
| REQ-090 | LAN discovery without USB device dependency | E128 / TEST-137/138; async refresh regression and real passive LAN connection | PASS (passive Ethernet; output actuation untested) |
| REQ-086 | LAN ShutterHub-to-cube tutorial (derived, PROJECT.md) | TEST-128 / E120; seven notebook scenarios, 74 affected tests | PASS (notebook/software only) |
| REQ-044 | Firmware update procedure preparation | E048 / TEST-058, update later completed E050 | PASS (preparation) |
| REQ-043 | Resolve KSC101 through KEH3 Ethernet with passive tests | E128 / TEST-138; real discovery, identity, TCPIP endpoint, Connect and release | PASS (one-pair passive LAN; output actuation separate) |
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
| REQ-082 | Review, fix, prune, commit and push | E114/E115 / TEST-122/123; source/wheel PASS; f2934c8 pushed and remote verified | PASS (software publication) |

| REQ-083 | Follow-up review, consistency fixes and publication | TEST-124/125 / E116/E117; source/wheel each188 passed,1 skipped; fd70b46 pushed/verified | PASS (software publication) |

| REQ-084 | Shut down GUI server and devices from launcher button | TEST-126 / E118; actual localhost HTTP exit/listener release plus software cleanup regressions | PASS (software) |

| REQ-085 | Kinesis-style four-mode instrument panels | TEST-127 / E119; source/wheel204 passed,1 skipped; desktop/narrow browser checks | PASS (software) |

| REQ-089 | Prune, commit and push integrated changes | TEST-131 / E123; E124 / TEST-132 exact remote hash | PASS (published) |
| REQ-088 | Documentation, screenshots and integrated consistency | TEST-130 / E122; docs/links/screenshots/regressions | PASS (software) |
| REQ-087 | Modern compact design with Kinesis control layout/four modes | TEST-129 / E121; source204/1, desktop/narrow browser | PASS (software) |
