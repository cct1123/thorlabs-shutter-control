# Engineering state

## REQ-105 COMPLETE - simple Connect / Apply TTL latency

Source: PROJECT.md current user request. Derived criteria: Connect uses one full
snapshot (250 ms default wait); Apply retains its prerequisite and compares one
full result snapshot (500 ms total default waits). Reuse only the current action's
completed feedback in the callback. Retain route/identity/ownership, no output on
Connect, TTL comparison, faults and cleanup. No changes to polling/discovery or
other actions. Baseline is clean 9d4491c; earlier TEST-156 hashes remain historical
once GUI changes. Physical qualification remains outside scope.

E148 / TEST-158 validates Connect (448b6b4): USB/LAN waits 500 -> 250 ms, no output
or configuration write, combined read fault retains cleanup. E149 / TEST-159
validates Apply: USB/LAN waits 750 -> 500 ms; Closed/Inactive/Manual precondition,
actual readback comparison, faults and cleanup are retained. Each action returns
its completed full snapshot; the callback reuses it only for that current event.

Final source and extracted wheel each pass 26 tests. The 59-callback comparison
preserves browser responses, discovery and non-target SDK call sequences; the five
target events each save 250 ms with unchanged request sets. Lint/format, package
parity and documentation checks pass. Driver, layout, polling/discovery, dependencies
and other actions are unchanged. Current evidence: records/latency-validation.json;
delivery: outputs/REPORT.md. Earlier strict TEST-156 equivalence is historical for
these intentionally changed target waits/request order. Physical acceptance and
calibrated timing remain untested. User subsequently requested documentation/README
updates, commit and push. Publication is authorized to existing origin/main;
documentation validation and publication evidence follow in E150 / TEST-160.

E150 / TEST-160: beginner README now follows setup/first use, configuration, timing
and troubleshooting; GUI/API/developer docs agree with batching. Refreshed overview
and expanded-trigger JPEG captures use the existing fake SDK throughout, fictional
serials/address, and the unchanged launcher layout. Preview GUI shutdown confirmed
fictional handles released and process exit 0. Old PNG is replaced, with provenance
in docs/assets/README.md. 89 local links/anchors and four Python snippets pass;
rebuilt README metadata and six package files match source. Runtime/CSS/test hashes
remain unchanged, so TEST-159's 26/26 results retain their scope. No new novice study
or physical qualification. Implementation d7a37f9 was pushed normally; independent
origin/main readback equals d7a37f9e96f4a1475296755632e0d461919c1229. This documentation
checkpoint completes the requested refresh; final publication uses the same main.

## REQ-104 COMPLETE - beginner readability implementation

Source: PROJECT.md user request to implement readability/scaffolding reduction,
preserve behavior and validate/commit step by step. Derived criteria: approachable
source walkthrough and state/error explanations; named GUI output wiring; clear
action/render separation; readable one/multiple-panel software checks; unchanged
public APIs, DOM IDs/messages, command/read order, waits, discovery and cleanup.
Review checkpoint 2498ee8; contracts/guide 117ff78; named outputs/rendering 568a408.
E144 / TEST-154 and E145 / TEST-155 validate those stages. E146 / TEST-156 validates
the final named discovery/action/render paths and per-panel update dictionaries:
18 tests pass from source and extracted wheel; 59 full callback/call-history/wait
observations match the pre-refactor tree in both. Driver executable AST and GUI
layouts are unchanged; lint/format, package/source parity and doc checks pass.
GUI coordinator shrinks 300 -> 101 lines. Total Python grows 1,952 -> 2,037 lines
with explicit maps and explanations; no net line-reduction claim. Current evidence:
records/readability-validation.json; operation/handoff: outputs/REPORT.md.

Software implementation and staged validation are complete. User subsequently
requested push; E147 / TEST-157 records normal publication through 5d829c0 and
independent origin/main equality verification. Hardware remains outside scope. An actual
uncoached beginner handoff remains untested; no claim of measured novice independence.

## REQ-103 COMPLETE - holistic efficiency review

Source: user request, 2026-10-21: holistic review of communication, latency,
simplicity and codebase reduction possibilities. Derived acceptance: inspect
current architecture; quantify programmed waits with software-only probes;
prioritize reductions while preserving current contracts; report physical limits.
E142 / TEST-152 PASS review: current15 tests pass; fake callback probes confirm
250ms per connected-panel refresh,500ms Manual Open,750ms Trigger Start and5s
LAN identity collection/absent-other-route delay. See outputs/REVIEW.md for
findings, methods and proposed order. These are programmed waits, not calibrated
USB/LAN/optical latency. Production code/config/tests remain unchanged.
No implementation or hardware action is pending; review recommendations require
a subsequent implementation objective. Existing physical qualification gaps remain.

User refinement: beginner developers must be able to understand and take over
development. E143 / TEST-153 completes the scaffolding/readability/docstring/comment
assessment in outputs/REVIEW.md. Static assessment: public API is approachable;
GUI/discovery handoff remains incomplete. Main gaps are positional GUI outputs,
mixed callback responsibilities, indirect LAN discovery and undocumented state/error
contracts. Passive schema inspection confirms 48 outputs per panel. Proposed novice
handoff exercise is UNTESTED; no claim of demonstrated beginner independence.
Readability now governs recommendations; the earlier line-reduction estimate is
secondary. Source/comments/docstrings/tests remain unchanged by this review.

