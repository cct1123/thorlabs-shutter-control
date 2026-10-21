# Communication, latency and simplicity review

REQ-103; 2026-10-21; inspected revision `3835d2c`. Review only: no production
source, dependencies, configuration, tests or hardware changed.

This is the pre-implementation assessment. REQ-104 implements the readability
work with unchanged behavior; see [delivery report](REPORT.md). Proposed latency
optimizations and changes to element IDs remain outside that refactor.

## Conclusion

The runtime is already small: 38 tracked files and 1,952 physical Python source
lines. controller.py (1,085) and gui.py (780) account for 95.5% of those lines.
The main opportunity is reducing serialized waiting and duplicated orchestration.
Deleting lifecycle checks or replacing Dash would have a poor benefit/risk ratio.

## Beginner development handoff: governing criterion

User refinement: reduce scaffolding and examine human readability, docstrings and
comments. The essential criterion is whether beginner developers can understand
the system and take over development. This takes priority over the earlier line
reduction estimate. A change that adds a few clear lines can be an improvement.

**Static assessment: partly accessible, but not yet a self-contained beginner
handoff.** Public command names, explicit configuration, the small launcher,
hardware boundaries and normal core tests are approachable. GUI changes and LAN
discovery require substantially more implicit knowledge. No actual beginner
walkthrough has been performed, so beginner independence is not demonstrated.

### Scaffolding to simplify first

| Location | Beginner obstacle | Recommended direction |
| --- | --- | --- |
| gui.py:391 and :703 | 48 outputs per panel are declared in one list and populated positionally elsewhere; one field addition requires matching order | Named output groups with a local mapping from field to value; keep the framework wiring visible |
| gui.py:479 | The 300-line callback combines actions, prerequisite reads, exceptions, refresh policy, messages and rendering | Keep one visible callback coordinator; extract a few ordinary functions for action handling and panel presentation |
| gui.py:306 | One panel uses different ID spelling from multiple panels | One consistent ID convention, with the affected HTTP tests updated |
| controller.py:648 and :957 | LAN Connect travels hub -> channel -> hub -> channel filtering | Give selected-endpoint discovery one clear implementation and keep passive discovery separate from Connect |
| controller.py:976 | String dispatch also selects which methods require a route check | Name the route-check policy and explain it beside dispatch; retain explicit public methods and their signatures |
| tests/test_application.py:10 | The HTTP helper assumes the first callback and infers TTL values through nested ternaries | Explicit state defaults, plain conditionals and a short explanation of the Dash request shape |

The three controller classes already share their lifecycle implementation. The
17-line `_HubChannel` adapter is not itself a large reduction target. A generic
plugin/transport framework, generated public methods, pervasive `getattr`, or many
tiny helper modules would make the learning path harder. Small common helpers
such as `_command` and `_get_value` earn their place by keeping fault handling and
feedback waits consistent; explain them rather than copying them into every method.

### Docstrings and comments

Useful existing explanations should stay: setters issue commands without proving
motion; cached observations cannot authorize output; a clear interlock bit is
unknown; headless USB may report Connecting; discovery builds once before polling;
Close must target the retained handle after a fault. These comments preserve
physical facts and the reasons behind surprising code.

The main documentation gaps are specific contracts and state vocabulary:

- **ShutterStatus (`controller.py:71`):** explain that `has_device` means an SDK
  handle is still retained, including after a failed disconnect. It does not mean
  communication is healthy. Define slot, endpoint, polling and retained handle.
- **Snapshot getters (`controller.py:430`):** say explicitly that read exceptions
  become a fault snapshot, while narrow getters such as `get_trigger_config()`
  raise `ShutterError`. Explain what callers must inspect. Avoid an unqualified
  promise of "fresh" feedback when the mechanism is request, fixed wait and SDK
  cached getters.
- **`_command` (`controller.py:517`):** explain the context manager's three jobs:
  reject unavailable/faulted operations, clear display observations before writes,
  and record failures. Explain why `reading` and `allow_fault` exist. Its current
  single-sentence docstring does not teach these rules.
- **Cleanup (`controller.py:536,557,1056`):** explain why `BaseException` is caught
  here: continue the remaining release/slot attempts, then propagate interrupts.
  Explain that a failed native disconnect retains ownership to prevent another
  handle from opening. Do not turn this into a general exception-handling pattern.
- **GUI callback (`gui.py:479`):** document action -> prerequisite -> command ->
  selected-panel feedback -> presentation, plus the periodic refresh path. Explain
  that Dash `no_update` preserves a browser property; `None` is an actual value.
- **GUI naming (`gui.py:650`):** rename local `active` to `has_handle`; its current
  value is `status.has_device`, whereas physical Active/Inactive already means
  something different elsewhere in this module.
- **Test fixture (`tests/conftest.py:141`):** describe the fictional USB/LAN devices,
  virtual clock and monkeypatched SDK boundary. Expand `NS` where it improves
  understanding. Vendor-style method names in the fake intentionally match .NET.

