# Engineering evidence and decisions

The complete original E001-E078/D history and raw artifacts are preserved in
[the verified archive](archive/README.md). This index supersedes repeated progress
logs; original bytes/checksums remain available. Requirements live in STATE.md.

| Evidence | Durable conclusion |
| --- | --- |
| E050 / TEST-060 | Official KSC101 update1.0.6->1.0.7 completed; USB identity alias CONTROLLER_A repaired without a software alias |
| E068 / TEST-077; E070 / TEST-079 | Four-state matrix did not establish jack continuity; clear SDK bit remains unknown, key report is separate |
| E072 / TEST-081 | User removed dedicated Stage7/count criterion; removal is not a physical PASS |
| E075 / TEST-084 | Five SDK Open2s/Close2s cycles passed readback; user confirmed physical sequence |
| D018 / E076; E077 / TEST-085/086 | Explicit object/serial session interlock evidence; production Stage5 shutdown and Stage6 GUI/Ctrl+C cleanup readback passed |
| E078 / TEST-087 | Redesigned GUI actual browser/USB Open with2.015s visible hold, Close, passive trigger read, keyboard section, reconnect and global cleanup;440 then-current software tests passed |

Physical calibration/timing, three-pair, electrical TTL and physical fault tests
remain unexecuted. Historical Ethernet hub-only discovery predates cube firmware
update; no post-update cube qualification is claimed. See
[consolidated observations](hardware-validation.json).

## D019 / E079 / TEST-088 - Holistic cleanup and consistency review

User explicitly authorizes pruning logs/development junk, holistic fixes, commit
and push. Preserved136 original evidence/checkpoint/source/acquisition files in
hardware-2026-10-20.zip, verified every member SHA256 and ZIP integrity, and wrote
an external whole-archive checksum. Retained current bench summary, formal
incomplete bench record and actual GUI screenshot separately. Old prompt history,
unused generated screenshots and temporary SDK extraction/installer/build/cache
copies are cleanup candidates; installed Kinesis/.venv/live GUI remain untouched.

Review found stale untested/hold claims, pre-/post-firmware Ethernet conflation,
obsolete UI examples, mixed text encoding and incompatible tutorial readiness.
Current docs were reconciled. Tutorials03-05 now accept explicit confirmation for
selected serials and reject another target before SDK access. A supported cleanup
bug was fixed: identity mismatch plus failed release could previously cause output
cleanup on an unverified retained target. ExitStack now registers passive release
before Connect and Close only after successful identity/feedback verification;
callbacks continue through errors with normal Python exception chaining. New
regressions cover these cases.449 source software tests PASS; no driver/GUI/CLI
change or actual hardware operation in this cleanup. Previous bench evidence is
not promoted to three-pair/electrical/calibration acceptance.

Final validation:449 source tests and449 tests against the freshly built,
extracted wheel PASS. Wheel contains9 entries including CSS, with no records,
tests, docs or vendor binaries.100 verified files/directories pruned; .venv and
installed vendor runtime preserved.17 active Markdown files/67 local targets PASS;
Ruff/format/diff checks PASS. All136 archive member hashes and whole ZIP checksum
verified; secret-pattern scan has no matches. Active reviewed text normalized LF.
Build/test outputs were removed after qualification; no verified scratch/cache
folder remains. records/cleanup-validation.json records commands, hashes, removal
allowlist and limits. origin/main fetched equal to pre-review HEAD0833e84.
Implementation commit5445fec4a3fb6d3a9a39c63d74509d5bbc1419a3 pushed normally to
origin/main; git ls-remote returned the same hash. Publication metadata checkpoint
follows separately. No source change after validation, no new hardware operation.
Cleanup/publication criterion REQ-053 PASS; broader physical criteria unchanged.

## D020 / E080 / TEST-089 - Simplified hardware testing reference

The user requested an experience summary and substantial simplification of the
original test stages. The original process over-separated discovery/connection,
status/motion and GUI/cleanup, repeated unchanged readiness questions and reads,
and treated an incomplete comprehensive bench form as an ordinary-use gate.
The bench results E050/E053/E068/E070/E075/E077/E078 support a shorter vertical
path without inventing missing physical measurements.

Decision: replace the old ordered stages with three commissioning checks:
connect/read; one Close/Open/approved hold/Close; production GUI and cleanup.
Reuse the functional cycle when performed in the GUI. Routine qualified-bench
operation needs only connect/read, Closed baseline, the intended operation and
Close/release; passive-only work needs no motion. No repeated approval, arbitrary
cycle count or complete old form is required. Existing authority/safeguards apply;
intervene only for a genuine unresolved dependency. Installation, firmware and
open-state shutdown regression are change-driven maintenance/qualification work.

Separate Ethernet, three-device, TTL, physical loss/recovery and calibrated timing
from routine USB use. Their unmet physical criteria stay visible and unchanged.
Old helper APIs and their stricter contracts are retained as optional diagnostic
tools; historical stage numbers/results remain historical. No test result is
promoted, raw record rewritten, source changed or hardware accessed. Updated
PROJECT/STATE/report and entry-point guides agree with the new reference.

TEST-089 / REQ-054 PASS (reference only): checked17 tracked Markdown files and74
local targets/anchors; exactly three commissioning stages; retained REQ-005/007,
006,023,031 gaps; passive example positional serial/parser and passive-release
contract match, AST parses offline. git diff --check PASS. Exactly8 documentation
files changed; executable files, raw JSON, archive and checksums unchanged. The
449-test source/wheel results remain prior E079 evidence, not a rerun in this task.
No hardware operation. The new reference supersedes REQ-036's ordered workflow,
while preserving the separate physical requirements and historical test results.

## D021 / E081 / E082 - Autonomous disconnected-port TTL qualification

User authorizes hardware TTL tests without intervention and reports both IO1/IO2
unconnected. Official KSC101 HA0368T RevD documents open-circuit input LOW, with
active-high inactive and active-low able to open when primed. Use that discriminating
matrix on each port alone, within1-second added windows; no external edge/voltage
qualification or interlock bypass. Restore original settings Closed and release.
Current GUI feedback verifies selected alias CONTROLLER_A, Closed/manual/inactive, key enabled,
interlock unknown/operator verified; two unused slots disconnected. Original
settings input/high and output/high. GUI owner identified as process12380/child63976;
release through normal callback before a standalone SDK owner. Detailed results follow.

E081 / TEST-090 software PASS: implemented an explicit opt-in single-controller
runner, with no hardware on import/help, serial-scoped readiness, requested added
window (0,2]s, no-input Arm rejection and independent per-port tests. On any
failure, Disarm/Close, restore original trigger settings while Closed and release;
all registered cleanup callbacks attempted. No automatic command replay. Initial
immediate-position expectation was improved to a bounded read window so transient
first feedback need not be final.8 new software tests cover the matrix, failure
restoration/no retry, initial stale feedback and invalid windows.457 full-suite
software tests PASS with tests/test_sdk.py excluded. Full scoped Ruff and helper
format checks PASS; --help ran offline. Driver and GUI source unchanged.

E082 / TEST-091 actual runs on alias CONTROLLER_A: both disabled and unloaded-output high/low
configuration readback PASS; no-input Arm refusal PASS; each isolated input/high
stayed Closed PASS. Each isolated input/low armed Triggered/Active with matching
settings but stayed reported Closed, bits8192: expected Open FAIL. IO1 was checked
with a bounded1s read window to distinguish initial stale feedback, then IO2 was
isolated in a separate run; neither satisfied the expectation. No blind retries
or polarity/bit remapping to force PASS. Separate Manual positive control Open,
1s added hold, Close PASS (8193 ->8192), without altering trigger settings.

Every run verified final Closed/Inactive/Manual, restored input/high + output/high
and released. GUI server left running; final refresh all3 slots disconnected.
[TTL summary](ttl-summary.json) contains commands, source/raw hashes and links to
the original failure, settled IO1, isolated IO2, Manual control and owner handoff.
Both active-low position checks remain FAIL, cause unknown; external pulse/voltage,
independent physical/timing and three-pair acceptance remain UNTESTED. No-cable
scope complete; further electrical diagnosis needs an approved source/measurement
fixture. No human intervention or outstanding request for this run.

