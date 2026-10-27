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
