# Baseline evidence and decisions

## E150 / TEST-160 - Beginner documentation, screenshots and publication

2026-10-21; user requested documentation/README updates, commit/push, beginner
readability and refreshed screenshots. Expected: current guidance, truthful timing
and image scope, unchanged runtime, normal publication to existing origin/main.
Observed: README starts with prerequisites, installation and first use; explains
configuration, feedback, timing and common problems. GUI, setup, API and architecture
guides clarify current-event combined reads, retained checks and direct API contracts.
No claim of total/physical response time or measured novice independence.

Two direct full-page browser JPEG captures show current d7a37f9: overview 1264x828
and expanded-trigger 1264x1180. Whole-session SDK fixture is fictional, with USB/LAN
serials 68000001/68000002 and documentation address 192.0.2.10. Launcher shutdown
control is present; UI expansion and cooperative shutdown verified. Preview reports
fictional handles released and exits 0. No vendor SDK, real device or LAN discovery;
only loopback HTTP. Old PNG replaced; provenance is in docs/assets/README.md.

89 local links/anchors and 4 Python snippets pass; rebuilt wheel's README and all 6
Python/CSS package files match source. All production/CSS/test hashes match TEST-159;
its 26 source/26 wheel functional results remain applicable. Functional tests were
not repeated for documentation-only edits. Machine evidence and capture hashes are
in records/latency-validation.json documentation_refresh. Whitespace checks pass.
PASS documentation/software scope. No physical qualification or novice study.

git push origin main published 448b6b4 and d7a37f9 normally. Independent git ls-remote
origin refs/heads/main returned d7a37f9e96f4a1475296755632e0d461919c1229, matching the
implementation HEAD. This documentation checkpoint is committed and published
after that verified implementation. Final remote equality is checked at session end.

## E149 / TEST-159 - Combined Apply TTL result and final validation, REQ-105 stage 2

Expected: default Apply waits 750 -> 500 ms while keeping the pre-write
Closed/Inactive/Manual check, actual settings comparison and fault cleanup. Before
changing Apply, two new USB/LAN timing tests observe 0.75 s versus expected 0.5 s;
active refusal, ignored-write mismatch and readback-failure checks already pass.
After batching, all 26 source cases pass in 0.61 s; the extracted wheel passes
26 in 0.57 s. Normal Apply retains the prerequisite requests, issues one TTL write,
then requests operating and TTL feedback in one batch and reuses that snapshot.
Active state prevents the write; actual mismatches report failure and preserve
actual settings; read failures disable activation while retaining cleanup.

59 callback steps preserve complete browser responses, discovery calls and
non-target device-call sequences versus the prior saved baseline (TEST-156 already
proved its equivalence to the readability delivery). The five successful target
events retain their request sets and each save 0.25 s; only batching order changes.
Connect's read error and Apply's readback errors use the existing full-status
fault diagnostic. Driver/readiness/layout, polling, discovery, dependency and
notebook sources remain unchanged. Six packaged Python/CSS files and README match
source; extracted import origin verified. Ruff lint/format, local documentation
links/snippets and whitespace checks pass. [Machine evidence](latency-validation.json)
records final source/test/package hashes and scope. PASS software only.

Commands: source pytest and Ruff as TEST-158; uv build --wheel --offline --out-dir
tmp/latency/package using the existing cache; extract, compare bytes/import origin,
run pytest with extracted PYTHONPATH. Functional checks use the existing fictional
SDK and virtual clock, never a live device/network. Native/optical latency and
physical qualification remain unmeasured. No new push is part of this request.

## D042 - Reuse only the completed current-action snapshot, REQ-105

Use existing get_status() batching and an explicit ShutterStatus-or-None return
from the action helper. The callback consumes that snapshot only for the selected
panel in the same locked event; no persistent freshness policy or worker is added.
Reject snapshot errors explicitly, keep Apply prerequisites before its write, and
compare actual trigger_config before success. Leave direct driver setters/getters,
intervals, endpoint discovery and all other action paths unchanged. Prior exact
wait/order equivalence is superseded only for Connect/Apply by TEST-158/159.

## E148 / TEST-158 - Combined GUI Connect feedback, REQ-105 stage 1

Expected: default GUI Connect programmed waits 500 -> 250 ms for USB and LAN,
retaining passive identity/route/ownership and safe fault handling. Before source
changes, existing 18 cases pass; the two new timing tests fail with observed
0.5 s versus expected 0.25 s. After implementation, all 21 tests pass in 0.45 s.
Successful Connect calls the existing full getter once, rejects its error field,
and returns that snapshot to the callback. The callback reuses only this event's
result. Normal call history is Connect, Poll, Identity, Status, Mode request,
Operation request, TTL request; no Enable, output, mode or TTL write occurs.

A failed combined TTL request remains a fault, disables Open/Arm, retains the
handle/selector and permits disconnect. Existing unknown-feedback, wrong-identity,
ownership, cleanup, four-mode, one/three-panel and notebook regressions pass. Driver,
transport, discovery, polling interval and other action paths are unchanged. Ruff
lint/format and git diff --check pass. Commands: source pytest with
-B -m pytest -q -p no:cacheprovider --tb=short; Ruff check/format --check --no-cache
src tests. PASS software-only: no real SDK/network/device operation, measured
transport latency or physical timing. [Current evidence](latency-validation.json).

## E147 / TEST-157 - Readability publication

2026-10-21; user explicitly requested push. Expected: publish the committed
readability delivery normally to its existing upstream and verify equality.
Observed: clean main at 5d829c01a49f4dcea8489af22e9574c4fb7b9153; git push origin
main succeeded from 3835d2c to 5d829c0. Independent git ls-remote origin
refs/heads/main returned the same full hash; HEAD...origin/main was 0/0 and status
was clean. PASS. This documentation-only checkpoint records publication; no
runtime/test/config change, hardware action or force push.