Final reference/evidence checks PASS:17 Markdown files/81 local targets and anchors;
all active JSON parsed;5 raw evidence SHA256 values and2 implementation hashes
match the TTL summary. git diff --check PASS. Driver/GUI and archive unchanged.

## D022 / E083 / TEST-092 - Illustrated documentation and privacy

User explicitly requests README/docs/screenshots/device pictures with real serials,
private data and credentials removed. Updated the README and GUI/hardware guides
with two full-page captures of the unconfigured production GUI and an unchanged,
attributed Thorlabs KSC101/SH05R product image. No image editing, synthetic connected
state or hardware access. Screenshot capture used a separate empty instance.

Preserved70 original project/evidence files, including the136-member raw archive
and old connected screenshot, in ignored inputs/private/documentation-originals/.
Verified original binary copies before removing them from shareable paths. Real
identities, actual LAN details, MAC/account paths and repository owner references
were removed from current shareable text/assets. Alias and environment-variable
examples preserve identity semantics without embedding a bench identity. Public
JSON is labelled sanitized; hashes describe derivatives, with private originals
retained. Old archive history was not rewritten and may still contain prior data.

Driver change is limited to a documentation-address example in an error string;
Ethernet tests use illustrative addresses. No native-call/control logic changed.
Copyable API cleanup examples now Close only after a verified connection. Existing
TTL active-low position FAIL and physical evidence limits remain unchanged.
TEST-092 / REQ-056 PASS within current shareable-file scope:457 software tests,
full scoped Ruff, diff check,18 Markdown files/93 local links/anchors and6 compiled
Python examples. Both screenshots visually inspected (1264x957 and1264x1360 JPEG)
and checked for EXIF/XMP/comment metadata; manufacturer WebP checked for EXIF/XMP.
Known real identifiers/account/network details and credential patterns absent from
shareable files. Private backup is Git-ignored. Newly built wheel has9 entries,
no private records/vendor binaries and no blocked identifiers/credentials; temporary
build removed after inspection. Sanitized raw/source/asset hashes verified.
records/privacy-validation.json records scope and checks. Temporary empty GUI
instance stopped; no actual hardware access or publication. Prior Git history
remains outside this privacy cleanup and may contain previously committed data.

## D023 / E084 / TEST-093 - Review, consistency fixes and publication preparation

User authorizes review/fix/prune/commit/push of the accumulated work. Fetch confirms
origin/main equals starting HEAD. Review found ambiguous historical/current report
claims and old GUI layout dimensions beside new screenshot metadata. Replaced
repeated progress prose with a current report; separated layout provenance and
timestamped the ownership handoff. Removed only redundant sanitized GUI widget
payload, retaining identity/state/normal-release evidence and private originals.

TTL helper preflight previously accepted bool duration/ports and float ports via
Python equality/coercion. Invalid direct-call arguments could reach controller
access before rejection. Now reject them before device access; add regressions.
Fictional numeric wrong-prefix/mismatched identities preserve realistic validation
coverage without restoring real bench IDs. Valid-input/native command sequence
unchanged; historical TTL low-position FAIL remains unresolved. No new bench run.
Current derivative/source hashes refreshed; E083 validation remains historical.
Final validation/publication pending. No private original/.venv/SDK/hardware owner
pruned, no force push or Git-history rewrite planned.

During E084 review the user requested removal of the README privacy section.
Renamed its combined heading to Development and removed the privacy guidance/link
there; underlying exclusions and scoped evidence remain unchanged.

## D024 / E085 / TEST-094 - KEH6 USB path and configurable slot count

During review/publish work the user requests KEH6 compatibility and any number of
shutters. Thorlabs KEH6 overview specifies six bays and USB hub linking. USB SDK
selection is per KSC101 identity, independent of hub model; KEH6 USB compatibility
is expected, not bench-qualified. KEH6 Ethernet mapping remains unverified and
is not generalized from KEH3. Full physical multi-pair acceptance remains open.

Removed the three-slot software cap. ShutterHub(slots=N)/CLI --slots N accept a
positive integer. Default count remains at least three and grows to fit explicit
serials; injected controllers define any nonzero count. Preserve serial uniqueness,
passive startup, first/last slot separation and all-slot best-effort cleanup. GUI
wraps larger counts across rows; refresh/shutdown remain sequential, not scalable
without latency or physical limits. Six/nine fake-device GUI tests cover independent
last-slot control, refresh without replay and cleanup reaching later slots after
an early failure. CLI/API tests cover default, explicit and inferred sizes and
invalid counts before SDK/server access. No new hardware operation.

Initial scale-test expectation was corrected to preserve deliberate preselection
on Discover; blank selections remain blank in multiple panels. Existing product
behavior was correct. Targeted hub/CLI/GUI regressions:83 PASS. Full validation and
updated default-GUI captures pending. E086 will record publication after validation.

E085 also removes legacy bench-form hardcoding of KEH3/three pairs. The form
checks factual completeness and unique mappings, not a fixed hub model or count;
physical qualification is still separate. Three/six/nine fictional-pair cases
cover this; missing hub information remains incomplete.

Final E084/E085 validation PASS:487 source and487 tests with production imports
from the extracted current wheel. Full Ruff/format/diff checks PASS;18 Markdown
files/92 local links/anchors and6 Python snippets verified. Current shareable
files/wheel have no known real identifiers or credential-pattern matches; JPEG
metadata checked and current captures visually reviewed.70 private-original hashes
and all136 archived payload hashes verified; ZIP contains137 entries including
its manifest. Clarified earlier ambiguous archive-count metadata. Removed22
verified temporary capture/build files, preserved private originals/.venv/SDK.
records/review-validation.json contains final commands/counts/hashes and scope.
Reviewed allowlist commit and normal push pending E086; no new hardware test.

## E086 / TEST-095 - Reviewed commit and verified publication

Staged only the explicit49-file reviewed allowlist, excluding private/runtime/
build paths; cached diff check PASS. Implementation a6b9e68b6da5613f2b044ebb78ea941abea14b3c
committed and pushed normally to origin/main. git ls-remote returned that exact
hash; checkout clean immediately afterward. REQ-057 publication PASS.487 source/
487 wheel regressions and E084/E085 evidence apply to this implementation.
README privacy section removed; configurable-count feature included; physical
TTL/KEH6/Ethernet limits retained. No force push, history rewrite or new hardware
operation. This metadata checkpoint follows separately; final Git refs record it.

## D025 / E087 / TEST-096 - Follow-up consistency review

REQ-059: user again requests review/fix/prune/commit/push. Clean baseline
c9c45c21cf92cdd111686557831180c863070144 matched origin/main after fetch.
The new --slots 1 path reused the direct-controller convenience branch, allowing
Connect with no dropdown selection to enumerate and connect a sole device or
fall back to a preselected identity. Larger ShutterHub panels reject that missing
selection before SDK access. Two software reproductions failed before the fix.
Now every hub panel routes through hub.connect; direct KCubeShutter GUI behavior
remains compatible. Discover may still visibly select a sole device in one panel.
No native command, output guard, visual layout or hardware state was changed.

489 source and 489 extracted-wheel cases PASS, real SDK test excluded. Ruff/format
PASS across 36 Python files; 9-entry wheel matches production bytes. Corrected
three/six-panel screenshot description and stale publication language. Condensed
repeated report history; retain meaningful bench evidence and ignored originals.
E084/E085 remain historical, with prior provenance/wheel hashes labelled accordingly.
Additional documentation/hash/privacy validation and publication follow below.

Final TEST-096 documentation/integrity PASS: 18 Markdown files, 91 local links/
anchors, 6 parsed Python snippets; current JSON/asset/TTL hashes verified. Current
files and wheel have no known bench identifiers/credential-prefix matches. All 70
private-original and 136 archive payload SHA256 values match. Removed only the
verified wheel/extracted-package temporary files; .venv/SDK/private originals and
hardware owner preserved. Commit/push pending E088.

## E088 / TEST-097 - Follow-up publication

