# Baseline evidence and decisions

## E145 / TEST-155 - Named GUI outputs and pure rendering, REQ-104 stage 2

Expected: remove positional output coupling and separate presentation without
changing DOM IDs, displayed values or device execution. Observed: `_panel_view`
maps component names to property values; `_panel_outputs` derives matching Dash
outputs from that view. `_control_hint` and presentation perform no device I/O.
Removed the separate 48-position schema/result list; callback shrinks 300 -> 195
lines. Total GUI lines 780 -> 777, prioritizing explicit names over compression.
Expanded the existing GUI workflows to one/three panels and included Apply/Read/
Arm/Disarm TTL. The HTTP helper now takes explicit selections and plain branches.

18 tests pass in 0.28 s. All 59 pre-refactor full callback responses, cumulative
SDK-call histories and virtual waits match, including normal actions, partial
discovery, unknown feedback, faulted Close, retained failed release and shutdown.
Ruff check/format and git diff --check pass. Commands/method: TEST-154, with the
updated essential suite. PASS software only; no native SDK/network/device action.

## E144 / TEST-154 - Beginner contracts and guide, REQ-104 stage 1

Expected: explain state/error/ownership contracts and provide a developer reading
path without changing execution. Observed: added driver/fixture docstrings and
cleanup rationale; extended the architecture guide with terminology, source map,
Open/LAN Connect traces and software-only first-change instructions. Driver and
fixture ASTs match HEAD when docstrings are stripped. All 15 tests pass in 0.17 s;
59 before/after callback responses, cumulative SDK-call histories and virtual waits
match for one/three panels, modes/TTL/discovery/faults/release/shutdown. Ruff check
and format --check pass for src/tests; git diff --check passes. PASS software.

Commands: .venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short;
.venv/Scripts/python.exe -B tmp/readability/compare_behavior.py compare;
.venv/Scripts/ruff.exe check --no-cache src tests; same tool format --check --no-cache.
Temporary probe and fictional baseline are ignored under tmp/readability. No real
SDK/network/device operation. Review checkpoint is committed as 2498ee8. Actual
novice handoff remains unexecuted; this stage validates documentation/execution
separation, not independent beginner performance.

## E143 / TEST-153 - Beginner handoff and scaffolding review, REQ-103