## E146 / TEST-156 - Behavior-preserving readability delivery, REQ-104 stage 3

Expected: readable named action/discovery/render boundaries, same application
behavior and integrated source/package validation. Observed: `discover_panels`
owns choices, `run_panel_action` handles explicit commands, and `update` coordinates
feedback/presentation under the same hub lock. One dictionary per panel replaces
parallel update lists. Coordinator 300 -> 101 lines; GUI 780 -> 807; production
Python 1,952 -> 2,037. Added explanations and named maps are deliberate; there is
no net source-line reduction claim. No new runtime dependency/module/framework.

18 source tests and 18 extracted-wheel tests pass in 0.29 s each. Both source and
wheel match all 59 pre-refactor callback responses, cumulative fake SDK calls and
programmed waits. Layout ASTs and driver executable AST (excluding docstrings)
match revision 3835d2c. Six package Python/CSS files and README match source;
extracted import origin verified. Ruff lint/format, documentation link/anchor and
whitespace checks pass. [Machine evidence](readability-validation.json) captures
the tested file hashes, package and comparison method. PASS software scope.

The default sandbox could not write uv's external cache; an offline build using
the existing cache with scoped execution approval succeeded. An empty local cache
did not contain Hatchling. A layout comparison initially used Windows' default
text decoding; repeating with explicit UTF-8 matched both layout ASTs. Neither
issue required a production/config/dependency change. No real SDK/network/device
operation or new physical qualification. No novice handoff study was performed.

Commands: source pytest and Ruff as TEST-154; uv build --wheel --offline --out-dir
tmp/readability/package; extract wheel, assert import origin and six-file parity,
run the same pytest and behavior probe with extracted PYTHONPATH. Comparison
fixture/method is described in machine evidence and the pre-implementation review.

## D041 - Preserve behavior while simplifying the learning path, REQ-104

The active request requires unchanged behavior. Retain one/multiple-panel DOM IDs,
whole-hub LAN discovery, native timeouts/waits, command/read sequence, route/identity
checks and retained-handle cleanup. Earlier proposed batching, selected-endpoint
discovery, ID unification and workers would change behavior and are deferred.
Keep explicit public hub methods and the small shared driver/adapter classes.
Use named panel values, ordinary functions and short contract explanations instead
of generated APIs or another application framework. Final source/package checks
supersede affected baseline hashes; retained physical evidence remains historical.

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


## E151 / TEST-161 - LAN class capitalization

2026-10-27; REQ-106. Expected: public discovery classes, exports, annotations,
constructors and API docs consistently capitalize LAN, with unchanged behavior.
Observed: both classes renamed; no compatibility aliases. Source validation:
`.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short`
reports 26 passed. Direct imports from the package and controller agree, and
construction of a discovery result containing a device succeeds. Ruff check
and format --check --no-cache pass for both changed Python files; git diff
--check passes. Current source/API guide contain no former mixed-case names.
PASS software only. No real SDK/network/hardware operation; no new wheel test.
Prior artifact hashes retain historical scope. No commit or push requested.


## E152 / TEST-162 - Entire-repository delay audit, REQ-107

2026-10-27. Expected: identify every maintained controller sleep, other application
wait/cadence, command/read path and repeated SDK work; quantify software waits
without device access. Inspected all five production Python files, CSS, tests,
both notebooks and operating docs. Existing source suite: 26 passed in 0.41 s.
81 virtual-clock/fake-SDK observations record USB/LAN GUI modes/TTL, scalar reads,
1/2/3/6-panel refresh, discovery and notebook cells. Pre-change waits: scalar or
snapshot 250 ms; Manual Open 500 ms; Trigger Start 750 ms; Close 250 ms; Read TTL
500 ms. Selected LAN Connect with an unrelated absent route: 5 s; immediate-identity
scan: 5 s; unified discovery with absent route plus scan: 10 s. Native durations
are excluded. PASS audit; these are not physical latency measurements.

Method: run tmp/delay-audit/probe.py with .venv/Scripts/python.exe -B; installs the
existing bench.__wrapped__(pytest.MonkeyPatch) fixture and timestamps device/manager
calls around actual Dash Flask callback HTTP. Source hashes, call counts and
observed virtual waits: [delay-audit.json](delay-audit.json). Full findings and
remaining opportunities: [audit](../outputs/DELAY_AUDIT.md). Raw traces and probe
are ignored local diagnostics. The following authorized change supersedes only
feedback-wait values, not discovery policy or physical qualification.

## D043 - Remove settling assumptions, retain paced discovery, REQ-108

User explicitly requested removal of fixed waits not prescribed by hardware/SDK.
Remove the three unconditional polling_ms/1000 sleeps in feedback reads rather
than assume an SDK polling period acknowledges a request. Keep request/getter
order, health/route checks, faults, cleanup, readiness checks and TTL comparison.
WaitForSettingsInitialized remains the SDK readiness wait. Two discovery loops
retain at-most-100 ms retry pacing until identity condition/deadline: this is
application backoff, not a documented hardware minimum. Deleting it would busy
poll; changing collection completeness or introducing event infrastructure is a
separate change. Do not claim all controller sleeps have been removed.

Primary local evidence: installed Kinesis 1,14,60,27990 header request/get sections
and reflection-only .NET API metadata. No device methods invoked. No prescribed
Python polling-period settling wait was identified. Native response completion
was not proven synchronous; GetStatusBits is documented as latest-received state.
Immediate getters can expose older SDK values. Software validation therefore
establishes preserved calls/checks and removal of Python waits, not fresh-response
acknowledgement, real TTL write confirmation latency or physical safety/timing.
These limits must remain visible in the API/operator guidance and checkpoint.