Reviewed and staged the explicit 10-file allowlist; cached diff check PASS.
Implementation 25bbe8e2cffefa3190a795a5a4e807b3f6cd684f committed and pushed
normally to origin/main. git ls-remote returned the exact implementation hash;
checkout clean afterward. REQ-059 PASS: E087 software/documentation/integrity
validation plus this publication. This metadata checkpoint records the verified
result; final Git refs identify metadata commits. No hardware operation,
force push, history rewrite or private/runtime file publication.

## D026 / E089 / TEST-098 - Illustrated supervisor reference

REQ-060: user requests a Notion HTML notebook for supervisor review and future
reference, with figures/graphs/block diagrams. Created a private workspace draft
(no parent/destination supplied) and self-contained outputs/supervisor-notebook.html.
The renderer reads pinned revision ca0d150, keeping this session reference stable
across later source changes. Nine sections distinguish software tests, actual
controller feedback and the user's independent five-cycle observation; unresolved
TTL/Ethernet/KEH6/multi-pair/timing/fault limits remain explicit.

Seven figures: physical topology, software boundaries, five-cycle schematic,
three host shutdown call durations (not blade timing), TTL expectation/feedback
matrix, original unconfigured GUI screenshot, and the simplified workflow.
TEST-098 PASS: unique/internal anchors, six SVG XML figures, embedded original
screenshot, no remote dependencies, known identifier/credential-prefix checks,
deterministic pinned-source rebuild and renderer Ruff/format. Desktop overview,
architecture and TTL figure visually reviewed. No fresh application/hardware tests
were needed for this documentation artifact; cited489/489 tests remain E087.

Notion page created and fetched successfully; HTML is a native embed. Downloading
the uploaded attachment matched its complete HTML string exactly. Private page:
https://app.notion.com/p/4005bb9cf275811c9d71f1a17d984397
records/notebook-validation.json contains file hash, counts and readback details.
No supervisor was messaged; no firmware, hardware access or sharing expansion.

## D027 / E090 / TEST-099 - Tutorial presentation without hashes

User requests removing hashes and making the notebook a tutorial. Revised the
existing Notion page/HTML rather than creating another page. Removed visible
commit IDs, checksum columns, audit IDs/delivery tables and supervisor sign-off
prompts. Added copyable passive GUI/status examples and clear routine-use advice;
retained all seven figures and unresolved TTL/Ethernet/multi-pair/timing scope.
Internal integrity records are separate from the reader-facing tutorial.

TEST-099 PASS: visible HTML/page prose contains no hashes/audit IDs; unique anchors,
internal links, SVG XML and unchanged embedded GUI image verified; renderer Ruff/
format PASS. Notion title/native content/HTML embed fetched after update, and a
fresh attachment download exactly matched the revised HTML. Existing document
permissions retained. E089 is historical presentation; no new hardware operation.

## D028 / E091 / TEST-100 - Direct project configuration and simple launch

REQ-062; user requests simple uv launch, no parsing and no environment parameters.
Added package config.py: KINESIS_DIR, SERIAL_NUMBERS, SLOTS, PORT and empty
VERIFIED_INTERLOCK_SERIALS. Launcher uses those settings without argparse;
`uv run shutter-control` starts the passive localhost GUI. Discover remains a GUI
action; SDK discovery helper/API remain available. SDK fallback uses config.py,
not KINESIS_DIR/ProgramFiles environment variables; explicit API kinesis_dir still
wins. Loader's internal PATH handling for native DLL dependencies is unchanged.
Normal interlock/protection verification remains selected-serial/session evidence;
configuration comments and setup require rechecking each run and clearing after use.
No actual serials, device access, writes, actuation or remote notebook changes.
Existing hardware diagnostics and the pinned prior notebook are separate artifacts.

Expected: configured counts/serials render without SDK calls; invalid identity,
duplicate/count/port settings fail before startup; explicit verification and
all-slot cleanup retain existing behavior; environment cannot choose SDK location.
Observed: `uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py` -> 489 passed. Full src/tests/docs examples/hardware
helpers Ruff check --no-cache and format --check -> PASS. SDK path test covers
project fallback despite environment override and explicit API path precedence.
Initial uv cache and pytest temp ACL errors were tooling issues; local uv cache
and a filesystem-free SDK path test allowed complete software validation.
No physical acceptance result is added or promoted by this change.

Additional package check: offline wheel rebuild could not run because hatchling
is absent both from .venv and the local uv cache. No package PASS is claimed for
this revision; build-system.requires already declares hatchling correctly.

## E092 / TEST-101 - GUI action latency diagnosis (REQ-063)

Expected before tracing: at default 250 ms polling, each _read_status call waits
one poll, including when trigger configuration is omitted. Open performs initial
status, two Close verification reads, Open verification, then GUI N-controller
reread. Close performs two verification reads, then GUI N-controller reread.
Expected programmed sleep: Open (4+N)*0.25 s; Close (2+N)*0.25 s;
refresh N*0.25 s. Open Active write at 0.75 s, Close Inactive write at 0 s.

Method: existing tests/conftest.py rig.__wrapped__(pytest.MonkeyPatch) and
FakeDevice plus tests/test_gui.py invoke exercised actual Dash HTTP callbacks
without a listener or hardware. One, three and six independent fake controllers
were connected Closed/Inactive/Manual. Existing virtual clock accumulated waits;
SDK record hooks captured write timestamps and per-device method counts.
Results in records/gui-latency-analysis.json: N=1/3/6 Open 1.25/1.75/2.50 s;
Close 0.75/1.25/2.00 s; refresh 0.25/0.75/1.50 s. Expected write timestamps match.
PASS for software timing model, first feedback read succeeds at each stage.
No USB/native SDK/network/mechanical timing measured, no source behavior changed.

Sources: controller.py _read_status/_read_trigger_config/get_status,
_wait_for_state/open_shutter/close_shutter; gui.py update dispatch ignores action
return values then synchronously reads all controllers under hub.lock;
__main__.py uses threaded=False. Routine 1 s interval refreshes use the same
callback/lock, so an in-flight refresh may delay click execution. Six connected
controllers already spend 1.5 s per refresh in programmed waits alone.

Optimization priorities: reuse completed action feedback and cached unaffected
panels; separate operating reads from TTL settings refresh; assess skipping
redundant Closed/Manual setup only with validated preconditions. Preserve the
Inactive/Closed confirmation before switching from Triggered to Manual; do not
blindly remove sleeps whose purpose is to allow requested feedback to arrive.
Real per-phase timings are needed to separate remaining SDK/transport latency.

## D029 / E093 / TEST-102 - Faster manual GUI path with safety verification

REQ-064; implement E092 improvements within software scope. Driver remembers only
successfully read snapshots for explicit display-only get_status(refresh=False).
Fault/disconnection takes precedence. Default get_status() remains full fresh
feedback; include_triggers=False retains requests/wait/health validation for
operating feedback, omitting TTL settings. GUI actions render verified snapshots
without another target/other-panel I/O pass. Routine refresh reads all panels'
operating feedback. TTL settings display is labelled last read, never used as
Arm authority; Connect/Read/Apply/Arm provide fresh TTL observations. Successful
Apply updates the verified snapshot, avoiding an old configuration overwriting it.

Open checks fresh operating/key/interlock/communication feedback. If already
Closed/Inactive/Manual, skip the redundant Close write/two verification waits;
otherwise preserve full Close preparation and recheck key/interlock afterward.
Close always sends Inactive and waits for Closed/Inactive; skip mode write/second
wait only when the same feedback already confirms Manual. Triggered/timed modes
still require Inactive acknowledgment before selecting Manual and verifying again.
All readiness, fault latch, failed-Open Inactive recovery, timeout and all-slot
cleanup semantics remain. Poll interval/feedback waits and serial locking unchanged.

Expected before verification: healthy first-read-success Manual Open=0.50s,
Close=0.25s at 250ms/poll, regardless of unrelated connected count. Open emits
Active at0.25s; Close Inactive at0s. Open requests=6, Close=3, no TTL request or
unrelated-panel I/O per action. Refresh remains N*0.25s with3*N request methods.
Observed via actual Dash HTTP callbacks and existing virtual-clock/FakeDevice
fixture, N=1/3/6: all predictions PASS. records/gui-latency-improvement.json
contains timestamps, request counts and per-device calls; TEST-101 baseline is
retained. These are SDK method counts, not measured USB transactions or latency.

