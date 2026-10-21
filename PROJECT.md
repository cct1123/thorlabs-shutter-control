# Project intent

## Review, prune and staged publication (REQ-100, derived)

User: "review all changes. fix inconsistency. prune before commit. commit stage
by stage. push". Review the complete pending diff, correct supported defects and
documentation drift, preserve private inputs/results and durable evidence, prune
verified disposable artifacts, validate source and package, commit in focused
stages and push to configured origin/main. Preserve passive startup, explicit
output actions and ownership/cleanup. No physical operation is needed. This
request authorizes publication of the accumulated REQ-090..099 work; their earlier
no-publication statements describe the scope of those historical requests.

## Unified USB/Ethernet discovery (REQ-099, derived)

User requests removing each shutter's connection/endpoint/apply controls and the
global Find devices on the LAN block. Discover should find USB and Ethernet
automatically using config.py LAN settings. Show detected routes with serials;
Connect applies the selected detected route without manual transport selection.
Preserve passive startup/discovery, explicit Connect/output commands, ownership,
retained-handle cleanup and partial-discovery diagnostics. Broad LAN scanning
still requires released process handles. Validate software and browser simulation;
no real hardware operation, commit or push is requested.

## Repository consistency and pruning (REQ-098, derived)

User: "update repo. fix consistency. prune". Reconcile current code/config/API,
operating guides and validation claims; remove redundant current-state/report
history and verified disposable generated artifacts. Preserve human criteria,
durable records, useful regression tests, notebooks with local inputs/results,
private files and the environment. Validate the integrated source and package in
software. No hardware operation or new remote publication is requested.

## LAN discovery defaults in config.py (REQ-097, derived)

User asks to use the LAN discovery parameters in config.py. Centralize default
start/end IPv4 addresses, per-address open timeout and scan-size limit there.
GUI initial values and omitted Python API arguments must use these settings;
explicit GUI/API ranges remain available. Preserve the 256-address maximum and
existing validation/ownership/passive behavior. Validate in software only.

## Discover LAN devices without an exact IP (REQ-096, derived)

User requests LAN discovery without knowing the device IP, default range
192.168.1.0 through 192.168.1.255. Provide on-demand vendor SDK scanning, a bounded
editable range and selectable KSC101 results with serial/endpoint. Selecting a
result fills the released panel's LAN route; connection stays explicit. Preserve
USB, exact-route validation, retained-handle protection and passive startup.
Validate protocol/GUI behavior in software; no shutter actuation is authorized.

## Choose USB or Ethernet in the GUI (REQ-095, derived)

User: "users should be able to choose in the gui ethernet or usb". Provide a
per-panel transport selector and LAN endpoint field, with an explicit passive
Apply action. No configuration-file edit or server restart is needed to change
a released panel's route. Preserve identity validation, USB/mixed operation and
cleanup; refuse route changes while a device handle is retained, including after
a failed release. Validate with software devices and a browser simulation, without
operating real hardware. Preserve the user's notebook settings/results.

## GUI Ethernet LAN support and notebook result (REQ-094, derived)

User reports the LAN notebook ran successfully and asks to update the repository
and GUI for Ethernet LAN communication. Record that success as human-reported
procedure evidence; do not infer calibrated timing, independent optical sensing
or an automated GUI bench test. Add per-panel Ethernet route configuration to the
normal launcher, show each panel's route, filter discovery options to that route,
retain USB/mixed support, passive startup, identity/ownership and cleanup. Validate
with software devices; preserve local notebook inputs/results. No real GUI
actuation/restart or new commit/push requested.

## Match working Kinesis Ethernet connection (REQ-093, derived)

User confirms Kinesis successfully connects to KSC101 and KEH3 over Ethernet and
requests ShutterHub use that same connection. Resolve SDK discovery using the
configured cube endpoint and real identity, preserve passive startup/no USB
fallback, test asynchronous/error/timeout behavior, and verify real discovery,
connection, identity and communication-only release. Do not actuate outputs,
change mode/enable/TTL, firmware, wiring or network configuration. Preserve local
notebook settings/results; no commit/push requested.

## Correct Ethernet implementation from vendor examples (REQ-092, derived)