## E153 / TEST-163 - Fixed feedback sleep removal, REQ-108

Expected: no unconditional polling-period delays in snapshot, TTL or scalar reads;
unchanged SDK method sequences and checks; essential regressions pass; current docs
state latest-available semantics and retained waits. The new seven-getter regression
first FAILed at 1.75 s versus required zero added wait. After removing the three
sleep sites, 27 source tests PASS in 0.42 s using:
`.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short`.
Connect/Apply tests now require zero virtual wait and retain exact request ordering,
active-state refusal, actual getter/readback mismatch, faults and cleanup checks.

The final 81-scenario probe (tmp/delay-audit/probe_final.py) preserves every recorded
SDK method-call sequence/count against TEST-162; Python object addresses are
normalized for argument comparison. All feedback sleep totals become zero;
discovery timing is unchanged and explicit notebook holds remain. Compared source
hashes change only controller.py and the two affected test modules; GUI, launcher,
configuration, CSS, fixture and notebook bytes are unchanged. Ruff check and format
--check --no-cache src tests PASS (9 files); git diff --check PASS. 87 local Markdown
link paths, four Python snippets and both notebook code sources validate.

[Current machine evidence](delay-removal-validation.json) includes source hashes,
81 before/after results, call counts, retained timing mechanisms and scope limits.
README/API/operator/architecture/interface/setup guidance and delivery report are
updated; earlier timing evidence remains historical. PASS software only; no wheel
revalidation, real SDK device operation, network discovery, hardware actuation,
optical timing or response-freshness qualification. No commit or push requested.


## D044 - Batch GUI feedback without cached readiness, REQ-109

2026-10-27; user authorized GUI read reduction/combining with safety checks and
explicitly requested 100 ms background updates. Use cached has_device for local
Discover ownership. Read TTL requests one full snapshot, checks errors/settings,
updates the draft and returns that same event's snapshot for display. Known
Trigger mode requests one full prerequisite snapshot. Cached mode only selects
read breadth; if requested feedback instead reveals Triggered, obtain actual TTL
settings before evaluating readiness. Ordinary Manual/Single/Auto Start remains
operating-only; no added TTL traffic on its normal path. Keep post-command result
reads and hub serialization. Do not reuse the prerequisite as the command result.

Set dcc.Interval to 100 ms; keep the callback-running pause. SDK polling remains
250 ms. Faster browser scheduling neither guarantees a new SDK sample on every
refresh nor establishes 10 Hz physical feedback or maximum command latency.
No driver, launcher, discovery completion, native polling or hardware changes.

## E154 / TEST-164 - GUI read reductions and 100 ms refresh, REQ-109

Expected: no device feedback for Discover ownership, including retained faulted
handles; combined Read TTL and known-Trigger prerequisites; actual readiness/input
checks and post-write results retained; 100 ms interval with callback pause.
Before implementation, focused checks observed seven expected failures and one
pass: the old 1000 ms interval, connected Discover reads, split TTL read ordering
and separate known-Trigger TTL access failed; retained fault ownership already
avoided reads. After implementation the full source suite reports 40 passed in
0.61 s using .venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short.

Focused coverage includes both USB/LAN batching paths, retained disconnect-failure
ownership, Read TTL fault/draft preservation/cleanup, disabled key, no input,
Active/Open, unknown state and read-failure Start refusal. A mode changed from
cached Manual to actual Triggered still reads actual input settings and refuses
Start when no input exists. Successful Trigger Start retains operating feedback
after the Active write. Layout checks confirm 100 ms in one/three-panel apps.

Reused the 81-scenario instrumentation from TEST-163 before/after the GUI change.
All 48 normal callback responses match. 71 recorded SDK sequences are unchanged;
10 scenarios have only the expected batching/removals. Read TTL transport lookups
4->2; known Trigger Start USB6->4/LAN7->5. Discover drops three requests, four SDK
getters and two transport lookups per healthy held panel; e.g. six-panel Discover
transport lookups18->6. Discovery enumeration itself is unchanged. No added wait;
Manual/Single/Auto Start request/getter sequences and TTL counts are unchanged.

Only gui.py and tests/test_application.py differ in runtime/test/notebook hashes
from the preceding working tree, preserving the pending controller/naming changes.
Ruff check and format --check --no-cache src tests PASS (9 files); git diff --check
PASS. 91 local Markdown link paths and four Python snippets validate. The callback
running configuration matches the original AST, including its refresh-disable pause.
Current guidance and report explain combined feedback, mode fallback and 100 ms
scheduling. [Machine evidence](gui-feedback-validation.json) stores source hashes,
81 scenario results and exact call deltas. Raw probes remain in tmp/gui-feedback.

PASS software only. No native device calls, network scan, hardware actuation,
response-freshness qualification, physical 10 Hz claim or new wheel validation.
No commit or push requested; prior source hashes remain historical where changed.


## E155 / TEST-165 - Documentation and integrated pending-change review, REQ-110

2026-10-27; user requested README/docs updates and review of all pending changes.
Expected: review REQ-106..109 source/tests together; truthful current API/timing/
readiness guidance; final source/package validation; no hardware or publication.
Inspected the full pending production/test diff, current guides, relevant evidence
and packaging. No additional confirmed code defect found in static/software review.
No runtime or test files changed in this pass; every TEST-164 source/test/notebook
hash remains exact. No assumption of hardware freshness is promoted to PASS.

