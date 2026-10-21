# Project intent

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
  from device settings. Apply only at Closed/Inactive/Manual. Arm uses readback
  and may open immediately. Cleanup attempts every slot despite failures/interrupts.
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