Command: uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py ->500 passed. Full src/tests/docs/examples/docs/hardware_tests
Ruff check --no-cache and format --check PASS. Eleven added regression cases cover
independent panel counts, no TTL refresh requests, cached-TTL Arm rejection after
actual settings change, retained fault after successful Close, stale display
cannot authorize Open, missing Inactive acknowledgment in Manual/Triggered and
key change during timed preparation. Existing triggered-closure, identity, key,
interlock, timeout, failure/interrupt and all-slot cleanup regressions pass.
Two old assertions updated for explicit TTL read faults and omission of redundant
Manual writes, preserving their fault/cleanup checks. Initial new-test setup was
corrected to request one actual slot rather than the default minimum three.

No hardware access, server restart, firmware change, commit or push. No physical
speed/safety qualification is claimed for the changed path. Prior REQ-004/008
bench PASS is retained as historical; affected current physical paths UNTESTED.
Refresh remains serial and can queue clicks; native calls can still block.

## D030 / E094 / TEST-103 - Controller read responsibilities and duplicate checks

REQ-065. Split recently added snapshot selectors into get_status() full fresh,
get_operating_status() fresh operating/safeguards, get_trigger_config() TTL only,
and get_cached_status() display-only. One _refresh_status handles fresh read
faults; existing _read_status owns request/wait/parse and pre/post health checks.
Original no-argument get_status and other established public contracts remain;
temporary include_triggers/refresh public flags removed and all project code/docs
migrated. Private include_triggers selects request content inside the shared reader.
GUI's fast no-reread action path remains unchanged in behavior.

Serial setter now owns syntax/retarget validation; connect translates its error
without validating again. CommsStatus is sampled once per health check. Baseline
predicate centralized in ShutterStatus.is_closed_manual. Open only rechecks
readiness after actual Close preparation, not on the same previously checked
snapshot. TTL-only reads no longer request operating feedback, and successful
readback updates TTL display history. TTL Apply reads fresh operating baseline,
writes, then reads new settings; it no longer requests old TTL configuration.
Arm skips redundant Close only with fresh Closed/Inactive/Manual evidence and
removes an extra sleep before _read_status's own wait. After real mode preparation
it rechecks key/interlock before enabling output. Health checks across a wait,
Inactive acknowledgment before Manual and final output feedback are intentionally
retained because they validate different states, not the same observation.

Expected before trace: at250ms/poll from independently connected healthy
Closed/Inactive/Manual with first feedback success, get_status4 requests/.25s,
get_operating_status3/.25s, get_trigger_config1/.25s, get_cached_status0/0s,
configure_triggers4/.50s, arm_triggers8/.50s, open_shutter6/.50s,
close_shutter3/.25s. Actual existing fake fixture/virtual-clock trace matches all
predictions: records/controller-api-validation.json PASS. Request-method counts
are not physical USB transactions; no hardware/native SDK or blade timing tested.

uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py ->508 passed. Full src/tests/docs/examples/docs/hardware_tests
Ruff check --no-cache and format --check PASS. Eight added cases cover each read's
request scope, correction of old invalid TTL config without an unrelated old read,
Arm command/wait count, key change during preparation, and connection loss during
TTL read wait. Existing500 safety/lifecycle/GUI/count/ownership/fault cases pass.
Affected current physical acceptance remains UNTESTED; no new actuation, firmware,
server restart, commit or push. Historical evidence and preexisting work preserved.

## D031 / E095 / TEST-104 - Simple shutter commands with shared failure handling

REQ-066. Removed copied exception/recovery blocks from Open, Close and Arm;
_command context manager owns fault latching, optional recovery, ordinary error
translation and interrupt propagation. Open still recovers with an immediate
Inactive command; Arm recovers with verified Close/Disarm; Close does not recurse
on failure. Both primary and failed recovery remain in the latched fault, and
recovery interrupts retain fault notes and propagate. The same boundary now owns
identity/TTL read/configuration errors; their interrupts also latch faults.
Open precondition refusals remain outside execution/recovery, preserving no-write
behavior. Close still always requests Inactive before feedback or mode changes.
No status waits, identity/ownership guards, readiness checks or tests removed.
GUI validated internal Open/Close commands share a single dispatch branch.

After formatting, public Open44->31 lines, Close21->13, Arm56->39; public command
bodies121->83, plus21 shared handler lines gives104 (before121). The handler is
also reused by three other device operations replacing their copied exception
blocks. Counts include docstrings/interior blanks; no line packing/minification.
records/command-simplification-validation.json captures this accounting.

Expected: existing command order, refusal, timeout, fault/recovery/interrupt,
identity/ownership/all-slot cleanup and GUI behavior remain; Manual Open0.50s with
6 request methods, Close0.25s/3, Arm0.50s/8 (250ms polling, initial Closed/Inactive/
Manual, first feedback succeeds). Actual isolated fake-SDK/virtual-clock trace
matches all three predictions. PASS is software-only; no USB or blade measurement.

uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py ->511 passed. Full src/tests/docs/examples/docs/hardware_tests
Ruff check --no-cache and format --check PASS. All508 prior regressions retained;
three added actual Open failure cases cover primary/recovery ordinary failures,
primary interrupt with failed recovery, and both interrupted. Existing recovery
interrupt and fault masking cases also pass. Current physical paths remain
UNTESTED; historical bench evidence is not promoted. No hardware operation,
firmware change, server restart, commit/push or unrelated cleanup.

## E096 / TEST-105 - Simple shutter API notebook

REQ-067. docs/examples/open_close.ipynb has five cells: introduction, editable
settings/imports, procedure, one direct API cycle with finally cleanup, expected
results/limits. SERIAL is empty, hold1.0s (operator must choose approved duration),
VERIFIED_INTERLOCK false; SDK folder uses project config.py. No argument parser,
environment parameters, added dependencies, output data or actual identifiers.
Link added to existing examples guide. Existing runtime source is unchanged.

Expected: setup passive, successful cycle reports Closed/Open/Closed and releases;
failed Open and Ctrl+C during hold attempt Close/release; wrong identity releases
without output; invalid hold fails before device access. Actual notebook source
compiled and executed with existing conftest rig/FakeDevice and virtual sleep:
all five cases PASS. All end disconnected; success/error/interrupt cycles Closed;
wrong identity and invalid hold perform no output/mode/enable writes.
records/notebook-api-validation.json preserves scoped results. JSON schema fields,
unique cell IDs and cleared execution counts/outputs inspected. No hardware calls,
Jupyter install/kernel changes, server restart, commit/push or physical timing
claim. Full511 runtime regressions remain E095; no runtime source changed here.

## E097 / TEST-106 - Current Open/Close latency and source drift

Current controller differs from the prior validated optimized working source.
Open calls full get_status, unconditional Close (two verification waits), then
Enable/Active and Open verification. Close sends Inactive, verifies, writes Manual
and verifies again. Expected programmed sleeps at250ms: Open4*.25=1.00s;
Close2*.25=.50s. Existing fake fixture/virtual clock confirms both; record:
records/current-api-latency.json. No hardware access; no controller edits.

The earlier get_operating_status/get_cached_status/shared handler and fast baseline
branches are absent in live controller, while GUI still references the newer APIs.
Cause of source replacement unknown. E093-E096 trace/test results cannot validate
this changed source; no current integrated GUI PASS is claimed. Preserve current
work and reconcile intended version before applying a source fix.

## E098 / TEST-107 - Skip redundant Close from verified manual baseline

REQ-069. Focused open_shutter change: retain fresh get_status and existing health,
Triggered-mode and key/interlock refusals. Skip Close only for exact reported
Closed/Inactive/Manual. Otherwise retain Close and recheck readiness on returned
post-preparation feedback. Final Open verification and failed-Open Inactive
recovery untouched; Close source/other controller APIs not restored or changed.

Expected at250ms, first-read success: Manual Closed baseline Open0.50s instead of
E0971.00s, no Inactive/Manual writes; Close remains0.50s in current source. Actual
fake-SDK/virtual-clock trace matches: only Enable/Active for Open. Added four
regression cases verify the baseline and each differing position/state/mode takes
full Inactive/Manual preparation.14 focused Open tests PASS, including existing
key/interlock/unknown-feedback, auto preparation and recovery tests. Scoped Ruff
check --no-cache and format --check PASS. No hardware operation/physical timing.