2026-10-21; user refinement makes beginner understanding and development takeover
the essential criterion. Expected: identify unnecessary indirection, readability
barriers, missing explanations and a concrete handoff validation method. Observed:
static trace of GUI actions, driver guard/cleanup, LAN discovery, tests and guides
identifies positional output coupling, a 300-line mixed callback, indirect selected
LAN discovery, ambiguous GUI `active` naming and missing state/error explanations.
Passive app construction with one/three panels confirms 51/147 callback outputs:
3 shared and 48 per panel; no SDK or device handle loaded. Existing useful comments
and thin public wrappers support understanding and should remain. See the
[review addendum](../outputs/REVIEW.md#beginner-development-handoff-governing-criterion).
PASS review scope only. No novice developer exercise was performed; independent
beginner takeover remains unvalidated. No production, test, config or hardware
change; no additional functional test run was needed for this documentation review.

## D040 - Readability governs reduction, REQ-103

User's essential criterion supersedes line count as the optimization target.
Recommend an existing-guide developer walkthrough, explicit state/error contracts,
named GUI outputs and a few ordinary action/render helpers. Preserve shared SDK
guards, thin public method signatures and physically motivated comments. Avoid
generated APIs, a new transport framework and worker scheduling without a measured
need. Proposed acceptance is an uncoached software-only newcomer exercise: setup,
trace Open, add a status-bits readout for one/multiple panels, explain discovery
configuration and explain retained ownership/fault behavior. This is review guidance,
not authorization to operate hardware or a claim that the exercise has passed.

## E142 / TEST-152 - Holistic efficiency review, REQ-103

2026-10-21, revision3835d2c. Expected: review communication/latency/simplicity and
reduction possibilities with current source and software-only evidence. Observed:
15 tests pass in0.17s. Existing fake SDK/virtual clock plus Dash callback HTTP
confirm500ms Manual Open,250ms Close,750ms Trigger Start,750ms Apply TTL and
250/750/1500ms refresh waits for1/3/6 connected panels. Selected LAN Connect waits
5s when another configured LAN route is absent; immediate identities alone add
no sleep to configured Connect. Unified discovery with a found host adds5s;
its SDK-list builds number2 without configured routes or3 with one route.
38 tracked files;1952 physical production Python lines. See
[review](../outputs/REVIEW.md) for source locations, method, qualifications and
prioritized recommendations. PASS review only; fake timing cannot establish
real SDK/native/network/optical latency. No production/test/config change or
hardware/network operation. No new physical qualification claim.

## D039 - Prefer fewer waits and focused simplification, REQ-103

Review recommends batching existing full feedback for Connect/Apply, target-route
Connect discovery, shared discovery enumeration and named GUI output/rendering.
Estimated150-300 Python lines may be removable without feature cuts; this is an
unimplemented planning estimate. Preserve identity, ownership, retained-release
handles, all-slot cleanup and explicit read/write semantics. Do not infer timing
guarantees from polling intervals, simply enable HTTP threads under the same hub
lock, or stop broad scanning after the first identity. Review authorizes no new
actuation, discovery or implementation. Baseline source validation stays applicable.

Current test delivery: E141 / TEST-151 below. E138/139 describe the original
baseline before its tests were replaced; their old totals/hashes are historical.

## D038 - Current baseline, REQ-101

Source: user request quoted in PROJECT.md. The current USB/LAN system becomes the
only maintained baseline, with no compatibility adapters or alternate old workflows.
Remove obsolete staged diagnostics, duplicate scripts, supervisor reports, old
screenshots and incremental development records. Keep the two notebooks, current
tests, current guides and compact [physical evidence](hardware-evidence.json).

Historical intent, checkpoints and records are recoverable at Git5ab1f91 and in
hash-verified ignored inputs/private/baseline-5ab1f91. The private executed LAN
notebook and .venv are preserved. These archives are provenance, not active code.

## E138 / TEST-148 - Integrated software baseline

Expected: current USB/LAN/GUI/TTL/identity/ownership/error/cleanup/notebook contracts
pass with source and extracted wheel; removed single-controller GUI adapter and
operator-confirmation API are absent. No real SDK/network/device operation.
Observed: source217 passed,1 optional real-SDK skip; extracted wheel217 passed,
1 skipped. Wheel import origin verified under its extracted directory; all6
packaged Python/CSS files match source bytes. Ruff lint/format PASS. Three fake
controllers complete Manual/TTL/readback/cleanup; every handle released. The new
GUI boundary regression rejects direct-controller construction and missing serial
before device I/O. Remaining callback tests cover all modes, TTL, discovery,
partial failure, stale choices, identity, ownership and fault/interrupt cleanup.
The2 notebooks run12 fake scenarios, including errors/interrupts/passive release.

Tests removed with deleted diagnostics/scripts/confirmation/repetition explain the
251-to217 count change; no current-contract test was dropped to conceal a failure.
The first updated GUI test run exposed its helper supplying no selected serial;
callers now submit explicit selections as the actual GUI does. Scan fixtures use
the current vendor host-address contract. The USB notebook's superseded repeat
exercise is removed; its original template is archived privately.

Commands: .venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short;
Ruff check/format --check --no-cache .; uv build --wheel --offline --out-dir
tmp/baseline-package; extracted-wheel PYTHONPATH import plus full pytest;
python -B -X utf8 tests/simulated_demo.py --api. Scope: fake SDK and actual callback
HTTP, no new browser/bench operation. [Machine evidence](baseline-validation.json).

## E139 / TEST-149 - Baseline tree and documentation

Expected: no obsolete files/compatibility paths/dangling references; current docs
and snippets agree; private evidence/environment remain; package matches source;
generated scratch is pruned. Prior tree:109 tracked files,2,323,179 bytes.
Observed:68 removed files,43 maintained files after2 consolidated evidence files,
about0.54MB (about77% smaller by working-file bytes). Only2 documentation assets
remain.16 Markdown files,2 cleared notebooks/15 code cells, local links/anchors
and5 Python snippets check successfully; no obsolete symbols/references remain.
All46 archived files match their original hashes. The executed LAN notebook hash
remains unchanged and ignored; .venv is present. No private identities were found
in maintained public text. Detailed deletion inventory/hashes are private; Git
history is preserved. Physical qualification remains incomplete.

Exact generated cleanup targets are resolved inside the workspace, checked for
reparse points/tracked contents and inventoried before removal. Final checks and
source/package/archive hashes are in baseline-validation.json. Focused commits,
normal push/remote equality and the baseline marker follow after cleanup.

## E140 / TEST-150 - Baseline publication

Expected: focused commits, clean tracked tree, exact origin/main equality and
baseline-2026-10-21 marker on the final checkpoint. Observed implementation77ede6a,
baseline/tree/docs/evidence d1453d3; cached paths/diffs/whitespace reviewed, both
commits pushed normally. Independent git ls-remote returned
d1453d3730db4c18e1af085dc1637b393bfeb298, equal to HEAD; git status clean. PASS.
Final documentation-only checkpoint records completion. Its annotated baseline
marker and branch are published together, then both refs are checked against
the same final HEAD. No source change after TEST-148; no physical operation.

## E141 / TEST-151 - Rewrite all tests as essential workflows

REQ-102; user request in PROJECT.md. Expected: a newly written, small suite for
normal USB/LAN/TTL, GUI/launcher, both notebooks and essential identity/ownership/
cleanup failures. Production code and private results unchanged; software only.

Replaced all10 test/helper files with3 test modules and1 new shared protocol fake.
2486->405 lines;217 tests/1 optional skip ->15 tests/0 skips. Removed fuzz/type
matrices, implementation traps, speculative races/forged-input checks, the real
SDK opt-in test and preview helper. No old test module remains. The new fake has
no physical TTL/timing model or real SDK/network access. Normal callbacks use
actual Dash Flask HTTP, and both notebooks execute one complete software cycle.
Operational failures retained: wrong identity, failed release retaining ownership,
continuing all-slot cleanup after Close failure, LAN scan failure preserving USB,
and the observed unknown operating-state0 keeping GUI activation unavailable.

Observed: first source run15 passed; extracted-wheel15 passed. Ruff lint/format,
package Python/CSS parity and current source/CSS hashes PASS. Production unchanged
from runtime baseline8e50258. Commands: .venv/Scripts/python.exe -B -m pytest -q
-p no:cacheprovider --tb=short; Ruff check/format --check --no-cache .;
uv build --wheel --offline --out-dir tmp/essential-tests-package; extracted-wheel
PYTHONPATH import-origin check and pytest. Current commands/docs updated; native
operations and physical qualification are outside this test rewrite.
[Machine evidence](tests-validation.json) records scope and hashes. PASS means
the15 essential cases pass; it does not retain the removed suite's coverage claims.