User reports devices rebooted and Kinesis lists both KEH3 and KSC101, supplies
its Connect screenshot, and requests studying the official Python examples at
https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python and correcting
Ethernet communication. Follow the actual vendor TCPIP discovery contract, keep
no USB cable dependency, verify identity/route and use passive hardware checks
only. Preserve notebook settings/results. Physical Open/Close is not authorized
by this diagnostic request.

## Diagnose empty LAN cube discovery (REQ-091, derived)

User reports the LAN notebook returning an empty KSC101 list at the configured
left-bay endpoint. Diagnose using passive identity/discovery only; distinguish
network reachability, hub response, cube response and software filtering. Do not
infer actuation authority or change wiring, firmware or network settings.

## LAN-only ShutterHub discovery (REQ-090, derived)

User: fix ShutterHub discovery via LAN; no USB is needed. Require no USB-connected
device; retain vendor SDK list building for TCPIP. Avoid implicit USB slots; preserve
explicit USB/mixed operation and identity/endpoint checks. Validate software-only;
no output actuation, network configuration or firmware change is requested.

## Prune, commit and push (REQ-089, derived)

User authorizes pruning redundant deliverables, reviewing the integrated pending
changes, committing them and pushing to the configured origin/main. Preserve
private inputs, environment, bench evidence and useful regression coverage.
Validate the final software revision; no incidental hardware actions.

## Documentation and screenshot review (REQ-088, derived)

User requests all documentation/READMEs and screenshots updated with a comprehensive
consistency review. Match current source behavior, distinguish historical bench
evidence from current software validation, refresh current GUI captures using
software devices only, verify links/snippets and run regressions. Preserve private
artifacts and concurrent work; no real device operation or live GUI restart.

## Modern compact GUI styling (REQ-087, derived)

User clarifies: retain the Kinesis control layout and four modes, but do not copy
its aesthetics. Replace red frames, silver gradients and glossy round buttons
with neutral surfaces, compact flat controls and clear status indicators. Preserve
all existing mode/state behavior and shutdown. This supersedes the visual style
of REQ-085 only. Validate browser desktop/narrow layouts without real hardware.

## Ethernet tutorial notebook (REQ-086, derived)

User requests a tutorial notebook using Ethernet/LAN through ShutterHub to control
the shutter cube. Provide explicit KEH3 endpoint/serial settings, passive discovery
and identity checks, deliberate Manual setup, one Open/hold/Close cycle, cleanup
and troubleshooting. Validate with software TCPIP devices; no incidental real
actuation or claim of physical Ethernet qualification. Preserve existing GUI work.

## Kinesis-style GUI (REQ-085, derived)

User requests a Kinesis-like design and supplies Manual, Single, Auto and Trigger
mode screenshots. Implement red instrument title bars, compact silver panels, a
2x2 mode selector, round Open/Close or Start/Stop controls and truthful status lamps.
Use existing mode/state APIs; keep independent serial panels, TTL drafts/readback,
passive startup, cleanup and launcher shutdown. No software interlock gate, fake
timing values, implied blade sensing or physical actuation during validation.
Validate all mode transitions with software devices and inspect browser layouts.

## Launcher shutdown button (REQ-084, derived)

User requests a button to shut down the Dash GUI server and device when the GUI
is run as main. The owning launcher exposes the button; it attempts Close/release
for every device, returns feedback and exits its local server normally. Keep the
server available on cleanup failure. Embedded create_app instances retain host
server ownership unless explicitly supplied a shutdown callback. Validate with
software devices and an unconnected localhost HTTP server; no real actuation.

## Follow-up integrated review (REQ-083, derived)

User repeats: review all changes, fix issues, ensure consistency, prune, commit
and push. Review the published REQ-082 contract, fix supported regressions, retain
state-only Open/Close and no software interlock gates, validate the final software
and publish normally to origin/main. This is software-only; no device operation.

## Active delivery: review, simplify and publish

User requests reviewing all accumulated changes, fixing issues, ensuring
consistency, pruning, committing and pushing. REQ-082 (derived): reviewed source,
examples, package, documentation and evidence agree; representative software
checks pass; generated clutter and real device identifiers are excluded from
publication; commit and push the reviewed changes to origin/main.