Corrected current GUI claims of fresh feedback/settings, clarified latest SDK
values versus request/write acknowledgement, documented the uppercase LAN API
break without aliases, and separated 100 ms GUI scheduling, 250 ms automatic SDK
polling and discovery retry pacing. Replaced the README's 0 ms action table with
mechanisms to avoid implying instantaneous response. Clarified that explicit GUI
requests also run, with nominal 30 status/mode/state requests/s/panel at ten refreshes
per second as a calculation, not measured throughput. Updated commissioning's
remaining response-age/readback qualification, historical review pointers and
screenshot scope. Rewrote outputs/REPORT.md around the final system; the staged
records/evidence retain historical results. Review: outputs/CHANGE_REVIEW.md.

Observed source suite: 40 passed in 0.69 s. Newly built/extracted-wheel suite:
40 passed in 0.62 s with PYTHONPATH pointing at tmp/final-review/wheel; import origin
verified before tests. Passive wheel import leaves the SDK unloaded and no owners;
LANDevice/LANDiscovery exports and construction pass; mixed-case aliases are absent
from package and controller. All six packaged application files match source bytes;
wheel metadata matches the final README. Ruff check/format --check --no-cache src
tests PASS (nine files); final git diff --check PASS. 17 Markdown files validate:
93 local links, ten local heading fragments, four Python snippets and 15 notebook
code cells. Snippets are parsed, not executed against hardware.

The first isolated offline uv build failed because its selected empty workspace
cache lacked hatchling. Existing default-cache hatchling 1.32.4, pathspec and
trove_classifiers were then imported read-only under python -B; calling the
hatchling.build.build_wheel backend built the wheel successfully without download
or dependency changes. Independent package inspection and wheel tests followed.

Current machine evidence: records/change-review-validation.json stores final
runtime/test/notebook and current document hashes, package hash/parity, commands,
results and review scope. Stage TEST-164's 81-scenario/48-browser-response comparison
retains current source applicability. Prior 250/500/750 ms waits and 1 s GUI cadence
are historical; prior physical observations do not qualify this revision.

PASS software documentation/review/package validation. The significant open gap
is real SDK response freshness/write acknowledgement after sleep removal; current
fakes respond immediately and cannot establish it. Native/queued latency, 10 Hz
physical updates, optical timing and electrical TTL qualification remain UNTESTED.
No real SDK device calls, network scan, hardware action, commit or push performed.


## E156 / TEST-166 - Publication preparation

2026-10-27; subsequent explicit user instruction: "commit and push". Expected:
commit only the reviewed REQ-106..110 delivery; normal push to existing origin/main;
verify exact remote equality. Preflight: branch main, origin
git@github.com:cct1123/thorlabs-shutter-control.git; local HEAD and independent
origin/main read both e01054c431bc128a1ac1543e809569e26fcb1919. TEST-165 source/test/
notebook and document hashes all match the reviewed checkpoint before these
publication notes. Therefore 40 source + 40 extracted-wheel results retain their
scope; no new source validation needed for publication-only documentation.

The sandboxed Git SSH helper initially failed Windows CreateFileMapping access;
the same read succeeded under the authorized elevated execution. This was an
execution-environment issue, not evidence of a remote divergence. No hardware,
force push or unrelated paths. PASS preflight only; publication result follows.


## E157 / TEST-167 - Verified delivery publication

2026-10-27; explicit user commit/push instruction. Expected: reviewed paths only,
normal push to existing origin/main, independent exact remote equality and clean
checkout. Observed: 24 delivery paths explicitly staged; cached diff/whitespace,
evidence JSON and TEST-165 source hashes checked. No scratch/private/environment
paths were staged. Commit 54619a01361998ff7edf08063fa01f90125ca71d, "Remove fixed
feedback waits and streamline GUI updates", pushed normally from main to existing
origin/main. git ls-remote --heads origin main independently returned exactly
54619a01361998ff7edf08063fa01f90125ca71d, matching HEAD; git status --short was empty.
PASS publication of the reviewed delivery.

Only STATE.md, outputs/REPORT.md and this record change in the accompanying final
publication checkpoint. Runtime/test/notebook hashes remain identical to TEST-165,
retaining its 40 source/40 wheel validation. Review document hashes are historical
for the pre-publication notes. The checkpoint is committed/pushed normally to the
same branch and remote equality/clean status are checked again before handoff.
No hardware operation, force push or unrelated file change.


## D045 - Direct protocol clean break, REQ-201..212

2026-11-04; current user explicitly requests a complete rewrite with no Kinesis,
Thorlabs software/SDK dependency or compatibility. PROJECT.md now contains the
full supplied engineering task. Replace the SDK implementation/API/GUI/templates,
not adapt it. Retain historical records and physical evidence under their original
scope. Use one canonical direct-protocol owner, reused by DiamondGUI. Preserve its
target methods and logical identities while intentionally replacing the constructor
and enforcing qualification/readback/fault policy. No commit or publication authority
is inferred from old requests. No hardware authorization window exists now.

## D046 - Unsupported routes and physical contracts stay unavailable

Manufacturer SRC-001 Issue 36 establishes direct USB framing and KSC101 solenoid
commands; SRC-002 HA0368T Rev D describes KSC101-specific physical/trigger behavior.
SRC-003 DOC-103012 Rev E establishes KEH3 ports and USB/Ethernet restrictions, but
does not establish the direct framing/management identity/firmware contract.
QMI revision 7b02875043985abd6366d902c1cf32af240a6881 is a reference only, not evidence
of KSC101/KEH3 support. No code was copied; licensing notice retained.