Use short behavior-focused docstrings for public methods and non-obvious internal
helpers. Explain inputs/units, side effects, returned failures and ownership only
where relevant. Hub methods can refer to the shared device contract rather than
copying the same paragraphs into every wrapper. Add comments for reasons and
constraints; avoid narrating obvious assignments or installing a docstring linter
merely to fill every function. Dense conditional expressions are better rewritten
as clear statements than supplemented with a paragraph explaining them.

### Handoff documentation and acceptance

The current architecture/API/operator guides describe the system but do not show
a newcomer how to change it. Add a short developer walkthrough to the existing
architecture guide, linked from README's development section, rather than another
parallel document. Include file responsibilities, a reading order, one GUI Open
trace, one LAN Connect trace, error/ownership rules and how the fake SDK is installed.
Explain unfamiliar terms on first use: SDK, Python.NET, device handle, FTDI USB
provider, TCPIP provider and TTL. Keep historical E/TEST identifiers in evidence
records; beginners should not need to read the project history to locate an edit.

Proposed handoff acceptance is a practical exercise with a developer who knows
basic Python but is new to this repository. Without coaching or hardware access,
they should be able to:

1. Set up the project and run the software-only tests using the written commands.
2. Trace GUI Open to the exact SDK setter and distinguish it from feedback reads.
3. Add a readout for existing `status_bits`, identify every required edit, and
   verify it for one and multiple panels using fictional devices.
4. Change one discovery setting and explain its latency effect and whether startup
   remains passive, without executing a live scan.
5. Explain why failed disconnect retains a handle, why Close remains permitted
   after faults, and where faults appear as values versus exceptions.

Record where they need assistance and revise those sections. No arbitrary line
count, docstring count or function-length threshold substitutes for this exercise.
The exercise is proposed and unexecuted; the review does not certify novice readiness.

E143 / TEST-153: source/doc/test walkthrough and passive callback-schema inspection.
Observed 51 outputs for one panel and 147 for three: three shared plus 48 per panel.
App construction retained no SDK or device handles. Production source, comments,
docstrings, tests and configuration remain unchanged; recommendations are review only.

## Findings, in priority order

1. **Status work blocks commands across all panels.** The launcher serves one HTTP
   request at a time (`__main__.py:33`); the entire GUI callback also holds the hub
   lock (`gui.py:481`). Refresh reads connected channels sequentially
   (`gui.py:630`). Each operating read explicitly waits one polling interval
   (`controller.py:317`), normally 250 ms. A three-panel refresh adds 750 ms and a
   six-panel refresh adds 1.5 s before native overhead. A queued Close cannot
   bypass the current request. Native calls can block indefinitely from Python's
   perspective; there is no demonstrated maximum command response time. Merely
   enabling HTTP threads would leave the hub-lock bottleneck intact.

   First bound and coalesce background refresh work, avoiding repeated stale
   refresh requests. If prompt Stop service is required, introduce one explicit
   device-work owner with command priority and display snapshots. Keep ownership
   and command ordering intact. A worker alone cannot interrupt a blocked native
   call; process isolation is a separate, larger fault-containment choice.

2. **Connecting a present LAN cube waits for unrelated absent routes.**
   `_HubChannel.discover()` calls `_discover_slot()`, which invokes whole-hub
   discovery (`controller.py:648,957`). Its completion condition waits for every
   configured LAN slot (`controller.py:901`). With one present route and a second
   absent route, the present cube connected only after the default five-second
   identity deadline in the fake experiment. Scope connection discovery to the
   selected endpoint. Preserve whole-hub discovery for the explicit Discover API,
   exact route/identity verification and exclusive serial ownership.

3. **Unified discovery repeats work and delays all results behind the scan.**
   `discover_available()` performs USB discovery, optional configured-route
   discovery, then broad scanning (`controller.py:913`). These rebuild the SDK
   list two times without configured routes, or three times with them. Whenever
   a scan finds a host, identity collection runs the full default five seconds
   (`controller.py:841`), even when identities appear immediately. The GUI returns
   USB results only when the complete operation finishes. Missing configured
   routes can add another five seconds. Native range-scan duration is additional
   and unmeasured. The default range contains 256 addresses at 100 ms/address;
   25.6 s is only a serial timeout-budget calculation, not an observed duration or
   SDK runtime bound.

   Narrowing the existing configured range to the actual hub address is the
   simplest operational improvement. In code, share discovery snapshots and
   separate result presentation from scan completion. Preserve partial warnings
   and the released-handle restriction. Do not end broad discovery at the first
   identity: that would miss late devices or occupied bays. A configurable scan
   policy would be a behavior decision, not a transparent optimization.