User confirmed state-only Open/Close: send Active/Inactive only and preserve mode
and enable state. EnableDevice is explicit setup, not repeated in Open/Close;
Disarm retains explicit Inactive/Manual preparation. Examine necessity against the
KSC101-specific vendor example and installed header without actuating hardware.

Latest steering extends REQ-081 to every project operation: no software
interlock gate in drivers, GUI, tutorials, notebook or diagnostic helpers. Users
manage the physical circuit. Retain informational readings and independent
identity/connection, key, operating-state and TTL configuration checks. No
hardware actuation, wiring change or device test is authorized by this review.

Earlier request sections below are historical intent; this scope supersedes
conflicting software interlock gating and prior no-commit/no-push constraints.

## Current request: users manage the physical interlock externally

User explicitly selected "Users manage it externally; remove software interlock
gating" after clarifying responsibility for the interlock. REQ-081 (derived): GUI
Open/Arm must not gate on interlock feedback or operator confirmation; retain the
readout, connection/identity, key, operating feedback and TTL prerequisites.
No per-session GUI confirmation control. Users set and verify the physical
interlock externally; no physical interlock command, wiring or firmware change.
This supersedes earlier GUI interlock-readiness gating criteria, including
REQ-079/080 notes. Optional Python status/confirmation APIs remain available.

## Current request: remove config interlock confirmation

User: "remove VERIFIED_INTERLOCK_SERIALS in config.py". REQ-080 (derived):
remove the setting, launcher consumption and active usage instructions; preserve
explicit Python API confirmation and existing GUI readiness checks. No hardware
operation or GUI restart requested.

## Current request: align the GUI with controller.py

User: "fix gui", clarified connection failure, then "update gui according to the
source codes controller.py". Update the GUI against the current direct setters,
explicit getters and hub dispatch contract. Preserve passive connection and
physical readiness safeguards. REQ-079 (derived): connection/retry sends no output
commands; button readiness matches callback checks; unknown operating feedback
does not invalidate a successful identity connection; transport labels reflect
configured hubs. Validate software and distinguish it from the old live server.

## Current request: remove generated clutter and substantially simplify tests

User explicitly requests removal of temporary/cache artifacts and substantial
test reduction/simplification. Remove only inventoried generated project files;
preserve .venv, Git, private inputs, bench records, notebooks, data and installed
SDK/runtime. Consolidate overlapping tests and replace exhaustive/history-specific
matrices with representative contracts and workflows. Preserve meaningful get/set,
identity/ownership, USB/Ethernet routing, error/interrupt/cleanup, GUI and tutorial
coverage. No runtime feature change, hardware operation, commit or push requested.

Derived REQ-078: materially fewer test files/lines/cases with an explicit retained
coverage map; reduced suite and lint pass; disposable cache/temp inventory removed
and rechecked without recreating caches; retained environment/evidence verified.

## Current request: USB-only cube and hub-owned Ethernet

User explicitly requests removing all Ethernet modality from KCubeShutter and
implementing Ethernet connection/command handling in ShutterHub. Preserve the
direct-set/explicit-get contract. Use existing Kinesis TCPIP support with explicit
per-slot endpoints rather than inventing a protocol or KEH6 network map. USB
remains the default. Mixed slots may be explicitly configured; network slots must
not fall back to USB. Keep shared identity ownership, passive construction,
diagnostic errors and all-slot cleanup. No hardware operation requested.

Derived REQ-077: KCubeShutter has no network parameter/property/branch and filters
USB devices only; ShutterHub owns immutable endpoint selection, discovery,
connection and slot command dispatch; get/set code is shared without duplicating
drivers; setters perform no operating feedback reads/waits; affected regression,
mixed-route, wrong-bay, fault/cleanup and GUI tests pass. Physical Ethernet remains
separate qualification.

Latest placement correction: keep RUN_REPEAT, REPEAT_COUNT,
REPEAT_HOLD_SECONDS and their validation in the optional repetition section,
so single-cycle setup has no repetition dependency (REQ-076).

## Latest steering: split the tutorial operation block into cells