Full command uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py --tb=no: before462passed/49failed; after467passed/48failed.
Same prior failures remain except post-preparation safeguard test now passes;
no new failing names. Prior snapshot/GUI/method drift is outside this focused
request and remains visible, not hidden by deleting/changing old tests. Focused
command: same uv/pytest options tests/test_controller.py -k
'open and not display_snapshot and not command_handler' ->14passed/98deselected.
records/conditional-open-validation.json captures scoped results. Broader suite
and current physical paths remain unvalidated. No commit/push or server restart.

## D032 / E099 / TEST-108 - Controller/GUI reconciliation and green suite

REQ-070 explicitly authorizes restoring the API contracts missing at E097/E098.
The GUI already used get_operating_status/get_cached_status and is_closed_manual;
restore these in the controller rather than rewriting the GUI or adding shims.
Cache only successfully completed reads; explicit cache getter performs no I/O and
fault/disconnection takes precedence. Open/Arm prerequisites always use fresh
feedback, never display cache. Default get_status remains full fresh readback.

TTL Read requests only settings and checks health before/after its wait. Apply
reads only fresh operating baseline, then writes and verifies new settings;
verified TTL settings update the display snapshot. Arm reuses fresh Manual Closed
baseline and removes stacked wait, retaining preparation/safeguard recheck for
other modes and post-command state/config/readiness confirmation. Close still
always commands Inactive and verifies Closed/Inactive; if the same feedback is
already Manual, no redundant mode write/second wait. Timed/Triggered transitions
still verify Inactive first and Manual afterward. Conditional Open kept, now with
operating-only preflight. Shared command failure handler retains fault latching,
primary/recovery error details and interrupt propagation; serial setter owns
validation. No test removed. Notebook formatting fixed without execution/output.

Initial reconciliation resolved46 of48 prior failures; last2 expected a redundant
SetManual even when current feedback was already Manual. Updated only those
expectations to match intended Close optimization, strengthened with an Enable
hook that requires actual fake state Closed/Inactive/Manual before output.
Existing refusal/unknown-state, timeout, failed Inactive, failed Open/recovery,
key/interlock changes, interrupt, ownership and all-slot cleanup cases unchanged.

Final command: uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider
--ignore=tests/test_sdk.py ->515passed/0failed in2.34s (previous467pass/48fail).
Full src/tests/docs/examples/docs/hardware_tests Ruff check --no-cache and format
--check ->PASS;38 files formatted including notebook. SDK-only test excluded;
no vendor SDK/device calls executed. Nine actual Dash HTTP callback/virtual-clock
traces at1/3/6 fake connected devices confirm Open0.50s/6 request methods and
Close0.25s/3 with no unrelated-device I/O; refresh remains0.25*N s and3*N requests.
Expected values defined before trace; all PASS. Notebook source compiles, outputs
stay empty, and success/failed-Open/hold-interrupt/wrong-identity/invalid-hold
scenarios all PASS with release/appropriate no-output cleanup.
records/controller-gui-validation.json is the current scoped evidence artifact.

E097/E098 failing-suite limitations are resolved. E093-E096 software requirements
revalidated on current source; historical artifacts retained without rewriting.
Current physical Open/Close/GUI paths remain UNTESTED; software timing is not USB,
native SDK, browser-network or blade timing. No hardware operation, server restart,
firmware change, new dependencies, commit or push.

## E100 / TEST-109 - Updated API notebook with independent call durations

REQ-071. Updated existing docs/examples/open_close.ipynb, not a duplicate. SERIAL
uses first config.SERIAL_NUMBERS value or empty editable fallback. SDK default,
explicit per-session verification and one-cycle finally cleanup retained.
perf_counter brackets only the actual Open/Close calls; added hold, Connect,
initial Close and cleanup are outside reported durations. Explanatory text covers
conditional Close preparation, fresh safeguards, timing scope and kernel restart
after source changes. Outputs/counts cleared. Examples guide aligned.

Expected: passive settings; successful cycle prints Open/Close state/duration and
releases; failed Open and hold interrupt close/release; wrong identity never
commands outputs; invalid hold fails before device access. Notebook code compiled
and executed with existing fake SDK and virtual sleep/perf_counter. All five cases
PASS; success prints exactly0.500s Open and0.250s Close, excluding1s added hold.
JSON cell IDs/counts/outputs checked; notebook Ruff check --no-cache and format
--check PASS. records/notebook-update-validation.json records software scope.
No runtime source/dependency/kernel changes, hardware access, server restart or
actual physical/API duration measurements. E099515 runtime tests remain current;
no unnecessary runtime-suite rerun for this notebook-only change.

## E101 / TEST-110 - Notebook serial type correction

REQ-072. Source inspection found an integer list assigned to the annotated
string tuple in local config. Corrected to a tuple of quoted strings without
changing device selection. Controller error now explicitly names the string
requirement; notebook explains quoted literals and config reload by kernel restart.
Expected: configured serial constructs without SDK access; integers remain rejected.
Observed: 134 controller/launcher tests PASS; passive construction and notebook
compilation PASS; scoped Ruff check/format PASS. Pytest emitted a cache-directory
permission warning; tests completed. No device access or physical validation.

## E102 / TEST-111 - String and integer serial inputs

REQ-073, user request: accept str or int. Shared normalization accepts either
valid eight-digit 68-prefixed identity and returns str; None retains optional
selection semantics. Reject booleans, floats, malformed strings and wrong prefixes.
Normalization precedes owned-target and confirmation comparisons; hub preselection
normalizes before duplicate detection. Launcher confirmation matches normalized
selected identities. Updated annotations and notebook/API guidance.
Expected: both forms select/confirm/connect the same fake device, same-identity
reassignment preserves confirmation, no incidental output commands, mixed-form
hub duplicates rejected, mixed-form launcher confirmation remains passive.
Observed: new parameterized cases and full suite PASS: 520 passed, 1 skipped.
Command: .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
Ruff check --no-cache and format --check on src, tests and notebook PASS.
Existing ownership, wrong-identity and confirmation-scope regressions also pass.
No hardware/SDK connection, server restart, commit or push. Historical E101
string-only acceptance superseded by explicit user input contract.

## E103 / TEST-112 - Undefined operating feedback at connection

REQ-074. Human-reported notebook trace: Connect fails on state='0', mode='manual'.
Source: fixed two-poll startup delay then one status read, despite asynchronous
RequestOperatingState/cache-getter API. Installed authoritative header:
C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.KCube.Solenoid.h,
SC_GetOperatingState documentation (lines 699-709): Active=1, Inactive=2. Zero
is undefined. A startup reply delay is plausible but not physically established.

Added private pending-feedback exception only for zero operating state. Connect
retries read-only status requests until valid feedback or feedback deadline;
no arbitrary unknown values are accepted, no Inactive inference or output write.
Each read waits one polling interval; timeout may overshoot by that read duration.
Settings initialization and initial polling wait remain separate. Operational
reads retain immediate fail-closed behavior; existing release/error paths retained.

Expected: delayed zero-to-Inactive feedback connects without output; persistent
zero times out and releases; unknown during Open prevents all output commands.
New delayed-reply test initially exhausted the fixture's 0.5s timeout before
its third reply; configured that scenario's timeout to 1s (three 250ms reads).
Separate timeout test retains short fixture deadline and verifies elapsed bound.
Observed final command: .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
522 passed, 1 skipped. Ruff check --no-cache src tests and format --check PASS.
No hardware access, kernel restart, device command, commit or push. Physical
resolution pending rerun on the affected bench; persistent zero requires further
protocol/SDK diagnosis rather than treating this mitigation as proven root cause.

## D033 / E104 / TEST-113 - Direct writes and explicit reads

REQ-075. Explicit user request: substantially prune KCubeShutter; setters send
commands without asking/returning status, getters request specific feedback.
This supersedes old driver prerequisite, preparation, acknowledgment and automatic
recovery behavior. Public action names retained; setters now return None.

