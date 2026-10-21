# Project intent

## Objective

Provide a reliable reusable Python controller and lightweight Dash GUI for KSC101
shutters, with clean interfaces for laboratory integration. Use Python, uv,
pyproject.toml/uv.lock and the official Thorlabs Kinesis API. Preserve the existing
KCubeShutter/ShutterHub public interface and passive startup.

## Required behavior

- Connect/disconnect, verify selected identity, report available state, Open/Close,
  explicit cleanup and clear communication errors. Never alias mismatched serials.
- Three independent GUI slots with explicit serial selection, status/errors,
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

The reported/USB-tested chain is computer -> KEH3 left bay -> KSC10168800777 -> SH05R.
Firmware1.0.7 repaired the historical hardware serial mismatch. USB single-pair
motion, reconnect and shutdown have recorded evidence; three-pair, electrical TTL,
physical fault injection and calibrated timing remain separate acceptance gaps.
Historical cube Ethernet tests before the firmware update found only the hub.

The user explicitly enabled GUI/hardware and removed administrative holds, then
authorized actual browser actions without human supervision and stated hardware
was safe to test. Prior normal interlock and independent source-block confirmation
is recorded separately from unknown SDK interlock feedback. The selected-serial
session confirmation may be used for readiness; physical safeguards stay intact.
The approved added Open hold used in the latest GUI run was2s. No automatic test
loop or broader firmware/TTL/fault-injection operation is inferred.

Stage7's dedicated repeatability test was explicitly removed; it is not a physical
PASS. Existing full three-pair, TTL and fault criteria remain unchanged. Historical
human instructions and stage-by-stage authority changes are preserved in the
[evidence archive](records/archive/README.md), not repeated as current restrictions.

## Latest request: review, prune, commit and push

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