User explicitly requests breaking the large validation/connection/Open/Close/
repeat/cleanup block into multiple sections. REQ-076 now requires independently
runnable sequential cells with explanations. This supersedes the prior single
complete-cycle cell layout. Preserve explicit readiness, error cleanup, disabled
repetition, and honest documentation of the open interval between cells.

## Current request: organize and rename the Open/Close notebook

User requests running/modifying the open_close notebook, organizing sections as a
tutorial, and renaming the file. Derived REQ-076: numbered instructional sections,
a descriptive filename with current links/tests, runnable complete-cycle cleanup,
and software execution checks. Retain the user-added repeat experiment as an
explicit opt-in exercise. This revision uses simulated execution; no new physical
repetition qualification or current bench state is inferred.

## Current request: prune KCubeShutter into direct writes and explicit reads

User explicitly requests substantial pruning: setters simply send commands,
without status requests, prerequisite reads or returned status; getters request
specific feedback. This supersedes prior implicit driver readiness checks,
Close preparation, acknowledgment loops, startup-feedback retries and automatic
recovery workflows. Preserve passive startup, string/int serial identity, local
ownership, argument validation, useful error reporting and all-slot release.
Setters return None; explicit getter calls replace result-consuming callers.
GUI/lessons own their readiness checks and explicit feedback reads; physical
interlocks are never bypassed. No hardware operation or publication requested.

Derived REQ-075: no feedback requests/getters/sleeps inside any setter; individual
getters request only their selected feedback; Connect verifies identity without
operating-status dependency; callers/tests/docs reflect the contract; software
regressions pass. Changed physical control paths require separate revalidation.

## Current request: undefined operating feedback during Connect

User reports Connect failing with operating state '0' and mode 'manual'.
Investigate against the installed vendor contract; handle delayed startup
feedback without inventing a safe state or sending output commands. Derived
REQ-074: bounded passive startup retries, persistent undefined feedback fails
and releases, operational safeguards remain strict, software regressions pass.
Physical resolution requires a subsequent observation on the affected device.

## Current request: accept string and integer serials

User explicitly requests accepting both str and int serial numbers. Normalize
valid eight-digit KSC101 identities to strings internally across selection,
connection, hub settings and session confirmation. Preserve identity, ownership
and confirmation scope. Reject floats, booleans and malformed identities.
This supersedes the earlier string-only input criterion below. REQ-073 (derived):
equivalent representations behave identically; regression tests pass; no hardware
operation is needed.

## Historical request: notebook serial type error

User reports a ValueError constructing KCubeShutter from the notebook serial.
Correct the project serial setting's type, explain quoted strings and kernel
reload, and clarify validation diagnostics. Software-only; preserve strict
identity validation and existing unrelated work. Derived acceptance: configured
serial constructs passively; invalid integers still fail; affected tests pass.

## Objective

Provide a reliable reusable Python controller and lightweight Dash GUI for KSC101
shutters, with clean interfaces for laboratory integration. Use Python, uv,
pyproject.toml/uv.lock and the official Thorlabs Kinesis API. Preserve the existing
KCubeShutter/ShutterHub public interface and passive startup.

## Required behavior

- Connect/disconnect, verify selected identity, report available state, Open/Close,
  explicit cleanup and clear communication errors. Never alias mismatched serials.
- A configurable positive number of GUI slots (default three), with explicit serial selection, status/errors,
  manual controls and all-slot best-effort cleanup. Prevent duplicate serial
  ownership within the process; exclude competing applications operationally.
- Trigger configuration/readback and explicit Arm/Disarm, with drafts separate
  from device settings. GUI/controlled procedures apply at Closed/Inactive/Manual
  and read settings before Arm. Direct driver setters leave checks/verification
  to callers. Arm may open immediately. Cleanup attempts every slot despite failures/interrupts.
- Keep driver/vendor logic separate from orchestration/GUI. Validate inputs,
  preserve faults and cleanup failures, use documented enums and meaningful waits.
- Demonstrate software behavior and, separately, physical discovery, opening,
  closing/repetition, reconnect, feedback agreement, recovery, shutdown and GUI.
  A software call is not independent physical or calibrated timing evidence.
