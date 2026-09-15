# Engineering state

Checkpoint: README diagram display fix **COMPLETE**, 2026-09-15 UTC;
[E014](records/RECORDS.md#e014). Intent: [PROJECT.md](PROJECT.md).
The preceding software cleanup is validated by [E009](records/RECORDS.md#e009);
[D006](records/RECORDS.md#d006) records the retained boundaries.
**AWAITING_HUMAN_REVIEW** remains the hardware status: no device communication or
actuation is authorized. Physical acceptance remains BLOCKED.

## Requirements

Full engineering criteria are in PROJECT.md; REQ-014–016 derive from the preceding
cleanup request's Goals, Preserve, Cleanup Process and Deliverables.
REQ-017 derives from the 2026-09-15 user request for a simple, visual README:
"What is it? → Install → Test → Connect hardware → Use safely", with all claims
verified against the repository, refined by the same-day follow-up:
"more focus on using with real hardware". Simulation is now an optional workflow.

| ID | Criterion | Validation / evidence | Status |
| --- | --- | --- | --- |
| REQ-001 | Python, uv, packaging and lock | TEST-001; fresh locked setup, build/install, E009 | PASS |
| REQ-002 | Reusable supported controller; separate GUI | TEST-002; source/API review, 49 software cases, E009 | PASS |
| REQ-003 | Physical discovery/identity/connect/reconnect | TEST-003; E002 historical empty enumeration only | BLOCKED |
| REQ-004 | Physical open/close and repetition | TEST-004; no independent physical observations | BLOCKED |
| REQ-005 | Status agrees with physical state | TEST-005; actual sensor/cache behavior unknown | BLOCKED |
| REQ-006 | Physical communication errors/recovery | TEST-006; physical loss/recovery untested | BLOCKED |
| REQ-007 | Physical safe shutdown | TEST-007; physical closure unverified | BLOCKED |
| REQ-008 | GUI through controller on hardware | TEST-008; software-only lifecycle available | BLOCKED |
| REQ-009 | Setup and troubleshooting documentation | TEST-009/018; source, Markdown and reference review, E011/E012 | PASS |
| REQ-010 | Accurate API, architecture, integration and simulation | TEST-010/018; examples E011; revised example E012 | PASS |
| REQ-011 | Actual simulated screenshots and editable diagrams | TEST-011/020; E007 screenshots; static README diagram/source and script-free render E014 | PASS |
| REQ-012 | Reproducible documentation workflow | TEST-012/018; setup/demo/build E011; revised instructions/example E012 | PASS |
| REQ-013 | Honest documentation-only historical delivery | TEST-013; E007/E008, prior request complete | PASS |
| REQ-014 | Remove unnecessary structure without losing behavior (derived) | TEST-014; diff/pruning review and regressions, E009 | PASS |
| REQ-015 | Validate final simplified package (derived) | TEST-015; 49 cases, lint/format, build/install, E009 | PASS |
| REQ-016 | Document architecture, reductions and retained complexity (derived) | TEST-016; report and references, E009 | PASS |
| REQ-017 | Simple visual README focused on hardware use (derived) | TEST-018/020; guide/examples E012/E013; static display fix E014 | PASS |

## Architecture and current validation

Dash GUI / CLI -> KSC101Controller -> Kinesis .NET via Python.NET -> USB.
Four production Python modules remain: public exports, controller, GUI and CLI.
Open reuses verified Close preparation; one concrete wait checks all feedback.
The controller retains lazy SDK loading, locking, safeguards, latched faults,
recovery and cleanup. The test fixture replaces SDK/clock for software-only runs.

[E012](records/RECORDS.md#e012): README leads with Kinesis/Python installation,
bench setup, discovery, serial selection, GUI operation and shutdown. Simulation
is optional; Python/architecture notes remain last. The revised interactive Python
example passes fixture checks for normal operation and interruption after Open.
Markdown, references and rendering PASS. E011's 49 software cases, demo API/HTTP
lifecycle and Ruff results remain applicable to unchanged source. E011 also
verified locked sync and a cached build; online build could not reach PyPI.
Source, configuration, lockfile and hardware procedure are unchanged. No SDK/USB access.

[E013](records/RECORDS.md#e013): prepublication review clarified Python bitness,
serial format, the test gate and GUI-to-script ownership. All 49 software cases,
normal/interrupted README example, Ruff, Markdown/reference checks and cached
package build PASS. Hardware commands remain unexecuted.

[E014](records/RECORDS.md#e014): user reported a GitHub rich-display error despite
the earlier local Mermaid render. The README now embeds a checked-in PNG and
links its unchanged Mermaid source. Diagram and screenshot load with JavaScript
disabled; source equivalence, links, image and Markdown checks PASS. Other guides'
Mermaid blocks and all application/hardware behavior are unchanged.

[E009](records/RECORDS.md#e009): 49 software cases PASS in a fresh locked environment
and against the installed wheel; Ruff lint/format, dependency compatibility,
CLI help, four API examples, normal/empty demo, package/CSS and documentation checks
PASS. Five Mermaid diagrams rendered; the simplified architecture was visually
reviewed. SDK/USB enumeration was explicitly excluded. No type checker is configured.

Windows x64, CPython 3.12.14, uv 0.11.2; 39 locked packages including Dash 4.4.1,
Python.NET 3.1.0, pytest 9.1.1 and Ruff 0.16.6. Other declared Python versions remain
untested. Hardware SDK/USB-driver readiness is unknown; historical SDK inspection
used Kinesis 1.14.60.27990. No SDK was loaded during cleanup.

Compared with baseline 1984b17: 39 -> 37 tracked files; production Python
637 -> 616 lines. All public signatures, CLI/config/dependencies and CSS remain
unchanged. Historical manifests describe their original revisions only. Final
changes, checks and intentional complexity are in [the report](outputs/REPORT.md).

## Next action and recovery

No README work or software cleanup remains. Resume physical validation only after
the conditions below are met. No device handle, server or browser is pending.
The pre-existing user edits in prompt log.txt were preserved byte-for-byte.
The current user instruction authorizes review, fixes, commit and push of the
README changes and the follow-up display fix to the existing origin/main.
[E013](records/RECORDS.md#e013) records the publication review; [E014](records/RECORDS.md#e014)
records the display fix. Git history and remote refs identify the published revision.

## Human action required for future hardware validation / B001

1. Known: current software checks pass (E013); physical REQ-003–008 have no acceptance
   evidence. [E002](records/RECORDS.md#e002) found no devices historically.
2. Blocker: the review hold prohibits device access; bench identity, power/cabling,
   safeguards, feedback, timing and shutdown behavior require external observations.
3. Required: approve the [ordered procedure](docs/HARDWARE_VALIDATION.md) and supply
   its stage-0 bench facts, independent beam block/source disable, observation and
   physical shutdown method, and approved shutter operating/dwell limits.
4. Return actual serial/model/firmware, installed SDK path/version/bitness, initial
   state, supply ratings/polarity, wiring/safeguard confirmation and dwell in seconds.
   Unknown values remain blockers for dependent stages.
5. After explicit launch approval, recheck stage 0 and proceed in order; require
   independent observations for every physical transition and stop on failed gates.

No human action is needed for the completed README refresh. No firmware modification or
interlock bypass is authorized. Do not infer device availability from old records.