Do not guess unwrapped APT-over-TCP or hub addresses. Reject unresolved routes at
the owner boundary, including injected transports. Keep VCP read-only until its
bridge-reset equivalence qualifies; keep TTL/cycles and finite exposure/duty loads
unavailable. Only documented, qualified continuous-duty manual loads can write.
These restrictions are unmet engineering scope, not waived acceptance criteria.
APT lacks transaction IDs: quarantine known ambiguous/late responses and document
the remaining arbitrary same-type ordering limitation without claiming an ACK.

## E158 / TEST-201..207 - Direct implementation and final offline verification

2026-11-04. Expected: hardware-free imports/help/verification; no old SDK loader or
compatibility API; exact identities/routes; validated framing; pre-output policy;
single-flight freshness/deadlines; priority cancellation; ambiguity and cleanup.
Observed on final hashes in records/direct-validation.json: 59 source tests and
the same 59 installed-wheel tests PASS, zero failures/errors/skips. The clean uv
environment contains no pythonnet/clr/ftd2xx/serial module and requires no Thorlabs
application or SDK DLL. Main Ruff lint/format PASS. The locked dev build backend
produces a wheel whose Python files match source byte-for-byte. Missing and stale
lockfiles are separately rejected; locked dependencies install with hash checks.

Command: uv run --locked python scripts/verify.py (with UV_CACHE_DIR pointing at
the project-local cache in this sandbox). It performs offline resolution checks,
source tests, locked-backend wheel build, clean uv environment/dependency install,
clean import/help and exact wheel tests. One-time download of already-locked
hash-verified dependencies populated the cache; final verification runs offline.

Byte-level fakes exercise all frame split boundaries/coalescing, wrong addresses,
channels/payloads, interleaved messages/faults, stale and delayed responses, partial
output writes, changed identities, duplicate routes, cross-process ownership,
concurrent controllers, active-query/hold cancellation, total deadlines, separately
bounded cleanup, persistent uncertainty, original-plus-cleanup errors, and retained
obligations after passive release. No output replay or wrong-route cleanup passes.
Electrical results never assert optical closure. Simulated protective dispatch
meets 250 ms; reported hold dispatch 0 ms reflects GetTickCount64's 15.625 ms clock
resolution. No native/physical dispatch or shutter timing was measured.

Initial filesystem-sandbox pytest temp ACL failures required running the inspected
offline suite outside that restriction. A nonfinite-input diagnostic assertion,
uv pip sync argument and uncached locked wheels were corrected. Final results
above supersede those failed intermediate attempts. No instrument was opened,
enumerated, commanded, reset or reconfigured; no driver package/binding changed.

## E159 / TEST-211 - DiamondGUI integration, software only

2026-11-04. Expected: reuse its existing manager-owned shutter interface, retain
logical names/CH/serial/routes, prevent a competing SDK owner and make protective
Close reach active owner work. Observed: 29 focused tests PASS, zero skips/errors.
Command from the DiamondGUI root: uv run --locked --group dev python -m pytest
hardware/optics/tests/test_shutter.py gui/tests/test_shutter_control_page.py
-m "unit and not hardware" -q -p no:cacheprovider, with an isolated temporary
basetemp and XML output records/diamondgui-tests.xml in the control project.
Inspected root/test fixtures isolate device access and runtime paths; gui.main
was not imported and no application was launched.

Canonical owner import, passive factory matching page metadata to new TOML,
public status schema, command-result reuse, passive rendering and protective
Close-before-page-lock pass. The unexecuted notebook remains gated/off with zero
outputs. Shutter registration remains disabled. Other native dependencies remain
for other instruments. Integration changes only the allowlisted paths/hashes in
records/diamondgui-migration.json; unrelated dirty work is retained. Existing
style drift in shared config/manager/page was verified against saved preimages;
unused rotator MotionLimits and unrelated formatting are not changed. New shutter
owner/tests pass lint/format; scoped page lint passes.

## E160 / TEST-212 - Delivery checkpoint and blocked handoff

2026-11-04. Expected: complete operator/source/traceability/matrix/cutover documents,
current evidence links and honest separate route/physical/driver results. Observed:
records/delivery-validation.json audits current local links, source/evidence hashes,
wheel parity and integration hashes. README, STATE.md and outputs/REPORT.md describe
the direct-protocol system. Former review reports are labelled historical; removed
tutorial templates had zero outputs/execution counts, and old GUI images/CSS were
specific to the removed implementation. Private inputs, datasets, old physical
records and other instruments are retained.

PASS software documentation delivery; BLOCKED engineering acceptance. Required
KEH3 direct contracts/routes, actual shutter specification/mapping/optical behavior,
native driver arrangement and reconnect/reboot/endurance remain unverified. Supply
the deployment evidence package in STATE.md to resume. Bench actuation and any
driver cutover require their precise authorized window/conditions before execution.
No source approval, SDK readback, process exit or communication release is treated
as evidence of physical closure. No commit or push performed.

## E163 / TEST-214 - QMI discovery and communication source investigation

2026-11-05. REQ-214 derives from the current user request to investigate QMI.
Expected: distinguish device enumeration, configured selection, identity checks,
transport dependencies and wire protocols, including relevance to KSC101/KEH3.
Observed: GitHub commits/main API returned SRC-005 revision
7b02875043985abd6366d902c1cf32af240a6881; recursive tree inventory and 17 downloaded
source files inspected. APT controllers use configured pyserial VCP ports;
USBTMC/HID enumeration applies to other families. No KSC101/KEH3 driver found.
PASS source investigation only. docs/qmi-discovery-review.md records methods,
limitations and pinned upstream links. No hardware was enumerated, opened or
commanded; no runtime code, driver binding, existing acceptance or authority changed.