- Provide reproducible setup, API/GUI/interface documentation and five beginner
  hardware tutorials. Retain developer simulation separately from hardware lessons.
- Never bypass the physical interlock or infer missing bench facts. Firmware,
  wiring, network settings and high-consequence actions need their specific authority.

## Current bench and authorization

The reported/USB-tested chain is computer -> KEH3 left bay -> KSC101 (alias CONTROLLER_A) -> SH05R.
Firmware1.0.7 repaired the historical hardware serial mismatch. USB single-pair
motion, reconnect and shutdown have recorded evidence; three-pair, electrical TTL,
physical fault injection and calibrated timing remain separate acceptance gaps.
Historical cube Ethernet tests before the firmware update found only the hub.

The user explicitly enabled GUI/hardware and removed administrative holds, then
authorized actual browser actions without human supervision and stated hardware
was safe to test. Prior normal interlock and independent source-block confirmation
is recorded separately from unknown SDK interlock feedback. The selected-serial
session confirmation may be used for readiness; physical safeguards stay intact.
The approved added Open hold used in the GUI run was2s. The latest request below
explicitly adds short no-cable TTL tests; no firmware/fault-injection operation
or automatic repeat loop is inferred.

Stage7's dedicated repeatability test was explicitly removed; it is not a physical
PASS. Existing full three-pair, TTL and fault criteria remain unchanged. Historical
human instructions and stage-by-stage authority changes are preserved in the
[evidence archive](records/archive/README.md), not repeated as current restrictions.

## Completed request: review, prune, commit and push

User: "prune the test log, the developement junk. holistic review. fix inconsistency.
clean up. commit. push". Review the accumulated project work, fix supported defects
and stale documentation, consolidate test history without losing consequential
hardware evidence, remove verified scratch/cache/build artifacts, validate source
and packaged behavior, then commit and push to the configured origin/main branch.
Preserve .venv, installed vendor runtime and the intentional live GUI owner. No
new actuation, firmware change or loss injection is required for this cleanup.

Acceptance for this request: coherent current documentation and evidence links;
checksum-verified historical archive; no verified disposable leftovers; meaningful
software/tutorial/package regressions pass; only reviewed project changes staged;
commit/push and remote identity verified. Stable requirement IDs live in STATE.md.

## Completed request: simplify hardware testing for future use

User: "summarize our hardware test experience. substantially revise the hardware
test stages and then simplify. for future reference. your original one is too
troublesome". Replace the long mandatory stage sequence with three practical
commissioning checks and a shorter routine-session path. Preserve the useful bench
lessons, established authorization and physical safeguards; remove redundant
reviews, repeated reads without a diagnostic question and full-form prerequisites
for ordinary operation. Separate optional capabilities from routine USB testing.

Acceptance: one primary reference covering experience, expected results, cleanup
and minimal recording; aligned example/helper guidance; historical stage numbering
explicitly distinguished; physical acceptance gaps preserved. No source change,
new hardware operation or retrospective promotion of evidence is required.

## Executed request: autonomous TTL tests with both ports disconnected

User explicitly requests implementation and actual hardware TTL tests without
human intervention and reports IO1/IO2 connected to nothing. Use the established
single-pair USB bench, independent source protection and normal interlock authority.
Test configuration/readback, each disconnected input's high/low polarity response,
Disarm/Close and cleanup. Use short armed windows within the prior2-second added
hold; active-low may open immediately. Exclude external signal/wiring/voltage,
firmware and network changes. Preserve original settings and restore them Closed.
Pass applies only to actual single-controller electronic observations; external
pulses, output voltage/timing and three-controller electrical acceptance remain
unmeasured. No repeated human confirmation is required within this scope.

## Completed request: illustrated documentation and privacy cleanup

User requests updated README/docs, GUI screenshots and applicable device pictures,
with serial numbers, private data and credentials removed. Use clean captures of
the actual unconfigured GUI and an attributed manufacturer photo of KSC101/SH05R.
Replace real identities/network details/account paths in shareable text, examples,
records and assets. Preserve unredacted evidence only in ignored private storage;
label sanitized records as derivatives and refresh their hashes. Do not weaken
runtime identity validation or claim screenshots are bench proof. No new hardware
actuation, publication or Git-history rewrite is required by this request.