## REQ-102 COMPLETE - essential tests

Historical delivery below; REQ-104 / TEST-156 extends the current suite to 18 cases
and supersedes the old production/test hashes with readability-validation.json.

Source: PROJECT.md latest test-rewrite request. E141 / TEST-151: source and
extracted wheel each15 passed,0 skipped. All tests and doubles rewritten:
3 test modules plus1 fixture,405 lines versus2486 across10 files. Real-SDK opt-in,
preview helper, input-fuzz matrices and speculative/internal checks are removed.
The suite covers normal workflows and selected essential operational failures;
it is not exhaustive. Current evidence: records/tests-validation.json.
Production source/CSS hashes, private results and .venv are unchanged. No hardware
or actual network operation. The runtime baseline marker remains baseline-2026-10-21.

## Runtime baseline - REQ-101

Source: PROJECT.md current baseline request. Prior tree: 5ab1f91, 109 tracked
files, 2,323,179 bytes. Historical records/checkpoints are hash-verified in ignored
inputs/private/baseline-5ab1f91; the executed LAN notebook remains privately intact.

Removed obsolete diagnostic stages, duplicate script tutorials, supervisor output,
superseded screenshots and incremental development records. GUI construction now
requires ShutterHub; operator-confirmation metadata/API and alternate scan-address
format adaptation are removed. Current USB/LAN control and explicit reads/writes
remain. E138 / TEST-148 and E139 / TEST-149 record the original baseline's test/tree
delivery; TEST-151 supersedes that suite with the essential current tests above.
The original baseline tree was43 files versus109 before cleanup.
Implementation77ede6a and pruned baseline d1453d3 are pushed; origin/main was
independently verified at d1453d3730db4c18e1af085dc1637b393bfeb298 (E140/TEST-150).
This final checkpoint is marked baseline-2026-10-21. Physical acceptance remains
incomplete; software completion does not change the limits below.

## Architecture and configuration

Device -> Kinesis transport -> KCubeShutter/owned hub channel -> ShutterHub -> GUI.
Unified Discover combines USB, configured routes and a bounded LAN scan. Explicit
Connect applies the selected detected route. All process handles must be released
for broad scanning; failed releases retain ownership and cleanup. Startup is passive.

Defaults in src/thorlabs_shutter_control/config.py: empty serial/endpoint tuples,
SLOTS=None (three USB panels, or enough for supplied routes/serials), localhost8050,
LAN192.168.1.0..192.168.1.255, maximum256 addresses, open timeout100ms/address.
Kinesis folder defaults to C:/Program Files/Thorlabs/Kinesis. Native calls may block.

## Requirements and validation

| ID | Current criterion | Method | Status |
| --- | --- | --- | --- |
| REQ-105 | Simple Connect/Apply batching with safety checks | TEST-158/159; 26 source/wheel cases; virtual waits and 59 callback comparison | PASS software; physical latency unmeasured |
| REQ-104 | Beginner readability, less positional scaffolding, unchanged behavior | TEST-154/155 stages; TEST-156 source/wheel and 59 behavior comparisons | PASS software; novice study untested |
| REQ-102 | Rewrite all tests as a small essential suite | TEST-151 source/wheel,15 cases,405 lines | PASS software |
| REQ-101 | Slim current baseline, no compatibility paths | TEST-148 source/wheel; TEST-149 tree/docs; TEST-150 publication | PASS software baseline/publication |
| REQ-099 | Unified USB/LAN Discover and detected-route Connect | TEST-148 fake SDK and actual Dash callback HTTP | PASS software |
| REQ-020 | Ownership and all-slot cleanup | TEST-148 lifecycle/error/interrupt regressions | PASS software |
| REQ-075 | Direct setters and explicit getters | TEST-148 controller/GUI/notebook regressions | PASS software |
| REQ-003/004/007/008 | Current physical USB, motion, shutdown and GUI | Authorized bench qualification | UNTESTED |
| REQ-006/023/031 | Physical loss recovery, multiple pairs and electrical TTL | Dedicated bench measurements | BLOCKED by unavailable physical validation |
| REQ-043 | Explicit-endpoint passive KEH3 LAN communication | Retained E128 / TEST-138 observations | Prior revision PASS; current baseline UNTESTED |

## Physical limits

records/hardware-evidence.json retains USB readback/user-observed cycles, passive
one-pair LAN identity/Connect/release, and the unresolved active-low no-cable TTL
position FAIL. These do not qualify changed source, live range scans, Ethernet
actuation, KEH6/multiple real pairs, electrical signals or calibrated timing.
No hardware/network discovery or actuation is performed during baseline cleanup.

## Next action and human action required

No human action needed for software delivery. Baseline provenance marker:
baseline-2026-10-21; current latency delivery is REQ-105. Physical acceptance
requires a separately authorized bench session with the intended topology,
independent source protection and observations recorded under the current revision.