Removed _wait_for_state, zero-feedback startup exception/retry, conditional Close
preparation, Open/Arm readiness reads, trigger write/readback matching loops and
implicit output recovery. Open writes Enable/Manual/Active; Close writes
Inactive/Manual; Arm writes Enable/Triggered/Active. Local argument, handle/fault,
identity/serial ownership, command-error/interrupt reporting and all-slot release
remain. Snapshots invalidate on writes. Specific getters request position,
operation, mode or status bits; aggregate/TTL/display reads remain available.
Connect checks identity and communication without requesting operating feedback.
Zero/undefined operating values are unknown, never Inactive.

GUI, notebook, five tutorials, optional hardware helpers and simulation now use
explicit reads where they consume feedback. GUI and controlled lessons own their
readiness checks; the driver no longer supplies those implicitly. Shutdown sends
Close then releases without establishing feedback closure. No claim that a
successful setter proves actuation or that a mode transition was acknowledged.

Expected: setter calls contain only their specified vendor writes and return
None; forbidden SDK getter/request/sleep hooks remain untouched. Specific getters
request only chosen feedback, with no outputs. Unknown-zero startup connects
without retry/sleep; separate read reports unknown. Writes invalidate display
history; readback mismatch can be observed explicitly without changing setter
semantics. SDK errors/interrupts latch fault and remain visible; release attempted.

Observed: 495 passed, 1 skipped, zero failures/errors. 11 parameterized setter
cases forbid all SDK getters/requests, _check_connection and sleep. Individual
read contract, command sequence/repetition, separate trigger mismatch, direct
write error/interrupt and existing ownership/cleanup/GUI regressions PASS.
Five notebook cases PASS: success (0.000s programmed write times), failed Open,
hold interrupt, wrong identity, invalid hold. Three-device simulated_demo --api
PASS with all handles released. Ruff check --no-cache and format --check PASS
on src/tests/docs/examples/docs/hardware_tests (39 files). git diff --check PASS.
Commands and superseded test names/reasons: records/get-set-validation.json.
Tests for implicit workflows were replaced deliberately; the previous test count
and timing/feedback guarantees are historical, not current validation.

No hardware access, GUI restart, firmware/wiring change, commit or push. Current
physical Connect, manual/TTL actuation, GUI and shutdown paths need revalidation;
existing hardware/physical qualification gaps remain. Restart the notebook kernel
before using this API. Software request complete; no physical completion claimed.

## E105 / TEST-114 - Organize and rename the Open/Close tutorial

REQ-076. User requests running/modifying the notebook, tutorial sections and a
new filename. Inspected current saved notebook: separate live control cells,
truncated `raise RuntimeErro`, executed outputs with a bench identity, and a
20-cycle 0.04 s repeat experiment outside guaranteed cleanup. No claim about
current connection or physical state can be derived from those saved outputs.

Renamed to docs/examples/shutter_open_close_tutorial.ipynb. Five numbered sections
cover preparation, settings, operation, feedback/timing interpretation and optional
repetition. Two executable cells provide settings and a complete try/finally cycle.
Retained repetition through disabled RUN_REPEAT, REPEAT_COUNT=20 and
REPEAT_HOLD_SECONDS=0.04; explicitly unqualified physical timing. Added positive
count/dwell validation; readiness read occurs before each Open. Session interlock
confirmation defaults false. Identity failure releases without Close; successful
identity permits cleanup Close plus release. Cleared execution counts/outputs.
Updated example guide, live report links and notebook test path.

Expected: default single cycle and opted-in repetition finish Closed/released on
the fake device; failed Open and interrupts attempt Close/release; invalid inputs
and wrong identity produce no output writes. Observed: all eight notebook cases
PASS within 49 tutorial tests. Repeat test executes three cycles with six 0.04 s
virtual waits; interrupt test stops during the second cycle and verifies cleanup.
Commands: .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
tests/test_examples.py (49 passed); .venv\Scripts\ruff.exe check --no-cache
tests/test_examples.py docs/examples/shutter_open_close_tutorial.ipynb and
ruff format --check for the same paths PASS after formatting the modified test.

Scope: Python execution with software-only SDK/time doubles; no real hardware,
SDK connection, source timing measurement, commit or push. Notebook is delivered
unexecuted for a fresh session. Existing unrelated working changes preserved.

## E106 / TEST-115 - Split the tutorial into executable steps

REQ-076, explicit user correction: break the large code block into multiple
sections. E105's combined-cell design is superseded. Notebook now has ten numbered
sections and ten code cells: settings, validation, controller/error cleanup,
Connect, initial Close, Open/hold, Close, optional repeat, Disconnect. Small shared
session_step context manager closes/releases on BaseException; successful steps
retain the connection. Identity-gated cleanup remains. The Open-to-Close cell gap
is an unbounded open interval, explicitly documented; no whole-notebook finally
or automatic between-cell cleanup is claimed. Rerun setup only after disconnect.
Repeat is an additional, separately enabled exercise and closes on loop exit.

Expected: sequential cell execution maintains shared state and explicit read/write
semantics; default and repeat paths finish closed/released on the fake; errors
and interrupts trigger cleanup, wrong identity/invalid input send no output writes.
Observed: .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
tests/test_examples.py: 49 passed, including eight notebook scenarios executing
each code cell separately in a shared namespace. Scoped ruff check --no-cache
and format --check tests/test_examples.py
docs/examples/shutter_open_close_tutorial.ipynb PASS after test formatting.
README/report/checkpoint updated for the actual cell lifecycle. Notebook outputs
remain empty. Software simulation only; no SDK connection or physical actuation.

## E107a / TEST-116a - Local repetition settings

REQ-076, user requests placing RUN_REPEAT, REPEAT_COUNT, REPEAT_HOLD_SECONDS in
the section that uses them. Moved these into a separate section 8 settings cell;
moved validation into that section's session_step guard so invalid settings also
release the connected session. Removed repetition dependency from initial setup.
Updated tests to override repetition values after executing local settings.
Expected: ordinary and optional notebook paths retain cleanup. Observed:
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_examples.py:
49 passed. Scoped ruff check --no-cache and format on the notebook/test pass.
Software-only execution; no actual hardware operation.

## D034 / E107b / TEST-116b - Hub owns Ethernet; cube is USB-only

REQ-077, explicit user request: strip Ethernet from KCubeShutter and implement
Ethernet connection/command handling in ShutterHub. Preserved direct setter /
explicit getter semantics from D033. Existing documented KEH3 TCPIP endpoint
support is reused through Kinesis; no new wire protocol, hub IP/firmware write
or KEH6 Ethernet mapping inferred.

KCubeShutter no longer accepts/exposes ethernet_endpoint and has no network
registration/routing branch. USB discovery filters FTDI devices even after
manual network entries exist. A private transport-neutral _KinesisShutter shares
identity, ownership, SDK lifecycle, get/set and release logic. Hub-owned private
channels delegate endpoint matching/discovery to their creating hub; they cannot
be reinjected into another hub as USB controllers. ShutterHub validates immutable
ethernet_endpoints per slot (None=USB), registers explicit network entries,
filters TCPIP/provider/comspec and routes slot-first get/set/lifecycle methods.
Default slot count includes endpoint length; explicitly configured network slots
never fall back to USB. GUI actions now call hub setters, including network slots.

Hub and channel locks serialize dispatch. Network writes check routing metadata
without requesting operating state, trigger feedback or sleeping. Route mismatch
faults before output commands. Close/Inactive may still target the original
retained handle after faults; no new handle or route is selected for cleanup.
All-slot cleanup, interrupts, failed-release retention and shared serial ownership
remain. Identity mismatch and provider changes before handle creation fail without
output writes. Default launcher is USB; explicitly constructed network hubs can
be supplied to create_app. Updated API/interface/architecture/README/Ethernet docs.

