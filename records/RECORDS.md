# Engineering records

Durable evidence and decisions. Software doubles, SDK enumeration, and physical
observations have distinct scopes. Each record identifies its scope; subsequent
documentation evidence is appended below. No physical shutter operation has
been observed or claimed.

## E001

Kind / scope: official documentation and SDK inspection; TEST-002, REQ-002/005.
Sources: [interface notes](../docs/INTERFACE.md) link the official KSC101 Python/C#
examples, manufacturer manual and Kinesis download page. Python example source
revision: `d85b2014d12018028c3eba1f724f42e94d3c47bf`.

Method: inspect examples without executing their device-control code; extract/read
the manual and visually inspect its specification/interlock pages. Download the
official x64 Kinesis 1.14.60 package; verify its published SHA-256 and Authenticode
signature; extract an MSI administrative image into the workspace. Load its
DeviceManagerCLI/GenericMotorCLI/KCube.SolenoidCLI assemblies via Python.NET;
reflect the actual properties, method names and enum values. Compare state meanings
with the vendor KSC101 C header included in the SDK.

Expected: authentic vendor package and real KSC101 API members supporting the
required class boundary. Observed: SHA-256
`298c4cc03a6c3b4d5c174964ae9193d13baca63dab10c1595b4e9ad5d914ff05` matched;
signature valid, signer Thorlabs, Inc. SolenoidCLI file/product version
`1.14.60.27990`. .NET Framework and all selected assemblies loaded.
GetSolenoidState is distinct from GetOperatingState; enum values and health/
key properties match [test_sdk.py](../tests/test_sdk.py). Native header documents
the interlock bit 0x1000. PASS for source/API selection and reflection scope.

Local, ignored sources: `tmp/references/`, `tmp/pdfs/`, `tmp/kinesis-sdk/`.
The initial extraction-only switch produced no usable image; documented MSI
administrative extraction succeeded (log ACTION=ADMIN, return 0). No system Kinesis
driver installation or firmware modification performed. CHM extraction produced no
usable HTML; API conclusions are based on actual assembly reflection, vendor
header and official examples, not inferred CHM contents.

Limitations: loading/reflection does not validate hardware commands, exact polling
freshness, or physical feedback. The manual contains legacy APT software material;
current Kinesis APIs were taken from the SDK/examples.

## E002

Kind / scope: environment/USB inventory and real SDK discovery; TEST-003, REQ-003.
Method: inspect usual Kinesis folders; inspect connected PnP device descriptions;
execute `DeviceManagerCLI.BuildDeviceList()` and `GetDeviceList(68)`, also through
`uv run --locked shutter-control --list --kinesis-dir "tmp/kinesis-sdk/Program Files 64/Thorlabs/Kinesis"`.
Use `--cache-dir .uv-cache` on this sandbox.

Observed: only Thorlabs OPM in the usual program folders; no standard Kinesis
installation found. Connected PnP inventory had no device identified as KSC101/
Thorlabs. WMI OS query was denied, so it was not used as hardware evidence.
The real SDK returned `[]`; CLI displayed `No KSC101 devices discovered.`
with exit code 0 (enumeration completed, not a hardware PASS).

Result: BLOCKED for required physical discovery/connection. No controller serial,
shutter model or power arrangement was discovered. USB-driver readiness is
unverified; empty enumeration alone does not distinguish unavailable hardware
from connection/power/driver problems. No Connect or output command reached hardware.
Bearing: B001 in STATE.md; REQ-003..008 require operator/hardware access.

## E003

Kind / scope: software tests and packaging; TEST-001..008 (software scope only).
Configuration: Windows x64, uv 0.11.2, CPython 3.12.14, Dash 4.4.1, Plotly 7.0.0,
Python.NET 3.1.0, pytest 9.1.1; official Kinesis x64 1.14.60.27990 for the opt-in
SDK check. [validation-manifest.json](validation-manifest.json) fingerprints the
tested source/configuration and final build outputs.

Method / expected:

- `uv lock --check`, `uv sync --locked --offline`: lock consistent; environment reproducible.
- `uv run --locked ruff check src tests`, `ruff format --check src tests`: no findings.
- Set KINESIS_TEST_DIR to the extracted SDK and run
  `uv run --locked pytest -q -p no:cacheprovider`: all tests pass without physical actuation.
- `uv build --offline`: build sdist/wheel; inspect wheel for controller, GUI, CLI,
  CSS and absence of vendor DLLs/test files.

Observed: locked/offline sync passed with 39 resolved packages; lint clean, formatter
left files unchanged. Final test run: **43 passed in 0.57 s**, exit 0. Final
sdist/wheel built successfully; package contents verified. An earlier pytest cache
warning was an environment permission issue; use of the cache provider was disabled
for final validation and its failed generated cache directory was removed.

Tests demonstrate input/selection validation; no output writes during connect;
partial-connect cleanup; 20 repeated open/close cycles in a software double;
manual-mode ordering; safeguard refusal; missing-feedback timeout and recovery-close
attempt; fault latching and unknown state, including connection loss during sampling;
release even after close/polling errors or interrupted close; retained handle on
disconnect failure; context-manager error preservation; CLI shutdown on server
failure; Dash lifecycle callbacks and no command replay on refresh. The optional
test loads actual DLLs/checks SDK members and enumerates, without connecting.

Result: PASS for REQ-001 and software architecture portion REQ-002. Physical
REQ-003..008 remain BLOCKED. Software-double transitions are not observations of
the real shutter. Kinesis's own USB/cache timeout behavior remains to be measured.

## E004

Kind / scope: real-browser GUI inspection with real SDK, no device; TEST-008.
Method: run the local Dash server with the extracted SDK on 127.0.0.1:8050,
inspect rendered page, click Discover, click Connect, and inspect feedback.
Review the final compact CSS layout after reload.

Expected: passive initial state, no unintended output commands, actionable
no-device error and disabled Open/Close. Observed: Disconnected, unknown identity/
state/key/interlock; Discover showed `Found 0 device(s).`; Connect showed
`Expected one KSC101; found 0. Connect a device or explicitly select its serial number.`
Open and Close stayed disabled. Page/callback/asset requests returned HTTP 200;
layout reviewed visually. PASS for this no-device browser scope.

Server stopped after verification; no controller handle had been opened. Stopping
this no-device server is not evidence of physical shutdown behavior. Successful
connected GUI lifecycle was exercised through HTTP callbacks with a software double
in E003; its physical counterpart remains blocked.

## D001

Decision: accept the user's 2026-09-09 autonomous launch as superseding the original
initialization-only pause. Updated PROJECT.md's current scope accordingly.
Basis: explicit user instruction to begin and continue the engineering loop.
Consequence: research, reversible local implementation and software checks proceed;
physical actions remain bounded by the actual setup and AGENTS.md. Requirements
and firmware/interlock restrictions unchanged.

## D002

Decision: use a single public Python controller around official Kinesis .NET via
Python.NET; Dash only orchestrates that public interface.
Basis: E001 and the user's supported-interface/minimal-structure constraints.
Consequence: Windows/Kinesis runtime required for hardware; vendor binaries are
external prerequisites. One SDK version per process, one owner per device.
Reconsider if official KSC101 interface support or the host platform changes.

## D003

Decision: connect without explicit output/mode commands; explicit Open/Close use
Manual mode; default disconnect attempts close before release and reports failures.
Never represent a successful setter as independent physical verification.
Basis: user requirements, manufacturer mode/state semantics (E001), failure-path
software checks (E003). Recovery must preserve an unknown state after a fault.
Consequence: close on context exit/Ctrl+C is best-effort; default disconnect changes
output. A deliberate communication-only disconnect is available. Browser closure,
forced termination and USB loss do not guarantee closure. Physical acceptance
must verify the documented policy before the project can be COMPLETE.

## E005

Kind / scope: hardware-readiness source audit and reproduced defect; 2026-09-09.
Reviewed PROJECT, AGENTS, STATE, engineering records, controller/real SDK boundary,
test double, GUI/CLI/assets, all tests, packaging/lock and documentation. Read local
official Python example, KSC101 native header and manual text; no SDK load, USB
inventory, discovery, connection or actuation was performed during this audit.

Baseline: 42 software tests passed in 0.17 s with tests/test_sdk.py explicitly
excluded. E003's 43 included one real-SDK enumeration test; that result is historical,
not rerun evidence. E004's rendered-browser zero-device result is also historical.

Finding: Open preparation required only Manual feedback before EnableDevice/Active,
so it proceeded even when the preceding Inactive command still reported Active or
Open. Two software regressions injected those independent disagreements: both
FAILED before the fix (DID NOT RAISE), reproducing false successful preparation.
The single production change requires Closed AND Inactive AND Manual before
EnableDevice/Active. It retains the existing timeout/recovery-close/fault behavior.
Both regressions and the full software suite now PASS. No API, GUI, dependency or
backend abstraction was added. E003 alone no longer validates the changed code;
E006 supplies current software evidence. Physical feedback freshness remains unknown.

