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
