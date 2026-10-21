# Project intent

## Simple GUI latency improvements - REQ-105

User: "now implement the simple latency improvements for Connect and Apply TTL.
keep code beginner-readable and retain safety checks. validate and commit step by
step."

Derived acceptance: use the existing combined operating/TTL snapshot to reduce
default programmed waits for GUI Connect from 500 to 250 ms, and Apply TTL from
750 to 500 ms. Reuse the completed action's result in the callback rather than
reading it again. Preserve Connect identity/route/ownership and passive output
behavior; preserve Apply's Closed/Inactive/Manual prerequisite, actual TTL
readback comparison and fault/cleanup handling. Keep other command paths, driver
contracts, polling intervals and discovery policy unchanged. Validate software
only and commit Connect and Apply separately. These waits exclude native calls
and do not establish physical response time. No hardware action is authorized.

## Beginner readability - REQ-104

User: "implement the readability and scaffolding reduction. prioritize beginner
understanding. keep behavior unchanged. improve docstrings and comments where
needed. validate and commit step by step."

Derived acceptance: give a developer with basic Python a clear source reading
path; explain state, ownership and failure contracts; replace positional GUI
output bookkeeping with named values; separate action handling from presentation;
keep tests understandable and cover one/multiple panels. Preserve public APIs,
GUI element IDs/messages, startup, discovery, command/read order, waits and cleanup.
Validate with software-only regressions and before/after callback and SDK-call
comparisons. Commit focused stages. Hardware operations are outside this request.
An actual novice handoff exercise remains separate from software validation.

## Essential tests - REQ-102

User: "clean out all tests. rewrite all tests. simply and essential. no speculative
check tests." Replace the full test suite and its doubles/helpers with a small
current-contract suite. Cover normal USB/LAN commands and feedback, TTL settings,
identity and retained ownership/cleanup, unified GUI discovery/modes, passive
launcher shutdown and both notebook workflows. Keep only essential failure cases
with an operational reason; remove fuzz/type matrices, implementation traps,
speculative race scenarios and real-device opt-in tests. Production behavior,
private results and the environment remain unchanged. Validate software only;
record the narrower scope honestly and update the documented test command.

## Current baseline - REQ-101

User: "update. clean out development trash. slim down repo. remove all legacy.
set this as baseline. remove any compatibility support".

Maintain one current Windows Python application and library for KSC101/SH05R
control through USB or documented KEH3 Ethernet routes. The current USB/LAN
workflow is the baseline. Breaking removal of obsolete interfaces is intentional;
provide no aliases, migration adapters or alternative old workflows.

## Acceptance criteria (derived)

- Retain passive startup, unified Discover, explicit selection/Connect, four GUI
  modes, TTL settings, configurable panel count and explicit output commands.
- Retain identity/transport validation, exclusive serial ownership, retained-handle
  protection, partial-discovery diagnostics and all-slot cleanup after failures.
- Use ShutterHub as the GUI boundary. Keep KCubeShutter as the direct USB API.
  Remove the single-controller GUI adapter and unused operator-confirmation API.
- Remove numbered diagnostic stages, duplicate script tutorials, supervisor
  deliverables, obsolete screenshots and incremental development records.
  Keep two current notebooks, focused regression tests and concise operating docs.
- Preserve private inputs/results and .venv. Consolidate physical observations
  and unresolved limits without presenting old bench results as current validation.
- Validate maintained source, extracted wheel, notebooks, documentation links,
  package contents and cleanup. No hardware operation is needed or authorized.
- Commit focused stages and push the reviewed baseline under the existing
  publication authorization; verify the remote and clean checkout.

## Supported system

Windows x64, Python 3.12 x64, official Kinesis .NET Framework runtime and Python.NET.
USB addresses individual cubes directly or through USB hubs. Ethernet uses the
documented KEH3 ports only. KEH6 Ethernet mapping is outside the implementation.
Driver setters write; explicit getters read. Applications own readiness and
sequencing. Users manage the physical interlock and independent source protection.

## Evidence and continuity

STATE.md is the current checkpoint, records/RECORDS.md records baseline decisions
and tests, and outputs/REPORT.md describes delivery. Physical observations are in
records/hardware-evidence.json. Earlier intent/checkpoints/records are recoverable
at Git commit 5ab1f91 and hash-verified ignored inputs/private/baseline-5ab1f91.
Those artifacts provide provenance, not maintained workflows or compatibility.
Current physical qualification remains incomplete; see docs/HARDWARE_VALIDATION.md.