Expected: cube signature has no Ethernet option; USB ignores TCPIP entries;
network slots connect only to their endpoint/identity without USB readiness;
get/set commands reach the selected slot only; setter hooks reject any feedback
request/getter/sleep; wrong provider/bay/change refuses outputs; failed release
holds ownership until retry; GUI dispatch and cleanup work for mixed transports.
Observed: 47 Ethernet tests PASS, including old migrated tests and new mixed-route,
zero-feedback-write, wrong-bay, network GUI, injection and failed-release cases.
Final full suite: 528 passed, 1 skipped, zero failures. Optional real SDK test is
skipped without KINESIS_TEST_DIR; no physical test is inferred. Ruff check --no-cache
and format --check src/tests/docs/examples/docs/hardware_tests PASS on39 files,
including the concurrently revised tutorial. Three-device simulated_demo.py --api
PASS; documentation Python snippets compile. git diff --check PASS.
Commands, source hashes and scope: records/hub-ethernet-validation.json.

Earlier full runs saw five saved-notebook failures while another notebook update
was in progress. That work was preserved. E105/E106 finalized its renamed/split
source and tests; the final integrated suite above passes. This transport task
neither operated hardware nor rewrote the notebook. E107b/TEST-116b/REQ-077 avoid
colliding with those concurrent record IDs.

No real SDK DLL load, network connection, device command, server restart, firmware
change, commit or push. Physical Ethernet discovery/actuation/timing/recovery
remain unqualified. Software request complete; the documented passive LAN-only
qualification remains the bench resumption procedure, under its own authority.

## E109 - GUI/controller alignment; TEST-118 / REQ-079

User reported native Connect failed: Device is not connected, including StopPolling
cleanup failure, and requested updating GUI from controller.py. Existing source
GUI/controller/launcher/transport baseline: 97 software cases PASS before concurrent
REQ-078 consolidation. No code failure reproducer for that native exception found.

Passive SDK discovery found one USB controller matching the configured selection.
An isolated current-source Dash callback using the real SDK returned Connected,
Closed, Manual/Inactive and unknown session interlock readiness. Communication was
released in finally with disconnect(close_shutter=False); no output command was
requested. This proves current electronic connection/readback only, not optical
behavior, browser actuation or final live-server replacement.

Browser inspection showed the older KEH3 USB caption and the reported fault;
current source caption was USB. Process inspection found two project GUI launches,
including a legacy --serial/--verified-interlock/--port command; port 8050 belonged
to the console-script process tree. No process was stopped. Shell HTTP checks timed
out while the in-app browser could load the old page; do not infer a wedged server
solely from those shell timeouts. Browser retry did not establish a successful
connection. Root cause of the old native Connect exception remains unproven.

Focused source update: share Open/Arm readiness predicates between buttons and
fresh callback checks, explain unknown feedback, retain Close for held handles,
and derive USB/Ethernet labels from hub endpoints. No driver API or configuration
change. Preserve unrelated dirty work and concurrent test pruning.
Expected: successful identity Connect can coexist with unknown feedback; Open/Arm
are disabled/refused without output writes; failed Connect retries successfully;
Arm requires Closed/Inactive/Manual; existing lifecycle/TTL/routing tests remain green.
Observed: full reduced suite 181 passed, 1 skipped; GUI regression cases including
unknown position/state/mode, failed Connect retry and Arm readiness PASS. Optional
SDK test remains skipped. Commands (PYTHONDONTWRITEBYTECODE=1):
- .venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
- .venv\Scripts\ruff.exe check --no-cache src/thorlabs_shutter_control/gui.py tests/test_gui.py
- .venv\Scripts\ruff.exe format --check src/thorlabs_shutter_control/gui.py tests/test_gui.py
Both scoped Ruff checks PASS. Final source must be loaded by restarting the old
GUI under normal bench safeguards; that browser check remains UNTESTED. No new
physical motion, interlock confirmation, commit or push.

## E110 - Actual browser connection recovered; TEST-119 / REQ-079

User reported same connection failure after restarting. Expected: current GUI
source serves localhost:8050; explicit Connect verifies selected identity and
returns usable readback without output commands. Observed before correction:
port 8050 owner 63976 was the legacy Python -m launch with obsolete serial,
verified-interlock and port arguments. A second console-script GUI process tree
was also running. Browser still showed old KEH3 USB caption, native Connect fault,
and no held device handles on all three panels (Close/disconnect disabled).

Read exact process identities with Get-CimInstance Win32_Process and port owner
with Get-NetTCPConnection -LocalPort 8050 under approved elevation. Rechecked the
legacy command line and stopped only process 63976 with Stop-Process -Force;
no shutdown callback/output command was invoked. Port owner then became 39044,
the user's already-running current console-script GUI. No new server started.
Browser reload showed current USB caption and current transport-aware tooltips.
Clicked #connect-1 through the browser and observed Connected, 1 of 3 connected,
controller identity, Closed, enabled key and unknown interlock readiness. Open
remained disabled. Screenshot/AX observation confirmed actual browser result.
TEST-119 PASS (real electronic connection/readback and browser, no optical proof).

Left current GUI running with slot 1 connected for the user. Transient ownership
and feedback must be checked again before future operations. No Open, Close,
Arm, interlock confirmation, firmware change, source edit, commit or push.
No tests rerun: runtime-only recovery; prior E109 source tests remain applicable.
The remaining native exception cause inside the legacy SDK session was not
isolated; stale runtime removal followed by current browser success is the
supported operational fix. Prior E109 restart/human-action gap is resolved.

## E111 - All shutter GUI instances absent

User requested close all gui. Current elevated Win32_Process inspection found no
Python -m thorlabs_shutter_control or shutter-control.exe GUI launches. A broader
project executable-path scan found only the VS Code isort LSP process, preserved.
Get-NetTCPConnection -State Listen -LocalPort 8050 returned zero listeners.
All shutter GUI processes had already exited before action; no process stopped,
no new browser tab opened and no hardware/output command issued in this turn.
E110's running/connected state is superseded. Actual cleanup/physical shutter
state was not observed; process absence does not prove optical closure.

## D035 / E108 / TEST-117 - Reduce tests and remove generated caches/temp

REQ-078, explicit user instruction: remove temp/cache; substantially cut and
simplify tests. Initial tests directory had18 Python files (16 test modules),
4,002 lines; last integrated suite had528 passing cases and1 optional SDK skip.
Preserved unrelated dirty work, runtime environment, private inputs, physical
records and active notebooks. No production-controller change was made here.

Merged get/set and serial-confirmation tests into test_controller.py; network
selection/dispatch tests into test_hub.py. Consolidated five historical stage
modules and the no-cable tests into representative test_diagnostics.py workflows.
Retained focused GUI/launcher/tutorial/trigger modules, common fake SDK/time rig,
simulation and opt-in real-SDK boundary check. Removed duplicate lifecycles,
exhaustive invalid-value/configuration products and historical CLI serialization
permutations. Retained ownership while initializing, wrong identity/endpoint,
pre-factory route changes, metadata/readback separation, write errors/interrupts,
failed release, all-slot cleanup, GUI draft/readiness checks and notebook cleanup.
The manifest identifies retained coverage and retired function names rather than
claiming identical old branch/permutation coverage.

Notebook tests previously required cleared saved outputs and hard-coded editable
lab durations. Runtime tests now preserve saved outputs and explicitly inject
fake serial/dwell/repeat settings; all eight real control-flow scenarios remain.
No notebook cell/source/output was edited. Initial failures on saved metadata and
changed repeat dwell were test assumptions, not controller regressions.
Concurrent REQ-079 / E109 updated gui.py and added readiness/retry tests; those
changes were preserved and tested, not reverted to obtain smaller counts.

Final tests:10 Python files including rig/demo,8 test modules,2,014 lines. This is
1,988 fewer lines (49.7%),50% fewer modules and184 collected cases versus529
(65.2% fewer). Command: .venv\Scripts\python.exe -B -m pytest -q
-p no:cacheprovider --tb=short. Observed183 passed,1 skipped,0 failed. Optional
real SDK check skipped because KINESIS_TEST_DIR is not set. Ruff check --no-cache
and format --check --no-cache src/tests/docs/examples/docs/hardware_tests PASS
on31 files. Python -B tests/simulated_demo.py --api PASS for three distinct fake
devices with all handles released. git diff --check PASS. README documents the
cache-free test command and new grouping.