## E164 / TEST-215 - Beginner tutorial notebooks, software only

2026-11-05. Requirement source: user's request for separate beginner notebooks on
discovery, connection, status query, settings, modes and ON/OFF; PROJECT.md captures
derived acceptance. Expected: six standalone current-API notebooks, hardware-free
saved defaults, explicit device/write gates, accurate feature limitations and
separation of electrical/optical state, simulated opt-in paths and error cleanup.

Observed: 18 tests PASS, zero skips/failures; records/notebook-tests.xml.
Command: uv run --locked --offline --no-sync python -m pytest
tests/test_tutorial_notebooks.py -q -p no:cacheprovider
--basetemp tmp/pytest-notebooks-final --junitxml records/notebook-tests.xml.
Default cells execute from repository root and notebook directory. Byte-level
simulated transport checks cover identity/status, explicit Single-to-Manual change,
one ON/OFF pair and partial-write failure preserving original/cleanup errors with
no ON replay or OFF frame on a transmit-misaligned stream.

All six PASS nbformat schema, relative Markdown links and default Jupyter execution
in one shared local kernel with namespace resets. records/notebook-validation.json
retains that successful run; saved tutorials retain empty outputs/execution counts.
The optional notebooks dependency group locks JupyterLab/ipykernel separately from
driver runtime. uv lock --check --offline and focused Ruff lint/format PASS.
UV_CACHE_DIR points to project-local .uv-cache. Python optional GUI/VCP/D2XX extras
were restored after notebook dependency sync; no native binding was changed.

Initial sandbox runs hit pytest/Jupyter Windows ACL restrictions. Offline tests
passed outside that restriction. Repeated kernel/context creation intermittently
failed with ZeroMQ timeout, including a later run of the saved verifier. One full
six-notebook run via tmp/validate_tutorials.py passed with shared-kernel namespace
resets; scripts/verify_notebooks.py retains that procedure for reproduction. This
is evidence of notebook execution, not reliable repeated-kernel startup. Physical
operation remains UNTESTED. No device enumeration/connection/output, native driver
change, commit or push occurred. Prior engineering blockers remain unchanged.

## E165 - Local discovery comparison, source inspection only

2026-11-05. User asked whether the two local repositories use similar discovery.
Inspected thorlabs-control cli.py _discover, transport/d2xx.py list_serials,
transport/serial_vcp.py usb_descriptor, devices/common.py identity validation;
compared shutter-control __main__.py, transport.py and device.py.
thorlabs-control explicitly lists FTDI devices through FT_CreateDeviceInfoList /
FT_GetDeviceInfoDetail or COM ports through pyserial comports. Its VCP open also
checks OS descriptor metadata for the selected port. shutter-control offers no
discovery command and opens configured serial/port directly. Both D2XX paths open
by serial; both verify APT controller model/serial/firmware on the selected route.
D2XX implementation differs: ctypes versus ftd2xx wrapper. Neither selects the
first discovered controller. No enumeration or hardware I/O executed.


## D047 - Reference-driven framing, timing and persistent-mode corrections

2026-11-05; REQ-213, user's explicit local-controller reference instruction.
Initial reference C:/repo/thorlabs-control was clean at d70f2a6e8f494516a3aed169f33bcf6775fdd982.
Its controller, framing, link and timing paths were inspected only. Subsequent
reference commits/dirty notebooks belong to other work; inspected code/document
paths still match the pinned revision. No reference code is copied or added as a
dependency. pyproject declares MIT; no separate LICENSE file was found.

Use perf_counter for high-resolution monotonic deadlines, OFF intervals and
dispatch measurement. Reject known malformed message headers immediately and
make decoder failure terminal, preserving decoded diagnostics and the raw tail.
Use SRC-001 p34's 255-byte bound for the supported protocol revision.

SRC-002 p20 independently confirms that the last used operating mode is remembered
between power cycles. Correct the previous omission in guidance: mode transitions
require separate allow_persistent_mode_changes permission, default false. Selecting
an already Manual/OFF controller must not rewrite it. A refused permission is not
an ambiguous write and does not itself latch an error. No EEPROM command is sent.

A partial/unknown-count write leaves command framing uncertain. Refuse all further
frames on that connection, including cleanup OFF, rather than appending a new frame
to an incomplete command. Preserve the original failure, cleanup refusal and unknown
physical state; require independently protected source and explicit recovery. A
complete-but-late write or receive-only failure still permits a qualified OFF attempt
when transmit alignment is known. It cannot confirm optical safety.

Do not adopt guessed KEH3 stream/address probes as operational support or a
quiet-period resync without a manufacturer latency bound. Existing physical,
firmware, optical and driver acceptance remains open. Rotation code is out of scope.

## E161 / TEST-213 - Controller reference comparison and regression reproduction

2026-11-05. Expected: inspect the user-selected controllers, verify material
findings against manufacturer sources, implement warranted improvements without
copying weaker acceptance assumptions or granting hardware authority.
Observed: 11 new timing/schema/mode cases failed before implementation; two
partial/unknown-write cleanup cases failed while the complete-but-late control
case passed. All pass after D047. docs/controller-reference-review.md records the
adopted and deliberately retained differences. records/controller-reference-validation.json
pins inspected Git blobs, manufacturer source hashes and final validation scope.
PASS source comparison and simulated regression correction only.

## E162 / TEST-201..207, TEST-211..213 - Reference follow-up validation

