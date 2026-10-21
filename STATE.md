# Engineering state

## REQ-102 COMPLETE - essential tests

Source: PROJECT.md latest test-rewrite request. E141 / TEST-151: source and
extracted wheel each15 passed,0 skipped. All tests and doubles rewritten:
3 test modules plus1 fixture,405 lines versus2486 across10 files. Real-SDK opt-in,
preview helper, input-fuzz matrices and speculative/internal checks are removed.
The suite covers normal workflows and selected essential operational failures;
it is not exhaustive. Current evidence: records/tests-validation.json.
Production source/CSS hashes, private results and .venv are unchanged. No hardware
or actual network operation. The runtime baseline marker remains baseline-2026-10-21.

## Runtime baseline - REQ-101

Source: PROJECT.md current baseline request. Prior tree: 5ab1f91, 109 tracked
files, 2,323,179 bytes. Historical records/checkpoints are hash-verified in ignored
inputs/private/baseline-5ab1f91; the executed LAN notebook remains privately intact.

Removed obsolete diagnostic stages, duplicate script tutorials, supervisor output,
superseded screenshots and incremental development records. GUI construction now
requires ShutterHub; operator-confirmation metadata/API and alternate scan-address
format adaptation are removed. Current USB/LAN control and explicit reads/writes
remain. E138 / TEST-148 and E139 / TEST-149 record the original baseline's test/tree
delivery; TEST-151 supersedes that suite with the essential current tests above.
The original baseline tree was43 files versus109 before cleanup.
Implementation77ede6a and pruned baseline d1453d3 are pushed; origin/main was
independently verified at d1453d3730db4c18e1af085dc1637b393bfeb298 (E140/TEST-150).
This final checkpoint is marked baseline-2026-10-21. Physical acceptance remains
incomplete; software completion does not change the limits below.

## Architecture and configuration

Device -> Kinesis transport -> KCubeShutter/owned hub channel -> ShutterHub -> GUI.
Unified Discover combines USB, configured routes and a bounded LAN scan. Explicit
Connect applies the selected detected route. All process handles must be released
for broad scanning; failed releases retain ownership and cleanup. Startup is passive.

Defaults in src/thorlabs_shutter_control/config.py: empty serial/endpoint tuples,
SLOTS=None (three USB panels, or enough for supplied routes/serials), localhost8050,
LAN192.168.1.0..192.168.1.255, maximum256 addresses, open timeout100ms/address.
Kinesis folder defaults to C:/Program Files/Thorlabs/Kinesis. Native calls may block.

## Requirements and validation

| ID | Current criterion | Method | Status |
| --- | --- | --- | --- |
| REQ-102 | Rewrite all tests as a small essential suite | TEST-151 source/wheel,15 cases,405 lines | PASS software |
| REQ-101 | Slim current baseline, no compatibility paths | TEST-148 source/wheel; TEST-149 tree/docs; TEST-150 publication | PASS software baseline/publication |
| REQ-099 | Unified USB/LAN Discover and detected-route Connect | TEST-148 fake SDK and actual Dash callback HTTP | PASS software |
| REQ-020 | Ownership and all-slot cleanup | TEST-148 lifecycle/error/interrupt regressions | PASS software |
| REQ-075 | Direct setters and explicit getters | TEST-148 controller/GUI/notebook regressions | PASS software |
| REQ-003/004/007/008 | Current physical USB, motion, shutdown and GUI | Authorized bench qualification | UNTESTED |
| REQ-006/023/031 | Physical loss recovery, multiple pairs and electrical TTL | Dedicated bench measurements | BLOCKED by unavailable physical validation |
| REQ-043 | Explicit-endpoint passive KEH3 LAN communication | Retained E128 / TEST-138 observations | Prior revision PASS; current baseline UNTESTED |

## Physical limits

records/hardware-evidence.json retains USB readback/user-observed cycles, passive
one-pair LAN identity/Connect/release, and the unresolved active-low no-cable TTL
position FAIL. These do not qualify changed source, live range scans, Ethernet
actuation, KEH6/multiple real pairs, electrical signals or calibrated timing.
No hardware/network discovery or actuation is performed during baseline cleanup.

## Next action and human action required

No remaining software action, generated scratch or pending process. Current baseline
marker: baseline-2026-10-21. No human action needed for software delivery. Physical acceptance
requires a separately authorized bench session with the intended topology,
independent source protection and observations recorded under the current revision.