Procedure defect: TEST-003's initial disconnect used the default Close policy.
Replaced it with explicit disconnect(close_shutter=False) for communication-only
checks; documented exact first vendor calls, first Close before Open, normal
shutdown before GUI/repeated cycles, and closed-state USB fault injection last.
All potential actuation and observation gates are identified. Clarified that no
explicit persistence call does not prove a mode change is nonpersistent: the
manufacturer manual describes remembering the last mode across power cycles.
The ordered procedure was reviewed against actual public methods and shutdown paths.

## E006

Kind / scope: current software/packaging acceptance; TEST-001..008 software scope.
Configuration: Windows x64, CPython 3.12.14, uv 0.11.2; locked 39-package environment
including Dash 4.4.1, Plotly 7.0.0, Python.NET 3.1.0, pytest 9.1.1, ruff 0.16.6.
Application source/build/document fingerprints: [readiness manifest](hardware-readiness-manifest.json).
Base Git revision: bdcb48fffd8a579edc83a2cadf91eed5256a385f plus the audited changes.

Commands run from repository root with
`C:\Users\ctcheung\.local\bin\uv.exe --cache-dir .uv-cache`:

1. Unset KINESIS_TEST_DIR. `run --locked --offline pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`:
   **44 passed** after fix (0.19 s).
2. Set UV_PROJECT_ENVIRONMENT=tmp/audit-venv and run `sync --locked --offline --python
   C:\Users\ctcheung\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`:
   created a fresh environment, installed all 39 locked packages. Repeat software
   test command: **44 passed in 0.43 s**.
3. `run --locked --offline ruff check src tests`: PASS;
   `run --locked --offline ruff format --check src tests`: 9 files already formatted.
   `run --locked --offline shutter-control --help`: PASS without SDK loading.
4. `build --offline --out-dir tmp/audit-dist`: sdist and wheel built successfully.
5. `pip install --offline --python tmp/audit-venv/Scripts/python.exe --no-deps
   --reinstall tmp/audit-dist/thorlabs_shutter_control-0.1.0-py3-none-any.whl`:
   replaced editable install with wheel. Using that environment's Python directly,
   `-m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`: **44 passed in 0.17 s**.
   Installed CLI --help and `pip check --python tmp/audit-venv/Scripts/python.exe`: PASS.
6. Verified import path is the audit environment's site-packages, wheel contains
   CSS and no vendor DLL/executable, and passive Flask page/layout/CSS routes return
   200. Asserted _loaded_sdk is None and clr/pythonnet/Thorlabs modules absent.

Meaningful simulated coverage: discovery/selection and no-device handling, passive
connection, partial-connect cleanup, 20 cycles, safeguard refusal, incomplete
preparation, missing feedback, communication faults and unknown-state latching,
shutdown failure/retry/interruption, original-exception preservation, CLI cleanup,
real Dash HTTP callback lifecycle/error handling and no replay on refresh.
The fake applies normal updates immediately; it does not model USB timing, vendor
cache age, drivers, electrical interlocks or mechanics. No claim of real-time or
physical acceptance is made. The real SDK opt-in test was excluded, not counted
as a current PASS. Final documentation-only package rebuilds preserve tested code.

Reproducibility boundary: runtime/dev dependencies are locked and a fresh cached
install was demonstrated on Python 3.12 x64. Other allowed Python versions are
not validated. Fresh uncached hosts require package/Python downloads and a separate
supported vendor runtime/driver installation. Hatchling's allowed build dependency
range is not a claim of byte-identical builds on every host; artifact hashes record
the actual builds. Neither vendor binaries nor drivers are supplied by uv.lock.

## D004

Decision: user-requested review supersedes autonomous hardware continuation.
After E005/E006, record HARDWARE_READY, then AWAITING_HUMAN_REVIEW; retain BLOCKED
for physical REQ-003..008. These explicit user-requested readiness states refine
the template workflow; neither means COMPLETE or grants physical authority.
PROJECT.md's current scope records the same user instruction. No hardware
communication, actuation, firmware changes or safeguard bypass occurred in this audit.
Resume only after human approval using docs/HARDWARE_VALIDATION.md from stage 0.
Unknown bench facts remain unknown until discovered or supplied. Preserve E001–E004
as historical evidence; use the new manifest for the current reviewed candidate.

## D005

Decision / scope: documentation-only follow-up to the user's
[request in prompt log.txt](../prompt%20log.txt), REQ-009–013. Preserve the production controller,
GUI, CSS, tests, dependency configuration and hardware-review hold. No device access,
hardware validation or architectural change is authorized by this request.

Inspection found no production simulator or separate backend class: the real
Kinesis implementation is inside controller.py, and simulation is the pytest rig
in tests/conftest.py. Document this existing structure rather than inventing
`--simulate`, `open()`/`close()` aliases or a pluggable backend interface.
Add only a source-checkout documentation helper under docs/examples that reuses
the existing fixture for the API walkthrough and actual GUI screenshots. It
replaces the SDK loader before use and restores it after cleanup; it is not an
installed command or public backend. This is documentation-enabling support,
not production feature work. No concrete production defect was found in the
documented workflows.

Keep the detailed hardware procedure's sequence/gates and historical readiness
evidence intact. Replace its machine-specific working-directory/uv path with a
repository-root instruction and PATH lookup; this changes no device operation.
The readiness manifest still identifies the unchanged code/test/configuration
candidate; its older document/build hashes are historical after this pass.
Do not interpret documentation completion as physical project completion.

## E007

Kind / scope: documentation, software-only examples, GUI browser captures,
Markdown/diagram checks and packaging on 2026-09-09/10 UTC. TEST-009–013,
REQ-009–013; software evidence also supports unchanged REQ-001/002.
No real SDK loading, USB enumeration, device communication or actuation occurred.

Expected results: current commands/examples match implementation, the actual GUI
renders the documented simulated states, internal links/assets resolve, Mermaid
renders, packaging succeeds, and production/test/configuration fingerprints remain
unchanged. Physical REQ-003–008 are excluded, not counted as PASS.

Observed software validation:

- Fresh `tmp/docs-venv` environment: `uv sync --locked --offline` installed all
  39 locked packages with CPython 3.12.14 x64 and uv 0.11.2. In this sandbox, set
  `UV_CACHE_DIR` to `.uv-cache`, `UV_PROJECT_ENVIRONMENT` to `tmp/docs-venv`, and
  `UV_PYTHON` to the existing bundled Python 3.12 executable. The initial offline
  attempt without that interpreter reference could not discover Python 3.12;
  explicitly selecting the installed interpreter resolved it. This is a fresh
  environment equivalent, not a new system Python/uv installation.
- `uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`:
  **44 passed in 0.46 s**. The SDK test was explicitly excluded regardless of
  environment. `ruff check src tests docs/examples` and
  `ruff format --check src tests docs/examples`: PASS, 10 Python files.
- `uv run --locked shutter-control --help`: PASS. Documented hardware CLI flags
  match argparse; actual `--list`/Connect/actuation were not run on hardware.
  Git HTTPS clone URL matches the configured origin; remote cloning and the
  documented uv installer command were not executed. Fresh-clone network/access
  conditions and vendor-driver installation are not established by this pass.
- `uv run --locked python docs/examples/simulated_demo.py --api`: PASS; fictional
  identity `68000001`, Closed → Open → Closed → Disconnected. All four Python
  example blocks in README.md / docs/python-api.md executed against the existing
  fixture. Integration callback return and exception paths both closed the fake.
  `_loaded_sdk` remained None; no clr/pythonnet/Thorlabs modules were loaded.
  Detailed temporary result: `tmp/docs-example-results.json`.
- All 13 source/test/configuration fingerprints covered by this review match
  the prior readiness manifest, including source CSS, tests, pyproject.toml,
  uv.lock and .python-version. User-maintained prompt log.txt was not edited.
- `uv build --offline --out-dir tmp/docs-dist`: wheel and source distribution
  PASS. Installed the wheel with `uv pip install --offline --python
  tmp/docs-venv/Scripts/python.exe --no-deps --reinstall` and its wheel path;
  `uv pip check --python tmp/docs-venv/Scripts/python.exe` and installed CLI help
  PASS. Verified import from site-packages, passive GUI page/layout/CSS HTTP 200,
  current README in package metadata, CSS in wheel, no demo/test/vendor binaries
  in wheel, and demo plus all four screenshots in sdist. No vendor modules loaded.
  Detailed temporary result: `tmp/docs-package-results.json`.

Observed GUI/visual validation:

- Ran the actual `create_app`/callbacks/CSS with the documentation fixture helper.
  Microsoft Edge 152.0.4191.66, Playwright, viewport 820 × 850 px, scale 1.
  Captured fresh disconnected, connected/Closed, Open, and empty-discovery error
  states. Normal browser lifecycle ended with Close & disconnect; the error case
  remained disconnected with Open disabled. No browser JavaScript errors in the
  normal lifecycle. Screenshots were inspected visually without pixel editing.
