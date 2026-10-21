# Engineering state

## REQ-101 VALIDATED - publication pending

Source: PROJECT.md current baseline request. Prior tree: 5ab1f91, 109 tracked
files, 2,323,179 bytes. Historical records/checkpoints are hash-verified in ignored
inputs/private/baseline-5ab1f91; the executed LAN notebook remains privately intact.

Removed obsolete diagnostic stages, duplicate script tutorials, supervisor output,
superseded screenshots and incremental development records. GUI construction now
requires ShutterHub; operator-confirmation metadata/API and alternate scan-address
format adaptation are removed. Current USB/LAN control and explicit reads/writes
remain. E138 / TEST-148: source and extracted wheel each217 passed,1 optional SDK
skip. E139 / TEST-149: current docs/notebooks/package/private archive checks PASS.
The maintained tree is43 files, about0.54MB versus109 files/2.32MB before cleanup.

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
| REQ-101 | Slim current baseline, no compatibility paths | TEST-148 source/wheel; TEST-149 tree/docs/private preservation | PASS software; publication pending |
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

Prune generated package/checker scratch; commit/push focused stages and mark
baseline-2026-10-21 after verification. No human action needed for software delivery. Physical acceptance
requires a separately authorized bench session with the intended topology,
independent source protection and observations recorded under the current revision.