4. **Some GUI reads pay two waits for feedback the driver already batches.**
   Connect reads TTL, then operating feedback (`gui.py:548,630`): 500 ms of waits.
   A single `get_status()` already requests both and samples after one 250 ms wait.
   Apply TTL currently pays prerequisite + TTL readback + result waits: 750 ms.
   Combining the final readback/result with `get_status()` would reduce that to
   500 ms, retaining the prerequisite and comparison. These are source-derived
   improvement estimates; no implementation has been changed or benchmarked.
   Trigger Start also has two prerequisite waits, but optimizing it must retain
   actual input-settings feedback without adding unnecessary TTL traffic to
   Manual Open. Do not shorten all sleeps blindly: request-plus-sleep is not
   acknowledged response freshness, and optical timing remains unmeasured.

5. **GUI bookkeeping is the clearest maintenance-reduction target.**
   `create_app()` spans 484 lines, including a 300-line callback. The output field
   schema (`gui.py:391`) and positional result assembly (`gui.py:703`) must be
   edited in matching order. One-panel versus multi-panel ID conventions add
   another branch. Use named output groups, small action/render helpers and one
   panel-ID convention. Share transport enumeration/filtering between discovery
   paths. Retain the documented public USB/hub boundaries. Avoid dynamic public
   method generation just to remove approximately 54 lines of explicit hub
   wrappers: that would obscure typing, signatures and route policy.

## Measured software waits

The existing fake SDK and actual Dash Flask callback HTTP were used, with a
virtual clock. These numbers count programmed sleeps only; they exclude native
calls, HTTP queue time, browser rendering, transport and mechanical motion.

| Operation | Programmed wait |
| --- | ---: |
| Connect, one panel | 500 ms |
| Manual Open | 500 ms; 250 ms before the output command |
| Close / Stop | 250 ms after the output command; queue delay is additional |
| Mode change | 500 ms |
| Trigger Start | 750 ms; 500 ms before the output command |
| Apply TTL | 750 ms |
| Arm TTL | 500 ms |
| Disarm TTL | 250 ms |
| Read TTL | 500 ms |
| Refresh 1 / 3 / 6 connected panels | 250 / 750 / 1,500 ms |
| LAN Connect, all configured identities immediately present | 0 ms of sleeps |
| Same Connect with another configured LAN route absent | 5,000 ms |
| Unified discovery, host and identity immediately present | 5,000 ms plus native scan work |

Operating refresh issues three explicit request calls per connected panel, in
addition to SDK polling. Fake HTTP responses for 1/3/6-panel refresh were
2,219/6,653/13,226 bytes. Payload size is small compared with the programmed waits;
network bandwidth optimization is a low priority on localhost.

## Reduction judgment and next steps

A reasonable planning range is **150-300 fewer production Python lines**
(approximately 8-15%), mainly in GUI output/render bookkeeping and shared discovery
logic. This is an estimate, not a demonstrated patch. Removing half the code is
unsupported while retaining current USB/LAN, four-mode, TTL and cleanup contracts.
The two declared runtime dependencies are already focused. No evidence supports
rewriting the UI stack for speed. The unused `.preview-banner` CSS rule is a minor
cleanup; it has no meaningful latency benefit. Tests were just reduced to 405
lines; further blanket test deletion is not an efficiency improvement.

With beginner handoff as the governing criterion, first write the developer
walkthrough and clarify state/error contracts; replace positional GUI output
bookkeeping; simplify the callback and discovery call paths. Batch Connect/Apply
feedback within those focused changes where useful. Defer worker scheduling
until measured responsiveness needs justify the additional concepts. Keep changes
separate and validate the affected normal workflow plus its operational failure
case. Add only focused latency assertions for a changed contract, rather than
restoring a large suite.

Before promising a timing target, measure click-to-command, native setter duration,
request-to-feedback age and independent optical response separately on the intended
USB/LAN topology. Report median, tail and maximum observed values with configuration
and sample count. No existing evidence establishes calibrated optical latency.

## Evidence and reproduction

E142 / TEST-152. Current suite command:
`.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short`:
**15 passed in 0.17 s**. No real SDK, socket, discovery or output operation.

The timing probe loaded `tests/conftest.py` with `runpy.run_path`, entered
`pytest.MonkeyPatch.context()`, and called `bench.__wrapped__(monkeypatch)` to install
the existing fake SDK and virtual clock. Single-panel callback requests used the
same request structure as `tests/test_application.py:click`. Elapsed programmed
time was `controller.time.monotonic()` after minus before each callback. The
sequence was Connect, Open, Close, Trigger mode, Start, Stop, Manual mode, Apply,
Arm, Disarm, Read TTL and Refresh. Each transition used the fake's normal state.

For scaling, independently constructed 1/3/6 fictional USB devices, registered them
in the fake manager, connected all slots, then posted Refresh with matching panel
IDs. For discovery, used the fixture's immediately visible LAN identity; compared
one configured endpoint with the same endpoint plus an absent second bay. Fresh
fixtures isolated the four cases: Connect/all present, Connect/other bay absent,
unified/no configured routes, unified/one configured route. Build counts were
1/1/2/3 respectively; waits were 0/5/5/5 s. Observed scope is control flow and
programmed waiting, not vendor scheduling or physical performance.
