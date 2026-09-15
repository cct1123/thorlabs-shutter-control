# Simplification report

Software cleanup is complete; physical acceptance remains **AWAITING_HUMAN_REVIEW**
with REQ-003–008 **BLOCKED**. This pass used software fixtures only, without loading
Kinesis or communicating with hardware. Final evidence: [E009](../records/RECORDS.md#e009).
The subsequent publication review is recorded in [E010](../records/RECORDS.md#e010).

## First-time-user guide refresh

The 2026-09-15 README rewrite and hardware-focused follow-up are complete
([E011](../records/RECORDS.md#e011), [E012](../records/RECORDS.md#e012)). It leads with
status, installation, bench setup, discovery, actual serial selection and a GUI
operating/shutdown checklist. Hardware troubleshooting precedes the optional
simulator. The existing simulated screenshot stays explicitly labeled; a
connection diagram and small tables support the hardware workflow. Python usage
and developer notes are last.

49 software tests, API examples, demo HTTP lifecycle, Ruff, Markdown/reference
checks and README rendering PASS. Locked setup and cached build PASS; online
build was blocked by PyPI connectivity. Commands and hardware claims were checked
against the repository; no SDK/USB access or physical validation occurred.
Production code, configuration and the ordered hardware procedure are unchanged.
The follow-up's interactive Python example also passes software-fixture checks
for normal operation and interruption after Open; its hardware dwell limits are
explicitly operator-managed. Final Markdown, links and rendering checks PASS.
The [publication review](../records/RECORDS.md#e013) clarified Python bitness,
serial format, the software-test gate and releasing GUI ownership before a script.
All 49 software tests, example checks, lint/format and cached build pass.

## Simplified architecture

Dash GUI / CLI → KSC101Controller → official Kinesis .NET via Python.NET → USB KSC101.

Four small production Python modules remain: public package exports, controller,
GUI and CLI. Hardware behavior stays in the controller; the GUI uses its public
API. Open preparation now calls the same verified Close used by explicit Close
and shutdown. One state wait checks position, Active/Inactive and Manual mode,
plus key/interlock feedback for Open. No predicate callback or command registry
is needed. See [architecture](../docs/architecture.md) and [API](../docs/python-api.md).

## Removed or collapsed

- Removed root `ARCHITECTURE.md`, which repeated the engineering workflow already
  specified in [AGENTS.md](../AGENTS.md).
- Merged `docs/assets/README.md` into the [GUI guide](../docs/gui.md#screenshot-provenance),
  alongside the screenshots it explains. All four images and reproduction details remain.
- Collapsed three predicate callbacks and duplicated Close preparation into the
  controller's existing closing path and one concrete feedback wait.
- Removed redundant Dash asset-path construction/import and an explicit default
  callback setting; package-local CSS and initial refresh are still checked.
- Removed the fake's unused clock export and special stuck-position flag. Tests
  inject disagreement at the affected device method instead.
- Replaced a custom fake server class/factory with a patched Dash run method,
  exercising the real app construction during the CLI shutdown test.
- Shortened checkpoint/report duplication and removed the architecture diagram's
  artificial split between the public controller and its implementation.

No dependencies were removed: Dash, Python.NET, pytest, Ruff and Hatchling each
serve a required purpose. Packaging, lockfile, CLI flags and public signatures are
unchanged. Timeout errors now name the full expected state; failed Open preparation
can include the underlying Close failure before the recovery result.

## Size and validation

Against baseline 1984b17, tracked files decreased **39 → 37**; production Python
lines decreased **637 → 616** (21 lines, about 3.3%). Test code increased by 13 lines
for the five added safety cases. Counts exclude ignored builds/caches and the
user's prompt-log edits. The runtime was already compact; no production module
merger met the stated preservation criteria.

Final checks in [E009](../records/RECORDS.md#e009):

- 49 software tests PASS in a fresh locked environment and against the installed wheel.
- Ruff lint/format PASS; all 39 installed dependencies compatible; CLI help PASS.
- Source distribution and wheel build/install PASS; installed GUI/layout/CSS HTTP 200,
  passive initial callback and package assets checked without vendor modules loading.
- Four documented Python examples and normal/empty API demos PASS (empty exit 1 expected).
- Markdown lint and internal references PASS; five Mermaid diagrams rendered without
  browser errors and the revised architecture diagram passed visual review.

The original 44 software cases passed immediately after the controller reduction.
Five additional feedback cases cover ignored Manual mode during preparation and
operating-state/mode/key/interlock disagreement after Active. All existing lifecycle,
selection, passive startup, fault-latching, cleanup, interruption and GUI cases remain.

The real-SDK test enumerates USB and was excluded under the hardware hold. No
physical movement, feedback freshness, timing or shutdown guarantee is established
by these tests. No static type checker is configured; Ruff and Python/package
execution are the project's configured checks.

## Complexity intentionally retained

- `KSC101Controller`, immutable `ShutterStatus`, and `ShutterError`: the required
  reusable interface isolates vendor types and gives callers explicit fault snapshots.
- SDK cache/DLL handles and locks: retain native dependencies, enforce one loaded
  Kinesis installation and serialize calls on a controller instance.
- Health checks around status reads, feedback timeouts, safeguard checks, latched
  faults, recovery Close and retained handles after failed release: protect correctness.
- Separate Close and disconnect operations, passive release, context cleanup and
  the public `safe_shutdown()` wrapper: actively documented APIs with different
  ownership/output consequences. Cleanup still runs after failure or interruption.
- GUI/CLI modules, packaged CSS, and SDK/controller/GUI/CLI tests: each isolates a
  real runtime or validation boundary. Merging them would couple unrelated concerns.
- The shared fixture/demo and historical evidence manifests: avoid duplicate
  simulators and preserve reproducible software examples and revision-specific evidence.

## Documentation pass

The prior documentation delivery remains available: README, setup, GUI, API,
architecture and hardware guides, four simulated screenshots and five editable
Mermaid diagrams. [E007/E008](../records/RECORDS.md#e007) and the
[historical manifest](../records/documentation-manifest.json) identify that delivery.
Old manifests do not identify the refactored candidate; E009 records its validation.

## Hardware handoff

The [ordered hardware procedure](../docs/HARDWARE_VALIDATION.md) is unchanged.
[STATE.md](../STATE.md#human-action-required-for-future-hardware-validation--b001)
records the missing bench facts, safeguards and exact resumption condition.
Explicit approval and stage-0 verification are required before device access.
Shutdown remains a best-effort Close and release; USB/power loss, hung native calls
or forced termination cannot guarantee closure. No firmware or interlock changes
are authorized. The user's pre-existing `prompt log.txt` edits are preserved.