- [Asset provenance and reproduction steps](../docs/gui.md#screenshot-provenance) identify
  every screenshot as simulation. Fictional identity and test-double description
  are visible in connected captures. No private desktop material, real device
  serials or vendor photographs were included. Missing bench photos are documented.
- Browser/server sandbox restrictions initially prevented localhost binding and
  headless process launch. Scoped automatic escalation allowed the fixture-only
  server and temporary-profile browser; no hardware fallback was used.
- Markdown/diagram tools were installed only in ignored `tmp/docs-tools` with
  scripts disabled, without changing project dependencies. Markdownlint-cli2
  0.23.2 uses an ignored config permitting HTML img elements and long lines/tables
  (MD013/MD060 disabled). Seven user-facing Markdown pages checked. An underscore
  in a CLI link label was corrected. Mermaid blocks rendered in an isolated
  local-content browser; diagram labels were shortened after visual inspection.
  Final link/render result: `tmp/docs-render-results.json`.
- Final user-page render: seven pages, 77 internal references, five Mermaid
  diagrams, zero missing references/images and zero browser JavaScript errors.
  Broader checkpoint/report/reference-document links are checked again with the
  final manifest present. Both screenshot servers were stopped after verifying
  their process command lines; the normal simulated device had already been
  closed/disconnected. No pending device/process operation remains.

Command verification distinguishes executed software commands from source-checked
hardware/installer/remote-clone commands. Official uv instructions and Python.NET
runtime guidance were checked online. The vendor download page was reachable but
provided no readable text; the linked manual could not be refetched by the web
reader, so its existing local extraction and E001 were used to verify the quoted
hardware context. No new vendor version/compatibility claim is made.

Final outcomes, artifact hashes and check counts are captured in the
[documentation manifest](documentation-manifest.json). New documentation status
and limitations are summarized in [the report](../outputs/REPORT.md#documentation-pass).
These results do not change the blocked physical acceptance criteria.

## E008

Kind / scope: user-requested review, pruning and publication of the documentation
with `prompt log.txt`. TEST-009–013, REQ-009–013; no device access. Expected result:
concise, accurate guides with valid links/builds and unchanged production behavior.

Review found repeated simulation, status and shutdown explanations, plus a full
request archive already present verbatim in the prompt log. Removed that duplicate
and linked the original log; shortened README, architecture/hardware/setup text,
asset notes and the report: 2,730 words removed, including the 2,137-word duplicate
request. Kept all examples, screenshots, diagrams, public API
details and hardware-validation gates. No production defect was identified.

The user explicitly authorized committing the prompt log with these changes and
pushing. Its content was preserved; Git applies the repository's LF normalization.
Fetched origin and confirmed main had no divergence before preparing the commit.
Markdownlint reports zero issues; all 110 internal references resolve, and four
Python documentation blocks pass against the fixture, including acquisition
failure cleanup. Final builds/installed-wheel checks and file hashes are in
[the manifest](documentation-manifest.json).
E007's screenshots, example execution and 44-test results remain applicable to
unchanged source/tests/demo. Publication is identified by Git history/origin/main;
physical acceptance remains blocked under the existing review hold.

## D006

Kind / scope: active user-requested aggressive simplification, superseding only
PROJECT.md's prior documentation-only implementation restriction. Hardware hold
and all acceptance criteria remain. REQ-014–016 derive from that request.

Retain four production modules: exports, hardware controller, Dash UI and CLI.
Each has a current API/runtime boundary. Reuse Close during Open preparation and
replace generic predicate waits with one concrete state wait. Preserve the vendor
call order, full feedback/safeguard gates, fault latching, locks and cleanup.
Exception type is unchanged; timeout messages now name the full expected state,
and Open preparation errors can include the nested Close failure.

Remove duplicate workflow documentation, merge screenshot provenance into its
GUI guide, use Dash's package-local asset default, and prune unused fixture state
and a custom server fake. Keep used public wrappers, vendor isolation, dependency
lock/build configuration, all important tests and historical evidence. No new
framework, production abstraction or dependency was introduced. The only adjusted
historical record link points to the relocated screenshot provenance.

## E009

Kind / scope: software cleanup on 2026-09-10 UTC, base commit `1984b17`.
REQ-001/002, REQ-009/010/012 and derived REQ-014–016; TEST-014–016, with affected
TEST-001/002 and TEST-009/010/012 rechecked. Physical REQ-003–008 remain BLOCKED.
No real SDK load, USB enumeration, device communication or actuation is authorized.

Expected: preserve public signatures and command/safety/cleanup behavior, remove
redundancy, pass all software tests and documented examples, and build/install the
package with functional passive GUI/CSS. Real-SDK enumeration is explicitly excluded.

Observed:

- Baseline: 44 software cases PASS (0.23 s), Ruff lint/format PASS. After collapsing
  Close and feedback waits, the same 44 cases PASS (0.18 s). Ruff identified one
  line wrap, corrected with its formatter before subsequent checks.
- Added five parameter cases for preparation-mode and post-Active operating-state,
  mode, key and interlock disagreement. All 49 cases PASS after fixture/GUI pruning
  (0.22 s), retaining every existing behavior/regression case.
- Fresh `tmp/cleanup-venv`: `uv --cache-dir .uv-cache sync --locked --offline`, with
  `UV_PROJECT_ENVIRONMENT=tmp/cleanup-venv` and `UV_PYTHON` pointing to the existing
  bundled CPython 3.12.14 x64. uv 0.11.2 installed all 39 locked packages. This
  validates a fresh environment from cache, not a fresh network/OS installation.
- Fresh environment: `python -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`
  PASS, 49 cases (1.02 s); `ruff check src tests docs/examples` and
  `ruff format --check src tests docs/examples` PASS, 10 files. CLI `--help` PASS;
  `uv pip check --python tmp/cleanup-venv/Scripts/python.exe` PASS, 39 packages.
- All four README/API Python blocks PASS using the patched fixture, including
  acquisition success/failure cleanup; no clr/pythonnet/Thorlabs module loaded.
  Demo `--api` returned 0 with Closed → Open → Closed → Disconnected; `--api --empty`
  returned the expected 1 with the missing-device diagnostic. One-off verification
  source: `tmp/cleanup-examples.py`; it excludes obsolete unchanged-source assertions.

- `uv --cache-dir .uv-cache build --offline --out-dir tmp/cleanup-dist`: sdist and
  wheel PASS. Installed with `uv pip install --offline --python
  tmp/cleanup-venv/Scripts/python.exe --no-deps --reinstall` plus the wheel path.
  All 49 software cases PASS against site-packages (0.21 s). Passive GUI, layout
  and CSS return HTTP 200; initial callback remains enabled; no vendor modules load.
  Wheel includes CSS/current README and excludes tests/demo/vendor binaries; sdist
  includes the demo/screenshots and excludes the two deleted documents. Check source:
  `tmp/cleanup-package.py`. Builds use the configured Hatchling range, not a claim
  of byte-identical artifacts across build-tool versions.
- Markdownlint-cli2 0.23.2: 11 maintained Markdown files, zero issues using the
  existing ignored `tmp/docs-lint.json` (long lines/tables and HTML images allowed).
  A pre-existing bare URL in the hardware procedure was converted to a link; its
  ordered steps/limits are unchanged. `tmp/cleanup-docs.cjs` checked internal links
  and rendered six user pages/five Mermaid diagrams: zero missing references/images
  or browser errors. The simplified architecture was visually reviewed. Headless
  Edge initially hit sandbox EPERM; scoped automatic escalation permitted the
  temporary local-only browser check. Browser closed normally; no server was needed.
- Public method signatures checked with AST comparison against HEAD; package
  exports, CLI, CSS, pyproject.toml, uv.lock and .python-version are byte-identical
  to baseline. User-maintained prompt log.txt matches its pre-cleanup SHA256.
  No static type checker is configured; none was added for this refactor.
- Final pruning reviewed every remaining module, helper, configuration and dependency.
  39 -> 37 tracked files; production Python 637 -> 616 lines (3.3% reduction).
  Test Python 534 -> 547 lines for five additional safety cases. No public API or
  dependency removed; no permanent verification framework/manifest introduced.

Changed production SHA256 (other production/configuration files match base 1984b17):

- `controller.py`: `7761daa9f3dc383384e58bc3f990b3a19f7eb78e101708e05b3cb944cd594baf`
- `gui.py`: `a52e176194de1e7d17a445f9ade1942440633c886f73835a656843919c0bc775`

TEST-014–016 PASS; affected software/documentation requirements revalidated.
Cleanup is COMPLETE. Physical REQ-003–008 remain BLOCKED under the review hold.
Historical manifests still identify their original candidates. No hardware operation,
server or browser remains pending; no commit or push was requested/performed.

## E010

Kind / scope: user-requested review, fixes, commit and push of the cleanup,
2026-09-10 UTC. TEST-017: prepublication review of REQ-014–016 and current software
validation, followed by Git publication verification. Hardware hold unchanged.

Reviewed the full pending diff, including the shared Close path, all feedback gates,
fault/recovery behavior, Dash defaults, revised tests and documentation removals.
No production defect found. Corrected stale checkpoint statements referring only
to baseline tests and saying publication had not been requested. Production/test
files remain the candidate validated in E009; its source fingerprints still apply.

Current source suite: `python -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`
PASS, 49 cases (0.20 s). Ruff lint/format PASS for all 10 Python files; `git diff
--check` PASS. Internal references resolve; E009's package/example/diagram checks
remain applicable. No real SDK load or device access occurred.

Fetched origin and confirmed HEAD/origin/main had no divergence before publication.
The reviewed commit includes the related user-maintained prompt-log additions;
their content is preserved, with Git's configured LF normalization in the index.
The active user request authorizes commit and push to the existing origin/main.
Git history and the matching origin/main revision identify the publication result.

## E011

Kind / scope: first-time-user README rewrite, 2026-09-15; base `b40ec49`.
Derived REQ-017 from the current user request; TEST-018 rechecks affected
REQ-009–012. Documentation only; the hardware-review hold is unchanged.

Expected: a concise Install → Test → Demo → Hardware → Safe use guide, with
repository-backed commands, interfaces and validation claims; usable existing
screenshot, valid diagram/links, and no SDK/USB access.

Observed:

- Inspected controller, GUI, CLI, packaging/lock, fixture/demo, hardware procedure,
  current checkpoint and E009/E010. Reused the existing simulated GUI screenshot
  after visual inspection; its provenance remains in docs/gui.md.
- `uv sync --locked` PASS: 39 packages checked. This shell lacked uv on PATH;
  prepended the existing `C:\Users\ctcheung\.local\bin` for verification and used
  project-local `UV_CACHE_DIR=.uv-cache`. uv 0.11.2, CPython 3.12.14 x64.
- Documented software pytest command PASS: 49 cases in 0.23 s. Real-SDK test
  explicitly excluded. Normal API demo PASS with documented states; empty API
  demo returned the expected missing-device message and exit 1. CLI help PASS.
- README Python block executed against the patched fixture and cleanup verified;
  three additional API-guide blocks also PASS using `tmp/cleanup-examples.py`.
  No clr, pythonnet or Thorlabs module loaded.
- Documented Ruff lint/format commands PASS (10 files). `uv build` could not reach
  PyPI for Hatchling in this environment; `uv build --offline` PASS from the existing
  cache, producing wheel and sdist. A fresh network install was not demonstrated.
- Clone URL matches the configured GitHub repository; cloning was not repeated.
  Real-hardware commands were checked against source and tests, not run on devices.

- Markdownlint-cli2 0.23.2 PASS for README; local Markdown/image/anchor checks
  PASS. The README rendered with its screenshot and one Mermaid diagram without
  broken images or browser errors; rendered top section and diagram visually
  reviewed. Sandbox browser launch initially returned EPERM; scoped automatic
  escalation permitted the local-only render. Browser closed normally.
- Exact Quick Start demo launch started the server at 127.0.0.1:8050. HTTP layout
  and CSS returned 200; real Dash callback requests exercised initial state,
  Discover, Connect, Open, Close and Close & disconnect with the documented identity
  and states, all PASS (`tmp/readme-demo-check.py`). After verified Disconnected,
  Ctrl+C stopped the terminal session (wrapper exit 1); this is not a physical
  shutdown validation. Existing screenshot assets were preserved.

TEST-018 PASS; REQ-017 and affected documentation REQ-009–012 revalidated.
The README task is COMPLETE. Physical REQ-003–008 remain BLOCKED. No hardware
operation is authorized or performed. No server or browser remains pending.

## E012

Kind / scope: same-day user follow-up, "more focus on using with real hardware".
TEST-018 revalidates revised REQ-017 and affected documentation REQ-009–012.
Expected: hardware setup/operation is the main README path, simulation optional;
retain accurate validation limits and the existing hardware hold.

Observed:

- README now leads with Windows/Kinesis installation and software checks, bench
  topology/checklist, discovery, actual serial selection, GUI connection,
  Close/Open/Close observations and shutdown. Troubleshooting prioritizes hardware.
  The simulated screenshot is explicitly labeled; no hardware imagery or bench
  configuration was invented. The simulator is an optional later section.
- Reviewed CLI flags, environment-variable use, serial selection and GUI workflow
  against source, hardware notes and the ordered procedure. Discovery remains
  gated by approval; the GUI follows first-use stages 2–5. No procedure stages,
  physical limits or acceptance criteria changed; no device access occurred.
- Revised Python example uses the selected serial and prompts for Closed/Open
  observations. It makes no timing guarantee and explicitly leaves approved
  dwell/thermal limits to the operator. `tmp/readme-hardware-example-check.py`
  executed the actual README block against the fixture: normal completion and
  KeyboardInterrupt at the second prompt both leave the fake Closed/released.
  No clr/pythonnet/Thorlabs modules loaded. This is software-only evidence.
- Markdownlint and internal Markdown/image/anchor checks PASS. Local browser render
  PASS: one Mermaid diagram, no missing images or browser errors; top section
  visually reviewed. Existing screenshot/diagram assets retained. Browser closed.
- E011's source tests, software demo, dependency and Ruff checks remain applicable;
  production code/configuration is unchanged. Hardware commands are documented and
  source-checked, not physically executed. No redundant full-suite run or build.

TEST-018 PASS for the revised guide. Documentation COMPLETE; physical REQ-003–008
remain BLOCKED under AWAITING_HUMAN_REVIEW. No hardware/server operation pending.

## E013

Kind / scope: user-requested review, fixes, commit and push, 2026-09-15.
TEST-019: prepublication review of the README change and REQ-009–012/017;
TEST-018 example/reference checks rerun. Hardware-review hold unchanged.

Reviewed all five changed documentation files against controller/CLI/GUI source,
packaging, existing guides and E011/E012. Corrected four first-use gaps: specify
Python 3.12 x64, show the eight-digit serial format beginning with 68, stop on
failed software checks, and explicitly Close & disconnect/stop the GUI before
running the Python example. Updated the stale publication checkpoint. No
production, test, configuration, dependency or hardware-procedure changes.

Validation:

- `uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`:
  49 PASS (0.18 s). No real-SDK test or device operation executed.
- Actual README Python block: normal completion and interruption after Open PASS
  against the fixture, ending Closed/released; no vendor modules loaded.
- Ruff lint/format PASS, all 10 Python files. Cached wheel/sdist build PASS.
- Fixed a pre-existing missing blank line before the E003 list. PowerShell
  command blocks parse; Markdown lint, internal references and
  `git diff --check` PASS. E012's diagram/screenshot rendering remains applicable;
  only small text clarifications were made during this review.
- Fetched origin; HEAD and origin/main both at b40ec49 with zero divergence before
  publication. Only the five reviewed documentation files are in scope.

TEST-019 PASS. The current user request explicitly authorizes commit/push to the
existing origin/main. Git history and remote refs identify publication; no force
push or hardware access is part of this action. Physical REQ-003–008 remain BLOCKED.

## E014

Kind / scope: user-reported GitHub diagram failure, 2026-09-15. TEST-020;
REQ-011/017. User observed "Unable to render rich display" and an undefined
`render` property. This invalidated the README's viewer-compatibility conclusion
from local Mermaid rendering; the exact GitHub/client runtime cause is unconfirmed.

Expected: the README diagram displays without a viewer-side Mermaid dependency,
with the same hardware topology and accessible editable source.

Changed README to embed `docs/assets/hardware-connections.png` and link
`hardware-connections.mmd`. The source matches the prior README Mermaid block
exactly. Exported with local Mermaid 11.17.2 and headless Edge at scale 2:
2080 x 692 px, 44,400 bytes, white background. Reviewed the labels and connections;
used opaque label backgrounds to avoid lines crossing text. Export helper is
`tmp/export-hardware-diagram.cjs`; the committed .mmd is the source of truth.

Validation: source equality and absence of a README Mermaid fence PASS; local
README render with JavaScript disabled PASS, both images load, no broken images
or browser errors. Markdown lint, local links and whitespace checks PASS. Test
helper: `tmp/readme-static-review.cjs`. No source/configuration change, SDK load,
USB access or hardware actuation; prior software tests remain applicable.

TEST-020 PASS for the static display path. The reported GitHub renderer was not
repaired or diagnosed; the README no longer invokes it. Other guides' Mermaid
blocks are outside this reported README issue. Existing authorization to fix,
commit and push this documentation covers publication to origin/main. Physical
acceptance remains BLOCKED under AWAITING_HUMAN_REVIEW.

Post-publication check: commit `5ef79a1` was pushed to origin/main. A fresh headless
browser opened that commit's GitHub README (HTTP 200); the visible diagram decoded
successfully at 2080 x 692 px. Screenshot: `tmp/github-readme-diagram.png`;
check: `tmp/check-published-readme.cjs`. GitHub display PASS for the static image.
The browser closed normally. This supplements the local script-free rendering check.

## E015

Kind / scope: compatibility review, 2026-10-20; REQ-018 (derived from user
request to review multiple shutter cube controllers with KEH3), TEST-021.
Expected: distinguish hardware hub suitability, serial selection, simultaneous
control, Ethernet support, and demonstrated versus inferred compatibility.

Observed from source:
- controller.py discover() enumerates type 68; connect() requires an explicit
  serial when discovery is ambiguous and creates a serial-addressed handle.
- Per-instance device, fault and lock state permit separate Python objects in
  principle. No duplicate-serial ownership registry exists; BuildDeviceList uses
  per-instance locking only. Cross-instance SDK behavior is not validated.
- gui.py create_app(controller) and CLI main() own one controller. GUI serial
  selection/discovery is disabled while a handle exists. No multi-shutter panel,
  coordinated commands or aggregate shutdown exists.
- _check_connection() requires USBConnected == Connected. No Ethernet discovery,
  address configuration or hub initialization is implemented. Ethernet support
  cannot be inferred from the hub offering Ethernet.
- tests/test_controller.py tests ambiguous enumeration/explicit selection, but
  tests/conftest.py returns the same FakeDevice for every requested serial.
  This does not demonstrate independent concurrent device operation.

Vendor references consulted:
https://www.thorlabs.us/newgrouppage9.cfm?objectgroup_ID=16708
Thorlabs describes KEH3/KEH6 as Ethernet and USB hubs for up to three/six cubes.
https://www.thorlabs.com/catalogpages/Obsolete/2025/SC10.pdf
Historical KSC101 product documentation describes multi-cube USB hub operation
using KCH301/KCH601; it is not direct KEH3 acceptance evidence. Search-indexed
vendor content was accessible; several direct current product fetches failed.

Conclusion: KEH3 USB operation with multiple KSC101s is plausible, conditional
on actual SDK enumeration and bench validation. Existing UI selects one device
at a time. Multiple independent objects/processes require distinct serial
ownership and validation; synchronized operation is not established. Ethernet
is unverified, not claimed incompatible at vendor level.

Validation attempt: uv run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py failed before collection due to default cache access.
Retry with --cache-dir tmp/uv-review-cache and --offline created .venv but
could not resolve cached ruff==0.16.6. No tests executed or passed in this review.
No SDK loading, USB/device communication or actuation. Production code unchanged.
TEST-021 PASS for documented source assessment only; physical REQ-003-008 remain
BLOCKED. Further hardware work requires the existing staged approval.

## D007

2026-10-20; REQ-019–023. The user explicitly authorized three KSC101 shutters
through KEH3 USB in one GUI and explicitly kept hardware access on hold.

Keep one driver per serial and add a small ShutterBank for fixed GUI slots,
shared discovery and aggregate cleanup. Retain the existing single-controller
API. Guard serial ownership inside this process, including partial initialization
and failed release; serialize shared SDK enumeration/creation. Do not create a
new transport, dependency, background worker or cross-process ownership service.

Use explicit selection in multi-device slots, independent status/faults and
individual controls. Bank shutdown is sequential, attempts all slots after
reported errors/interrupts, and preserves diagnostics. It cannot bound hung
vendor calls or prove physical closure. Global success text does not claim
closure for disconnected or previously faulted slots. Keep the operator's
single-process ownership responsibility and existing physical safeguards.

Interpret KEH3 USB as the intended hub carrying separately addressed KSC101
identities. Do not claim Ethernet, synchronization or physical USB compatibility
from source or simulated tests. Stage 9 of the hardware procedure prepares
combined acceptance without authorizing execution.

## E016

Kind / scope: three-shutter implementation and software validation, 2026-10-20;
REQ-001/002/009–012/015–017/019–022; TEST-022–025. Human source: PROJECT.md,
Three-shutter KEH3 USB follow-up. REQ-023 / TEST-026 and physical TEST-003–008
remain BLOCKED under the user's explicit hardware hold.

Expected results before testing:
- TEST-022: three distinct fake USB identities connect without output writes;
  each panel's commands/state/faults are independent, and refresh never replays
  old button counts. A lost retained identity remains visible until cleanup.
- TEST-023: duplicate serial claims, including concurrent initialization, are
  refused; failed release retains ownership. All-slot cleanup attempts later
  slots after errors/interrupts, aggregates slot/serial failures and re-raises
  interruption after remaining attempts. A failed closure never becomes verified
  merely because its handle was released or cleanup was retried.
- TEST-024: default GUI/CLI provides three passive slots; up to three distinct
  serial arguments preselect only. Invalid/duplicate/excess arguments fail before
  SDK/server access. CLI server failure/Ctrl+C still performs all-slot cleanup.
- TEST-025: locked environment, distributable module/CSS, software examples,
  lint/format, user guides and actual simulated browser layout remain usable.

Implemented: bank.py and package export, process-wide serial registry/shared SDK
locks, three-panel GUI and all-shutdown button, repeated CLI --serial, independent
fake device mapping, three-device demo, focused tests and updated documentation.
PROJECT.md records the authorized scope; STATE.md and outputs/REPORT.md describe
the current result. No dependency/lockfile changes.

Observed validation:
- `uv sync --locked`: PASS; 39 locked packages installed after approved cache/
  dependency access. Environment: Windows x64, CPython 3.12.7 (Anaconda build),
  Dash 4.4.1, Python.NET 3.1.0, pytest 9.1.1, Ruff 0.16.6.
- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
  --ignore=tests/test_sdk.py`: 98 PASS in 0.35 s on final source.
- `.venv\Scripts\python.exe -m ruff check src tests docs/examples`: PASS.
  `ruff format --check src tests docs/examples`: all 12 Python files formatted.
- `uv --cache-dir tmp/uv-review-cache pip check`: 39 packages compatible.
- `uv build`: final source distribution and wheel PASS. Extracted that wheel to
  tmp/wheel-validation and put it first on sys.path; verified imports came from
  the extracted package. Passive three-panel layout/HTTP 200 and packaged CSS
  smoke check PASS with SDK loading replaced by a forbidden-operation function.
  A fresh interpreter ran the full software suite from that package: 98 PASS
  in 0.34 s. No vendor-boundary test ran.
- `.venv\Scripts\python.exe docs/examples/simulated_demo.py --api`: PASS;
  discovered distinct fictional 68000001/2/3, read each identity, Open/Close,
  then all three Disconnected. The documented bank example also ran under the
  patched rig and ended with all three Closed/released.
- Actual local browser at http://127.0.0.1:8059 used only the patched simulator.
  Connected all three, opened Shutter 2: rendered Closed/Open/Closed. Global
  cleanup returned all three Disconnected and disabled Open/Close. Screenshot:
  docs/assets/gui-three-simulated.png, 452 x 2237 px, responsive stacked layout,
  all identities explicitly TEST DOUBLE, NOT HARDWARE. Browser tab and simulator
  were closed after cleanup; no server/device handle remains pending.
- Documentation Python blocks parse; local referenced paths resolve; Markdown
  fences and `git diff --check` PASS. Historical single-panel screenshots are
  labeled as such. The deferred hardware procedure includes three-cube mapping,
  independent operation/reconnect and combined cleanup/shared USB cases.

Validation harness issues, resolved without changing product behavior: the
initial CLI/GUI tests still assumed a single object/callback signature and were
adapted to the three-slot interface. The full tests exposed missing-selection
auto-connect; bank selection now explicitly rejects None. A review caught a
false global closure claim for no-handle cleanup; text and regression tests now
preserve unverified state. An extraction using tempfile.mkdtemp hit Windows
permissions; a normal workspace directory worked. The first wheel test harness
left its forbidden SDK patch installed, causing the missing-SDK-message test to
fail; a fresh interpreter passed all 98 packaged tests. Prior cache-permission
and missing-offline-dependency failures from E015 were resolved by locked sync.

Reproducibility hashes/configuration: records/three-shutter-validation.json.
TEST-022–025 PASS within software-only scope. No real Kinesis assembly loading,
USB enumeration, device connection/actuation, calibration or firmware writes.
Actual KEH3 USB and physical criteria remain BLOCKED; follow B001 in STATE.md
before any future bench work. No commit or push was requested or performed.

## D008

2026-10-20; REQ-024, user-directed rename/module consolidation and pruning.
`KCubeShutter` replaces the public `KSC101Controller` name with no compatibility
alias. Move ShutterBank into controller.py and remove bank.py; keep its class and
behavior. Update current imports/guides/examples, preserving historical evidence.

Use the atomic driver serial registry as the sole ownership authority. Remove
the redundant bank scan that read another device's status to reject duplicate
assignment; it could perform unnecessary SDK I/O and latch an unrelated fault.
Keep slot/selection validation, driver and bank locks, retained ownership after
failed release, per-device safeguards/faults and all-slot cleanup/interrupt logic.
Reuse existing fake handles, simplify CLI padding and share repeated readout
markup. Do not add operation dispatch abstractions or widen hardware authority.

## E017

Kind / scope: KCubeShutter rename and simplification, 2026-10-20. REQ-024 /
TEST-027 and affected software TEST-022–025; supersedes E016 for changed source.
Physical TEST-003–008/026 remain BLOCKED under the unchanged hardware hold.

Expected: public imports use KCubeShutter; ShutterBank shares controller.py;
bank.py and the old class alias are absent. Retain independent controls, passive
startup, atomic serial ownership, latched faults and all-shutter cleanup despite
failures/interrupts. Reduce redundant implementation without altering GUI layout.

Changed: all current source/tests/demo and API examples use KCubeShutter; package
exports both driver and bank from controller.py. Removed bank module/imports and
its duplicate ownership scan. Reused rig.devices in the independent-device test
fixture; factored repeated GUI readouts without changing output structure;
shortened CLI serial padding. Current documentation/source maps/checkpoint/report
were reconciled. Historical E records/manifests retain their original names.

Measured against the working-tree implementation at the start of this request:
production Python 5 -> 4 modules and 839 -> 802 lines (37 lines removed). Driver
and bank are separate classes in one module. Dependencies/lockfile, CSS, controls,
timeouts, hardware command sequence and supported CLI flags are unchanged.

Validation / observed results:
- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
  --ignore=tests/test_sdk.py`: 99 PASS in 0.43 s. New regression proves duplicate
  assignment does not read/fault the current owner's status; existing race,
  retained-claim, independent-state and error/interrupt cleanup cases still pass.
- Ruff check PASS; format --check PASS, 11 Python files. Dependency compatibility:
  39 packages compatible. `git diff --check` PASS.
- `uv build`: source distribution/wheel PASS. Checked both omit bank.py. Extracted
  wheel to tmp/wheel-refactor-validation; verified imports resolve there, both
  KCubeShutter/ShutterBank come from controller.py, and no old class export exists.
  Passive three-panel HTTP/layout/CSS smoke PASS with the SDK loader forbidden.
  Full software suite against packaged code: 99 PASS in 0.42 s; one benign Dash
  assertion-rewrite warning because the smoke check imported it before pytest.
- Compared both default three-panel and injected one-panel /_dash-layout JSON
  against E016's extracted package in separate Python processes: identical.
  The healthy GUI screenshot therefore remains representative; no new browser
  or hardware session was needed for this structural cleanup.
- Simulated demo --api PASS for three distinct fictional serials: identity,
  Open/Close and all Disconnected after cleanup. Renamed README single-device,
  API single-device and API bank examples executed under the patched rig; all
  fake shutters ended Closed/released. Documentation Python blocks parse,
  local links resolve and Markdown fences balance.
- Static search: no old class name, bank module imports or bank.py references in
  active src/tests/docs/README. Historical records and PROJECT's quoted human
  rename request intentionally retain the old name. A final rebuild captures
  updated report/evidence references; package source is checked against final src.

Environment remains Windows x64 / CPython 3.12.7 with unchanged uv.lock versions.
TEST-027 PASS in software-only scope. No real SDK loading, USB/device discovery,
connection, actuation or firmware write; no server/handle pending. No commit/push.
Final source/configuration/artifact hashes: records/controller-cleanup-validation.json.

## E018

Kind / scope: current manufacturer-documentation verification, 2026-10-20;
REQ-009/010/018/023, TEST-028. User supplied the official product-page URL:
https://www.thorlabs.com/k-cube-r-solenoid-controller?tabName=Overview

Expected: determine whether the current KSC101 product documentation explicitly
supports the requested three-controller KEH3 USB topology and whether it changes
our software-interface assumptions. Do not infer physical acceptance or authority.

Observed: direct web fetch failed; the actual page loaded in the in-app browser
as 'Thorlabs · K-Cube Solenoid Controller'. Overview / Power Supply Options and
Compatible Power Supplies explicitly list KEH3 for up to three K-/T-Cubes and
KEH6 for up to six. They describe a USB 2.0 hub circuit, power/communications,
single power connection, and combined cube load not exceeding 4.6 A. The KSC101
is described as a 15 V solenoid controller suited to SH05R(/M), with interlock/key
safeguards. Overview/product details explicitly advertise USB control using
Kinesis or XA, superseding the reference notes' prior lack of a KSC101 XA claim.

Conclusion: manufacturer documentation now directly confirms KSC101/KEH3 USB
compatibility as a supported topology, strengthening E015's indirect evidence.
It does not establish this bench's supply/load, installed SDK/driver behavior,
three-serial enumeration/mapping, physical state/feedback or closure. Ethernet
and XA backends remain unimplemented/unvalidated here; keep the established
Kinesis API and safeguards. No source or configuration change is required by
this reference alone.

Updated docs/INTERFACE.md, docs/hardware.md, STATE.md and outputs/REPORT.md with
these distinctions and the current source. TEST-028 PASS for documentation
verification only. Physical TEST-003–008/026 and REQ-023 remain BLOCKED. Prior
99-test software evidence E017 remains applicable to unchanged code. No new
software tests/build were needed for reference-only text updates. Local links,
Markdown fences and whitespace checked. No SDK, USB/device operations, actuation
or authority change; hardware access remains on hold.

## D009

2026-10-20; REQ-025. User requested ShutterBank -> ShutterHub, simpler
construction and removal of unnecessary controller scaffolding. Rename without
an alias. Give the hub one normal construction path from serial preselection;
retain a keyword-only controllers injection path for existing integrations/tests.
Centralize count/duplicate checks and padding; do not add factories, backend
classes, generic command wrappers, or timing/configuration passthrough layers.

Controller review retained the small lazy SDK boundary, per-instance/shared
locks, strong serial-owner claims (including the claimed serial), fault snapshots,
verified command waits and cleanup/interrupt logic. Each enforces real behavior:
removing these would weaken ownership, safeguards, recovery or all-shutter cleanup.
Remove duplicate CLI setup and the unused single-controller demo/count wrapper.
Consolidate slot validation but keep missing-selection rejection and retained
fault/handle behavior. No hardware authority or physical acceptance change.

## E019

Kind / scope: ShutterHub rename/construction/controller review, 2026-10-20;
REQ-025 / TEST-029 and affected software TEST-022–025/027. Human source:
PROJECT.md, ShutterHub construction and controller review. Supersedes E017 for
changed code. E018's vendor topology evidence and the hardware hold remain valid.

Expected: imports/exports use ShutterHub without an old alias; constructor
preselects up to three distinct serials, pads remaining slots without SDK access,
and rejects invalid/excess/duplicate configuration. Explicit controller injection
must preserve one to three distinct objects and not silently ignore hub options.
Retain independent controls, atomic ownership and failure/interrupt cleanup.

Changed: hub class/current callers/docs/test file renamed; ShutterHub(serials,
kinesis_dir=...) owns construction, validation and preselection. CLI now creates
one hub in one call; its duplicate validation and controller-list/padding code are
removed. Injection uses controllers= explicitly. Removed the unused simulated
single-controller wrapper/count option and collapsed slot validation. Updated
README/API/source-map/checkpoint/report and hub-message callback ID. No dependency,
CSS, backend or hardware-command changes. Production modules remain four;
production Python is 802 -> 806 lines, with real configuration validation moved
into the hub rather than omitted. Unused demo support was removed separately.

Observed validation:
- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
  --ignore=tests/test_sdk.py`: 107 PASS in 0.37 s. Constructor tests exercise
  zero/one/three serial selections, passivity/configuration propagation, invalid/
  duplicate/excess serials and conflicting injected-controller options. Existing
  race/ownership, status/fault, GUI and all-slot shutdown/interrupt checks pass.
- Ruff check PASS and format --check PASS, 11 Python files. Dependency check:
  39 installed packages compatible. `git diff --check` PASS.
- `uv build`: wheel and source distribution PASS. Extracted wheel to
  tmp/wheel-hub-validation; verified every packaged Python file matches final src
  bytes, expected imports resolve there, ShutterHub exports come from controller.py,
  the old class export is absent and no bank.py is present. Passive serial
  preselection, three-panel HTTP/layout and packaged CSS smoke PASS with SDK
  loading forbidden. Fresh-interpreter software suite on packaged code:
  107 PASS in 0.34 s.
- Default three-panel and injected one-panel /_dash-layout JSON match the previous
  extracted package after normalizing bank-message -> hub-message. Visible layout
  is unchanged; E016's healthy simulated screenshot remains representative.
- Simulated demo --api PASS: distinct fictional serials 68000001/2/3, identity,
  independent Open/Close and all Disconnected after cleanup. README single-device,
  API single-device and serial-configured hub examples executed only under the
  patched rig; all three fakes ended Closed/released.
- Documentation: seven Python blocks parse, local referenced paths exist and
  Markdown fences balance. Static scan of active src/tests/docs/README finds no
  old class/demo wrapper references; historical project quotes/evidence are kept.

TEST-029 PASS in software-only scope. Physical TEST-003–008/026 and REQ-023 remain
BLOCKED. Environment unchanged: Windows x64, CPython 3.12.7, existing uv.lock.
No real SDK loading, USB discovery, device connection/actuation, firmware writes,
new browser session, commit or push; no server/device handle pending. B001 remains
the exact bench-resumption dependency.

## D010

2026-10-20; REQ-026. User requested gui.py construction simplification while
preserving three independent controls and keeping hardware on hold. Build each
panel with one plain function, compute slot suffixes once and reuse message/
readout elements. Use Dash's named event/selection grouping instead of slicing
raw callback arguments, and its documented zero counter defaults instead of
repeating them in every component.

Keep one serialized callback, explicit output bindings and action branches,
per-slot transient messages/selections, hub locking, safeguard/fault gating,
retained identity and all-shutter cleanup. Replacing these with a widget framework,
generic command dispatcher or independently scheduled callbacks would add
unneeded machinery or change behavior. Preserve injected single/two-slot views.

## E020

Kind / scope: GUI construction cleanup, 2026-10-20; REQ-026 / TEST-030 and
affected software TEST-022–025/027/029. Human source: PROJECT.md, GUI construction
cleanup. Supersedes E019 for changed GUI code; controller/CLI/CSS/dependencies and
E018's manufacturer evidence remain unchanged. Physical requirements stay BLOCKED.

Expected: reduce construction/scaffolding without changing three independent
serial/connection/state/error/safeguard controls, passive startup, event routing,
message persistence, fault/identity handling or complete best-effort shutdown.
Keep supported injected views and the existing rendered layout/accessibility.

Changed only production gui.py: pure panel/message/readout helpers, one suffix
list for layout/bindings, declarative panel list and named callback event/selection
groups. Removed nested ID builders/card append loop, repeated explicit zero
click/interval defaults, raw callback argument slicing and a status-label helper
recreated inside the rendering loop. Kept one lock-protected callback and explicit
per-slot commands/output fields. gui.py 257 -> 237 lines; production Python total
806 -> 786 lines. No new module, framework, dependency or controller abstraction.

Observed validation:
- `.venv\Scripts\python.exe -m pytest tests/test_gui.py tests/test_cli.py
  -q -p no:cacheprovider`: 26 PASS in 0.30 s.
- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
  --ignore=tests/test_sdk.py`: 107 PASS in 0.34 s. Existing cases cover independent
  states and controls, duplicate ownership, mixed faults, passive startup,
  retained lost-device identity, non-replayed refresh and all-slot error cleanup.
- Before editing, saved default/single/two-slot/preselected /_dash-layout JSON
  snapshots. Final layouts compare equal after normalizing omitted n_clicks=0
  and n_intervals=0. Installed Dash 4.4.1 Button.py/Interval.py explicitly document
  these zero defaults. All labels, IDs, disabled states, CSS/accessibility props
  and panel ordering remain equal. E016's healthy simulated image remains useful;
  no new browser/physical visual test is claimed.
- Ruff lint PASS; format --check PASS, 11 Python files. Dependency check: 39
  packages compatible. `git diff --check` PASS.
- `uv build`: source distribution and wheel PASS. Extracted wheel to
  tmp/wheel-gui-validation, verified packaged Python bytes match final source,
  and imports resolve there. Passive three-panel HTTP/layout/packaged CSS smoke
  PASS with real SDK loading forbidden. Fresh-interpreter software tests against
  packaged code: 107 PASS in 0.50 s.
- Current docs/README/checkpoint/report updated; corrected the stale architecture
  sentence about the removed single-controller demo helper. Documentation links,
  Python syntax and Markdown fences checked. Prior examples/controller tests
  continue to apply to unchanged API and hardware-command paths.

TEST-030 PASS in software-only scope. Environment unchanged: Windows x64,
CPython 3.12.7, Dash 4.4.1, existing uv.lock. Hardware hold remains in force:
no real SDK loading, USB/device discovery, connection/actuation, calibration or
firmware writes. No server/device handle pending; no commit or push. Physical
TEST-003–008/026 and REQ-023 remain BLOCKED under B001 in STATE.md.

## E021

2026-10-20; TTL capability/configuration clarification, TEST-031 source/manual
review, relevant to REQ-002/010. User asked whether KCubeShutter supports IO1/IO2
TTL and how configuration is set. No implementation change was requested.

Source inspection: the class exposes no per-port direction/polarity, TTL-state or
trigger-arming API. Constructor options are serial, SDK directory, feedback
timeout (5 s) and polling interval (250 ms). Connect makes no explicit trigger
configuration/output writes and status reads operating mode. Open prepares via
Close; Close selects Inactive then Manual. Default shutdown also closes/selects
Manual and does not restore a prior triggered mode. Thus the manual GUI cannot
be used as a TTL arming interface while preserving external-trigger operation.

Thorlabs KSC101 manual HA0368T Rev D, section 3.4.1, describes bidirectional
TRIG1/TRIG2, default input/output respectively, 5 V logic, selectable active
polarity, Triggered mode and a separate priming requirement. It warns that an
open input is LOW and active-low operation can open when primed. This is
manufacturer documentation, not observed bench configuration. Reference:
https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf
The document is legacy APT material; exact current Kinesis TTL setters have not
been validated. Do not borrow trigger APIs/electrical limits from other cube models.

TEST-031 PASS for capability assessment only. Actual stored port settings are
unknown under the hardware hold. TTL support would require an explicit future
configuration/arm/disarm API and appropriate validation. No code, SDK/device
operation, actuation or authority change; E020 software evidence remains valid.


## E022

2026-10-20; Ethernet SDK assessment, REQ-027 / TEST-032. Human request in
PROJECT.md: verify official Kinesis/XA support for three KSC101s through KEH3
Ethernet and identify code changes, with hardware access on hold.

Expected: distinguish vendor support, exact inspected APIs, inference, unresolved
SDK details and physical evidence; identify current source assumptions without
implementing or exercising a hardware backend.

Observed: DOC-103012 Rev E, January 22, 2026, sections 4.2/4.3/4.3.1 documents
KEH3 Ethernet routing and Kinesis connection of attached cubes. Section 6 notes
identical cube enumeration can depend on firmware. Official product page supports
three bays and Ethernet. The manual was read through the web text extractor;
direct PDF download/screenshot returned access errors, so the bay-port figure
was not visually verified. No exact per-bay mapping is asserted by this review.
Source: https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351

Official Motion_Control_Examples revision
3ef959523e2be48d57704af964f7a2c24547b722 includes a BBD Ethernet example and API
CHM. Downloaded as data; hh.exe -decompile extracted help only. SDK help confirms
ScanEthernetRange(startIPAddress,endIPAddress,portNo,openTimeout),
CreateManualDeviceEntry(comSpec), DeleteManualDeviceEntry(comSpec),
GetManualDeviceEntries and GetTransportInfo(serialNo). The BBD example does not
prove KSC101 bay registration grammar. The KSC101 Python example supplies the
serial-based device factory/connect path. No real SDK assemblies were loaded.
CHM SHA-256: dfa52c72df9c0c9859bd29a9cfb9efe7a29e33787f9b4ddec0e720704de29b7d.

Official XA PyPI 1.9.1.28941 wheel and source archive inspected without import,
installation or native DLL execution. Wheel SHA-256 verified against PyPI:
48f0405cd094689ca790691b3fc174ae4f9271b9e97c786f1e984e606830fa2f.
Its changelog adds KSC101 in 1.7.0 (2026-09-18); product/factory, solenoid feature
methods and device/transport/parent discovery fields are present. DLL string
inspection finds TLMC_DiscoverEthernetDeviceInfo; historical changelog documents
Ethernet fixes. These establish components, not this topology's runtime behavior.
SystemManager has transport-aware open_device_as but no dedicated Ethernet scan
method in the inspected Python wrapper. Native discovery signature/startup settings
schema remain unresolved; no invented binding/transport literal is proposed.
Static source also shows Device.parent_device_id returning _device_id; assessment
warns against relying on it for hub mapping.

Current production review: discover() uses BuildDeviceList/GetDeviceList(68),
connect() creates a serial-based KCubeSolenoid; _check_connection() requires
USBConnected, and no Ethernet endpoint configuration/registration exists.
ShutterHub already provides three instances and failure-tolerant cleanup.
Assessment documents transport-aware discovery/health, ownership across transport
aliases, shared registration lifetime, CLI/status propagation and software/bench
test needs; XA would require a larger driver/lifecycle/status mapping change.

Result: TEST-032 PASS for research/source assessment, not SDK execution or physical
acceptance. Kinesis is the documented incremental route; XA is a supported-device
candidate with its exact Python KEH3 discovery contract still unresolved. Full
sources, limitations and proposed changes: docs/ethernet-assessment.md. Production
source, uv.lock and dependencies unchanged; prior E020 tests remain applicable.
No USB/network hardware scan, device connection, actuation, configuration/firmware
write, commit or push. No SDK/device handle or helper process remains pending.

## D011

2026-10-20; REQ-028–030 / TTL follow-up in PROJECT.md. Use one immutable normalized
TriggerConfig, the existing KCubeShutter driver and one serialized GUI callback;
retain separate per-panel draft settings and device readback. No generic trigger
backend, compatibility fallback, new dependency or automatic arming. Apply requires
Closed/Inactive/Manual; Arm uses device settings and checks safeguards/input.

Disarm/Close must verify Closed/Inactive before selecting Manual. Basis: Active
in Manual requests opening, while a primed Triggered/Active cube can be closed
because its input is inactive. Changing mode before acknowledged Inactive could
therefore request opening. If the command/feedback fails, skip Manual, report
closure/disarming as unverified and still attempt release and remaining slots.
This tightens the prior sequence without claiming physical proof; the model
explicitly reproduces Manual/Active opening. No prior trigger mode is restored.

## E023

2026-10-20; TRIG1/TRIG2 implementation, REQ-028–030 / TEST-033. Expected: verified
KSC101-specific configuration/readback contract, explicit independent arming and
disarming in driver/GUI, passive startup, draft separation, faults/refusals,
safe cleanup sequencing and all-slot continuation, reproducible package/docs.
Authority: user's local implementation/software-validation request in PROJECT.md;
hardware hold unchanged. Physical REQ-031 / TEST-034 remains BLOCKED.

Static official contract: extracted the previously downloaded Thorlabs Kinesis
.NET API CHM (official Motion_Control_Examples revision
3ef959523e2be48d57704af964f7a2c24547b722). Read KCube.SolenoidCLI KCubeSolenoid
`a07553.html`, TriggerConfigSettings `a07565.html` and OperatingModes
`a07549_a4682b683a86f17b04ee9fe588f7f913f.html`. Verified request/get/set trigger
configuration methods, four settings properties, Disabled/TrigIN_GPI/TrigOUT_GPO,
TriggerHigh/TriggerLow and Triggered mode. No assemblies were loaded. This is
static API evidence, not validation of the installed SDK. Links and exact mapping:
docs/INTERFACE.md#ttl-interface. CHM SHA-256 remains
dfa52c72df9c0c9859bd29a9cfb9efe7a29e33787f9b4ddec0e720704de29b7d.

Implementation: public TriggerConfig and per-status trigger_config/ttl_armed;
get_trigger_config/configure_triggers/arm_triggers/disarm_triggers. Both settings
and arming require matching reported feedback. Unknown enum values, communication
errors and setting mismatch invalidate TTL status. Arm requires key/interlock and
an input; failed/interrupting arm attempts closure. Close requires Inactive/Closed
before Manual (D011), then verifies Closed/Inactive/Manual. Default release, hub
and CLI retain every-slot error/interrupt cleanup and serial ownership semantics.
No explicit settings-persist/EEPROM/firmware command. A communication-only explicit
disconnect(close_shutter=False) retains its existing output/mode semantics.

GUI: both ports' mode/polarity drafts, independent readback and Apply/Read/Arm/
Disarm buttons in every panel. Read replaces drafts; ordinary refresh preserves
them and cannot replay a write. Arm uses device readback, never unapplied drafts.
Apply requires Closed/Inactive/Manual; Manual Open refuses Triggered. Faulted
readback is Unknown, Apply/Arm disabled, cleanup available for retained handles.

Observed final validation, Windows x64 / CPython 3.12.7 / Dash 4.4.1 /
Python.NET 3.1.0, unchanged dependencies/uv.lock:

- `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py`:
  **187 PASS in 0.50 s**. Baseline 107 plus 80 TTL regressions. Includes all 36
  mode/polarity combinations, malformed values, both input polarities on TRIG2,
  modeled active-low opening, Armed/Closed distinction, existing armed connect
  without writes, idempotent arm, faults/safeguards/no-input refusals, setting
  mismatch, failed arming/interrupts, no Manual after unacknowledged Inactive,
  retained-handle cleanup and continuation across all three shutters.
- HTTP GUI tests verify independent Apply/readback/arming, draft preservation,
  Read draft replacement, invalid browser values, fault gating and global cleanup.
  Background browser additionally connected three fake identities, armed only
  Shutter 2 (Armed/Closed with LOW input and high polarity), verified gating,
  Disarm and all-slot shutdown. Native JPEG detail saved as
  docs/assets/gui-ttl-simulated.jpg, 1265 x 712 px. Existing pre-TTL captures are
  labeled historical. Browser layout is unchanged by the final driver-only
  Inactive-feedback gate. Simulator/listener on 8058 and temporary tab closed.
- Ruff check and format --check PASS (12 Python files); `uv ... pip check`: 39
  compatible packages. `git diff --check` PASS. Three-device simulated_demo --api
  PASS for manual/TTL/configuration/arming/disarming, all three finally disconnected.
- `uv build` PASS for sdist and wheel. A restricted-cache build first failed on
  network resolution; normal approved build succeeded. Extracted final wheel to
  tmp/wheel-ttl-final; verified packaged Python bytes equal final source and import
  resolves from that tree. Fresh-interpreter packaged tests: **187 PASS in 0.49 s**.
  Final wheel SHA-256:
  ae296ea4d82b42097160f61b8bccadbc069c349460b8e017b0112745affe35c3.
- Updated README, API/GUI/interface/architecture docs, simulated example, STATE
  and report. Prepared stage 10 TTL acceptance as unexecuted TEST-034. Manifest
  records source/artifact hashes and scope: records/ttl-validation.json.

TEST-033 PASS for software scope only. Readback waits one polling interval after
requests but remains vendor-maintained data, without certified age or pin voltage.
Three panel refresh adds at least 750 ms at default polling plus SDK time. The
manual's open-input LOW/active-low warning is documented; no actual wiring,
electrical behavior, priming, persistence, closure or timing has been demonstrated.
Shutdown remains sequential/best effort, with no bound on hung vendor calls.
No real SDK import, USB/network device scan, connection, actuation, calibration,
firmware write, commit or push. E022 Ethernet research remains intact; production
transport is USB. AWAITING_HUMAN_REVIEW / B001 and physical blockers remain in force.

## D012

2026-10-20; consistency review, REQ-032 / TEST-035. Separate operating feedback
needed to close/disarm from optional TTL settings readback. A configuration read
or unknown configuration enum must not prevent verified Inactive/Manual cleanup.
Open/Close/Disarm command snapshots can omit trigger_config; get_status/connect/Arm
still request full settings. Preserve the original fault until successful cleanup.

Release collects failures/interruption from StopPolling and Disconnect separately,
attempts both, then updates handle/ownership and re-raises any interruption. Apply
the same fault-before-propagation rule to failed connection and Open recovery.
Verify returned identity at connect and sample operating feedback after the
settings delay. Keep the existing driver/hub and one serialized GUI callback;
no new framework or hardware authority. Historical validation artifacts remain
unchanged; E024 supplies current LF-normalized source/package evidence.

## E024

2026-10-20; user requested consistency review, pruning/fixes, commit and push.
REQ-032 / TEST-035; full software regressions also revalidate current three-shutter
and TTL requirements. Publication is REQ-033 / TEST-036, recorded separately.
Expected: reproduce supported defects, fix their causes, preserve independent
controls/ownership/shutdown and hardware hold, align docs and validate packaging.

Review findings and fixes:

1. StopPolling interruption skipped Disconnect; release interruption could also
   bypass fault/ownership bookkeeping. Release now attempts both steps, preserves
   errors/interruptions and keeps the claim only when the handle remains retained.
   Failed connect cleanup records a fault even when interrupted.
2. TTL settings reads were required by every closure wait. A settings failure or
   unknown enum prevented the Manual step despite otherwise valid Closed/Inactive.
   Operating-only waits now allow verified disarm without settings readback.
   Full status/GUI still reports the latched settings fault until disconnect/reconnect.
3. Status sampled key/interlock/state before the TTL polling delay, returning
   values already superseded during that wait. It now samples operating feedback
   after the settings request/read. This reduces an avoidable stale interval;
   it does not establish atomic feedback or physical/cache freshness.
4. Connect accepted returned identity without comparing it to the selected serial.
   Identity mismatch now fails/release before any output write. Non-string serials
   produce actionable validation errors before SDK access.
5. An interrupt during failed Open recovery escaped before recording a fault.
   Open/Arm recovery records faults before propagation; an interrupted failed
   Open cannot subsequently appear healthy.

Pruning: build enum maps once per configuration call, consolidate separate release
handlers and remove duplicate recovery-message construction. GUI construction and
its single serialized callback stay unchanged. Corrected status/API semantics,
Close's two confirmation stages versus Open/Arm's three, identity/shutdown docs,
historical screenshot labels and publication intent. Ignore only pytest-generated
temporary cache names; no recursive cleanup/deletion. Normalize current source to
the repository's LF policy so committed/package hashes are reproducible.

Observed validation (no real SDK/device access):

- Re-ran 14 focused new regressions against the E023 extracted wheel at
  tmp/wheel-ttl-final: **14 FAIL**, 197 deselected. Failures reproduce identity,
  pre-delay feedback, interrupted Open recovery, release interrupts in normal and
  failed-connect paths, and disarm blocked by settings reads/unknown enums.
- Final source command `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider
  --ignore=tests/test_sdk.py`: **211 PASS in 0.60 s**, including 24 added cases.
  Includes interruption in one armed slot while remaining slots still close/release.
- Ruff check and format --check PASS, 12 Python files. uv dependency check: 39
  compatible packages; dependencies/uv.lock unchanged. Simulated API completes
  manual/configuration/Arm/Disarm on all three fake identities, then disconnects all.
- `uv build` PASS. Wheel and sdist Python bytes match final source; CSS present;
  no tmp, venv or pytest-cache artifacts. Final wheel extracted at
  tmp/wheel-review-validation; explicit import path verified. Fresh-interpreter
  packaged software tests: **211 PASS in 0.50 s**. Wheel SHA-256:
  9d152e4c50074f6cde54e42c89d22211fc7db4d035f64ccddabdb4f3bd15eccd.
- GUI/CSS bytes, normalized to LF, match the E023 package; no new browser test is
  claimed. HTTP/layout regressions pass. Current source/artifact/environment
  evidence: records/review-validation.json. Earlier JSON manifests describe their
  historical workspace/artifacts and must not be used as current-source hashes.
- Origin fetched successfully; before commit HEAD and origin/main both ca47dd2,
  ahead/behind 0/0. User explicitly authorizes normal commit/push. No history rewrite.

TEST-035 PASS (software only). Physical tests remain BLOCKED. No SDK assembly
loaded, USB/network device scan, device connection/actuation, calibration,
electrical measurement or firmware change. No simulator/device handle pending.
Source/package/doc review is complete; normal commit/push and remote verification
are the remaining authorized publication steps.
