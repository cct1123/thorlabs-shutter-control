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
[review addendum](https://github.com/cct1123/thorlabs-shutter-control/blob/5d2adc1edeb93a3b827974c12ee957a2b6c9255f/outputs/REVIEW.md#beginner-development-handoff-governing-criterion).
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
[review](https://github.com/cct1123/thorlabs-shutter-control/blob/5d2adc1edeb93a3b827974c12ee957a2b6c9255f/outputs/REVIEW.md) for source locations, method, qualifications and
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
remaining opportunities: [audit](https://github.com/cct1123/thorlabs-shutter-control/blob/5d2adc1edeb93a3b827974c12ee957a2b6c9255f/outputs/DELAY_AUDIT.md). Raw traces and probe
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


## D050 - Live-only example notebooks, without simulated execution

2026-11-05, REQ-215. Active human instruction: "revise all the example notebooks.
directly deal with the hardware . no simulator." Supersedes the earlier
fictional-config/default-skipped and fake-transport notebook acceptance. Keep
REQ-215 / TEST-215 stable and preserve old E164/E168 results as historical.

All six notebooks call production APIs. Discovery directly invokes native D2XX
or VCP inventory without configuration or device open. Other examples require
ignored shutters.local.toml and an explicitly selected name; no example identity
is used as a live default. Read-only operation cells connect directly. Mode and
ON/OFF operation cells require typed confirmation for that serial before opening,
with real policy/identity/interlock checks still enforced by the owner. The ON/OFF
pair remains within one cell; cleanup and release failures preserve the first
error. Unsupported VCP writes, KEH3 operation and TTL/cycle modes remain unavailable.

Notebook validation is static: schema, compilation, local links, cleared outputs.
Remove kernel execution and injected fake notebook paths, rather than enabling
live cells in automated verification. Existing driver/protocol regression fakes
remain offline tests, separately scoped from actual notebook/bench behavior.
The source owner/API and DiamondGUI are unchanged. No physical qualification or
exact actuation window is inferred from a request to revise examples.

## E169 / TEST-215 - Live notebook revision, actual native inventory and static checks

2026-11-05. Expected: six standalone live-hardware examples, no simulator,
no silent skipped-success path, explicit identity/configuration, retained write
qualification and cleanup, no automatic execution of live cells by verification.
PASS static implementation; actual controller/physical execution BLOCKED.

Actual host operation: existing .venv/Scripts/python.exe imported
thorlabs_shutter_control.discovery and called list_d2xx_devices() and
list_vcp_ports() once each, printing rows. Four D2XX entries and six COM entries
were reported; see records/notebook-hardware-inventory.json for the exact output.
No visible descriptor identifies a KSC101. One D2XX row has blank serial/description,
VID/PID 0000:0000 and OPEN flag; this is unknown, not proof of absent hardware.
No entry was opened or selected automatically. shutters.local.toml is absent.
Readback, mode, solenoid, optical state and timing tests were NOT RUN.

Command (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
Observed: six schema/syntax/link/cleared-output PASS results, each explicitly
hardware_execution=NOT RUN. records/notebook-validation.json contains hashes.
No kernel was started, no tutorial cells were executed, and no simulator injected.

Integrated command (same workspace cache):
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
Observed: 129 full source tests (1.28 s), identical 129 installed-wheel tests
(1.50 s), zero skips/failures/errors; lint/format, lock, exact wheel/source parity,
clean dependency installation/import/help, stable input hashes, negative lock
checks and the separate passive script PASS. Test count falls from 131 because
18 old default/fake notebook checks were replaced with 16 static/prerequisite
checks. Existing control/protocol tests remain software-only. Runtime source is
unchanged, so E168's 29 DiamondGUI integration results remain applicable.
records/direct-validation.json, offline-tests.xml and wheel-tests.xml are current.

The initial sandbox verifier failed on Windows temporary-directory access
(WinError 5). The same full software-only verifier then passed outside that
restriction; no test was skipped or relabelled. Final notebook schema checks have
no missing-cell-ID warning. No controller connection/query/actuation, laboratory
socket, driver/binding/firmware change, commit or push was performed. To resume
live controller testing, supply the reviewed exact controller/configuration and
actual setup/qualification; prepare an approved bounded window for write/physical
acceptance. Project deployment remains BLOCKED, not validated completion.


## D051 - One actual read-only attempt on the Windows-identified shutter

2026-11-05, REQ-202/203/215. Human instruction: "try to communicate with the
shutter". Authorizes current native/PnP inventory and exact-target read-only
identity/status communication. Retain all physical, ownership and driver/security
boundaries. No broad COM probing, mode/output command, driver/binding change,
security bypass, or unverified network fallback is justified by this instruction.

Present-only Windows inventory identifies USB VID_0403/PID_FAF0 serial 68800777 as
Kinesis Solenoid Controller. Use this current identity, not the blank D2XX row or
first device. Ignored shutters.local.toml selects logical name shutter, application
channel 0, physical role explicitly unverified, exact serial, D2XX, no policy.
Expected firmware 1.0.7 comes from historical records for this serial and remains
a strict check; no current firmware is inferred. Use canonical ownership locks,
5 s connect/identity and 3 s status budgets, standard production initialization,
communication-only release and no automatic retry. If native open fails, inspect
binding metadata before any protocol or device-state hypothesis.

## E170 / TEST-202 - Actual shutter connection failed at D2XX native open

2026-11-05, actual host/hardware, no simulator. Expected: exact serial 68800777
opens, model/firmware/channel identity verifies, and read-only status returns;
no mode/output commands. Result: FAIL native open; identity/status NOT RUN.

Repeated real D2XX/VCP inventory matches E169: four D2XX entries (one blank/OPEN)
and six COM entries, no named KSC101 descriptor. Sandboxed CIM metadata read was
denied; read-only Windows metadata outside that restriction succeeded.
Get-PnpDevice -PresentOnly confirms Kinesis Solenoid Controller
USB\VID_0403&PID_FAF0\68800777, status OK. This supersedes descriptor-only lack
of identification; it does not prove a functioning protocol path.

Actual command (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --no-sync python tmp/read_only_shutter.py.
The script loads the no-policy config, constructs ShutterHub with normal locks,
and calls connect("shutter"), followed by identify_device/get_status only if
connection succeeds. Finally calls hub.close() and writes the result. It ran
outside the filesystem restriction for canonical LOCALAPPDATA ownership locks.
At 2026-11-05T23:56:04.370481+00:00 it failed in connect with
ftd2xx.DeviceError DEVICE_NOT_OPENED after 0.05634319999808213 s. The failure is
at FT_OpenEx for the exact serial, before USB initialization or APT transmission.
Communication release completed. No timeout, identity mismatch or protocol
failure was observed because no controller request could be sent. No retry.

Diagnostic command:
pnputil /enum-devices /instanceid "USB\VID_0403&PID_FAF0\68800777" /drivers /services /stack.
Observed: device Stopped; class/GUID/manufacturer Unknown; stack CSDeviceControl,
USBHUB3. Get-PnpDeviceProperty reports empty service, driver INF/version and driver;
problem code 0, devnode status 25190400. Parent is
USB\VID_0424&PID_2514\7&22314d84&0&4. Win32_SystemDriver identifies CSDeviceControl
as running CrowdStrike Device Control Service, path
C:\Windows\system32\drivers\CSDeviceControl.sys. The apparent PnP OK versus
PnPUtil Stopped states are preserved; neither is rewritten as a protocol PASS.

Conclusion: current exact-serial D2XX access fails; device presence is confirmed.
No function-driver binding is reported. A CrowdStrike filter is present in the
stack, but its causal role/policy decision has not been established. Do not
claim a firmware/protocol defect or remedy this with a security bypass. Required
resumption: administrator-reviewed restoration of approved USB access and binding
for this exact instance, with any driver cutover under the established downtime/
inventory/rollback rules, then repeat metadata and one read-only attempt.

Evidence: records/live-shutter-communication.json (config snapshot, native error,
exact PnP/stack observations, command/script hash and release outcome). Config is
local/ignored; no policy was fabricated. Prior software test evidence remains
applicable because no runtime/test/notebook source changed. No mode/output,
driver/binding/security change, lab-network socket, unrelated device open,
commit or push occurred. Optical/electrical state and current firmware remain
unknown; deployment remains BLOCKED.


## D052 - Query the user-confirmed Ethernet endpoint without enabling control

2026-11-05, REQ-208/217. User instruction: "try ethernet instead", then
"try 192.168.1.19", followed by the exact current mapping:
SHUTTERHUB_IP="192.168.1.19", SHUTTERHUB_PORT=40303,
SHUTTER_CH_MAP={"verdi shutter":{"CH":0,"SN":68800777,"IP_PORT":40304}}.
User confirms: "Yes—powered, Ethernet connected, USB IN disconnected". This is
human-reported current physical evidence satisfying the KEH3 manual section 4.3
USB IN exclusion; it does not establish optical state or load qualification.

The preserved executed LAN notebook already recorded this IP, bay port and serial;
its historical evidence was used to prepare the candidate before the user supplied
the current map. Its SHA256/provenance are in the artifact. Hub serial/firmware
remain unknown, explicitly marked UNKNOWN in the diagnostic-only config; expected
controller firmware 1.0.7 remains historical. No unknown field counts as verified.

Authorize one separate KEH3Probe on 192.168.1.19:40304, candidate 0x50, one
HW_REQ_INFO (05 00 00 00 50 01), 5 s total budget and canonical serial/endpoint
claims. No scan, retry, other bay, mode/output, settings or route qualification.
Following TCP refusal, test only the user-supplied hub management port with a
TCP connect/close (no payload), one ping and local connection metadata. Do not
send controller queries to the undocumented management protocol or modify any
security/driver configuration. These explicit Ethernet diagnostics supersede
the earlier offline/no-network authority only within this bounded scope.

## E171 / TEST-208 - Real Ethernet: management reachable, shutter bay refuses TCP

2026-11-05 (America/Chicago). Actual lab network, no simulator. Expected: selected
bay TCP opens, one candidate identity request yields KSC101 68800777; matching
identity would remain unqualified for operation. Result: FAIL bay TCP; identity
NOT RUN. Management TCP and ICMP are separate PASS reachability observations.

Initial local metadata: Find-NetRoute selects Ethernet, host 192.168.1.201,
192.168.1.0/24 directly connected, route metric 256. Cached neighbor .19 was
Unreachable with 00-00-00-00-00-00; this was not treated as a current live test.
Sandbox metadata access was denied; the read-only check succeeded outside that
restriction. The manual restriction was checked and human confirmation obtained
before any target socket was opened.

Actual command (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --no-sync python tmp/read_only_ethernet.py.
At 2026-11-06T00:44:03.646229+00:00 (5 November local), KEH3Probe.run returned
probe-unconfirmed: [WinError 10061] No connection could be made because the target
machine actively refused it. Elapsed 2.0469001999954344 s; request_hex/raw_hex
empty, identity null, no frames. Thus no APT request was sent, not a firmware,
framing or identity failure. cleanup_error=null; no retained transport or claim.
The actual diagnostic logical label was shutter_ethernet_candidate; the user's
later explicit label "verdi shutter" refers to the same exact serial/endpoint.

Follow-up command:
uv run --locked --offline --no-sync python tmp/check_hub_management.py.
At 2026-11-06T00:44:33.865658+00:00, TCP 192.168.1.19:40303 connected from
192.168.1.201:23024 in 0.027860099995450582 s and closed successfully. Zero
application bytes sent. Then ping.exe -n 1 -w 2000 192.168.1.19 returned one
32-byte reply in <1 ms, TTL 64, sent=1/received=1/loss=0%. Neighbor metadata now
Reachable, MAC D8-47-8F-93-68-CB. Neither observation identifies a hub/controller.
Get-NetTCPConnection -RemoteAddress 192.168.1.19 then found no current connections
from this PC; other machines/owners remain outside this observation's scope.

Conclusion: the confirmed IP is reachable and accepts the management TCP port;
its configured shutter-bay port refused access. No cause is established. Missing
cube power/placement, another owner, forwarding/initialization/firmware behavior
or network access policy are not distinguished by these observations. The
manufacturer troubleshooting section requests cube power, USB IN absence and
Ethernet indicators; user already confirmed hub power/Ethernet/USB IN state.
The remaining precise human check is cube serial/left-bay confirmation and exact
display/LED state without moving a powered cube, plus any known application owner.
The question is pending. Do not automatically scan, reboot, redock, broaden
address candidates or send unknown management commands.

Artifacts: records/live-ethernet-communication.json (actual config, source hash,
current human map, native failure, no transmitted bytes, released claims) and
records/live-hub-management-tcp.json (TCP/ICMP/neighbor and owner snapshot).
No runtime/tests/notebook source changed; prior source/wheel/static evidence
remains applicable. No mode/output, settings, driver/security change, commit or
push occurred. Hub identity, controller firmware/status, optical behavior and
operational routing remain UNTESTED/BLOCKED, not validated completion.


## D053 - Correct the selected bay from current human evidence, retain control gates

2026-11-05, REQ-202/203/208/217. User replied "middle" to the physical rear-view
bay question. Treat this as a current correction of the prior left-bay/40304 map,
not permission to scan all ports or physically move the cube. SRC-003 section
4.3/Figure 17 and Route.endpoint map middle to 40305. Logical CH remains 0; the
expected serial remains 68800777 and is verified from the reply. Within existing
power/Ethernet/USB IN confirmation and query-only authority, repeat the same
bounded candidate identity method once at this corrected endpoint. This is a
new evidence-driven target, not an automatic retry of the failed left-bay route.

Use the existing KEH3Probe, raw HW_REQ_INFO destination 0x50, 5 s total deadline,
normal canonical serial/endpoint claims and no mode/output/settings. A matching
controller reply does not identify the hub, prove future exchanges/reconnects,
establish manufacturer support or authorize actuation. Do not remove the normal
owner's KEH3 restriction from this one observed identity result.

## E172 / TEST-208 - Actual middle-bay Ethernet controller identity PASS

2026-11-05 America/Chicago. Expected: query 192.168.1.19:40305 returns KSC101
serial 68800777 with allowed firmware and channel count, no mode/output command,
complete communication release. PASS for this one actual identity exchange.

Command (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --no-sync python tmp/read_only_ethernet_middle.py.
At 2026-11-06T00:47:15.450867+00:00, one 6-byte request 05 00 00 00 50 01
received one complete 90-byte HW_GET_INFO response. Actual decoded identity:
serial_number=68800777, model=KSC101, firmware=1.0.7, hardware_version=3,
channels=1. The source/destination and payload layout matched the existing
candidate decoder. First-byte observation 0.005952100000286009 s; total probe
0.06683550000161631 s. These are single software observations, not a distribution,
native latency guarantee or physical shutter timing measurement.

Probe verdict candidate-controller-match-hub-unverified; error=null,
cleanup_error=null; retained_transport=false, retained_claim=false. Request and
complete reply hex, response SHA256, script/source hashes, parameters and current
corrected mapping are in records/live-ethernet-middle-communication.json. Only
one HW_REQ_INFO was sent; no status, mode, output, hub settings, scan, driver or
security change occurred. Standard-library sockets plus the direct APT decoder
were used; no simulator, SDK or native FTDI transport was involved in this probe.

Correct map: SHUTTERHUB_IP=192.168.1.19, SHUTTERHUB_PORT=40303,
SHUTTER_CH_MAP={"verdi shutter":{"CH":0,"SN":68800777,"IP_PORT":40305}}.
Also saved in ignored inputs/private/current-ethernet-topology.json. The prior
shutters.local.toml is the USB commissioning config, not this Ethernet map; no
external DiamondGUI setting was edited. E171 remains evidence of a refusal on
the formerly assumed left bay; it no longer supports a claim that the intended
shutter is inaccessible via Ethernet. The physical-bay question is resolved.

Actual controller identity/firmware on this endpoint are now observed, replacing
historical-only expectation. Hub identity/firmware, other messages, reconnect,
wrong/swapped/empty bays, actual electrical/mode/interlock/optical state, timing,
loads and safe operation remain unqualified. Normal operational KEH3 routes stay
unavailable; project deployment remains BLOCKED. The user's read-only communication
attempt is fulfilled. No runtime/test/notebook source changed, no further test or
identity retry is needed for this result, and no commit or push occurred.


## D054 - Fixed-endpoint Ethernet notebooks with a generic shutter name

2026-11-06, REQ-215. Active user instruction: update all example notebooks to use
Ethernet at 192.168.1.19:40305 for the specified shutter, no simulator; follow-up:
"remove the verdi wording". Use generic label shutter in current examples and
guide. Keep actual serial 68800777, CH 0, middle bay, allowed firmware 1.0.7;
management port 40303 is distinct. Historical evidence labels are not rewritten.

All six setup cells construct this exact validated diagnostic configuration;
no local TOML, USB/COM inventory/fallback or example identity is used. Notebook 1
uses the existing one-query KEH3Probe. The other read cells use one shared example
EthernetReadOnly helper, actual TCP, existing APT Session/KSC101 query methods and
canonical serial/endpoint claims, explicit deadlines, no retry or injection.
Only connect/status/close are exposed. Read failures end the diagnostic session;
close failures retain resources on the reader and preserve original error notes.
Add TCPTransport.read_nowait for Session's unsolicited/late traffic check, using
select with zero wait. Existing real localhost transport tests exercise empty,
fragmented data and EOF. No operational KEH3 route gate is bypassed or removed.

Mode and ON/OFF notebooks read actual diagnostics and present optional owner calls
against the same Ethernet config, explicitly expected to raise UnsupportedRoute
today. No policy is fabricated, raw-write control interface exposed, USB fallback
used or physical permission inferred. ON/OFF cleanup is attempted only after an
ON attempt, preserving first failure and release notes. Read-only status must
not claim optical closure or turn an unsupported state into OFF.

A real status run revealed scalar state 0, not the documented ON=1/OFF=2. Preserve
strict driver rejection and add raw frame hex to the ProtocolError. The helper
retains partial identity/mode/interlock observations with status_complete=false;
notebooks print that partial diagnostic and re-raise. Do not broaden accepted
state values, change modes/outputs or hide the failure to make examples pass.

## E173 / TEST-215 - Fixed Ethernet notebooks: software PASS, complete live status FAIL

2026-11-06. Expected artifact criteria: all six notebooks select shutter/68800777/
CH0/middle 192.168.1.19:40305, no simulator, current APIs, passive setup, actual
read diagnostics, clear write restrictions and preserved first/cleanup failures.
PASS revised artifacts and software; actual complete status FAIL, not completion.

Commands (workspace UV_CACHE_DIR=.uv-cache):
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
Observed six schema/syntax/link/cleared-output PASS; hashes recorded in
records/notebook-validation.json. Lint/format now covers all docs/examples,
including notebooks and helper. Passive tests execute only initial config cells
from root and docs/examples, forbid socket creation and assert exact serial,
endpoint, route and no output policy. No simulated notebook replies are used.

Final integrated command:
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
Observed 131 full source tests (1.15 s) and identical 131 isolated installed-wheel
tests (1.47 s), zero failures/errors/skips. Lock, lint/format, locked wheel build,
clean hash-checked install/import/help, exact wheel/source parity, stable input
hashes, missing/stale lock rejection and separate passive script PASS. XML and
records/direct-validation.json are current. These remain software/localhost
results, distinct from actual lab data. Existing protocol tests retain their
separate offline transports; none substitutes simulated execution of a notebook.

First final-verifier attempt had 12 test-reader failures after Ruff normalized
notebook source to standard line lists; compile expected a string. Normalize
source before compiling in the passive test, then full source/wheel checks pass.
This was a verification-reader defect, not a skipped test or successful device
operation. Source/helper changes invalidated earlier hashes until final checks.

Actual hardware command, authorized read-only continuation on exact user route:
uv run --locked --offline --no-sync python tmp/validate_ethernet_status_notebook.py.
Only notebook 3's exact Python cells execute in a fresh interpreter, no Jupyter
kernel, saved-output modification, simulator or mode/output/settings command.
At 2026-11-06T19:30:27.451897+00:00, identity verified but complete status failed
ProtocolError Unsupported scalar value 0 in 0x04cd, elapsed 0.17213740000443067 s.
Socket/claims released. Artifact records/ethernet-notebook-live-status.json.

One diagnostic follow-up retained raw error bytes and partial observations.
At 2026-11-06T19:31:41.274126+00:00, actual identity KSC101/68800777/1.0.7,
hardware 3, one channel; mode triggered; interlock_required=true. Solenoid reply
cd0401000150 has param2=0. SRC-001 pp193-194 defines 1 ON and 2 OFF; no supported
interpretation for 0 was established. Complete status FAIL, status_complete=false,
optical unknown. Error note retains raw bytes. Elapsed 0.14694159998907708 s;
no retained transport/claim, no output/mode/settings request. See
records/ethernet-notebook-live-status-diagnostic.json for exact notebook/helper/
TCP hashes and receipt time. These two single durations are not timing acceptance.

Conclusion: the requested generic fixed-Ethernet examples are implemented and
statically verified; actual identity/mode/interlock reads are observed, but
complete electrical status, hub identity, route/control/recovery support and
physical behavior remain unqualified. Manufacturer interpretation of this exact
state reply is the next dependency. Mode/ON/OFF cells were not executed, and
normal owner refuses them before I/O. No driver/security change, physical action,
external DiamondGUI edit, commit or push occurred. Project remains BLOCKED.


## D055 - Reduce notebook code by sharing config and removing unavailable write sequences

2026-11-06, REQ-215. User: "simplify and reduce codes in the notebooks".
Keep the exact real 192.168.1.19:40305/68800777/shutter route and no simulator.
Move the repeated validated SHUTTER config and timeout to the existing read-only
helper. Keep a short bootstrap compatible with root and docs/examples; no hidden
test import-path substitution is needed. EthernetReadOnly defaults to that frozen
config. Preserve explicit reader variables and context cleanup so resources remain
available after a failed close. No additional abstraction or hardware API is added.

Attach partial observations to the original raised exception, next to the raw
reply note. This removes repeated printing/except blocks without suppressing or
reclassifying failures. Replace long, currently unavailable mode/ON/OFF owner
sequences with require_supported_route(SHUTTER), the same production eligibility
gate. Those cells raise before I/O and do not ask for meaningless actuation
confirmation, attempt ON or create an OFF-cleanup obligation. No output boundary,
status interpretation, ownership requirement or physical criterion is weakened.

## E174 / TEST-215 - Simplified notebooks and final software evidence

2026-11-06. Expected: substantial notebook code reduction, unchanged generic exact
Ethernet target, independent passive setup, live read semantics/strict errors,
no simulator and no new hardware operation for a presentation refactor. PASS
software/static artifact criteria; physical/status gaps from E173 remain open.

Notebook physical Python code-cell lines, including blanks, before/after:
01 discovery 52 -> 18; 02 connection 49 -> 11; 03 status 53 -> 11;
04 settings 59 -> 18; 05 modes 65 -> 14; 06 ON/OFF 90 -> 14.
Total 368 -> 86, reduction 76.6304347826087%. Both snapshots use Ruff-formatted
sources. Counting excludes Markdown and the shared helper; shared configuration
and diagnostics are explicit in docs/examples/ethernet_readonly.py. This metric
measures notebook readability, not hardware performance or total package size.
records/notebook-simplification.json records counts and all six final hashes.

Commands, workspace UV_CACHE_DIR=.uv-cache:
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
Six schema/syntax/link/cleared-output checks PASS. Full source 131 and exact
installed-wheel 131 tests PASS, no failures/errors/skips, with lint/format,
lock/build/clean install/import/help, source/wheel parity, stable input hashes and
negative lock checks PASS. XML/direct-validation.json contain exact timings and
commands. The software verifier ran outside the previously recorded Windows
sandbox temporary-directory restriction; no new test failure occurred.

Passive tests execute each first setup cell from root and examples, forbid
socket creation, clear the helper module cache and verify shared name/serial/
endpoint/route/no policy. No simulated device response or notebook execution is
used. Runtime transport/driver/owner source was unchanged in this refactor.
No new hardware result is claimed, and E173's raw state-0 ProtocolError remains
unresolved. Historical actual record hashes refer to their recorded revision.
No lab query, mode/output/settings command, driver/security change, external
DiamondGUI edit, commit or push occurred. Requested simplification is complete;
project deployment remains BLOCKED by the previously recorded engineering gaps.


## E175 / TEST-215 - Inspect the user's saved notebook 3 traceback

2026-11-06. User: "ran notebook 1 and 2. 3 ran into problems. check error message".
Read the current saved outputs of notebooks 01/02/03; no device access, code edit,
re-execution, simulator, source formatting or notebook output clearing performed.
Notebook 01 saved candidate-controller-match-hub-unverified with one matching
KSC101 68800777/firmware 1.0.7/hardware 3/channel 1 frame from 192.168.1.19:40305.
Notebook 02 saved the same verified identity. Notebook 03 saved ProtocolError:
Unsupported scalar value 0 in 0x04cd, raw controller reply cd0401000150.

Saved traceback points to EthernetReadOnly.status -> KSC101.state -> scalar.
Reply decodes as message 0x04CD, channel 1, state param2=0, destination 1/source
0x50. scalar accepts only documented states (1,2), marks the session poisoned
and raises. This is after successful identity/mode/interlock reads, not a failure
to open TCP or identify the selected controller. Partial observation includes
triggered mode, interlock_required=true and failure receipt time
2026-11-06T20:07:51.971533+00:00; status_complete=false, optical_state=unknown.
This is the same raw state-0 result observed independently in E173. Its semantic
cause remains unresolved; no evidence establishes OFF or optical closure.

records/notebook-3-error-inspection.json preserves file SHA256 values, execution
counts, output and ANSI-stripped traceback. The user's notebook outputs remain
untouched. Their saved execution changes notebook byte hashes and cleared-output
criterion relative to E174; no claim is made that old static output-cleared PASS
applies to the current executed files. No source/runtime change or new test was
needed to identify the existing strict-decoder rejection. No mode/output/setting,
firmware/driver/security change, external application action, commit or push.
The next dependency remains firmware-specific interpretation of state 0; do not
broaden accepted states or change device mode merely to silence the exception.


## D056 - Repair read-only status using independent actual status bits, not an invented zero enum

2026-11-06, REQ-203/215. User explicitly requested investigation of firmware1.0.7
state0 and notebook3 repair using real hardware, no simulator. Bounded read-only
queries on exact 192.168.1.19:40305/68800777 are authorized; mode/output/enable,
priming, settings, resets and driver/security changes remain outside scope.
User reports "solenoid off mode is trigger" and confirms OFF in response to the
front-display question. These describe the same human-reported current condition,
not independent optical/electrical measurements or an ON test authorization.

APT Issue36 pp193-194 and Issue42.1 pp190-191 enumerate only ON=1/OFF=2. A pinned
manufacturer-authored solenoid SDK header in the official Thorlabs repository
also enumerates only 1/2 and documents status bit0 as output enabled/disabled.
That header is TCube-family, not a firmware-specific KSC101 contract. No published
1.0.7 definition for 0 was found in this bounded search. The official KSC101
example uses the SDK's operating-state interface, not a documented raw0 mapping.
Search/retrieval failures are not proof that a private/newer contract cannot exist.
No SDK binary was installed/loaded or used for real control. SRC-007 records the
primary header URL/blob/hash; downloaded reference files stay ignored.

Use fresh 0x0429/0x042A status bits for read-only output display, corroborated by
actual current capture, human OFF display and historical same-controller 0x2000
closed/0x2001 open records. Preserve legacy0 as raw undocumented data/warning;
never normalize it to OFF. Allow raw0 only in the identity-verified firmware1.0.7
diagnostic path; production state() and output preflight retain strict rejection.
Add fixed 0x042A length6 schema, exact channel1/status-dword decode and poisoning
on invalid channel. No catch-all error suppression, query fallback/retry or
operational route qualification. Optical state remains unknown.

Before repair, back up user notebook3 to ignored inputs/private/notebooks/
03-status-before-state-zero-fix-0472ebe61c4a.ipynb. Notebooks1/2 and their output
remain byte-identical to E175. Save notebook3's new actual output after executing
it in a fresh real kernel. Static validation now inventories existing execution
without clearing/failing saved hardware evidence; syntax/schema/link checks remain.

## E176 / TEST-203 / TEST-215 - State-zero real investigation and repaired notebook3 PASS

2026-11-06, actual hardware, no simulator. Requirements: investigate raw0, preserve
uncertainty, fix and execute notebook3 on exact target without changing outputs.
PASS read-only repair/real execution. Universal firmware meaning of legacy0 is
not established; hub/actuator/physical qualification remains BLOCKED.

Actual investigation 1 command, workspace UV_CACHE_DIR=.uv-cache:
uv run --locked --offline --no-sync python tmp/investigate_state_zero.py.
At 2026-11-06T20:15:59.736863+00:00, identity reverified 68800777/KSC101/1.0.7,
hardware3/channel1. TX/RX: 050000005001 -> 90-byte identity;
c10401005001 -> c20401040150 (mode4);
c70401005001 -> c80401010150 (interlock requirement1);
cc0401005001 -> cd0401000150 (raw0). Read-only status-update request
800401005001 had no reply in 5 s; DeadlineExceeded, total5.092015799993533 s.
Stop and close/release; this request was not replayed. Raw capture artifact:
records/state-zero-hardware-investigation.json. No state interpretation was
silently substituted for the timeout.

Independent query command:
uv run --locked --offline --no-sync python tmp/investigate_status_bits.py.
At 2026-11-06T20:16:35.016962+00:00, a new identity-verified session sent
290401005001 -> 2a0406008150010000200000. Exact payload010000200000 decodes
channel1, status8192/0x2000; bit0 clear. Total0.06320879999839235 s; release
completed. Artifact records/state-zero-statusbits-investigation.json. This is
a distinct documented read query following failed 0x0480, not its retry or a
scan. Header documentation and historical/current OFF observations support the
read-only output-bit interpretation; no new ON/physical timing result is claimed.

Repair adds diagnostic status_bits decoding, retains raw legacy0 and warning,
and calculates electrical_state only from actual fresh bits. Wrong frame form,
length and channel, unsupported nonzero codes and timeouts still fail. The
notebook3 code stays short; Markdown explains sources, limits and kernel restart.
Original failed output remains in the backup/E175 evidence.

Actual final command:
uv run --locked --offline --no-sync python tmp/validate_and_save_notebook3.py.
At 2026-11-06T20:20:45.102512+00:00, a fresh python3 Jupyter kernel from this
project .venv executed notebook3 against actual hardware and saved its output.
Result: identity68800777/1.0.7/hardware3/channel1; mode triggered;
interlock_required=true; legacy_solenoid_state_raw=0; status_bits=8192;
electrical_state=off; electrical_state_source=0x042A bit0; explicit legacy warning;
status_complete=true; optical_state=unknown; hub identity/operational route false.
All socket/claims released, collector cell was not saved. Total kernel workflow
4.178309999988414 s; not a timing acceptance measurement. Artifact
records/notebook3-state-zero-fix-live.json contains actual output, source/notebook
hashes, interpreter and released-resource flags. Local Jupyter emitted nonfatal
Windows event-loop/TCP warnings; execution itself passed. No output/mode/enable,
priming, settings or physical action occurred.

Final software commands:
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
Six schema/syntax/link/static execution-inventory checks PASS. Full source137
(1.28s), exact installed-wheel137 (1.50s), zero failures/errors/skips. Six new
protocol tests use an actual captured frame and malformed channel/form/length
variants; no simulated notebook responses. Existing control regressions keep
their separate software-only transports. Lock, lint/format, build, clean hashed
install/import/help, wheel/source parity, stable input hashes and negative lock
checks PASS. Evidence direct-validation.json, XML and notebook-validation.json.

No user notebook1/2 edit (hash-verified), external DiamondGUI edit, SDK/native
runtime dependency, firmware/driver/security change, commit or push. Hardware
state0's published meaning remains unknown beyond the observed OFF/Trigger
correlation; the repaired notebook no longer depends on inventing that meaning.
Project deployment remains BLOCKED by the existing operating/physical criteria.


## D057 - Correct state-zero interpretation using exact KSC101 API reference

6 November 2026; source: user's instruction to read the manual/API reference,
continuing the authorized real-hardware state-zero investigation and notebook3
repair (REQ-203/215). Exact KSC101 Kinesis .NET SolenoidStatus documents
SolenoidStates Closed=0/Open=1, distinct from OperatingStates Active=1/Inactive=2.
The exact KSC101 C header and older APT state table use a different 1/2
representation. The earlier D056/E176 broad claim that zero was undocumented was
incomplete; retain those records as historical evidence, superseded on this point.

SRC-008 documents a validly Thorlabs-signed local Kinesis installer1.14.60.0.
Only header/API help files were extracted using archive readers and a read-only
MSI File-table lookup. No installer, SDK, DLL, driver, binding or security policy
was executed/installed/changed. Provenance/hashes: records/ksc101-api-reference-findings.json.
The exact KSC101 GetStatusBits defines output mask0x00000001 enabled1/disabled0;
therefore the notebook output-bit interpretation no longer relies on a TCube-only
reference. Bit0x2000 is unused, not interpreted as physical interlock readiness.

Keep raw0x04CD in solenoid_state_reply_raw, accepting zero diagnostically only on
identity-verified firmware1.0.7. Independently query status bits to display output
OFF/ON and corresponding documented controller Closed/Open feedback0/1. No
universal raw-wire enum across firmware or optical measurement is asserted.
Production state() remains strict1/2; no operational route/output gate changes.
Original failed notebook3 and all previous capture artifacts are preserved.

## E177 / TEST-203 / TEST-215 - Exact API correction and final real notebook3 PASS

Expected: exact 68800777/1.0.7, triggered, raw0x04CD0, fresh output bit0 clear,
controller feedback0/Closed, optical unknown, all queries validated, socket/claims
released, zero mode/output commands. Conditions: same powered Ethernet/middle-bay
setup and user's OFF/Trigger observation; USB IN disconnected as confirmed by
user. Read-only authorization persists; no output, enable, priming, settings,
mode, reset, driver/security changes or ownership takeover authorized/performed.

Command: uv run --locked --offline --no-sync python tmp/validate_and_save_notebook3.py.
Final actual fresh Jupyter kernel timestamp 2026-11-06T20:36:51.756567+00:00.
Observed identity68800777/1.0.7/hardware3/channel1; triggered;
interlock_required=true; raw solenoid_state_reply_raw=0; status_bits=8192;
solenoid_state_raw=0; controller_solenoid_state=closed; electrical_state=off;
source=0x042A bit0 (exact KSC101 GetStatusBits); status_complete=true;
optical_state=unknown; hub/operational route false. PASS expected conditions.
Socket/claims released, no output/mode command. Kernel .venv/Scripts/python.exe,
workflow 1.2598744 s (single observation, not timing qualification).
Notebook saved real output; unsaved result collector removed. Artifact
records/notebook3-api-corrected-live.json contains source/notebook hashes and
release flags. Nonfatal local Jupyter Windows event-loop/TCP warnings did not
prevent execution. Original user notebooks1/2 hashes remain byte-identical to E175.

Final software commands:
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
Source137 and exact installed-wheel137 PASS, zero failures/errors/skips. Lock,
lint/format, build, clean dependency/install/import/help, source/wheel parity,
negative lock and passive import checks PASS. All six notebook schema/syntax/local
link checks PASS without live-cell execution; saved output inventoried/preserved.
Source/notebook hashes match the final actual hardware artifact and verification
manifests. Tests with software-only transports remain distinct from real notebook
validation; no simulated notebook response was used. Evidence: direct-validation.json,
notebook-validation.json, offline-tests.xml and wheel-tests.xml.

REQ-203/215 PASS for this read-only correction. Broader KEH3 control, actual-load,
optical, driver/persistence and endurance acceptance remain BLOCKED/UNTESTED as
recorded in STATE.md. No new commit, push or external DiamondGUI edit.


## D058 - One source-backed owner/API; retire candidate and notebook implementations

6 November2026, user comprehensive source/control/API review and slimming request;
PROJECT.md source/API criteria, REQ-219. Sources of truth: SRC-001/007 APT framing/
command tables; SRC-002 KSC101 mode/trigger/persistence behavior; SRC-003 KEH3 port/
USB restrictions; SRC-008 exact KSC101 C/.NET programmer reference. Keep .NET
feedbackClosed0/Open1, OperatingStatesActive1/Inactive2, C feedbackClosed2/Open1
and APT output-command1/2 distinct. Older T-Cube text does not override the KSC101
manual; no new physical timing/trigger/control qualification is inferred.

Replace both normal readback and electrical command confirmation with fresh status
bits (exact KSC101 mask0x1). Do not infer operating Active/Inactive from output bits.
The explicit get_solenoid_state_reply API returns an unmodified raw byte; normal
status no longer queries it or needs a firmware-specific zero-acceptance branch.

Consolidate read-only Ethernet into ShutterHub. This revises the former blanket
connection refusal, not control qualification: require_control_route still blocks
all KEH3/VCP mode/output writes before dispatch, even with policy/injection. Remove
the obsolete candidate probe/analyzer/CLI and duplicate notebook owner, preserving
captures and pre-review notebooks/outputs. Add context-managed passive release,
reuse connect identity in CLI identify, and keep the existing DiamondGUI surface.

Correct command-path gaps: ordinary sends refuse a receive-poisoned session; mode
transitions share ON/pulse ambiguity/cleanup handling; healthy read-only shutdown
has no incidental OFF obligation. Existing partial-write alignment, durable fault
journal, priority OFF, separate cleanup budgets, policy and explicit recovery stay.
These are software changes, not authority for physical output or driver changes.

## E178 / TEST-203/204/205/206/207/212/215/217/219 - Source/API review and final validation

Expected: exact source-backed command bytes and distinct state meanings; one owner
for all apps; no simulator/injected transport in notebooks; code reduction without
weakening ownership/timeout/output constraints; correct real read-only status and
resource release on exact68800777/1.0.7 at192.168.1.19:40305. Mode/output and physical
acceptance are out of live scope. Conditions retain user power/Ethernet/USB IN and
OFF/Trigger report; transient state is queried again. No target scan or takeover.

Review artifact records/source-api-review.json lists reviewed files,8 resolved
findings, exact source hashes and reduction. Baseline records/source-review-baseline.json.
Runtime/scripts/shared notebook support2125->1843 lines:282 removed,13.27%; notebook
code86->80 lines. Tests/output/unchanged standalone example excluded from the first
count. Obsolete probe-only17 parametrized cases retired with their implementation;
7 behavior/API regressions added, leaving127 current cases. Original user/pre-review
notebooks preserved byte-for-byte via records/source-review-notebook-backups.json.
Historical state-zero raw captures, E176/E177 artifacts and original failed3 remain.

Commands: uv run --locked --offline --no-sync python tmp/review_live_notebook.py1,
2 and3 (each separate explicit invocation, actual script takes a space before the
number). Fresh real python3 kernels, actual TCP, no simulated response or transport
injection. Unsaved Session.send audit rejects non-query IDs; unsaved collector
checks exact identity, expected status and released handle/claim. Original notebook
cells/actual output saved; audit/collector cells not saved. Final runs:
- Notebook1: 2026-11-06T20:50:31.177939+00:00; PASS; 1.1154503s workflow; sent ['050000005001']; no retained handle/claim.
- Notebook2: 2026-11-06T20:51:06.764680+00:00; PASS; 1.4344325s workflow; sent ['050000005001']; no retained handle/claim.
- Notebook3: 2026-11-06T20:50:49.292296+00:00; PASS; 1.2012994s workflow; sent ['050000005001', '050000005001', 'c10401005001', 'c70401005001', '290401005001']; no retained handle/claim.
Notebook1/2 identity68800777/KSC101/1.0.7/hardware3/channel1; notebook3 triggered,
electrical off, bits8192/0x2000, interlock requirementtrue, operating/optical unknown.
No raw0x04CD is requested by normal get_status. Artifacts
records/source-review-live-notebook-1/2/3.json contain final notebook/config/runtime
hashes and query frames. Times are single workflow observations, not timing acceptance.
Notebook2 initial unsaved collector NameError (asdict import missing) is preserved
in source-review-live-notebook-2-collector-failure.json; actual original cells had
completed. Corrected collector and fresh explicit rerun PASS. No production-source
or hardware change was needed. Nonfatal local Jupyter Windows event-loop/TCP
warnings did not prevent actual execution.

One separate explicit actual get_solenoid_state_reply read returned0, identity
verified, sent050000005001 twice andcc0401005001, resources released. Artifact
records/source-review-raw-diagnostic.json. Byte0 is retained without enum conversion.
No output/mode/enable/priming/settings/reset or other physical action was performed.
All audited frames were queries on the one authorized endpoint.

Final commands:
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
127 source +127 exact installed-wheel tests PASS; no failures/errors/skips. Full
lock/lint/format/build/clean hashed dependencies/install/import/help/source-wheel
parity/negative locks PASS. Six schema/syntax/link checks and12 passive setup cases
PASS; no automatic batch live notebook execution. Notebooks4/5/6 static/passive
only. Final manifests/direct-validation/XML/source-api-review and real artifacts
hash-match current runtime/notebooks. Original backup SHA values match preserved
user1/2 output evidence. Local documentation links and git diff whitespace check PASS.

No external source edit/commit/push. External C:/Users/HFNV/diamondgui checkout
is absent, so historical29 integration cases cannot be marked current PASS; local
owner-method/schema/CLI/GUI regressions PASS. REQ-219 local review PASS; deployment
still BLOCKED by hub/control/actual-load/optical/driver/persistence criteria in STATE.md.

## E179 / TEST-220 - Repository manuals and APT protocol copies, 6 November 2026

Human request: ensure the device manual and APT command protocol documents are
in the repository. Expected: unchanged, non-ignored PDF copies for KSC101,
KEH3/KEH6 and both protocol revisions already used by the project; valid PDF
identities/revisions/page counts; SHA-256 equality with registered originals;
working local index/source links. No hardware operation is in this test scope.

Existing downloads were present only under ignored inputs/reference. Copied
ksc101.pdf, keh3.pdf, apt.pdf and apt-42.pdf to docs/manuals with descriptive names.
All four match the original byte content and registered SHA-256 values exactly:
45, 33, 421 and 443 pages respectively; total 36,142,241 bytes. The index retains
SRC-002/003/001/007 provenance and both APT revisions to preserve historical page
references. The legacy KSC101 cover warning is explicit. Copyright/notices remain
unchanged. Actual optical shutter model/manual (SRC-004) is still missing.

Validation: pdfinfo and pypdf independently confirm page counts. Fresh pypdf text
from the first six and last two pages confirms model, document number/revision
and dates. pdftoppm rendered each title page; all four were visually inspected.
Poppler emitted missing Symbol/ArialUnicode font warnings while rendering the
originals; the inspected title pages remained legible and the PDFs were unchanged.
git check-ignore returns 1 (not ignored); git ls-files --cached --others
--exclude-standard sees every PDF. Local Markdown links in README.md,
docs/sources.md, docs/manuals/README.md and outputs/REPORT.md pass.

Final verification command (documentation tools, no project dependency change):
uv --cache-dir .uv-cache run --no-project --offline
C:/Users/HFNV/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
tmp/verify_manuals.py. Result PASS; manifest records/manuals-verification.json.
Initial verifier attempts encountered inaccessible default uv cache, unavailable
pdftotext and incomplete identity-page sampling; the final run uses a local cache,
bundled pypdf and the expanded page selection. No document/source defect was found.

Updated PROJECT.md, STATE.md, source register, root index and report. No runtime,
dependency, notebook, hardware or driver change; existing dirty work preserved.
No commit or push. REQ-220 PASS for repository availability/integrity only;
deployment/physical acceptance remains BLOCKED under its existing conditions.

## E182 / TEST-222 - Manual consistency and package validation, 6 November 2026

Human request: read the manuals, check consistency and validate the package.
Expected: implemented supported frames and state semantics agree with manufacturer
sources; operator instructions describe the actual API; final source and isolated
wheel checks pass; physical acceptance is not inferred from software tests.

Freshly extracted all four repository PDFs and reviewed relevant KSC101 Rev D,
KEH3/KEH6 Rev E and APT Issues36/42.1 sections. Rechecked exact KSC101 API HTML
and hashes. Command IDs, six-byte layouts, identity offsets, mode/interlock values,
ON1/OFF2, fault frames and D2XX initialization agree. Visually checked KEH3
Figure17: rear-view left40304/middle40305/right40306, management40303. The generic
status-query layout alone does not establish KSC101 applicability; exact SDK mask
and recorded real firmware1.0.7 exchanges provide the additional basis. Generic
trigger cycling differs from KSC101 level/priming behavior; TTL remains unsupported.

Corrected stale documentation of the docked-KEH3 blanket write ban and query-only
notebooks; documented Trigger exit confirmation/GUI limitation; repaired the
example's missing OFF preparation/pause; registered the formerly dangling SRC-009
SH05R reference after online manufacturer-manual review. Local unchanged SH05R
PDF retrieval failed (HTTPS/HTTP mirror timeout; manufacturer legacy URL HTML),
so no local copy/hash is claimed. Four existing PDFs are unchanged and non-ignored.
Current REQ-221 disambiguates the documentation requirement from REQ-220 control;
historical E179 retains its original duplicated REQ/TEST IDs.

Added15 software cases:6 literal request/reply exchanges,3 docked-bay control
cases,1 missing-policy refusal,3 default TCP route selections,2 delayed/absent
transition cases. The current driver waits for output transitions within the same
deadline and never repeats ON/OFF; the new tests cover transient old bits and
deadline expiry. No runtime source, device command or notebook cell was changed
or executed by this review. Separate commissioning files arrived in the shared
checkout; their exact runtime/config hashes match the validated package. Their
single recorded ON/OFF and final Manual/OFF/release are acknowledged, not repeated.
The live record explicitly reports no independent optical/blade observation.

Final command: uv run --locked --offline --no-sync --group dev --extra gui
python scripts/verify.py with UV_CACHE_DIR=.uv-cache.144 source +144 exact installed
wheel tests PASS, zero failures/errors/skips; lock, Ruff, clean hashed dependency
install, build/parity, SDK-free import/help and negative locks PASS. Six notebook
schema/syntax/link checks PASS using scripts/verify_notebooks.py; no cells run.
Restricted attempts failed on pytest temp-directory WinError5; authorized runs
outside the filesystem sandbox passed, without changing ACL/driver/security
settings. One intermediate check caught guide formatting; normalized before rerun.

Final integrity/link collector: bundled Python through uv --no-project --offline,
tmp/manual-review/record_review.py. All4 PDF identities/pages/hashes, all current
software/notebook hashes, commissioning-runtime/config equality and local Markdown
links PASS. git diff --check PASS. Exact snapshot/counts/limits are in
records/package-consistency-review.json; current direct-validation/XML/notebook
manifests replace their older generated contents, which must not be attributed
to E178's revision. External DiamondGUI checkout remains absent. No commit/push;
unrelated dirty work preserved. REQ-222 PASS for the stated review/software scope;
optical behavior, other topologies, native timing, persistence and endurance remain
unqualified. Current transient device state must be rechecked before future use.


## D059 - Admit documented docked KEH3 control; explicit protected OFF/Manual preparation

6 November2026. User explicitly requests real shutter ON/OFF at192.168.1.19:40305
using Thorlabs manuals/protocol, no simulator, then confirms currentSH05R and safe
setup in response to the independently blocked source/isolated-trigger question.
This is new controlled-action authority beyond the earlier read-only review.
One1s added ON hold,2s OFF pause, finishOFF/Manual/release; no TTL, other target,
interlock bypass, firmware/driver/security/network or other settings changes.

The blanket docked-KEH3 ban was local software policy, not a manufacturer prohibition.
APT/SRC-007 section2.1 defines transport independence; pp190-191 define0x04CB1/2.
KEH3/SRC-003 section4.3/Figure17 defines bay-port routing. Existing actual identity/
status frames establish this endpoint/address. User selects this exact controller
by live model/serial/firmware/channel count at the stated endpoint; unknown hub
serial/firmware are metadata, not falsely verified or a new blocker for this scope.
Broader wrong-hub/swap/shared-failure and other topology qualification stay open.

Control-route check now admits docked bays with the existing load policy; VCP and
external USB OUT remain unavailable. Explicit protected Trigger->Manual needs
source_inhibited=True and persistent-mode permission. It sends OFF/deactivate,
confirms output clear, selects Manual then verifies Manual/OFF; ordinary ON/OFF
does not change mode. Native SH05R/KSC101 load/design mapping is supported by
SRC-009, current model/protection user-reported; this is not independent optics.

Output confirmation requests fresh status bits within the original deadline until
the bit matches, with no output resend or failed-query retry. TCP returns the send
count to Session before the late-success check, preserving known alignment after
a complete-but-late send. Partial/unknown writes still forbid further frames;
ordinary poisoned commands, ownership, durable uncertainty, separate cleanup and
no ON replay remain intact. CLI pulse explicitly preparesOFF/rest before ON.
Tracked config/shutter.ethernet.toml and ignored shutters.local.toml now select the
actual Ethernet SH05R; old local USB config is backed up privately. Notebooks5/6
now expose explicit mode preparation / balanced real ON/OFF, no simulated response.

## E181 / TEST-220 / REQ-220 - Actual Ethernet SH05R ON/OFF and final package PASS

This evidence ID avoids E179 (manual copies, historical TEST-220 now REQ-221) and
E180 reserved by the concurrent manual/package review. That review performs no
device actions; the independently authorized live work here must remain separate.

Expected: fresh exact KSC10168800777/1.0.7/hardware3/channel1 at192.168.1.19:40305,
source blocked/triggers isolated per current user confirmation; explicit OFF/Manual,
one1s added ON hold, positive output-bit readback, OFF bit clear, Manual retained,
release complete. No simulator, SDK/native DLL or transport injection used for live
validation. Optical/operating state must not be fabricated from electrical bits.

Pre-actuation full source/wheel129/129 and static6 checks passed at that point.
A later integrated suite includes the parallel manual-review regressions and is
142/142; those software transports do not establish physical behavior.
Initial notebook display imports were caught by Ruff, corrected before any writes.

Actual preparation command:
uv run --locked --offline --no-sync python tmp/ethernet_manual_prepare.py.
At2026-11-06T21:26:03.171963+00:00 fresh initial Triggered/OFF, interlock requirement
true; sentcb0401025001 then c00401015001, verified fresh Manual/OFF0x2000, released
socket/claim. Audit forbids ON in this phase. Artifact
records/ethernet-control-manual-preparation.json contains exact sent/reply frames,
identity, before/after status, code/config hashes and release flags. PASS.

Actual cycle command:
uv run --locked --offline --no-sync python tmp/ethernet_on_off_notebook.py.
At2026-11-06T21:26:53.535384+00:00, a fresh project .venv Jupyter kernel executed
the original notebook6 cells, plus unsaved real-message audit/result collector.
Explicit OFF and2s pause, exactly onecb0401015001 ON, fresh status0x2001,1s added
hold, prioritycb0401025001 OFF, fresh final0x2000, Manual and no error/journal fault.
Observed status sequence8192,8192,8192,8192,8193,8193,8193,8192,8192.
The transient reads during OFF were resolved by bounded fresh-status observation,
not by resending ON/OFF. ON-to-OFF host dispatch1.0569155999983195s; total Jupyter
workflow4.5788799000001745s. These are software observations, not calibrated optics.
Socket/claims released. Actual notebook output saved; audit/collector cells removed.
Artifact records/ethernet-control-live.json includes source/config/notebook hashes,
all TX/RX frames,1 ON attempt, interpreter, final status/release and scope. PASS.

Human independent-observation answer: "I did not observe it". Therefore controller
ON/OFF is demonstrated; independent blade motion/optical closure/timing are NOT
PASS. No repeat cycle was performed to obtain that observation. Current native
SH05R Hall-sense return is not independently sampled by this implementation.

Fresh post-release real CLI status verified Manual/OFF0x2000, same identity and no
persistent fault; CLI released normally. Artifact records/ethernet-control-final-status.json.
No other output/mode/settings/enable, priming, other-target, driver/security or
firmware operation occurred. Manual selection is remembered, as documented.

Final integrated verification:
uv run --locked --offline --no-sync --group dev --extra gui python scripts/verify.py.
uv run --locked --offline --no-sync python scripts/verify_notebooks.py.
142 source +142 exact installed-wheel tests, zero failures/errors/skips. Lock,
lint/format/build/clean dependency/install/import/help, source-wheel parity,
negative locks and all6 static schemas/syntax/links PASS. Notebook6 additionally
has this real execution; others retain their separately dated evidence. All current
source/config/notebook/manifests hash-match the actual sessions. No simulator is
used as hardware evidence; software regression scopes remain explicitly separate.

Manufacturer-authored SH05R manual was read via web PDF; direct download timed out,
no local hash invented (records/sh05r-manual-reference.json, SRC-009). Repository
manual copies and the concurrent software review are preserved, not replaced.
No external DiamondGUI source edit, SDK installation, commit or push. Exact-target
REQ-220 PASS for implementation/control/readback/release. Wider optical, interlock/
local/TTL behavior, other bays/topologies, hub recovery, native timing, reboot and
endurance acceptance remain open; no repeated hardware work is pending.


E181 final integrated recheck: the parallel manual/package review is now E182
(not the earlier reserved E180). Additional source-only regressions increased the
final suite to 144 source and 144 installed-wheel tests, no failures/errors/skips.
Current actual-control runtime/config/notebook hashes still match both real sessions;
source/static manifests match current files. These new software tests do not add
physical cycles or alter the hardware evidence. Canonical STATE/report retain
REQ-221/222 documentation work and the separately completed REQ-220 live result.

## D060 - Holistic review scope and migration boundary (6 November 2026)

User explicitly requested review, fixes, pruning, consistent naming, documentation,
cache/temp cleanup, staged commits and push. Publication is now authorized.
Preserve the pending migration, actual hardware records, manuals, executed notebook
outputs/private backups and environments. Do not repeat device operations. Keep
the public DiamondGUI owner surface; retire only superseded internal/candidate
paths. External DiamondGUI integration and broader physical acceptance remain open.

## E183 - TEST-223 owner, GUI and migration review (6 November 2026)

Baseline: uv run --locked --offline --group dev --extra gui python scripts/verify.py
passed 144 source and 144 isolated installed-wheel tests. The sandbox denied uv's
existing global cache; the same software-only command ran with approved access.
No instrument or lab-network operation was performed.

Added targeted regressions before fixes. The selected run produced 16 failures
and 1 pass: it exposed incidental qualified read-only shutdown OFF, a too-early
rest timer, and unselected GUI Release closing a connection; other GUI cases
confirmed inconsistent target rejection. Fault-only read sessions previously
entered the output cleanup path. Corrected shutdown obligation tracking, explicit
GUI target selection and electrical OFF rest accounting. Read-only faults remain
visible and persistent, but never create an incidental output command. Prior
output/mode attempts retain cleanup obligations and aggregate failures.

Affected suite after fixes: 86 owner/application tests PASS. Integrated checks:
160 source + 160 isolated-wheel tests PASS, no failures/errors/skips. Lock,
Ruff lint/format, clean build/install/import/help, exact source-wheel parity,
negative lock cases and passive configuration validation all PASS. Command:
uv run --locked --offline --group dev --extra gui python scripts/verify.py.
All six notebooks PASS schema/syntax/link checks, with no cell execution:
uv run --locked --offline --group notebooks python scripts/verify_notebooks.py.
Artifacts: records/direct-validation.json, offline-tests.xml, wheel-tests.xml,
notebook-validation.json. Tests use simulated byte transports and localhost only.

Retired the candidate keh3 module/commands, duplicate notebook connection path
and redundant gated direct_control.py example. One owner serves Ethernet and USB;
current examples use the same shutter name and TOML route. The raw diagnostic,
electrical output, operating state and optical observations remain separate.
Preserved DiamondGUI method/status names are public integration contracts, not
duplicate legacy backends. Migration replacements are in docs/cutover.md.

Verification now removes its own successful disposable environment, suppresses
Python/Ruff caches for subprocesses and retains failed-run work for diagnosis.
Initial tooling rechecks caught an incorrectly placed Ruff cache flag and CRLF
inside a new fenced example; both were corrected before the passing full run.
Hardware E181 and manual/package E182 retain their original hashes. This review
changes controller/GUI runtime code, so the old live result is historical evidence
for its recorded revision; current software checks do not requalify physical use.

## E184 - TEST-223 documentation and publication preparation (6 November 2026)

Reviewed current documentation and migration replacements. Corrected stale E179
live-control references to E181; E179 itself remains the original manual-copy
record with its historical ID collision. The example name is consistently shutter;
the notebook guide now shows the actual SHUTTER configuration API instead of a
retired route dictionary. Removed repeated mode-protection prose. External
DiamondGUI availability and current-vs-historical validation are explicit.

Repository audit: 113 local Markdown targets exist; all 49 current JSON evidence
files and all 5 XML files parse. The four manufacturer PDF byte counts/SHA-256
values match manuals-verification.json. A targeted credential-pattern scan of
the pending text files found no private-key/token patterns. This is a focused
publication check, not a claim of a comprehensive secret audit.

Normalized only reviewed changed text to the repository's LF policy and reran the
integrated 160 source / 160 wheel and six static-notebook checks. All manifest
input hashes were verified against the exact staged Git blobs before stage 1,
b9b2309. Six byte-exact notebook snapshots before normalization are retained
under inputs/private/notebooks/holistic-review-before-lf; hashes and normalized
paths are recorded in records/holistic-normalization.json. Saved outputs were
not cleared. Four original PDFs remain binary/unchanged. No new physical test.

## E185 - TEST-211/223 actual external integration check (6 November 2026)

A live path check contradicted the earlier unavailable-checkout assumption:
C:/Users/HFNV/diamondgui exists and is dirty. Inspected its AGENTS.md, pytest
hooks/config, local-config loading, passive shutter adapter, both focused tests
and the page source before execution. The page has zero executable AST nodes:
its entire contents are commented out. Current metadata still selects the old
logical key/left-bay port 40304. No external source/configuration was edited.

From the external repository root, using this package's uv-selected environment,
disabled pytest plugin autoload and Python bytecode, ran only:
hardware/optics/tests/test_shutter.py and gui/tests/test_shutter_control_page.py,
with -m "unit and not hardware", -p no:cacheprovider and basetemp/XML redirected
inside this project. No live HardwareManager/runtime/device was resolved.
Observed 3 owner/factory PASS and 26 page FAIL, all missing attributes from the
commented module. This supersedes the historical 29-case integration PASS and
blocks integrated deployment; local package checks do not conceal that failure.
Evidence: records/diamondgui-current-integration.json (exact source hashes,
metadata and external revision), records/diamondgui-current-tests.xml.
Asked whether restoring the separately edited integration belongs in this task;
without a scope change, preserve those external dirty edits and report the gap.

## E186 - TEST-223 scoped cleanup and final review (6 November 2026)

Inventoried 58 explicitly generated targets before deletion: repository-local
Python/Ruff/uv caches and disposable verification/pytest directories. Verified
each resolved absolute path stayed inside this workspace and contained no tracked
files. Native PowerShell removal completed all 58, zero failures, in 86.69 s;
178,212 files, 5,317,497,320 logical bytes. A later inspected integration-test
directory was similarly removed, bringing the scoped target count to 59. The
environment configuration hash was unchanged. Preserved .venv/current wheel,
manuals, records, private notebook backups, source preimages, reference originals,
runtime ownership state and ambiguous investigation/history files. Logical bytes
do not equal physical savings when hardlinks are shared. Manifest:
records/holistic-cleanup.json. No tracked deletion came from cache cleanup.

Runtime Python is 1,588 lines versus 1,702 at 9d486b3: net reduction 114 (6.7%).
The user-requested staged runtime/manual commits are b9b2309 and 2297162.
Current checkpoint/report now distinguish the passing package review, external
integration FAIL, historical E181 cycle and unmet physical/deployment acceptance.
The latest remote main was fetched before publication; no force push is planned.

Final recheck: 160 source + 160 isolated-wheel cases PASS, six existing static
notebook manifests still match current files, and the wheel's embedded README
matches the current README. The verifier now includes README in its input hashes
and explicitly passes -B alongside -I because isolated Python ignores environment
bytecode settings. Removed the small leftover test/example caches from the prior
tool run; all 59 scoped cache/temp targets are absent after final verification.
112 final local Markdown targets resolve. records/holistic-review.json captures
these results and the separate 3 PASS / 26 FAIL external integration result.

## E187 - TEST-223 verified publication (6 November 2026)

Pushed origin/main with an ordinary fast-forward: 8f324a6 ->
c6f6661eb948a5acd4a6d21b9345ae68363ad57d. This publishes review stages b9b2309,
2297162 and c6f6661 and the pre-existing unpushed migration checkpoint 9d486b3.
git ls-remote --heads origin main returned exactly local HEAD c6f6661; the working
tree was clean after refreshing the index for byte-identical LF-normalized files.
No source content was changed by that refresh. No force push or external-repository
change occurred. records/holistic-publication.json preserves this observed result;
this follow-up checkpoint records it, and final local/remote parity is checked
again after publishing the checkpoint. REQ-223 scoped repository review/delivery
PASS. Full project remains BLOCKED by E185's external integration failure and the
unmet physical/deployment requirements; no new physical action was performed.

## E188 - TEST-224 actual WebUI baseline (6 November 2026)

User requested actual hardware control through the WebUI, no fake/simulator,
with issue diagnosis, fixes and script updates. The user confirmed: "Yes,
unchanged and protected for this WebUI test" for SH05R, KSC10168800777 at
192.168.1.19:40305, independently blocked source, isolated triggers and intact
key/interlock. This is the current protected test window, separate from E181's
earlier one-cycle authorization. No unrelated device or external application edit.

Production CLI startup at the fixed default 8050 failed. Native socket diagnosis
confirmed another listener (PID52384); explicit local bind9857 was available.
Added a validated gui --port option; started the real production GUI at9857,
without touching the existing application. Browser automation used visible page
controls, no hidden/direct callback submission, injected transport or simulator.

Browser Release with no selected target was refused. Selected shutter and
Connect verified68800777/1.0.7/hardware3/channel1. Read returned actual Manual,
electrical OFF0x2000, interlock requirement true, no fault. Connect's original
result had unknown feedback. At23:06:58UTC the first ON was refused even after a
long preceding read/wait: the rest timer started only on the first ON attempt.
After the rest, visible ON/OFF clicks returned ON0x2001 at23:07:11.233867UTC,
OFF0x2000 at23:07:11.629272UTC, no fault. Released after OFF before restarting.
Those are dated electrical observations, not calibrated exposure or blade motion.
Evidence: records/webui-baseline-live.json and webui-baseline-off.jpg.

## E189 - TEST-224 corrected real WebUI and passive package validation

Fresh OFF feedback now starts the configured rest interval; any observed ON
invalidates the previous interval. The WebUI Connect explicitly requests fresh
status after identity. Early ON shows the remaining rest and states that ON was
not dispatched; no automatic wait, retry or hidden output preparation was added.
Library connect remains identity-only. GUI --port validates1..65535 and remains
localhost-only. scripts/verify.py now checks passive GUI help; the new
scripts/verify_webui_evidence.py checks saved browser observations without
connecting or simulating devices. Such a checker cannot authenticate provenance
or replace live browser/hardware evidence.

Restarted the corrected production server and reloaded the visible browser.
Connect at23:09:04.333209UTC returned fresh Manual/OFF on the exact identity.
After the OFF rest, the FIRST ON click succeeded: fresh0x2001 at
23:09:20.904994UTC; the following OFF click returned0x2000 at
23:09:21.251408UTC. Explicit OFF followed by immediate ON was correctly refused
with1.66s remaining; fresh Read remained OFF/no fault. The already-Manual button
returned Manual/OFF without a mode transition. Final Release then Read reported
disconnected, has_device=false, requestedOFF, no fault. Stopped only the test
server after release. Two short ON/OFF cycles total in this campaign: one before
and one after fixes, plus explicit OFF/guard checks; no endurance sequence.
No independent optical observation has been supplied; do not infer blade motion.

Actual evidence: records/webui-final-live.json, webui-final-off.jpg and the
hash/provenance wrapper records/webui-live-validation.json. The saved-observation
checker PASS is records/webui-evidence-validation.json. All changed runtime
sources were unchanged between the final live run and package/hash validation.

Passive checks PASS: syntax compilation, scoped Ruff lint/format, locked uv
dependencies, exact wheel/source Python parity, clean isolated wheel install and
imports with no SDK/native/GUI dependency loaded, GUI help with --port, invalid
port rejection before app creation, and the saved actual-observation checker.
The updated wheel is retained under dist; its temporary environment was removed.
Artifacts/commands: records/webui-package-validation.json. No simulated-device
tests were run in this no-simulator campaign; old160+160 results are historical
and are not represented as current full-suite coverage after these source changes.
Broader physical, fault-injection, external DiamondGUI and deployment qualification
remain separate. REQ-224 PASS for the actual selected WebUI/controller workflow.

## E190 - WebUI independent-observation follow-up (6 November 2026)

User reply: "I did not observe the blade". This applies to E188/E189
WebUI cycles. Recorded controller ON/OFF remains PASS; independent blade motion
and optical closure remain UNTESTED. This is absence of observation, not evidence
that motion failed. Preserved original browser captures/hashes and recorded the
human follow-up separately in records/webui-observation-followup.json. Updated
current state, report and derived live-validation summary. No device operation,
mode/output change or additional cycle was performed.

## E191 - One explicitly requested 1-second WebUI cycle (6 November 2026 local)

The user requested: "open the webui again. I will watch the blade this time.
run one ON/OFF cycle with a 1-second hold, then leave it OFF and release. same
protected SH05R setup." This is authority for exactly one further cycle on the
same protected controller/load/route, not a repeat endurance or settings test.

Added an explicit WebUI timed button calling the existing hub.pulse(target,1.0),
so the server owner times the hold after internal fresh ON readback. Updated the
existing target-guard test's callback input list for the new button. Scoped Ruff
lint/format PASS; no fake/simulated-device test or transport was run. No new
backend, pulse implementation or direct callback substitute was introduced.

Opened the visible browser and production localhost9857 server. Connect verified
68800777/1.0.7/hardware3, Manual/OFF0x2000, interlock requirement true and no fault.
After the OFF rest and an announced3s viewing delay, clicked the timed button
exactly once. It returned successful Manual/OFF/no fault with electrical OFF
readback at2026-11-07T00:10:45.272947UTC (6 November local). The existing pulse
confirms ON internally before the1s hold; no separate transient ON browser
snapshot was captured. Host hold/browser duration is not calibrated optical time.

Saved OFF screenshot, clicked Release, then Read reported disconnected,
has_device=false, requestedOFF and no fault. Left the WebUI open for the user
with no hardware connection; owned server session3080. No second ON/cycle and no
mode/settings/other-device change. Asked for the user's independent blade
observation; it is pending and must not be inferred from this successful return.
Artifacts: records/webui-one-second-cycle.json, webui-one-second-off.jpg and
webui-one-second-validation.json. Source/artifact hashes and saved-record checks
PASS. No further actuation is planned or authorized by this consumed cycle.

## E192 - User observed blade motion for E191

User reply after the single timed WebUI cycle: "Yes, it opened and returned
closed". Record this as independent human-reported qualitative blade motion PASS
for E191's exact protected setup/cycle, separate from controller OFF readback.
No detector/extinction or optical timing calibration is established, and broader
local/TTL/interlock/endurance acceptance remains open. Preserved raw browser
capture/hashes and saved this later report in records/webui-one-second-observation.json;
updated the derived validation/current state/report. Passive wheel/source parity
and syntax checks also PASS for the timed-button change. No additional physical
operation or cycle was performed in response to the observation.

## E193 - KSC101 UI reference and APT contract review (6 November 2026 local)

REQ-225 / TEST-225 source inspection: the user supplied ETN017648-D03 PDF and
screenshot and explicitly prohibited Kinesis/SDK control. The retrieved official
PDF is HA0368T Rev F September2026,41 pages,26,149,045 bytes, SHA256
007d604c718378b3b8b6bc6f46876f00f91c6a4e4d839c2a175681ac3c122597.
Copied unchanged into docs/manuals, retained older references, registered SRC-010.
Read sections4.3,5.2,6.2-6.3 and visually inspected rendered pp28/31 GUI/settings.
Cross-checked APT42.1 pp43/99/184-190 for Identify, cycle-only EEPROM request,
mode/cycle read/set and ON/OFF. User documents are reference data, not authority
to execute their vendor-software steps or physical operations.

The protocol's MMI0x0520/trigger0x0523 model table includes KSC101, but the
detailed sections specify motor-family fields and conflicting lengths. No
trustworthy KSC101 display/trigger layout or Key/Ready mapping was established.
A newer official APT URL retrieval returned1313-byte HTML, not a PDF; no new
protocol revision is claimed. No vendor SDK, installer or binary was used.

## D061 - Manufacturer-style panel, canonical APT control and truthful gaps

Implement four named modes, mode-dependent Open/Start and Close/Stop,
On/Off/count readout, cycle Settings and Identify using only the existing owner,
driver, APT session and real transport. Native Start sends one ON/prime request,
never claims cycle completion from an OFF sample and requires Stop before Release.
Cycle writes require Manual/OFF, source assertion, separate permissions, validated
limits and exact RAM readback; optional cycle-only EEPROM requests cannot claim
unacknowledged persistence. MMI/trigger settings are visibly disabled, Key/Ready
Unknown. Do not substitute motor layouts or SDK behavior. Preserve existing
Manual API, interlock/load/rest checks, timeout/quarantine/cleanup and recovery.

Native modes need explicit qualified_modes; continuous cycles, device settings
and EEPROM requests have independent default-false gates. Current real SH05R
configuration remains byte-unchanged/Manual-only. No new device actuation or
configuration is authorized; the earlier observed cycle authority is consumed.

## E194 - TEST-225 software/package and passive browser review

Requirement -> method -> result: supported panel/APT contracts -> literal frames,
all packet splits, invalid values/channel/length, policy refusal before I/O,
native Start/Stop dispatch, settings mismatch/fault/cleanup, release guards,
unknown-state renderer and existing full suite -> PASS software only.
Command: uv run --locked --offline --group dev --extra gui python -B scripts/verify.py.
201 source +201 isolated installed-wheel tests PASS, zero failures/errors/skips;
Ruff lint/format, locked build/install/import/help, missing/outdated-lock refusal,
passive config checks and exact wheel Python/CSS parity PASS. The installed
package has no pythonnet/clr/FTDI/serial dependencies loaded. This suite uses
software fixtures/localhost loopback, not hardware evidence or a simulator backend.
Six notebooks static PASS using verify_notebooks.py; no hardware cell ran.

Browser used the actual new production app at127.0.0.1:9860, started passively
with the unchanged Ethernet TOML; no transport injection or fabricated connected
state. Selected the profile, opened/closed Settings and inspected1100px desktop
and390px phone breakpoints. Never clicked Connect, Identify, output or Apply.
Corrected mobile grid targeting Dash's selector wrapper; kept Settings Stop/OFF
header sticky. Disconnected lamps/times remain Unknown/Not read. Zero console
warnings/errors. Viewport override reset; preview left open/disconnected. The
prior9857 server and other8050 application were not taken over.

Artifacts: records/direct-validation.json, offline-tests.xml, wheel-tests.xml,
notebook-validation.json, webui-apt-validation.json and three webui-apt PNGs.
New native modes/timing/priming/Identify flash/storage/revised physical workflow
remain UNTESTED; E191/E192 retain only their historical exact Manual-cycle scope.
Full GUI parity remains BLOCKED on the source contracts described in STATE.md.
Temporary review artifacts are removed only after preserving durable evidence;
environments, source downloads, ownership state and earlier bench records remain.
The exact review directory required a narrow elevated deletion retry after an
ordinary access-denied result; absence was then verified. No scope was broadened.
The preview was passively restarted on final source with -B (owned session14309).
140 local Markdown targets, five manual hashes, saved artifact hashes and final
source/configuration hashes PASS in webui-apt-validation.json. Stage1 implementation
commit ab80236; documentation/evidence publication is the next checkpoint.

## E195 - Staged WebUI delivery and remote verification

Stage1 ab80236 contains the canonical APT owner/driver extensions, revised panel
and CSS, regressions and exact CSS-wheel verification. Stage2 8c1e1f4 contains
the unchanged RevF manual, API/GUI/README/source docs, checkpoint/report and
software/passive-browser evidence. Reviewed explicit staging allowlists and
cached diff checks; all verified source and artifact hashes matched exact staged
Git blobs. Current SH05R TOML and four prior manual hashes remain unchanged.
Only generated review/test material and the one-off aggregation script were
removed; .venv, downloads, ownership state, wheel and all bench records remain.

git push origin main succeeded from238f9b3 to8c1e1f4. git ls-remote origin
refs/heads/main returned8c1e1f45033abfe6c21fc8e8478622dacf6144dd, matching HEAD;
git status --porcelain was empty. This final publication checkpoint follows
those two observed published commits; final parity is checked again after push.
No device operation was performed for publication. Full REQ-225 parity remains
PARTIAL/BLOCKED on the specific wire contracts in STATE.md; all new physical
mode/settings/Identify functions remain UNTESTED.

## E196 - Modern minimalist visual refinement, REQ-226 / TEST-226

The user requested a modern minimalist palette, flat design, refined typography,
consistent spacing, subtle borders, responsive layouts and intuitive hierarchy.
This supersedes the literal manufacturer appearance, preserving its supported
functions. Replaced red chrome/gradients/bevels/mechanical circles with white
surfaces, slate text, muted teal accents and flat output controls. Added semantic
Operating mode / Output control / Controller status headings, consistent field
groups, visible keyboard focus and reduced-motion support. Renamed the obsolete
round-action style to output-action. No new dependencies/fonts/network assets.

Before restarting the owned preview, Read state returned disconnected,
has_device=false, generation0 and no requested output. No hardware request was
dispatched. Restarted only that owned localhost9860 app, now session67798/-B.
Reviewed the actual production app disconnected at1100/768/390/320px widths;
observed scroll widths1100/753/375/305px respectively, no horizontal overflow.
Selected only the profile and opened/closed/scrolled Settings. Mobile dialog
client/scroll width334px; after626.4px scroll, header top43px and Stop/OFF bounds
93.4..135.4px remained visible. Zero browser console warnings/errors. Reset
viewport and left the modern preview open/disconnected. No Connect/Identify,
output, mode or Apply action and no simulator/backend substitution.

Requirement -> method -> result: visual clarity/responsiveness -> desktop/tablet/
phone screenshots and bounds/scroll inspection -> PASS. Retained control behavior
-> AST comparison of all GUI functions except layout constructor, byte-unchanged
hardware TOML and full existing source/wheel suite -> PASS software. No new
implementation-mirroring tests were added for this presentation-only change.
Command: uv run --locked --offline --group dev --extra gui python -B scripts/verify.py.
201 source +201 isolated installed-wheel tests PASS, zero failures/errors/skips;
lint/format, locked build/install/import/help and exact Python/CSS wheel parity PASS.
148 local Markdown targets PASS. Prior direct-validation/XML artifacts were
restored byte-for-byte after retaining the new run under webui-modern-* names;
their historical evidence/hashes are preserved. No bench result was reclassified.

Artifacts: records/webui-modern-validation.json, webui-modern-direct-validation.json,
webui-modern-offline-tests.xml, webui-modern-wheel-tests.xml and desktop/phone/
Settings/scrolled-phone PNGs. README, GUI guide, PROJECT/STATE and report updated.
REQ-226 PASS within presentation/software scope. REQ-225 remains partial on its
specific missing KSC101 contracts; native physical qualification remains UNTESTED.

## E197 - Visual implementation publication checkpoint

Committed only gui.py's presentation headings/class names and shutter.css in
66bc05e, after cached-diff checks and the E196 source/wheel/browser validation.
git push origin main succeeded from44a9db6 to66bc05e; git ls-remote returned
66bc05e21d61e486f349a5839e2c75e2c8f9783c, matching the implementation checkpoint.
Documentation, current state/report and separately preserved modern evidence are
included in this following checkpoint; final staged source/artifact hashes and
remote parity are checked before/after its publication respectively. No device
operation or expansion of qualification occurred for publication.

## E198 - Current real modern-WebUI baseline and supported finding

REQ-227 / TEST-227: the new user request calls for real WebUI hardware testing,
operator-like control, fixes and script updates. Read-only actions proceeded;
a new bounded output confirmation was requested because the prior1s-cycle scope
was consumed. No answer has been received in this checkpoint. The proposed scope
is up to two protected Manual cycles, Open/Close within5s and one1s host hold,
at least2s OFF between, then OFF/readback/release. This is not granted by elapsed time.

Visible localhost9860 production controls connected to actual SH05R/KSC101
68800777, firmware1.0.7/hardware3/channel1, endpoint192.168.1.19:40305. Connect
returned Manual/OFF0x2000, interlock requirement true and no fault. Read device
settings returned2000ms ON,2000ms OFF,5cycles. Live readback advanced timestamps
but replaced "Device cycle settings read. No defaults were written." with
"Readback updated." Confirmed the message-loss finding in actual browser captures.
Released the real handle before restarting the owned server for the fix.
No SDK, simulator, direct callback substitute or output/configuration write.

## D062 - Preserve operator messages and isolate campaign evidence

Successful background polling updates sample data but leaves the last command/
refusal notice intact; explicit Read still reports its own result. Timed pulse
requires displayed Manual/OFF as well as independent fresh owner preflight.
The owner, APT frames and live qualification TOML remain unchanged. Verification
may select explicit paths under tests and prefix safe filenames under records,
while retaining full-suite defaults. Always record selected coverage, never
promote omitted physical tests to PASS and preserve older campaign artifacts.

## E199 - Real read-only verification of fixes and scoped package checks

Restarted the verified-released app on9860, owned session45170/-B. Reconnected
and re-read real identity/Manual/OFF and unchanged2000/2000ms/count5. Actual
polling after the fix advanced the electrical timestamp while preserving the
settings-command message. Already-Manual selection followed the existing no-op
query path. No new mode/EEPROM/trigger/output command. Final actual read at
2026-11-07T01:01:25.564769UTC was Manual/OFF0x2000/no fault; Release and Read
then returned disconnected, has_device=false, no requested output and unknown
feedback. Browser console warnings/errors empty; viewport reset, preview retained.

Method -> result: actual browser/production TCP read flow and command-message
retention -> PASS for exact configuration; new Manual ON/OFF and timed cycle ->
UNTESTED/BLOCKED pending physical safeguards/cycle confirmation. No new blade
observation, calibrated timing or broader native-mode qualification is claimed.

Four offline UI cases use preserved actual ON/OFF observations, no emulated
device or byte transport: poll preserves notice, explicit Read supplies a notice,
OFF enables the timed button and ON disables it while OFF remains available.
4 source +4 isolated installed-wheel cases PASS. Command:
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py
--test-path tests/test_webui_live_regressions.py --record-prefix webui-hardware-.
Lint/format, locked build/install/import/help, Python/CSS parity and config checks
PASS. Invalid test paths and path-like prefixes are refused before verification.
The broader201-case simulated/fault suite was not run in this campaign; previous
records remain intact. The historical saved-evidence checker still PASS; the new
record intentionally returns PARTIAL and exit2 because recorded cycles=0.

Artifacts: webui-modern-hardware-live.json, settings/OFF/released screenshots,
webui-modern-hardware-evidence-validation.json, webui-hardware-direct-validation.json,
webui-hardware-offline-tests.xml, webui-hardware-wheel-tests.xml and the hardware
validation manifest under records. Current session is blocked only for physical
control; no additional action is authorized by a pending unanswered prompt.

## E200 - Approved actual two-cycle flow on final GUI source

The user answered "Confirmed; up to two protected cycles" to the exact setup,
source-blocked/trigger-isolated/key-interlock question and proposed5s Manual,
1s host hold,2s minimum OFF, final OFF/release limits. Recorded the renewed scope
before actuation. Finished the third supported UI fix: released Read must state
disconnected/no device feedback, rather than claim "Readback updated." Restarted
the verified-released owner to final GUI source, localhost9860/session57830/-B.

Rechecked the new disconnected message, then actual68800777/1.0.7/Manual/OFF.
Used visible controls only, no injected transport/API/callback/SDK substitute.
Checked the human-confirmed protection assertion. After initial OFF rest and
an announced3s viewing delay, clicked Open/ON once. Fresh ON0x2001 at
2026-11-07T01:09:20.350605UTC; timed pulse was disabled. Clicked Release while
active: refused with Stop/OFF guidance, has_device=true/requestedON/no fault.
In a finally-protected browser sequence clicked Close/OFF; fresh OFF0x2000 at
01:09:21.098912UTC. Readback interval0.748307s, ON-click to OFF-click0.708s,
both within5s. These are host/controller observations, not calibrated optical time.

After28.177088s from OFF readback to the next click (>=2s), clicked the1s timed
button exactly once at01:09:49.276UTC. Existing owner completed its internal
ON/readback/1s host hold/OFF and returned Manual/OFF at01:09:50.631357UTC.
No transient ON screenshot is claimed for this timed cycle; the separate first
cycle captured fresh ON. No third ON or hidden retry. Read cycle settings again:
2000ms ON/2000ms OFF/count5 unchanged. Final fresh Manual/OFF/no fault at
01:10:10.710233UTC, then Release/Read confirmed disconnected, no handle and
unknown feedback with the corrected disconnected message. Cleared the local
protection checkbox, reset viewport and retained the released WebUI. Console
warnings/errors empty. Authority for those two cycles is consumed.

TEST-227 requirement -> actual browser/production-controller method -> PASS for
the selected flow: ON/OFF, timed hold, active-release refusal, ON-state pulse
gating, settings unchanged, final OFF/release and truthful disconnected read.
Independent blade observation was requested separately and is pending; no optics
or native-mode/EEPROM qualification is inferred. Existing broader gaps remain.

Final5 saved-real-sample UI cases PASS from source and5 from an isolated wheel;
Python/CSS parity, lint/format, locked build/install/import/help/config checks PASS.
Command: verify.py --test-path tests/test_webui_live_regressions.py
--record-prefix webui-hardware-final-. No emulated device/transport test ran.
The initial4/4 software results remain under webui-hardware-* and final5/5 under
webui-hardware-final-*. The live-evidence checker now PASS with recorded_cycles2;
it previously returned PARTIAL/exit2 while cycles were missing. Final raw captures
and final OFF/released screenshots remain distinct from the read-only phase.
The final checker also rejects three altered saved-data cases without device
I/O: missing cycles remains PARTIAL/exit2, unconfirmed output authority fails,
and an inconsistent ON observation fails. Results are in
records/webui-hardware-checker-negatives.json. Capture provenance clarifies that
early read-phase captured_at values mark capture start; controller feedback
timestamps, not those capture-start values, define the recorded readback intervals.

## E201 - Current WebUI fixes and evidence delivery

Implementation43e80a4 includes the three GUI fixes, five saved-real-sample UI
regressions and scoped/prefixed verification plus strict live-evidence checking.
Reviewed the explicit staged allowlist/cached diff; final source/package checks
are recorded in webui-hardware-final-direct-validation.json. The preserved real
fixture records/webui-final-live.json remains unchanged and is hashed separately
from the new real capture; it is offline regression input, not a new bench result.

git push origin main succeeded38f006a ->43e80a4. Bounded git ls-remote returned
43e80a4804143978203efce75b0c8281312cac66, matching the published implementation.
This following checkpoint contains docs, state/report, raw real observations,
both software phases, validator results and actual screenshots. Final staged
source/artifact hashes and remote parity are checked before/after publication.
No additional device action is associated with delivery. Independent blade
observation for this run remains pending; consumed two-cycle scope is not renewed.

## E202 - Human observation follow-up for the two-cycle run

The user reports: "I did not observe both cycles". Independent blade motion for
the complete E200 run remains UNVERIFIED; this is not evidence of failed motion.
records/webui-modern-hardware-observation.json preserves the exact report and
interpretation separately from the unchanged raw capture. The derived hardware
summary points to this follow-up; controller readbacks and final release remain
as recorded. E191/E192's earlier single observed cycle is a separate result.
No new cycle authority is granted.

## D063 - Connection-scoped state and explicit validation boundaries

Retire confirmed-safe output history at release so a future read-only session
does not send incidental OFF. Preserve active requests, faults and uncertainty;
only protected verified recovery clears stale requests without output. Invalidate
OFF rest before every ON attempt. Scope GUI drafts/assertions to target and
connection generation, preserving same-connection edits during ordinary polls.
Keep public owner/status contracts, APT framing, configuration and permissions.
No SDK/compatibility backend or automatic device operation is introduced.

Hash the frozen real-observation regression input and require positive executed
JUnit counts with no failures/errors/skips. Preserve old campaigns separately.
The new tests use software fixtures only; their PASS does not renew bench proof.

## E203 - Follow-up review reproductions / TEST-228

Starting checkout 547ad94 was clean. New owner regressions reproduced eight
failures before fixes: stale OFF rest, incidental shutdown output after a healthy
or faulted read-only reconnect, stale recovery request, duty-policy bypass,
interlock changes after mode/settings writes and stale native Start request.
records/followup-review-baseline.xml preserves the failing run. The later GUI
baseline reproduced four failures and one passing control (eight deselected):
stale settings drafts and assertions after disconnect/reconnect.
records/followup-gui-baseline.xml preserves that separate phase.

Commands used the locked offline dev/gui environment, python -B -m pytest -q
--tb=short -p no:cacheprovider with explicit tmp basetemp and records JUnit paths.
Owner baseline selected tests/test_review_regressions.py at its eight-case
revision; GUI baseline selected that file with -k 'drafts or assertions'.
These were controlled software reproductions, not hardware tests.

## E204 - Final integrated software validation / TEST-228

uv run --locked --offline --group dev --extra gui python -B scripts/verify.py
--record-prefix followup-review-: 228 source and 228 isolated installed-wheel
tests PASS, zero failures/errors/skips. Lock, lint/format, build/install/import/
help/config checks, exact Python/CSS parity and frozen-fixture input hashes PASS.
records/followup-review-direct-validation.json and the prefixed source/wheel XMLs
preserve commands, totals, stdout and source/package hashes.

uv run --locked --offline --group dev --group notebooks --extra gui python -B
scripts/verify_notebooks.py: all six notebooks PASS static schema/syntax/link
checks, no cell execution. Copied result to records/followup-review-notebooks.json
and restored the earlier campaign's notebook-validation.json unchanged.
No instrument connection, physical operation or running-preview replacement
occurred. Owner/GUI changes require separate physical requalification.

## E205 - Migration, provenance and generated cleanup / TEST-228

Removed 32 verified generated cache/pytest directories: 699 files, 174667 bytes.
Each absolute target was checked for workspace containment, reparse links,
unchanged contents and absence of tracked files before native PowerShell removal.
records/followup-review-cleanup.json preserves inventory/results. Environments,
local config, ownership state, manuals, source preimages, backups, reference tools,
ambiguous tmp history and real evidence were retained. Review-owned inventory/
audit helpers were removed separately after use.

README/API/GUI/architecture/cutover/acceptance instructions now explain connection
lifetime, qualification limits and released-owner restart/browser reload.
STATE.md and outputs/REPORT.md contain current conclusions; prior history remains
in Git and these records. Retired SDK/probe/notebook-wrapper paths remain absent;
public DiamondGUI owner/status names remain intentional contracts.
records/followup-review-validation.json captures final source/fixture/manual/
artifact checks, local Markdown links and cleanup absence checks. Full project
acceptance remains BLOCKED on the documented physical/manufacturer/external gaps.

## E206 - Follow-up implementation and checkpoint publication

Commit 460286ffde8116e8f15b232f9402357d0825d648 contains the reviewed owner/GUI,
strict verification, shared callback helper, regressions and README/API/migration
instructions. All 43 validated inputs matched staged Git blobs before commit.
git fetch origin main found no divergence; push advanced 547ad94 -> 460286f.
Bounded git ls-remote returned 460286ffde8116e8f15b232f9402357d0825d648,
matching local HEAD. No device operation accompanied publication.

This following checkpoint delivers the compact state/report, acceptance notes,
human observation, before/after software evidence and cleanup/provenance manifests.
Explicit staged inputs/artifact hashes are checked before commit and final remote
parity/clean status after push. Full hardware acceptance remains BLOCKED as stated;
scoped repository-review completion does not extend any physical authorization.

## E207 - Cowork resumption reconciliation / TEST-228

2026-11-08 (hash inspection at 22:18 UTC), HEAD
5d2adc1edeb93a3b827974c12ee957a2b6c9255f. Starting working tree clean.
Read PROJECT.md, STATE.md, current report, source register, physical validation
plan and the final review records. PowerShell Get-FileHash SHA256 checked every
entry in followup-review-validation.json source_sha256, artifact_sha256,
prior_campaign_artifacts_preserved and manual_integrity: 86 checks, 0 mismatches.
Parsed saved source/wheel JUnit XML: each 228 tests, 0 failures/errors/skips.
This is artifact reconciliation, not newly executed test or hardware evidence;
no source change or new failure justifies repeating the satisfied software suite.

git rev-parse HEAD and git rev-parse @{upstream} both returned the revision
above. git -c credential.interactive=never ls-remote --exit-code origin
refs/heads/main failed before remote access: Git usr/bin/sh CreateFileMapping,
Win32 error 5, then "Could not read from remote repository". Current live remote
parity is UNVERIFIED; no remote divergence is inferred from this local failure.

No device operation, preview/server replacement or transient-state inspection.
Full acceptance remains BLOCKED. STATE.md now gives one concrete request for a
fresh protected, observed Manual WebUI cycle; prior consumed approvals are not
renewed by the user's "cowork session" request. No actuation is scheduled or
authorized by this checkpoint. External manufacturer, calibration, broader
deployment and DiamondGUI gaps remain unchanged.

## D064 - Separate mode selection from native activation / REQ-229

8 November 2026 user request: "allow operation mode selection on gui". The
connected SH05R screenshot showed Single/Auto/Triggered disabled because the
GUI and set_operating_mode used output qualified_modes as a selection gate.
Use the existing allow_persistent_mode_changes opt-in for protected selection
of all four published APT modes. Keep qualified_modes as the independent native
Start/priming gate; do not fabricate physical qualification or add another policy
field. Fresh OFF, interlock requirement, source inhibition, explicit OFF before
mode change, persistent-change permission and exact readback remain enforced.
Stop/OFF and failure cleanup accept supported selectable modes so selecting one
cannot strand the operator behind an activation-qualification refusal. No ON is
sent by mode selection. The tracked profile explicitly keeps qualified_modes
manual-only; settings/EEPROM permissions are unchanged. No live device operation
is authorized by this UI implementation request or performed here.

Concurrent edits consolidated ownership, errors and transports while this change
was being tested. The user explicitly chose "Integrate concurrent changes";
preserve those edits and validate the combined files. Focused callback/owner
checks passed (116 tests). Final software evidence will identify the integrated
source; earlier full-suite PASS evidence is historical after these source edits.

## D065 - Keep ownership and exceptions with their implementation / REQ-230

8 November 2026 user asks to slim repository structure and explicitly remove
ownership.py (handled in controller.py) and errors.py. Keep the existing OS lock
keys, directory, acquisition/release rules and persistent uncertainty journal
inside controller.py as a private implementation. Put shared/protocol errors
in protocol.py, identity mismatch in device.py and route rejection in transport.py.
Keep the package-level public exception imports. Consolidate TCP with the other
byte transports; do not add compatibility wrappers for removed internal modules.

Fold notebook schema/syntax/link checks into pytest, preserving actual notebook
files/outputs and passive exact-route tests. nbformat is now an explicit dev
dependency at its already locked version; no package version changed. Remove
the superseded Kinesis REVIEW/DELAY_AUDIT/CHANGE_REVIEW documents and the retired
KEH3 probe stub; historical evidence links point at immutable Git content.
Raw records, PDFs, backups, environments, local configuration and ownership
state remain. The independent mode-selection edits are retained and included
in combined software validation; no device I/O or server restart is authorized.

## E208 - GUI mode-selection integrated software validation / TEST-229

8 November 2026, final verification reconciled at 22:26 UTC. D064 implements
protected selection of Manual/Single/Auto/Triggered using the existing persistent
mode permission while retaining Manual-only activation qualification. Regression
coverage checks refused unprotected transitions before writes, OFF/readback,
all native selections, blocked native Start with no ON frame, Stop, return to
Manual, release, wrong-mode readback fault/cleanup, and GUI connected/disconnected/
faulted/native states. 116 focused tests PASS. The GUI's selected styling follows
actual readback; the Triggered tooltip no longer implies selection primes output.

Final command (existing complete user uv cache):
uv run --offline --no-sync python -B scripts/verify.py
--record-prefix gui-mode-selection-

236 source and 236 exact isolated-wheel tests PASS, zero failures/errors/skips.
Lock current/rejected-missing/rejected-outdated, lint/format, Python/CSS wheel
parity, hash-locked clean dependency install, SDK/native-free imports, CLI/WebUI
help and passive config checks PASS. Static notebook checks are now in pytest
under the user-authorized concurrent consolidation. All 39 verifier input hashes
matched current files after completion. Source edits in both sessions are
included; no changes were discarded. Detailed commands, stdout, test totals and
source/wheel hashes: records/gui-mode-selection-direct-validation.json, source/
wheel XMLs, focused XML and records/gui-mode-selection-validation.json.

Environment failures were resolved without touching hardware: Windows sandbox
pytest-directory access denied; project-local cache lacked locked dependencies;
concurrent dependency edits briefly invalidated the lock; active GUI executable
prevented project-environment sync. Outside-sandbox software execution with the
existing user cache and a --no-sync launch succeeded. The verifier independently
checks the lock and builds/installs/tests a clean wheel. The initial 489868-byte
generated untracked environment-error XML was removed after its access-denied
diagnosis was summarized here; final passing records are retained.

No device read/write, browser hardware exercise, server takeover, restart or new
physical qualification occurred. Existing GUI still requires a released-owner
restart and browser reload. Physical/deployment gaps and consumed cycle limits
are unchanged. REQ-229 PASS applies to software, not a live mode transition.

## E209 - Combined slimming validation / TEST-230

8 November 2026; D065 / REQ-230. Removed ownership.py, errors.py and ethernet.py
as separate internal modules; retained their behavior in controller.py,
protocol.py/device.py and transport.py respectively. Updated imports and the
cross-process test to exercise public ShutterHub ownership. Package-level
ShutterError/UnsupportedRoute names and owner/status contracts remain intact.
Runtime Python modules: 12 -> 9. Maintained scripts: 3 -> 2, with notebook
schema/syntax/link checks integrated into pytest. nbformat uses its existing
locked version; the lockfile adds only dev-group membership/metadata, with no
package version changes. Removed superseded outputs/REVIEW.md,
outputs/DELAY_AUDIT.md, outputs/CHANGE_REVIEW.md and the retired
KEH3-probe documentation stub; historical links use immutable Git content.
The current report now summarizes the resulting system rather than older reviews.

Command, using the existing complete user uv cache and installed environment:
uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix slimming-

Observed: 236 source + 236 isolated installed-wheel tests, zero failures/errors/
skips. PASS: current/rejected-missing/rejected-outdated lock checks, lint/format,
locked build/install, exact Python/CSS wheel parity, SDK/native-free imports,
CLI/WebUI help, passive config and all six notebooks' static checks. No notebook
hardware cell was run. Commands/stdout, source/fixture hashes, totals and wheel
hash are in records/slimming-direct-validation.json; source/wheel JUnit records
are records/slimming-offline-tests.xml and records/slimming-wheel-tests.xml.
Source inputs remained unchanged during verification. Concurrent mode-selection
work is retained and included (E208); this does not qualify a live mode write.

Initial attempts hit Windows sandbox access denial for pytest-created temporary
folders and incomplete project-local uv build metadata. The passing run used
normal filesystem permissions, the existing complete user cache and --no-sync;
the verifier itself checks the lock and constructs a clean isolated install.
Removed only tmp/slimming-owner-tests, .ruff_cache and
src/thorlabs_shutter_control/__pycache__: each absolute target was verified inside
the workspace, without tracked files or reparse links before PowerShell removal.
Raw evidence, PDFs, user notebook outputs/backups, .venv, local configuration,
ambiguous historical tmp contents and runtime locks/journals were preserved.
Final audit PASS: all 39 verifier input hashes still match, local links in 23
Markdown documents exist, and the lock differs only by nbformat dev membership/
metadata. Git confirms raw evidence, PDFs and notebook files are unchanged.
No device operation, server restart, commit or push.
REQ-230 is COMPLETE for software; full physical acceptance remains BLOCKED.

## D066 - Three-module core migration / REQ-231

8 November 2026: user says "implement" after the prune/migration plan. Preserve
public package-level ControllerConfig/Policy/Route/CycleParameters/owner/error
names and existing safety checks. Put Route, connection validation and explicit
inventory in transport.py; configuration, KSC101 driver, ownership and normalized
control in controller.py; retain APT framing/deadlines in protocol.py. Remove
config.py/device.py/discovery.py with no compatibility wrappers. Internal imports
are updated; the inspected external DiamondGUI adapter imports the package root.
No external application edit or device operation is included.

Allow absent hub serial/firmware metadata rather than explanatory placeholder
strings. Validate supplied metadata and reject conflicts between known values,
even when another route to the same host leaves one field unknown. Preserve
exact serial/firmware, duplicate mapping, operating permissions and load limits.
Consolidate equivalent read/fault handling and repeated parameter checks without
changing output, cleanup, freshness or persistence semantics. Current baseline
is the 39 reconciled E209 input hashes and its saved 236 source/wheel tests.

## E210 - Three-module core validation / TEST-231

8 November 2026; D066 / REQ-231. Implemented the approved plan. Removed
config.py/device.py/discovery.py, leaving controller/protocol/transport as the
control core plus GUI and package/CLI entry points. Configuration/load policy,
TOML loading and KSC101 driver now reside in controller; Route, route validation
and explicit inventory reside in transport. Package-level constructors, error
names and owner/status contracts remain. Internal old module paths have no
wrappers. The inspected external DiamondGUI hardware adapter and its canonical-
owner test import from the package root; no external application was edited.

Unknown hub serial/firmware are optional None and omitted from the tracked live
TOML. Known metadata still validates as nonempty text and conflicts are checked
per field across routes to the same host, including partial/unknown entries.
New software regressions cover actual expected-controller verification with
missing metadata, wrong-serial refusal without output, malformed optional values
and mixed known/unknown hub conflicts before I/O. Existing load/mode/ownership/
framing/deadline/recovery guards remain. Four read operations now share fresh
identity, serialization and fault recording. Repeated numeric/boolean/mode
checks are consolidated. Path-based owner construction avoids double collection
validation. Public parameter models and remaining TOML keys are preserved.

Baseline: all 39 E209 input hashes matched before edits; saved suites each
contained 236 passing tests. Runtime modules 9 -> 6; runtime Python lines
2568 -> 2550 (18 fewer, primarily structural consolidation). Driver KSC101,
Identity, CycleParameters and IdentityMismatch class ASTs match the original Git
implementation. A mechanical move briefly introduced GUI symbol encoding errors;
they were restored to UTF-8 before the passing test run and checked explicitly.

Final command with existing user cache/environment and normal filesystem access:
uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix core-migration-

Observed: 250 source + 250 isolated installed-wheel tests PASS, zero failures,
errors or skips. Current/rejected-missing/rejected-outdated lock checks,
lint/format, locked wheel build/install, exact Python/CSS parity, SDK/native-free
imports, CLI/WebUI help and passive config PASS. All six notebooks pass static
schema/syntax/links and passive exact-route setup; no hardware cells ran.
Commands/stdout, test totals and source/fixture/wheel hashes are preserved in
records/core-migration-direct-validation.json, with source/wheel JUnit evidence
in records/core-migration-offline-tests.xml and records/core-migration-wheel-tests.xml.

Final audit: all 36 verifier input hashes match, local links in 23 Markdown
documents pass and GUI Unicode symbols are intact. Raw records/manual PDFs/
notebook files are unchanged. Earlier pending mode-selection/slimming changes
are retained. No dependency or native driver change, device I/O, server restart,
external application edit, commit or push. REQ-231 COMPLETE is software-only;
full physical/deployment acceptance remains BLOCKED as documented in STATE.md.


## D069 - Organize controller responsibilities / REQ-234

8 November 2026: user requests organization of controller.py. Keep the approved
three-module core and use sections inside the existing file. Order validation,
configuration, KSC101 models/commands, application status, internal ownership
and the shared owner. Group public owner methods by lifecycle, reads, settings,
outputs and protection/recovery; place internal helpers afterward. Preserve all
method bodies, signatures, decorators, command order and safety checks. No new
abstractions, dependencies or hardware operation. REQ-234 / TEST-234 avoids the
REQ-232 identifier concurrently allocated by other organization work.

## E213 - Controller organization validation / TEST-234

8 November 2026; REQ-234 / D069. All 36 E210 verifier input hashes matched before
this edit. records/controller-organization-structure.json records exact before/
after controller hashes and PASS AST comparison: all 16 top-level definitions
and 44 ShutterHub methods preserved; comparison excludes only definition/method
order and the module navigation docstring. Section comments improve navigation.

Expected: unchanged API and executable method content, passing source and exact
installed-wheel regressions, no changed verifier inputs during the accepted run.
Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix controller-organization-

The sandbox-only launch could not access the existing uv cache; the authorized
normal-access offline run proceeded. Its 250 source + 250 wheel tests passed,
but final provenance checking correctly rejected the run because concurrent
protocol.py/transport.py work changed inputs. No PASS campaign is inferred from
that rejected attempt. Failed-run diagnostics remain under tmp/verification-*.
A fresh complete run on the combined checkout PASSed: 250 source + 250 installed-
wheel tests; zero failures/errors/skips. Lock checks (including missing/outdated
rejection), Ruff lint/format, exact wheel Python/CSS parity, clean install/import,
CLI/WebUI help and passive config checks PASS. Notebook checks are static and
passive only. No hardware cells, lab networking or device commands executed.

Evidence: records/controller-organization-direct-validation.json with commands,
stdout, source/fixture/wheel hashes and test totals; records/controller-organization-
offline-tests.xml and records/controller-organization-wheel-tests.xml. All 36
successful-run input hashes match at final audit; controller hash also matches
the structural comparison. Existing unrelated/concurrent work is preserved.
No server takeover/restart, external application edit, commit or push. Scoped
controller organization COMPLETE; full physical/deployment acceptance remains
BLOCKED on the existing dependencies. Software results do not qualify hardware.

## D070 - Organize protocol responsibilities without changing behavior

8 November 2026; user request "organize protocol.py", REQ-235 / TEST-235.
Keep the existing three-module core and public protocol names/signatures. Clarify
the message table and group definitions by responsibility. Extract the existing
pending-traffic check and reply polling into Session private helpers, keeping
send/query visible before their helpers. Preserve the order of transport access,
deadline/cancellation checks, decoder validation, event retention and poisoning
on any query failure. Reuse existing regressions rather than add tests that
mirror a behavior-preserving extraction. No device I/O is needed or authorized.
REQ-235/TEST-235 replaces this task's initially colliding REQ-232/TEST-232;
concurrent controller/transport organization tasks retain separate conclusions.

## E214 - Protocol organization validation / TEST-235

8 November 2026; D070 / REQ-235. Message IDs and payload sizes are annotated;
errors, deadlines, framing and serialized sessions have clear responsibility
groups. Session.query delegates pre-request traffic validation to _drain_pending
and reply polling to _wait_for_reply. Frame/Decoder logic, wire values, public
signatures and error strings remain unchanged. Existing pending core migration,
mode-selection, slimming and concurrent organization work is preserved.

Expected: existing software regressions pass in source and the isolated installed
wheel, with zero skips/failures/errors; lint/format and package parity pass.
Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix protocol-organization-

The initial sandboxed invocation failed before executing the verifier because
uv could not read its existing user cache (Access is denied, os error 5).
Rerunning the same offline software-only command with approved cache access
succeeded. Observed: 250 source + 250 isolated installed-wheel tests PASS, zero
failures/errors/skips. Coverage includes fragmentation, malformed frames, wrong
addresses/channels, faults, stale/duplicate replies, cancellation, deadline expiry,
partial/late writes, cleanup, owner/driver integration and static notebooks.
Lock checks (including rejected missing/outdated locks), Ruff lint/format,
locked build/install, exact Python/CSS parity, SDK/native-free imports, CLI/WebUI
help and passive configuration PASS. git diff --check PASS. All 36 verification
input hashes matched the working tree at final audit, including concurrent
controller/transport edits. This is combined software evidence, not authority to
claim those independently managed tasks complete.

Commands, results, input and wheel hashes:
records/protocol-organization-direct-validation.json. JUnit reports:
records/protocol-organization-offline-tests.xml and
records/protocol-organization-wheel-tests.xml.
REQ-235 PASS / COMPLETE in software scope. E214 revalidates affected earlier
software behavior on this revision; it does not extend physical evidence.
No device I/O, server restart/takeover, dependency change, external application
edit, commit or push occurred. Full physical/deployment acceptance remains
BLOCKED on the separate dependencies in STATE.md.


## E215 - Transport organization / TEST-233

8 November 2026; REQ-233 derived from the user's request to organize transport.py.
Grouped route configuration/selection before the TCP/VCP/D2XX byte backends,
followed by explicit informational inventory. Named the shared KEH3 bay-port
mapping and 4096-byte read limit. Documented the backend interface, route model,
USB initialization helper and USB backend constraints. Kept existing public names,
route mappings, lazy imports, initialization sequence, deadline checks, single-
send/partial-write behavior, cleanup and qualification guards. Existing regression
tests suffice for this structural change; none were added. Concurrent protocol/
controller work is preserved. The initially allocated REQ/TEST-232 collided with
protocol organization; transport uses REQ/TEST-233.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix transport-organization-

The first sandboxed launch failed before verification because uv could not open
its existing user-cache sdists-v9/.git. The same offline software-only command
then completed with approved normal filesystem access to that cache.
Observed: 250 source + 250 isolated installed-wheel tests PASS, zero failures,
errors or skips. Existing tests cover exact bay selection, loopback TCP fragments/
disconnect, exact-serial USB initialization, expired budgets, passive discovery
and owner/qualification guards. Lock/lint/format, exact wheel Python/CSS parity,
clean install/import/help, passive config and six static notebooks PASS.
Expected missing/outdated-lock rejection checks passed; no hardware cells ran.

Commands, results, source and wheel hashes:
records/transport-organization-direct-validation.json. Test evidence:
records/transport-organization-offline-tests.xml and
records/transport-organization-wheel-tests.xml. git diff --check PASS.
E215 revalidates combined pending software after E210; E210 remains historical.
Final audit: all 36 recorded verifier input hashes match the working tree.
No device I/O, server restart, external application edit, commit or push.
REQ-233 COMPLETE is software-only; full physical/deployment acceptance remains
BLOCKED on the separate dependencies in STATE.md.


## D071 - Remove unnecessary controller indirection / REQ-236

8 November 2026; user requests "clean up the codes" after the helper review.
Inline the single-use _cleanup_after_error into _output_operation and remove
text()'s unused return. Keep positive/text/utc_now and the shared policy/preflight
helpers: they avoid repeated validation and retain a useful operation boundary.
Preserve original exceptions, separate cleanup notes, protective OFF's independent
budget, uncertainty lockout and public owner methods. No hardware action.

## E216 - Controller helper cleanup validation / TEST-236

8 November 2026; D071 / REQ-236. All 36 E215 input hashes matched before editing.
Expected: only the planned controller edits, original-error/cleanup regressions
pass, unchanged public owner contract, and exact source/wheel integration PASS.
Reverse substitution of the two approved edits reconstructs E215's exact
controller SHA-256; this confirms no unrelated controller delta. Static AST check:
all five text() calls discard its return. Controller 1163 -> 1159 lines.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix controller-cleanup-
Ran with approved uv-cache access. Observed: 250 source + 250 installed-wheel
tests PASS, zero failures/errors/skips, including failed output/partial write,
separate cleanup budget, retained original error/cleanup note, cancellation and
fault lockout regressions. Lock checks, Ruff lint/format, exact wheel Python/CSS
parity, clean install/import, CLI/WebUI help, passive config and static notebooks
PASS. Existing regression tests suffice for this focused cleanup; no new tests
or dependencies. No notebook hardware cells, devices or lab network accessed.

Commands, stdout, source/fixture/wheel hashes and totals:
records/controller-cleanup-direct-validation.json; JUnit evidence:
records/controller-cleanup-offline-tests.xml and controller-cleanup-wheel-tests.xml.
All 36 input hashes match at final audit. REQ-236 COMPLETE, software scope.
Earlier organization evidence remains historical; this campaign revalidates the
combined software. Unrelated pending changes preserved. No server takeover/
restart, external application edit, commit or push; physical acceptance remains
BLOCKED on the existing dependencies in STATE.md.

## D072 - Inline single-use protocol helpers / REQ-237

8 November 2026; user explicitly requests inlining _drain_pending and
_wait_for_reply into query while keeping _check, _accept and clock. Remove
only the two single-use methods and their calls, retaining the transaction's
order, outer exception/poisoning boundary, errors, deadlines, cancellation,
event retention and reply ambiguity checks. Existing regressions cover the
behavior; no implementation-mirroring tests or device operation are needed.

## E217 - Protocol helper cleanup validation / TEST-237

8 November 2026; D072 / REQ-237. Inlined both helper bodies into query and
removed their definitions. _check, _accept and clock are unchanged. AST
comparison against Git HEAD confirms those three functions are identical;
query's executable AST matches the original committed transaction (excluding
the added explanatory docstring). Neither removed helper remains defined.
Other pending source, configuration, evidence and documentation are preserved.

Expected: existing protocol/owner regressions and source/isolated-wheel software
checks pass with zero skips/failures/errors and exact package parity.
Command, run with approved access to the existing uv cache:
uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix protocol-cleanup-

Observed: 250 source + 250 isolated installed-wheel tests PASS, zero failures,
errors or skips. Coverage includes fragmented/malformed frames, interleaved
events, wrong addresses/channels, rich faults, stale/duplicate replies,
cancellation, expired/late I/O, ambiguous writes and protective cleanup.
Lock checks, Ruff lint/format, exact Python/CSS wheel parity, clean install,
SDK/native-free imports, CLI/WebUI help, passive config and static notebooks
PASS. git diff --check PASS. All 36 verifier input hashes match at final audit.
Commands/results/hashes: records/protocol-cleanup-direct-validation.json.
JUnit: records/protocol-cleanup-offline-tests.xml and
records/protocol-cleanup-wheel-tests.xml.

REQ-237 COMPLETE in software scope. This revalidates affected prior software
behavior on the final configuration, not physical acceptance. No device I/O,
lab network, running-server operation, external application edit, dependency
change, commit or push. Full physical/deployment acceptance remains BLOCKED
on the independent conditions in STATE.md.


## D073 - Simplify transport logic without weakening route guards / REQ-238

8 November 2026; user approved the transport review's recommended first changes.
Use TCP read(0) directly for nonblocking reads, relying on existing no-data/EOF
handling; pass configured host and the shared bay-port mapping directly to TCP.
Inline the single-caller require_control_route checks into ShutterHub._policy,
keeping external-USB/VCP restrictions, order, exception types and messages.
Retain UnsupportedRoute in transport and at the public package root. Exercise
both restrictions through public owner operations rather than the removed helper.
Keep all three backend classes, USB waits/initialization, VCP/D2XX reads and
single-send handling unchanged. No new base class, device action or server change.
REQ/TEST-238 and D073 are allocated for this transport task; protocol helper work
is concurrent under REQ/TEST-237. Expected final evidence: E218.


## E218 - Transport logic simplification validation / TEST-238

8 November 2026; D073 / REQ-238. Removed TCP's redundant select readiness check
and import; read_nowait delegates to read(0), which already handles no-data and
EOF. Factory selection now passes route.host and the shared bay-port value
without an endpoint text round trip. Moved both route-write restrictions into
ShutterHub._policy in their original order, preserving UnsupportedRoute and
error messages before load-policy checks. Removed require_control_route without
a wrapper. UnsupportedRoute remains in transport and the public package root.
USB implementations, initialization, deadline checks and single-write semantics
are unchanged. Architecture documentation describes owner-side route guards.

Updated the existing restriction regression to connect through the public owner
using software transports for VCP and KEH3 external routes, attempt ON, safe_state
and Manual selection, require UnsupportedRoute, and assert no output frames and
released handles. Existing loopback tests cover no-data, fragmented receive and
peer disconnection; route tests cover exact docked-bay TCP selection without USB.
No new test file or dependency. Initial focused lint found an unbound lambda loop
variable and then a long line; both were corrected before the full passing run.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix transport-cleanup-
Ran with approved access to existing uv-cache dependencies. Observed: 250 source
+ 250 isolated installed-wheel tests PASS, zero failures/errors/skips. Lock
checks, Ruff lint/format, exact wheel Python/CSS parity, clean install/import,
CLI/WebUI help, passive config and six static notebook checks PASS. Expected
missing/outdated-lock rejection checks PASS. No hardware notebook cells ran.
Commands/stdout, source/fixture/wheel hashes and totals:
records/transport-cleanup-direct-validation.json. JUnit evidence:
records/transport-cleanup-offline-tests.xml and transport-cleanup-wheel-tests.xml.
Final audit: all 36 recorded input hashes match; git diff --check PASS.

E218 revalidates the combined pending software, including concurrent protocol
cleanup; prior campaigns remain historical for their recorded revisions.
Unrelated working changes are preserved. No device I/O, lab-network access,
server operation, external application edit, commit or push. REQ-238 COMPLETE
is software-only; full physical/deployment acceptance remains BLOCKED on the
separate dependencies in STATE.md.

## D074 - Prune duplicate protocol logic / REQ-239

8 November 2026; user says "prune" after the protocol review. Put short-write
rejection inside the transport-write try so one handler sets the two ambiguity
flags. Keep late-complete-write handling separate to retain protective cleanup.
Simplify known message form/length comparison using None for short frames.
Retain diagnostics, _check, _accept and clock; no new helper or device operation.

## E219 - Protocol pruning validation / TEST-239

8 November 2026; D074 / REQ-239. Two focused source edits implemented. Expected:
same framing/write behavior and passing source/isolated-wheel checks. Protocol
Ruff lint/format PASS. Using the exact protocol module from the E218 wheel,
verified its source hash against E218, then compared old/new form predicates for
both forms, all 65536 length values and expected sizes None/6/14/68/84: 655360
comparisons PASS. Ten transport outcomes (counts -1/0/1/5/6/7/None, exception,
complete and late-complete writes) give identical error text/types and flags.

Existing tests/test_protocol.py: 41 PASS, zero skips/failures/errors; JUnit:
records/protocol-pruning-targeted-tests.xml. Command: .venv/Scripts/python.exe -B
-m pytest tests/test_protocol.py -q --tb=short -p no:cacheprovider --basetemp
tmp/protocol-pruning-targeted-retry --junitxml records/protocol-pruning-targeted-tests.xml.
The initial sandboxed targeted run could not access its pytest temporary
directory; the same tests passed with approved normal fixture-directory access.

Full verifier command: uv run --locked --offline --no-sync --group dev --extra
gui python -B scripts/verify.py --record-prefix protocol-pruning-
Initial full run stopped at concurrent controller.py:743 indentation and
gui.py:692 Ruff errors. These unrelated active edits were preserved and repaired
by the concurrent task. The same full verifier then PASSed: 251 source + 251
isolated installed-wheel tests, zero failures/errors/skips. Lock checks, Ruff
lint/format, exact Python/CSS wheel parity, isolated install/import/CLI/WebUI
help, passive config and six static notebooks PASS. No hardware cells executed.
Commands/results/hashes: records/protocol-pruning-direct-validation.json; JUnit:
records/protocol-pruning-offline-tests.xml and protocol-pruning-wheel-tests.xml.
All 36 verifier input hashes match at final audit; git diff --check PASS.
E219 revalidates the combined software, including concurrent transport/controller
changes, and resolves the earlier shared lint blocker. REQ-239 COMPLETE in
software scope. No device I/O, lab network, running-server operation, external
application edit, dependency change, commit or push. Physical/deployment
acceptance remains BLOCKED on its independent conditions in STATE.md.


## E220 - VCP read pruning / TEST-240

8 November 2026; REQ-240. User says "prune" after the transport duplication review.
Replaced VCPTransport.read_nowait's timeout/queue-read body with return self.read(0).
No other transport code changed: reversing this single-method replacement gives
E218's exact transport SHA-256. Kept the route-validation tuple, all three backends,
USB initialization/waits, D2XX queue semantics, cleanup and public interface.

Scoped software checks PASS: a serial byte-buffer substitute with 0/3/5000 queued
bytes returns 0/3/4096 bytes respectively, with timeout 0 s in each case. Normal
package import passes after a concurrent controller indentation repair. Initial
checks could not import because controller.py:743 had unexpected indentation;
an isolated transport import separately passed before that repair. No controller
change from this transport task was applied. Transport Ruff lint/format and
whitespace checks PASS. No permanent test or helper was added for this one-line
prune; the software buffer check does not establish native USB timing.

Full command attempted with approved cached-dependency access:
uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix transport-prune-
Lock check PASS, then Ruff stopped at concurrent gui.py:692:101 E501 (102 > 100).
Its display string has mojibake. Rechecks show the same blocker; no source/wheel
suite was reached, and their earlier PASS results are not claimed for this revision.
Evidence: records/transport-prune-validation.json records scoped results, exact
transport hash/delta and the full-verifier failure. REQ-240 is implemented but
integration BLOCKED, not COMPLETE. Resumption condition: finish the concurrent
GUI repair, rerun the full verifier and require passing source/wheel/provenance
checks. Preserve other active changes; no hardware I/O, server change, external
application edit, commit or push was performed.


## D075 - Simplify status and shared channel metadata / REQ-241

8 November 2026: user requests "vastly simplify them" and "code reduction
substantially" after the controller dataclass review. Asked whether the existing
status-schema preservation constraint could change; user explicitly selected
"Simplify the schema; update repo consumers" after being told external consumers
would need updating. This supersedes prior status-schema preservation within
this migration; public owner operations and configuration/control guards remain.
REQ-241 / TEST-241 replaces the initially colliding REQ-238 identifier.

Merge ShutterFeedback into a flat ShutterStatus, remove derived identity display
fields and unsupported constant placeholders, name the interlock setting
interlock_required, and record human closure as optical_closed_at/evidence.
Have the private channel reuse status metadata and add only owner resources;
copy the explicit public dataclass fields into independent snapshots. Electrical
readings remain absent from host-only snapshots. Frozen configuration/identity/
cycle values remain; public status snapshots are independently mutable copies.
Version 2.0.0 marks the break. Update repo consumers, docs and notebook source;
retain historical captures/outputs. Do not edit the external DiamondGUI checkout
or operate devices/servers. Its consumers require migration before deployment.

## E221 - Dataclass simplification validation / TEST-241

8 November 2026; D075 / REQ-241. Expected: materially reduced status/state code,
unchanged configuration/driver/qualification/claim behavior, independent snapshots
without private resources or cached readings, migrated repo consumers, passing
source/isolated-wheel checks and retained historical evidence.

Observed: status/state definitions plus snapshot mapping 90 -> 41 lines (54%
less), their field declarations 54 -> 30, controller dataclasses 7 -> 6, complete
module 1165 -> 1117 lines. Policy, ControllerConfig, Identity, CycleParameters,
KSC101 and _Claim executable ASTs match the before snapshot exactly. Metrics,
original/current source hashes and evidence audit:
records/dataclass-simplification-models.json.

First 170 focused regressions PASS using normal temp-directory access. Sandboxed
pytest could not access its new temporary directories; that environmental failure
is not a software PASS. A Windows text-encoding issue was caught by lint during
editing and corrected before final validation. An offline uv lock regeneration
attempt changed dependency selections; restored the exact prior lock and changed
only the local project's version. Reversing that version change reproduces the
E216 lock hash exactly, proving dependency pins/artifacts remain unchanged.

Final command: uv run --locked --offline --no-sync --group dev --extra gui python
-B scripts/verify.py --record-prefix dataclass-simplification-
With approved uv-cache access, 251 source + 251 installed-wheel tests PASS; zero
failures/errors/skips. This includes the new snapshot mutation/isolation/private-
resource/no-cached-reading regression, existing fault/cancellation/cleanup/identity/
load limits, and migrated GUI callbacks using the frozen historical real captures.
Only the test fixture loader translates that historical schema; runtime has no
compatibility alias or fallback. Missing/outdated lock rejection, Ruff lint/format,
exact source/wheel Python/CSS parity, clean install/import, CLI/WebUI help and
passive configuration PASS. Six notebooks pass static/passive checks; no hardware
cells executed. All six notebooks' execution counts and outputs match Git HEAD;
source/banner changes explicitly identify saved outputs as historical.

Evidence: records/dataclass-simplification-direct-validation.json contains exact
commands/stdout and source/fixture/wheel hashes; records/dataclass-simplification-
offline-tests.xml and dataclass-simplification-wheel-tests.xml retain JUnit results.
All 36 verifier input hashes match at final audit. Current integration includes
concurrent protocol/transport work; previous transient lint/encoding blockers are
resolved on these hashes. Unrelated working changes preserved. REQ-241 COMPLETE,
software only. External schema migration and physical/deployment acceptance
remain open. No live device I/O, server takeover/restart, external application
edit, commit or push. Historical raw records and manuals are unchanged.


## D077 - Delegate GUI permission decisions to the owner / REQ-242

8 November 2026: user requests "pruning the gui.py reduce guardrails. happy path
focus." Remove duplicated route/qualification/settings policy decisions from
button and option availability. Connected, nonfaulted controls dispatch through
ShutterHub, which remains responsible for permissions, fresh feedback and physical
operating limits. Buttons are not evidence of permission. Preserve session-scoped
source/persistence confirmations, settings drafts, displayed-state conveniences,
exact-target validation, priority OFF, Stop-before-Release and server cleanup.
Remove unsupported display/trigger settings placeholders and their CSS, and use
CycleParameters directly for numeric input validation. This supersedes prior GUI
policy-disable expectations, not owner policy or device qualification.

## E223 - GUI pruning validation / TEST-242

8 November 2026; D077 / REQ-242. Expected: materially shorter GUI, retained supported
controls, owner refusals despite enabled controls, unchanged dispatch and shutdown
cleanup, and passing complete source/isolated-wheel software checks.

Observed: gui.py 806 -> 682 lines, 124 fewer (15.4%). execute_action and run have
identical executable ASTs to the pre-edit snapshot. The numeric adapter and
unsupported settings helper/controls are removed; Settings has one cycle fieldset.
Rendering no longer duplicates route, qualified-mode or settings permission checks.
Enabled controls can therefore receive an explicit owner refusal; Continuous and
EEPROM opt-ins do not grant permission. Updated docs and callback expectations.
Three existing native-mode tests now also dispatch ON through the Dash callback:
all report qualified_modes refusal without an ON frame or latched fault. A new
settings callback test reports allow_device_settings refusal without device I/O.
Existing exact-target, confirmation/draft reset, pulse availability, unknown-state,
polling-message, active-release and cleanup-error regressions pass.

Command: .venv/Scripts/python.exe -B scripts/verify.py --record-prefix gui-pruning-
Initial sandbox run stopped at uv cache access denied; it did not reach tests.
Rerun with approved cache/temp access: 255 source + 255 installed-wheel tests PASS,
zero failures/errors/skips. Lock, Ruff lint/format, exact Python/CSS wheel parity,
clean install/import, CLI/WebUI help, passive configuration and static notebook
checks PASS. All 36 recorded input hashes match at final audit. Concurrent
REQ-244 changed controller.py independently; the complete verification includes
that combined source, and this task did not edit controller.py. Metrics retain
both its hashes rather than claiming the controller was unchanged.

Evidence: records/gui-pruning-metrics.json, records/gui-pruning-direct-validation.json,
records/gui-pruning-offline-tests.xml and records/gui-pruning-wheel-tests.xml.
REQ-242 COMPLETE, software scope. No live browser/physical test is claimed; no
device I/O, running-server operation, external application edit, commit or push.
Broader project physical/deployment dependencies remain open.


## D078 - Prune repeated controller policy checks and settings poll / REQ-244

8 November 2026: user says "prune" after the three-finding controller review.
Reuse preflight's final fresh OFF reading before a settings write; validate policy
at public operation entry and pass it explicitly to private ON/OFF; remove the
inner preflight recheck and the already-guaranteed supported-mode membership test
in protective OFF. pulse passes the policy already checked by validate_pulse.
Keep private locking/readiness, identity checks, interlock/load limits, post-write
readback, independent cleanup budgets, original/cleanup errors and public API.
REQ-244 / TEST-244 avoids the concurrent GUI task's REQ-242 identifier.

## E224 - Controller duplication pruning validation / TEST-244

8 November 2026; D078 / REQ-244. All 36 E221 verifier hashes matched before this
edit. Expected: one pre-write OFF sample with Manual/interlock qualification,
no settings/output writes when those prerequisites fail, unchanged protective-OFF
mode acceptance, and full source/installed-wheel regression PASS.

Observed: 1117 -> 1112 controller lines. The successful settings/storage regression
now verifies one status-bits query before the settings command and one afterward
(previously two before and one afterward). Three new software cases refuse
active output, non-Manual mode and disabled interlock requirement before any
settings/storage/output command. All public owner method signatures and all
non-owner class ASTs are unchanged. Exact old/new OFF condition comparison agrees
in all 128 combinations of four supported modes, eight valid qualified-mode sets,
electrical ON/OFF and persistent-mode permission. Exact source hashes and parity:
records/controller-prune-logic.json. This is software/static evidence only.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix controller-prune-
Concurrent GUI/CSS/test edits invalidated two otherwise passing runs' input
snapshots; a separate attempt stopped at concurrent GUI formatting. Those attempts
are not accepted campaigns. Applied formatting only to the GUI integration file,
preserving its concurrent semantics. Waited for the GUI code/tests to settle and
reran the complete verifier. Failed-run diagnostics remain under tmp/verification-*.

Final observed: 255 source + 255 isolated installed-wheel tests PASS; zero
failures/errors/skips. Missing/outdated lock rejection, lint/format, exact wheel
Python/CSS parity, clean install/import, CLI/WebUI help, passive config and six
static/passive notebooks PASS. Commands/stdout, source/fixture/wheel hashes and
totals: records/controller-prune-direct-validation.json; JUnit evidence:
records/controller-prune-offline-tests.xml and controller-prune-wheel-tests.xml.
All 36 input hashes match at final audit. Final integration includes the separate
GUI pruning; this task changes no GUI behavior. Preserved unrelated working changes,
records, notebook outputs, manuals, dependencies and public schema. No device I/O,
server operation, external application edit, commit or push. REQ-244 COMPLETE,
software scope; physical/deployment requirements remain separate and unvalidated.


## D080 - Order controller code by responsibility and operation / REQ-246

8 November 2026: user requests "reorganize the controller.py in logical order."
Keep one controller module and order validation utilities, configuration, data
models, APT driver, ownership and the shared owner. Within KSC101 group identity,
mode/interlock, electrical output and cycle settings. Within ShutterHub order
construction/shared guards, connection, status, mode/preflight, settings, output/
pulse, then protection/recovery/shutdown. Keep operation helpers beside their
related public operations. This replaces the earlier public-methods-first layout.
Reorder definitions and navigation comments only; no execution or API change.

## E226 - Logical controller ordering validation / TEST-246

8 November 2026; D080 / REQ-246. Expected: preserved executable content, public
API, dataclass field order, safety boundaries and source/wheel regression PASS.
All 36 E224 verifier input hashes matched before editing. Reorganized 15 top-level
definitions, 16 driver methods and 43 owner methods. Final formatted source AST
matches the baseline after normalizing only definition/method order and the
updated module navigation docstring; signatures, decorators, method/class bodies,
imports, assignments and dataclass field order are preserved. Exact hashes and
comparison scope: records/controller-logical-order-structure.json.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix controller-logical-order-
With existing approved uv-cache access: 255 source + 255 isolated installed-wheel
tests PASS; zero failures/errors/skips. Current/missing/outdated lock checks,
Ruff lint/format, exact source/wheel Python/CSS parity, clean install/import,
CLI/WebUI help, passive config and six static/passive notebooks PASS. No new
tests were needed for the structural move. All 36 verifier input hashes match
at final audit. Commands/stdout, source/fixture/wheel hashes and totals:
records/controller-logical-order-direct-validation.json; JUnit evidence:
records/controller-logical-order-offline-tests.xml and
records/controller-logical-order-wheel-tests.xml.

REQ-246 COMPLETE, software scope. Earlier results remain revision-specific;
E226 revalidates the combined software on these hashes. Unrelated dirty changes,
historical artifacts, dependencies and runtime state preserved. No device I/O,
server operation, external application edit, commit or push. Physical/deployment
acceptance and the version-2 external consumer migration remain separate.

## E225 - APT Issue42.1 coverage and happy-path review / TEST-245

8 November 2026; REQ-245. Inspected the unchanged local Issue42.1 protocol,
9 September 2025, 443 pages, SHA256
b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed.
Read the complete KSC101 applicability table and relevant detailed sections;
rendered/visually reviewed model-table, MMI and cycle pages. Extracted 39 unique
table IDs and compared actual KSC101 Frame/query/scalar calls, typed reply
handling and protocol event handling. Result: 10 transmitted, 5 queried replies,
3 inbound event handlers, 1 framing-only and 20 without a typed implementation.
Status-bit 0x0429/042A is additionally implemented but not in the KSC101 table.

Full ID/name/page/status/limitation mapping, driver AST and source hashes:
records/apt42-command-coverage.json. Grouped matrix: docs/INTERFACE.md. Core mode/
cycle/state operations exist. Interlock SET, channel-enable/query, automatic
updates, hub bay, LED/button and model-ambiguous MMI/trigger/motor families are
absent or partial. EEPROM exposes cycle storage only. HW_DISCONNECT has inbound
handling but is not sent when closing a connection. Generic Frame encoding is
not counted as a typed API, and GET replies are not counted as host commands.

The model table lists 0x0520/0523/0526 for KSC101 while the detail sections exclude
it, describe motor behavior and contain conflicting payload lengths. No guessed
KSC101 implementation is justified. Issue42.1 p186's 10000-second range conflicts
with the KSC101 RevF p31 range 100..10000 ms, which the code follows. Triggered
priming remains the restricted count0/level subset. No interlock bypass or alias
output API was added to improve coverage. Complete table coverage is not proved
necessary for ordinary shutter operation or supported by this inconsistent table.

The happy-path redundancy review began with all 36 E221 input hashes matching
its saved 251-source/251-wheel results. Concurrent controller/GUI pruning then
addressed duplicated preflight OFF/policy checks and unsupported GUI scaffolding.
Later logical controller reordering changed the whole-file hash; command-ID sets
were reconciled again unchanged before this audit was recorded. Remaining
candidates are duplicate identity requests in read-only settings/Identify,
six dynamic callback outputs for permanently Unknown Key/Ready indicators and
repeated cycle-input markup. Preserve write-boundary identity, fresh electrical/
mode/interlock checks, session scopes, claims, ambiguity handling and cleanup.
These are static findings, not implemented optimizations or latency measurements.

No runtime code, device I/O, server operation, external application edit, commit
or push in this audit. No software suite or notebook hardware cell was executed
by it; concurrent tasks own their validation evidence. REQ-245 PASS means the
audit is complete, not that every command is implemented or physically qualified.


## D082 - Document controller APIs and use descriptive state names / REQ-248

8 November 2026: user requests improved human readability and a docstring for
each API function/class. Document all explicit classes/functions, including
private helpers and lifecycle hooks, with concise summaries; expand public API
contracts where inputs, units, returned evidence or hardware effects matter.
Describe exact targets, deadlines, policy, query/write distinctions, independent
optical evidence, passive disconnect and explicit cleanup/recovery. Replace owner
c/d locals and private parameters with channel/deadline; constructor/configuration
collection locals use config. Keep public parameter names, data schema, operation
order and executable behavior. No hardware/server operation or external edit.

## E228 - Controller readability and docstring validation / TEST-248

8 November 2026; D082 / REQ-248. Expected: complete explicit class/function
coverage, accurate API contracts, readable channel/deadline names, unchanged
public signatures and executable behavior, and full source/wheel checks PASS.
All 36 E226 verifier input hashes matched before editing.

Observed: 86/86 explicit class/function/method definitions have nonempty
docstrings, including all public APIs and constructors/lifecycle hooks. Public
function/constructor signatures match the baseline. Final formatted AST matches
after excluding only docstrings and the explicit c/d-to-channel/deadline or
c-to-config local/private parameter substitutions. Field order, guards, command
frames/order, error messages and cleanup behavior remain unchanged. Token-aware
renaming includes names inside f-string expressions without changing literal
messages. Exact hashes, normalization scope and coverage:
records/controller-readability-structure.json.

Command: uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix controller-readability-
With existing approved uv-cache access: 255 source + 255 isolated installed-wheel
tests PASS; zero failures/errors/skips. Current/missing/outdated lock checks,
Ruff lint/format, exact source/wheel Python/CSS parity, clean install/import,
CLI/WebUI help, passive config and six static/passive notebooks PASS. No new
permanent tests were needed for documentation/local-name changes. Commands/stdout,
source/fixture/wheel hashes and totals:
records/controller-readability-direct-validation.json; JUnit evidence:
records/controller-readability-offline-tests.xml and
records/controller-readability-wheel-tests.xml. All 36 verifier input hashes
match at final audit.

REQ-248 COMPLETE, software scope. Documentation deliberately distinguishes
interlock configuration from continuity, host hold from optical exposure,
electrical readback from blade position, passive release from protective OFF,
and protected recovery from ordinary reads. Prior software campaigns are
historical; E228 revalidates this combined source. Unrelated work, historical
records/notebook outputs and dependencies are preserved. No device I/O, server
operation, external application edit, commit or push. Physical/deployment
acceptance and version-2 external schema migration remain open.

## D083 - Implement clear shutter commands without motor-layout guesses / REQ-249

8 November 2026 user requests implementation of missing clearly documented
KSC101 commands, simple/happy-path focused, without ambiguous motor layouts.
Use Issue42.1 headers/scalars/word pairs:0x04C6 require interlock,0x0211/0212
channel state,0x0065/0066 raw bay,0x04B3/B4/B5 LED indication mask,0x0011/0012
updates and0x0002 explicit hardware disconnect. The driver also encodes0x0210;
normal owner ON/OFF remains0x04CB and enable_device remains refused. No parallel
backend, background receiver, new state schema, GUI controls or policy flags.

Interlock API enables the requirement only, with existing settings permission,
source protection, Manual/OFF and confirmed readback. Already-required state is
idempotent. LED settings use documented mask bits1/2/8, RAM readback and the same
entry permissions/Manual/OFF/interlock; they have no output-cleanup obligation.
Shared settings access/confirmation keeps equivalent checks in one place and
retains cycle-settings behavior. Firmware qualification is not expanded.

Update messages are exposed as raw immutable APT frames from the bounded existing
queue. No position/status payload is decoded; callers stop updates explicitly.
Raw bay bytes never change KEH3 mapping. Hardware disconnect requires protected
Manual/OFF and no active request; ordinary release remains passive. New methods
are explicit Python APIs; no implicit initialization/configuration action.

Use0x04B4 from the model table and named command heading, not the inconsistent
0x0411 byte in p93's request diagram. Preserve raw LED-mask readbacks without
converting motor flags into shutter state. Keep button, position, MMI, trigger-
I/O and typed motor-status layouts excluded, plus interlock disabling. EEPROM
stays cycle-only. This implements clear wire operations, not the contradictory
whole model table or a new hardware-commissioning allowance.

## E229 - Documented shutter-command software validation / TEST-249

Issue42.1 reference and original audit are retained; current per-ID command
coverage/source hashes are in records/shutter-commands-coverage.json. Driver
now transmits20 distinct IDs and queries9 replies, including the existing
status-bit extension. Direct literal vectors cover required interlock, channel
ON/OFF alias, LED word payload, update start/stop and bus disconnect. Query
vectors cover channel/LED/bay, fragmentation, wrong channel/enum/reserved byte/
length, and unchanged controller-identity checks. Raw update frames interleave
with fresh queries without guessed content. Command acknowledgements are never
invented; faults/partial writes retain journals and are not replayed.

83 targeted owner/native/new-command cases passed before the final additional
error cases. Final command:
uv run --locked --offline --no-sync --group dev --extra gui python -B
scripts/verify.py --record-prefix shutter-commands-

Observed293 source +293 exact isolated-wheel tests PASS, zero failures/errors/
skips. Lock current/missing/outdated, lint/format, locked build/install, exact
Python/CSS parity, SDK/native-free import, CLI/WebUI help and passive config
PASS. Six notebooks pass static/passive checks; no hardware cells executed.
All37 verifier inputs and current coverage source hashes match after the run.
All107 explicit controller classes/functions/methods have docstrings. Detailed
commands/stdout/source/fixture/wheel hashes: records/shutter-commands-direct-validation.json;
source/wheel JUnit: records/shutter-commands-offline-tests.xml and
records/shutter-commands-wheel-tests.xml. The targeted XML is retained separately.

New regressions confirm permission/protection refusal before I/O, Manual/OFF
preconditions, idempotent interlock enable, exact LED readback, no incidental OFF
from LED-only writes, persistent uncertainty on failed readback/partial writes,
no cleanup bytes after transmit desynchronization, raw-event consumption and
explicit-only hardware disconnect. Existing command/cleanup/status regressions
remain passing. These are byte fixtures and loopback software tests, not bench
proof. No new command was sent to a physical controller.

API/README/current coverage docs explain new commands and exclusions. Corrected
the pre-existing manual-index link to the concurrently removed Issue36 PDF by
linking immutable Git history; its deletion is preserved. Manufacturer PDFs,
historical raw evidence/notebook outputs, live configuration, dependencies and
runtime locks are otherwise unchanged by this implementation. No device/server/
external application operation, commit or push. REQ-249 COMPLETE is software-only;
new commands require separate physical validation before deployment claims.

Final handoff audit: all37 verifier input hashes still match; local links in23
Markdown documents pass. Removed only tmp/shutter-command-tests after checking
workspace containment, no tracked files and no reparse links. No source change
after the passing integrated run.

## D085 - Serialize release guards and drain all pending chunks / REQ-251

8 November 2026. The final combined review retains controller/protocol/transport
as three core modules, per the user's clarification. Publication is authorized;
device I/O, running-owner changes and physical qualification are excluded.

Move the WebUI's Stop-before-Release check into disconnect(require_stopped=True)
under the owner lock. Preserve ordinary passive disconnect/close semantics.
Drain every already-arrived transport chunk before a query, checking the existing
deadline/cancellation between chunks; reject queued replies and incomplete tails.
Do not retry commands or claim transaction-ID freshness unavailable in APT.

## E231 - Final combined review reproductions / TEST-251

8 November 2026. Before interpreting the tests, expected outcomes were: a stale
reply behind a full 4096-byte event chunk is refused before dispatch; continuous
queued events exhaust the original deadline without dispatch; and a Release
waiting for the owner lock refuses an ON started by another callback first.
All three failed on the pre-fix code: two missing protocol exceptions and one
unprotected release (records/final-review-reproductions.xml). These are software
transport/concurrency tests, not hardware measurements.

After the protocol/owner changes, 158 protocol/ownership/documented-command tests
passed (records/final-review-core-tests.xml). GUI integration remains pending:
the separately active GUI command-exposure task is still editing gui.py and its
consumers. REQ-251 uses a separate ID from that task's REQ-250. Final source/wheel
validation and publication must wait for stable inputs and include both changes.

Environment: ordinary uv sync encountered the running shutter-control.exe and
could not replace it; no process was stopped or restarted. Tests use uv run
--no-sync and isolated wheel validation. Sandbox cache/temp ACL failures were
resolved by executing the authorized software-only checks outside the sandbox.
No hardware operations occurred. Final validation/publication evidence follows
in a later record; this entry alone does not establish completion.

## D084 - Expose documented commands through the shared GUI owner / REQ-250

8 November 2026. Keep the main output panel unchanged. Place LED indication
read/apply and enable-only interlock enforcement in Settings; place channel/bay,
device-message requests, raw event collection and protected hardware disconnect
in Diagnostics. Every device action calls the existing ShutterHub API. The GUI
adds no wire layouts, policy duplicate or second ON/OFF enable path.

Scope extra reads and LED drafts to target/connection generation. Label raw bay
bytes, opaque event frames and unacknowledged message/disconnect requests without
inferring optical position, hub routing or native activity. Preserve drafts and
notices during polling; mirror settings outcomes inside the dialog. Ordinary
Release remains passive; the hardware-disconnect request stays explicit.

## E230 - GUI command exposure validation / TEST-250

8 November 2026. Expected outcomes: nine new controls dispatch through shared
owner APIs; owner protections/refusals remain effective; exact target validation
precedes form parsing; drafts/readouts cannot cross connection scope; passive
desktop/phone layouts remain usable without hardware access.

The first targeted run found two error-ordering regressions: missing/unknown
targets on Apply cycle settings reported a numeric field error. The concurrent
review had removed a duplicate target guard; moving form parsing into the single
dispatcher after its target check resolved both without restoring duplication.
Initial evidence: records/gui-commands-targeted-tests.xml (138 passed, 2 failed).
Final targeted run: 140 passed, zero failures/errors/skips, in
records/gui-commands-targeted-final-tests.xml. Tests exercise actual Dash HTTP
callbacks and ShutterHub with software transports, not browser/hardware substitutes.

Final command: uv run --locked --offline --no-sync --group dev --extra gui
python -B scripts/verify.py --record-prefix gui-commands-
Result: 337 source and337 isolated installed-wheel tests PASS, zero failures,
errors or skips. Lock, lint/format, exact Python/CSS wheel parity, clean locked
installation, SDK/native-free import/help, passive configuration and six static
notebooks PASS. No hardware notebook cells were executed. All recorded input
hashes matched at the final audit. Evidence:
records/gui-commands-direct-validation.json, gui-commands-offline-tests.xml and
gui-commands-wheel-tests.xml. The run includes REQ-251's protocol/release fixes.

A separate production-backend preview used localhost9872 and the tracked Ethernet
config, without selecting Connect or any device action. Settings/Diagnostics
were inspected at1280x720 and390x844, including scrolling and disabled controls.
No horizontal overflow or browser warnings/errors were observed. Screenshots:
records/gui-commands-{settings,diagnostics}-{desktop,phone}.jpg. The tab was closed,
viewport override reset and only this preview stopped; port9872 had no listener
afterward. Existing servers were untouched. No physical controller was contacted.

records/gui-commands-coverage.json maps controls to shared APIs, captures callback/
layout scope, screenshot hashes, current input agreement and local Markdown link
checks. README, GUI guide, STATE and REPORT describe the result. No GUI source
work remains pending for REQ-251's separately authorized combined publication.
This chat made no commit/push. New hardware commands and physical/deployment
acceptance remain untested; prior live evidence applies only to its recorded setup.

## E232 - Final integrated review validation / TEST-251

8 November 2026; D085/E231 and the stable D084/E230 GUI handoff. Expected: all
software tests run without failures/skips, exact source/wheel runtime parity,
locked dependencies, passive startup/configuration, preserved interlocks/load
permissions/ownership/cleanup and current documentation/artifact integrity.

Final command: uv run --no-sync --locked --offline --group dev --extra gui
python -B scripts/verify.py --record-prefix final-review-. Result: 337 source +
337 isolated installed-wheel tests PASS; zero failures/errors/skips. Lock checks,
Ruff lint/format, exact Python/CSS wheel parity, clean locked installation,
isolated imports/help without SDK/native extras, passive configuration and all
six static notebook checks PASS. All 38 recorded verifier input hashes match.
No controller or laboratory network was contacted; TCP tests use loopback.

The first combined run found two error-priority regressions: invalid/missing
target plus invalid cycle inputs reported a field error before target selection.
records/final-review-integration-first-tests.xml retains 335 PASS / 2 FAIL.
GUI parsing now follows its single canonical exact-target check in execute_action;
the final suite covers every control's invalid-target refusal. No extra callback
target guard is required. The three new E231 protection regressions also PASS
(records/final-review-regressions.xml). Cycle-duty/count checks share one repeated
operation branch, with existing load-boundary tests retained and passing.

The separate GUI work completed its stable handoff without pending source edits;
its preview was stopped. The final review inspected all four saved desktop/phone
Settings/Diagnostics screenshots. No connected GUI or optical behavior is inferred.
The user also explicitly authorized a coordination message to that chat; it was
asked to leave the publication inputs stable. No messages were sent to others.

records/final-review-audit.json: 21 Markdown files / 111 local links PASS;
four current PDFs plus historical Issue 36 in Git 5d2adc1 match registered hashes;
all six notebooks retain their saved outputs and execution counts; 107/107 explicit
controller declarations have docstrings. The tracked live policy remains
Manual-only output, 2 s OFF rest, protected persistent mode selection and no
device-settings/EEPROM/continuous-cycle permissions. No qualification was expanded.

STATE.md and outputs/REPORT.md now describe the current system concisely instead
of repeating historical campaign summaries. Full decisions, observations, raw
evidence and prior campaign JSON/XML remain in records; superseded review files
and Issue 36 remain in Git history. Manufacturer-count and external DiamondGUI
wording now distinguish current local copies from historical checks. External
deployment, native modes/settings and physical/calibration/reboot/endurance
acceptance remain open. Ordinary active-app sync was not retried; the existing
shutter-control.exe and server were left running their earlier code. The final
wheel is a software-validated deployment artifact, not a running-app upgrade.

Software/doc review PASS. Publication is the remaining authorized action; record
its observed commit/remote result separately. Evidence:
records/final-review-{direct-validation,audit}.json and source/wheel XMLs.

## D086 - Preserve verification evidence bytes in Git / REQ-251

8 November 2026. Before staging, a raw-versus-filtered Git blob comparison for
records/gui-commands-direct-validation.json differed: raw 6cdb1e3da21ed3ed8ceda7f0c6d467fd2aa98546
versus text-filtered 541498da38cbf1c9de184fbb3ffe85a0797a3a3a. The current
automatic LF conversion would change CRLF records and invalidate referenced
artifact hashes. The final verifier's 38 inputs already contain no CRLF.

Disable text conversion for records/*.json and records/*.xml in .gitattributes;
preserve raw historical campaign data instead of rewriting its hashes. Confirmed
raw/filtered blob equality after this change. Normalize only the current Markdown
checkpoint/report/log to LF; do not rewrite the JSON/XML evidence. Staged byte
parity is checked before publication. No runtime behavior or hardware policy changes.

## E234 - Final revalidation including visible fault lockout / TEST-251

8 November 2026. A concurrent new REQ-252 live-read campaign exposed a misleading
generic success notice over a persistent owner fault. Its independently prepared
four-case software regression and small gui.py change were reviewed and included:
Connect, Read, Poll and Release must retain the fault in both notices; journals
and output lockout remain unchanged. Healthy polling still preserves messages.
The software cases reproduce and validate the UI behavior without device I/O.

The final verification command is the same as E232. Result: 341 source + 341
isolated installed-wheel tests PASS; zero failures/errors/skips. Lock, lint/format,
Python/CSS wheel parity, clean locked installation/import/help, passive config and
six static notebooks PASS. All 39 verifier inputs match, including the new test
file. records/final-review-{direct-validation,audit}.json and source/wheel XMLs
now describe this final revision; E232 is the earlier 337-case snapshot, and E230's
separate 337-case campaign remains preserved under gui-commands-*.

The document/artifact audit again passes 21 Markdown documents / 111 local links,
five registered manual hashes (four local, Issue 36 in Git), six preserved saved
notebook output/count sets and 107/107 controller docstrings. D086 preserves JSON/
XML evidence bytes in Git. README/API/GUI/architecture and the compact checkpoint/
report describe the final software and the unchanged physical boundaries.

Publication excludes the concurrent, incomplete REQ-252 hardware-run artifacts
and its new PROJECT/STATE sections. Explicit index snapshots publish only the
reviewed REQ-251 document sections; complete working files and new live-run data
are preserved for that task. The coordinator was informed with the user's explicit
messaging authorization. No device/server action was performed by this review;
the separate campaign has its own authority, observations and unfinished work.

REQ-251 software/doc scope PASS. Publication evidence will identify the observed
source commit and remote equality separately; physical acceptance remains open.

## E235 - Observed review publication / TEST-251

8 November 2026. Reviewed implementation/docs/evidence committed as
2bc53e28f93bcacd0dce0401b67a9f3cb8e97d90 and pushed normally to origin/main.
git ls-remote origin refs/heads/main returned the identical full hash.
All 136 staged paths matched the reviewed bytes and all 39 verifier inputs
matched the index before commit; scoped whitespace checks PASS.

records/final-review-publication.json records the observed result. The follow-up
checkpoint/report now marks REQ-251 COMPLETE in software/publication scope; full
physical/deployment acceptance remains BLOCKED. Concurrent REQ-252 live records
and PROJECT/STATE sections remain uncommitted and unchanged by this publication.
The final documentation checkpoint is committed/pushed separately, then remote
HEAD equality is checked again. No hardware operation was performed here.