2026-11-05. Final command: uv run --locked --offline python scripts/verify.py
--tests tests/test_owner.py tests/test_protocol.py tests/test_application.py.
Observed: 72 selected controller source tests and the same 72 isolated-wheel tests
PASS, zero skips/failures/errors. Locked dependency installation, no-SDK/native
module import/help, missing/stale lock rejection, source/wheel Python byte parity,
scoped lint/format and stable pre/post source/test/dependency hashes PASS.
The verifier records explicit selection and refuses drift during execution.

The initial broad verifier snapshot was invalidated by concurrent notebook/test
development. That unrelated work was preserved; its optional dependency group is
present in the final lockfile, and its evolving tutorial suite is outside the
selected controller result. A restricted metadata-read command attempted network
resolution during that update and failed; final verification is locked and offline.
The earlier delivery-audit snapshot is retained in
records/reference-before-delivery-validation.json; E158..160 remain historical.

29 existing, inspected DiamondGUI shutter tests PASS against the final owner.
The first locked attempt rejected stale local-package metadata; uv lock refreshed
only the notebook-group metadata already present in the local package. The outer
130 package identities, versions and sources are unchanged. No DiamondGUI source
edit occurred. Existing unrelated style drift is retained under E159's scope.

The high-resolution clock is QueryPerformanceCounter (reported 100 ns resolution).
Exact source/wheel simulated protective dispatch values are stored in the XML and
reference evidence JSON; both meet the 250 ms threshold. These individual software
measurements do not establish native dispatch, electrical/optical timing or safety.
No hardware query/output, network probe, driver/firmware change, application launch,
commit or push occurred. REQ-213 is PASS software; project acceptance stays BLOCKED.

## E166 / TEST-216 - Explicit D2XX/VCP discovery and retained identity gate

2026-11-05. User-authorized requirement REQ-216 is captured in PROJECT.md.
Expected: explicit inventory without device open, config loading, owner creation,
automatic selection or identity bypass; empty and failed enumeration distinguishable.
Implemented lazy discovery helpers using ftd2xx createDeviceInfoList once and
getDeviceInfoDetail(update=False), or pyserial comports. D2XX returns serial,
VID/PID, description and open flag; VCP returns port/hardware ID/description.
CLI dispatches inventory before configuration and never constructs a ShutterHub.
Missing extras/native library or enumeration errors fail nonzero. Existing exact
serial opens, identity/firmware checks, ownership and VCP restrictions are retained.
README/setup/discovery notebook document explicit commands and candidate limitations.

Validation: UV_CACHE_DIR set to workspace .uv-cache;
uv run --locked --offline --group dev --extra gui python scripts/verify.py.
PASS: 101 source tests (0.99 s), 101 isolated-wheel tests (1.31 s), lint/format,
locked backend build, no-SDK/native-module imports/help, missing/stale lock rejection
and passive example. records/direct-validation.json captures commands and hashes;
records/offline-tests.xml and wheel-tests.xml capture cases. New TEST-216 cases
mock both inventory backends and test absent config, no-open/no-owner boundaries,
other-device metadata, empty results, missing optional modules, enumeration failure,
missing explicit target and model/serial/firmware mismatch refusal before control.
Import/help test also covers discover --help without native imports.

Initial uv default-cache access and sandboxed pytest temporary-folder ACL failures
were environmental; workspace cache and approved offline verification outside that
filesystem restriction succeeded. No native inventory, hardware enumeration,
connection, actuation, driver change, commit or push was performed. Physical,
KEH3 and driver acceptance remain blocked; this is software-only evidence.
E165 renumbers the earlier local comparison heading to avoid collision with the
pre-existing E164 tutorial evidence; its findings remain historical.


## D048 - Keep KEH3 candidate diagnostics separate from operational qualification

2026-11-05, REQ-208/217. Manufacturer Rev E section 4.3/Figure 17 specifies
ports and USB IN exclusion. APT Issue 42.1, the inspected official example trees
and the local reference do not establish KEH3 framing, hub identity, route
addresses or firmware applicability. A controller identity reply cannot identify
its containing hub. Implement pure capture analysis and a separate bounded,
explicit candidate query, preserving rejection by the normal owner. No acceptance
file, inference from a different Ethernet controller, or matching child identity
may enable operation. No lab query window is authorized by this offline request.

## E167 / TEST-217 - KEH3 manufacturer investigation and offline diagnostics

2026-11-05. Human scope: focus on Ethernet using the local reference/manufacturer
docs and implement everything possible offline. Expected: reproducible source
findings; bounded/no-replay TCP diagnostic; malformed, fragmented, ambiguous,
wrong-identity, late and cleanup-failure handling; no operational qualification
or unauthorized socket access. PASS offline preparation only. REQ-208 BLOCKED.

Implemented ethernet.TCPTransport and keh3.analyze_capture/KEH3Probe; CLI
keh3-analyze and explicitly gated keh3-probe. Only HW_REQ_INFO is sent by the
candidate probe, to one explicitly supplied generic APT candidate address on one
configured endpoint. No scan, reconnect, mode/output/configuration command occurs.
The probe shares controller/endpoint claims and retains them after failed close.
Reports always mark hub identity unverified and operational routing unavailable.
Normal ShutterHub still rejects KEH3 routes before I/O, including injected I/O.

Final command: UV_CACHE_DIR set to workspace .uv-cache;
uv run --locked --offline --group dev --extra gui python scripts/verify.py.
Observed PASS: 131 source tests, 131 isolated installed-wheel tests; locked build,
source/wheel byte parity, stable pre/post source/test/dependency hashes, lint/format,
passive example/import/help without SDK/native modules and missing/stale-lock
rejection. Separate focused command: uv run --locked --offline --group dev python
-m pytest tests/test_keh3.py -q -p no:cacheprovider --basetemp
 tmp/keh3-final-offline-2 --junitxml records/keh3-tests.xml: 18 PASS (0.19 s).
