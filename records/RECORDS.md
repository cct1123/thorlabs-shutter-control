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