Cleanup was inventoried before deletion: .ruff_cache, .uv-cache,
pytest-cache-files-c65t9fsa, tmp, docs/hardware_tests/__pycache__,
src/thorlabs_shutter_control/__pycache__, tests/__pycache__. Every resolved target
was checked within this workspace, with no tracked contents/reparse links.
Normal removal handled five roots. Sandbox reads of the two temp roots failed;
exact elevated inspection showed an empty pytest folder and tmp containing two
empty test folders plus a one-byte generated .gitignore. Exact elevated deletion
succeeded without permission changes. Concurrent tooling recreated Ruff/source
bytecode caches; a final verified pass removed those too. Total64 generated files,
1,091,224 bytes across7 distinct roots. Final scan:0 generated temp/cache/bytecode
candidates,0 scan errors outside protected .git/.venv. Working inventory/XML files
were merged into records/test-pruning-validation.json and removed.

Controller source, active notebook and hardware-bench record match initial hashes;
.venv/Python and Git remain present. gui.py changed only through concurrent REQ-079
work. Intentional tracked deletions are confined to consolidated test modules;
cache deletion removed no tracked content. No SDK/hardware/device commands or
process termination by this cleanup task. No commit/push. Hardware/GUI restart
qualification and physical gaps remain independent; reduced tests are software
proof only. Exact counts, paths, hashes and coverage map are in the JSON evidence.

## E112 - Remove config interlock confirmation; TEST-120 / REQ-080

User explicitly requested removal of VERIFIED_INTERLOCK_SERIALS in config.py.
Removed the setting and its launcher loop/import dependency, obsolete invalid
setting test case and active README/setup/GUI instructions. Explicit Python API
confirm_interlock and readiness predicates remain unchanged. No GUI restart or
hardware operation. Expected: passive launch works without the removed attribute;
unknown interlock readiness continues blocking GUI Open/Arm. Observed: full suite
182 passed, 1 skipped; scoped Ruff check/format PASS. Active src/tests/docs/README
search found no removed-setting references. Historical records remain historical.
Commands: PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest -q
-p no:cacheprovider; .venv\Scripts\ruff.exe check --no-cache and format --check
for config.py, __main__.py, tests/test_cli.py. No commit or push.

## E113 - User-managed interlock; REQ-081 / TEST-121

User explicitly chose Users manage it externally; remove software interlock gating.
Removed interlock_ready from shared GUI Open/Arm predicates and interlock refusal
hints/messages. Readout remains informational; users manage physical setup and
verification. Existing connection/identity, key, known operating feedback and TTL
input/baseline gates remain. No confirmation control added; Python optional
status/confirmation APIs retained. Updated current guides and requirement scope.
This supersedes prior GUI interlock-readiness gating claims in E109/E112, not
historical measurements or the physical interlock circuit.

Expected: simulated None/False/True interlock feedback does not block GUI Open or
Arm; readout stays truthful; Connect still performs no outputs; independent
fault/key/state/TTL guards remain. Observed: all three interlock scenarios PASS
through actual Dash callbacks with fake devices. Full suite 184 passed, 1 skipped.
Scoped Ruff check --no-cache and format --check gui.py/tests/test_gui.py PASS.
Suite command: PYTHONDONTWRITEBYTECODE=1 .venv\Scripts\python.exe -m pytest -q
-p no:cacheprovider. git diff --check scoped paths PASS. No hardware operation,
GUI launch, physical interlock change, firmware change, commit or push. Final
changed GUI permission path remains physically UNTESTED.

## D036 / E114 / TEST-122 - Integrated review and publication

REQ-082: user explicitly requests review/fix/consistency/prune/commit/push of all
accumulated changes. Latest REQ-081 steering removes software interlock gates
throughout the project. Inspected driver/hub/GUI, launcher, changed procedures,
examples/notebook, reduced tests, configuration, docs and pending artifacts.

Removed remaining interlock-readiness checks, confirmation flags and required
interlock record fields from examples and diagnostic helpers. Existing notebook
and diagnostic integration tests trap any access to interlock_ready; GUI tests
cover None/False/True indications. Optional Python metadata remains informational.
Independent identity/ownership, connection, key, operating/TTL checks remain.
Published config has no actual serial; notebook outputs/counts are cleared and
repeat is disabled. Updated supervisor HTML examples from obsolete launcher flags
to config.py. Its historical bench claims/preview/Notion validation remain dated
historical evidence; no external Notion modification. Compacted STATE/REPORT to
remove contradictory current/historical runtime and validation claims.

Corrected an ID collision from concurrent earlier work: local repetition evidence
is E107a/TEST-116a; hub Ethernet is E107b/TEST-116b. Findings and observations are
unchanged; hub evidence JSON now uses the disambiguated IDs.

Initial source/extracted-wheel suites:184 passed,1 optional SDK skip. Package
build needed declared hatchling download; offline cache was absent and sandbox
network retries failed. Exact authorized network build succeeded. A later
concurrent driver edit changed Open/Close to Active/Inactive only while retaining
old docstrings/callers. Final source and wheel runs then failed16 cases,168 passed,
1 skipped. Prior PASS is invalidated until the intended command contract and its
callers/docs/tests are reconciled. User asked whether to retain state-only writes
or restore documented Manual/Enable sequences; edit preserved pending response.
No hardware access, GUI launch or physical state inference in this review.

Current checks: Ruff check/format PASS on32 files; all29 shareable Python files,
8 Python documentation snippets,26 JSON files and94 relative links checked.
Notebook has10 cleared code cells and disabled repeat. HTML anchors/SVG XML and
copyable Python/launcher syntax PASS. Generated tmp package extraction and Ruff
cache removed with resolved in-workspace targets and no reparse links; .venv,
Git, private inputs and historical evidence preserved. Final publication/checks
continue below; exact current results: review-publication-validation.json.

E114 continuation: user explicitly answered "Keep state-only Open/Close" and
asked whether SetOperatingState/EnableDevice are needed. The installed KSC101
header documents Active as mode-dependent: Manual opens, Single cycles once,
Auto cycles repeatedly, Triggered primes; Inactive closes. Vendor KSC101 Python
example enables once at setup then toggles Active/Inactive:
https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/Kinesis/KCube/KSC101/KSC101_pythonnet.py
Header: Thorlabs.MotionControl.KCube.Solenoid.h, enums around144-170 and setter721.
This supports separating enable/setup from repeated state commands; it does not
prove EnableDevice unnecessary on every real startup. No hardware trial made.

Kept state-only Open/Close and corrected docstrings, docs and caller contracts.
Added explicit enable_device() and hub dispatch (write-only, route-checked).
Disarm now owns its Inactive/Manual writes rather than aliasing state-only Close.
Manual lessons/diagnostics/notebook explicitly prepare enable and Manual baseline;
TTL Arm retains its compound Enable/Triggered/Active contract. GUI manual Open
requires Manual and assumes an enabled controller; it does not hide preparation
inside Open. Updated stale GUI/HTML/notebook claims that Close selected Manual.
Command tests now also prove Open/Close preserve an existing Auto mode. Explicit
enable coverage added to existing no-read/no-wait driver and hub matrices.
Current source suite186 passed,1 skipped; prior16 failures resolved against the
confirmed semantics. No interlock gate was reintroduced.

E114 final validation: source and extracted wheel each186 passed,1 skipped,0 failed;
wheel bytes match all current package sources/assets. Ruff check/format PASS on32
files; three-device simulation PASS. Shareable Python/JSON/snippet/link checks
PASS with exact counts and final wheel hash in review-publication-validation.json.
Old temporary failure results above are superseded by this final contract run.
No physical qualification inferred. Remote main verified at ca0d150 before commit;
normal commit/push is authorized by the active user request.

## E115 / TEST-123 - Reviewed implementation published

REQ-082: staged63 explicit reviewed paths; cached diff whitespace check PASS.
Commit f2934c8a100b2639de9ca06cbf47666323e861eb created and pushed normally to
origin/main. git ls-remote returned that exact hash; checkout clean after push.
Source/wheel software results remain186 passed,1 optional SDK skip each; physical
qualification is unchanged. Generated build/extraction/help-review paths removed.
Concurrent tools recreated source bytecode after earlier cleanup; exact generated
folder removed again without touching environment, Git or private data.
This checkpoint records publication; no further runtime source change or device
operation. A small documentation/evidence checkpoint commit follows.