A split-boundary test covers all 90 positions of the identity frame. Actual socket
coverage is localhost only; all device replies are simulated. Hashes, tree IDs,
PDF source URLs and command arrays are in records/keh3-validation.json.

Intermediate failures are not concealed: an earlier verifier used the same wheel
folder for build artifacts and pytest basetemp, deleting its own built archive;
the build output now uses build-wheel. Intermittent localhost connection timeouts
also occurred (including a focused 17 PASS/1 FAIL run). Three direct localhost
connects and the isolated failing test then passed; the final full source/wheel
and focused suites passed. The timeout cause remains unconfirmed. These results
do not establish Windows, lab-network, hub or physical reliability.

APT Issue 42.1 PDF SHA256 is
b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed;
its 443-page text has no KEH3/40303 contract. The two official Thorlabs example
repository inventories have no KEH3 paths. This is a bounded source finding,
not proof that a private or future contract cannot exist. See
 docs/keh3-offline-validation.md for the exact outstanding manufacturer request.
No laboratory socket, device query, output, driver change or physical actuation
was performed. Project acceptance remains BLOCKED, not validated completion.

## D049 - One control/cleanup contract and full-suite verification

2026-11-05, REQ-218; user requested comprehensive review, obsolete-code removal,
fixes, consistency, substantial code/script simplification and a local commit.
The user explicitly confirmed that all pending changes should be reviewed together.
Retain the direct APT migration and separate KEH3 diagnostics, preserving the
DiamondGUI owner methods and status schema. Remove SDK runtime/templates/assets
and duplicated internal state/paths, without weakening physical acceptance or
introducing compatibility aliases, fallback or implicit actuation.

Use one ON/pulse ambiguity guard, one priority OFF/cleanup boundary, one identity
decoder/matcher and one passive pulse validator. Never reuse an earlier OFF
success as the current cleanup outcome. A pending protective request owns its
cancellation event; recovery must defer rather than clear it. Queries and native
opens check their budget/cancellation before transport access. GUI cleanup has
one owner. Bound capture-file reads rather than relying on a prior file-size check.

The simplified verifier always runs the complete source and exact-wheel suite.
Share command/test orchestration, discover the wheel filename, compare wheel
Python bytes against source, and hash all source/tests/scripts/tutorials/example
configuration/dependency inputs before and after. Keep build and pytest directories
separate. Use the uv isolated interpreter runner; retain failure evidence without
claiming a root cause for observed localhost timeouts. Historical records and
review documents remain history; STATE.md and REPORT.md describe this checkpoint.

## E168 / TEST-218 - Comprehensive review and final integrated software evidence

2026-11-05. Expected: remove obsolete implementation paths, simplify repeated
control/verification logic, correct supported defects, preserve owner interfaces
and uncertainty/identity/interlock boundaries, and commit the reviewed result.
PASS software review; engineering deployment remains BLOCKED.

Four added regressions failed before implementation: ON retained a previous OFF
cleanup message; failed pulse OFF displayed stale successful cleanup; recovery
cleared a pending protective event; and a cancelled query read the transport.
All four pass after correction. Additional passing checks cover empty hub-only
fields on USB routes, passive shared pulse validation, expired native-open budgets,
single GUI cleanup ownership and bounded offline capture-file reads. The receive
queue, redundant OFF-interval state, diagnostic conversion helper and unused TCP
receive helper were removed. Tutorial content is unchanged apart from LF line
endings; Ruff's LF policy is explicit. API/architecture/checkpoint/report are
reconciled. Old SDK tutorials, CSS and GUI screenshots are absent.

Final command (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --group dev --extra gui python scripts/verify.py.
Observed: 131 full source tests and the identical 131 installed-wheel tests PASS,
zero failures/errors/skips; lock, lint, format, locked-backend build, clean
hash-checked dependency installation, no-SDK/native-module import/help, wheel/source
byte parity, stable pre/post input hashes, missing/stale-lock rejection and passive
example PASS. Evidence: records/direct-validation.json, offline-tests.xml and
wheel-tests.xml. The verifier no longer offers partial-suite selection or assumes
a particular wheel version. Saved tutorial code paths are exercised offline and
on simulated transports; the earlier real-kernel execution stays historical.

Affected integration command from C:/Users/HFNV/diamondgui:
uv run --locked --offline --no-sync python -m pytest
hardware/optics/tests/test_shutter.py gui/tests/test_shutter_control_page.py -q
-p no:cacheprovider --basetemp C:/repo/thorlabs-shutter-control/tmp/review-diamondgui
--junitxml C:/repo/thorlabs-shutter-control/records/diamondgui-tests.xml.
Observed: 29 PASS, zero skips, 0.22 s. No external source/dependency files were
edited or synced, and no application/runtime/device owner was started.

Initial sandboxed pytest encountered temporary-folder ACL failures; the same
software-only checks passed outside that restriction. Two fresh-interpreter
full-wheel runs encountered localhost TCP connect timeouts while the isolated
failing test passed separately. Final complete runs through the uv isolated runner
passed. A temporary build/test directory collision was corrected; final artifacts
use separate build-wheel and wheel folders. The timeout cause remains
unconfirmed, with no general Windows/network reliability claim. Failures were not
skipped or relabelled as PASS. Simulated dispatch values in XML remain distinct
from native latency and optical timing.

records/review-validation.json records the current link/hash audit and size
comparison. No device enumeration/open/query/output, lab-network probe, driver or
firmware change occurred. Local commit is explicitly authorized; no publication
is authorized. REQ-208/209/210 remain blocked under the unchanged physical criteria.