Acceptance: useful illustrated README/GUI/hardware guidance; no real bench IDs or
credentials in current shareable files; correct private/public boundary; passing
example syntax, documentation links, relevant software regressions and visual QA.
Earlier Git history can retain prior data; document that remaining scope clearly.

## Latest request: review, fix inconsistencies, prune, commit and push

User explicitly authorizes reviewing all accumulated project changes, fixing
supported inconsistencies, pruning verified redundant/generated material, then
committing and pushing to the configured origin/main branch. Preserve private
originals, installed SDK/.venv and the existing hardware owner; no new hardware
operation or Git-history rewrite is required. Keep unresolved TTL/Ethernet and
physical acceptance limits visible. Review the staged allowlist, run affected
software/documentation/privacy/package checks, publish normally and verify the
remote commit and final clean checkout. REQ-057 records this delivery criterion.

Latest steering: remove the privacy section from README while retaining the
Development instructions. Keep the actual cleanup boundary and evidence accurate.

## Latest steering: KEH6 and configurable shutter count

User asks for KEH6 compatibility and any number of shutters. Extend the USB-focused
hub/CLI/GUI beyond three, retaining passive startup, independent identities,
duplicate ownership guards and all-slot cleanup. Default remains three panels;
explicit --slots N selects a positive count, and more preselected serials expand
the default. No app-defined count cap; actual hub/USB/power/performance limits
still apply. KEH6 has six bays; multiple USB hubs can serve larger installations.
Document USB compatibility as expected from per-cube SDK addressing, not a new
physical qualification. Do not invent KEH6 Ethernet mappings or claim LAN works.
REQ-058 covers software extension and documentation; actual KEH6/multi-pair bench
qualification remains separate. Include reviewed implementation in commit/push.

## Follow-up request: review and publish the current system

User: "review fix inconsistency. clean up. prune. commit. push". Review the
published configurable-count implementation, correct supported inconsistencies,
prune only verified redundant/generated content, validate affected behavior and
publish with a clean checkout and verified remote. Preserve private evidence,
SDK/.venv, hardware ownership and unresolved physical qualification limits.
REQ-059 tracks this follow-up; no hardware operation is needed.

## Current request: illustrated supervisor notebook

User requests a Notion HTML notebook summarizing the session for supervisor review
and future reference, with figures, graphs and block diagrams. Create a private
Notion draft (no destination supplied) and a self-contained local HTML reference.
Distinguish software, controller feedback and independent human observation;
preserve unresolved TTL/Ethernet/multi-controller/timing limits and trace claims
to the published checkpoint/evidence. No hardware access is required. REQ-060.

Latest notebook steering: remove displayed hashes/commit IDs and make the existing
Notion/HTML notebook a practical tutorial. Keep diagrams, usable examples and
honest hardware limits; leave engineering integrity records outside the tutorial.

## Current request: simple project-configured launch

User: "simplify the uv run. no parse. put hardware config directly on project.
no env para". Replace launcher argument parsing with editable project Python
settings for SDK folder, optional serials, slot count, local port and explicit
serial-scoped operator confirmation. Launch with `uv run shutter-control`.
Remove runtime hardware environment overrides; preserve explicit Python API
configuration, passive startup, identity validation and cleanup. Earlier CLI
option instructions are superseded; configurable-count behavior remains required.
Acceptance (derived): project settings drive the passive GUI; invalid settings
fail before SDK/server access; software regressions and lint pass; current launch
instructions agree. Hardware diagnostics/tutorial scripts keep their separate
explicit procedures; no hardware test or remote notebook update is requested.

## Current request: identify GUI Open/Close communication overhead

User reports slow Open/Close response and asks to identify communication overhead
in the code. Trace action dispatch, driver waits and post-action reads; quantify
software-imposed latency separately from unmeasured transport/physical response.
Use software-only diagnostics; no runtime behavior change or hardware operation
is requested. Derived acceptance: source-linked causes, reproducible callback
trace and practical optimization priorities, with timing scope explicit. REQ-063.

## Current request: faster GUI actions with safety checks preserved

User explicitly requests implementing the diagnosed communication improvements.
Reuse verified action feedback, avoid rereading unrelated panels after each
button action, separate routine operating reads from TTL settings and remove
redundant Manual baseline work only after fresh validating feedback. Preserve
passive startup, identity/ownership/fault handling, fresh Open/Arm prerequisites,
Inactive acknowledgment before mode transitions, final state verification and
all-slot cleanup. Derived acceptance: tests demonstrate lower software wait/request
counts across 1/3/6 connected controllers and unchanged safety/error behavior;
operator/API documentation describes cached versus fresh readback accurately.
Software implementation/testing only; no physical actuation required. REQ-064.

## Current request: controller methods with one purpose and no duplicate checks

User: "each api class method in the controller serves for one purpose remove
repeated checking". Separate full, operating-only, TTL-only and cached display
reads. Remove duplicated serial validation, same-observation readiness predicates,
unrelated TTL reads before configuration, and stacked Arm preparation/waits.
Preserve state-transition verification, faults, identity/ownership and cleanup.
Original no-argument public methods retain their contracts; replace recently
introduced get_status selector flags with explicit read methods and migrate all
project callers/docs. Derived acceptance: focused request-count/latency and safety
regressions pass, with purpose and safety boundaries documented. Software-only;
no hardware operation is requested. REQ-065.

## Current request: substantially simplify Open/Close command handling

User requests shorter shutter Open/Close code and simple command handling.
Consolidate duplicated failure/recovery handling and GUI dispatch; keep established
public commands, current fast-path request counts, fresh safeguards, verified
Inactive-before-Manual sequencing, final feedback, fault latching and interrupt/
all-slot cleanup behavior. Derived acceptance: public command paths are shorter,
shared supporting code is accounted for, regression/latency tests pass and actual
hardware is not operated as part of refactoring. REQ-066.

## Current request: simple Open/Close API test notebook

User requests a simple notebook for shutter Open/Close API calls. Add an editable
serial, approved hold and explicit session verification setting, then one direct
Connect/Close/Open/hold/Close/disconnect cycle. Keep SDK settings in project config,
no arguments/environment parameters, and cleanup on ordinary errors/Ctrl+C. Do
not command an unverified identity during cleanup. Validate notebook/code against
software doubles only; do not run actual hardware. Derived acceptance: usable
.ipynb with clear setup, direct calls, cleanup and empty outputs. REQ-067.

## Current request: conditional Close preparation before Open

User explicitly requests removing unconditional Close when fresh feedback already
confirms Closed/Inactive/Manual, preserving safety and simple code. Change only
that branch; other states keep verified Close preparation. Retain fresh initial
readiness, Triggered-mode refusal, recheck safeguards after actual preparation,
final Open acknowledgment and failed-Open recovery. Derived acceptance: no
Inactive/Manual writes on the qualified baseline, full preparation otherwise,
reduced programmed waiting and no new regressions against current drifted source.
No broad restoration of missing GUI/controller APIs or hardware operation. REQ-069.

## Current request: reconcile controller/GUI and fix remaining failures

User explicitly authorizes fixing the controller/GUI API mismatch and all remaining
software test failures, with simple code and preserved safety. Restore the explicit
fresh/full, operating-only, TTL-only and cached-display contracts expected by the
GUI; keep conditional Open preparation, verified closure/mode transitions, faults,
interrupts and all-slot cleanup. Resolve stale expectations against the intended
optimized behavior without deleting safety tests. This supersedes the previous
focused-change restriction against restoring broader APIs. Derived acceptance:
full software suite, GUI callbacks, notebook scenarios and lint/format pass on the
same final source; current evidence/report supersedes the drift checkpoint.
No hardware operation is requested. REQ-070.

## Current request: update the API test notebook

User requests updating the notebook after controller/GUI reconciliation. Keep the
single-cycle direct-call example simple; use project serial/SDK defaults, add
separate elapsed Open/Close API timings, preserve session verification and finally
cleanup, and explain that API duration is not optical timing. Derived acceptance:
cleared, usable notebook; timing excludes added hold; software-double success and
error/cleanup scenarios pass; no hardware execution. REQ-071.
