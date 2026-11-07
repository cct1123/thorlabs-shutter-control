# Engineering state

## Current checkpoint

REQ-228 / TEST-228 follow-up holistic review: scoped repository review COMPLETE.
Implementation/software/cleanup PASS; implementation 460286f is pushed and remote
parity verified (E206). This checkpoint contains final docs/evidence delivery.
Full physical/deployment acceptance
remains BLOCKED on the specific gaps below. Source: PROJECT.md latest review
request. Starting checkout 547ad94 was clean; no hardware operation was performed.

E203 reproduced 8 owner/policy failures and 4 GUI-state failures before fixes.
E204: 228 source + 228 isolated installed-wheel tests PASS, zero failures/errors/
skips; exact Python/CSS parity, locked build/install/import/help and frozen fixture
hashes PASS. Six notebooks PASS static checks; no hardware cells executed.
E205: 32 verified generated cache/pytest directories, 699 files / 174667 bytes removed;
no tracked deletions, .venv/local configuration/backups/reference tooling retained.
Evidence: records/followup-review-validation.json, prefixed test/XML/notebook
records, baseline failure XMLs and records/followup-review-cleanup.json.

### Corrected behavior

- Every ON attempt invalidates prior OFF rest, including ON without a later poll.
- A confirmed-safe released output session cannot authorize OFF in a later reader.
  Faulted/active uncertainty still survives release and process boundaries.
- Protected recovery clears stale requests/cleanup obligations without output.
- Mode Stop updates requested OFF; settings/mode readback must retain interlock
  requirement. Cycle writes enforce recorded duty as well as timing/count limits.
- GUI drafts and assertions are scoped to target/connection generation. Disconnect
  and reconnect clear stale state; ordinary polling preserves active edits.
- Verification hashes frozen real-observation input and refuses failed/skipped/
  empty required suites. GUI callback test plumbing has one shared helper.

The current running preview, last observed at 127.0.0.1:9860 (session 57830), uses the
pre-review source. It was released after E200; its transient state has not been
polled during this review. Restart the released owner and reload the browser to
load reviewed code. No server takeover, device connection or driver change here.

## Architecture and fixed configuration

Device -> transport -> APT Session -> KSC101 driver -> ShutterHub -> Python/CLI/
WebUI/notebooks. One owner; no SDK backend, compatibility connection manager,
automatic retry/fallback, automatic startup connection or ON replay.

Canonical target: shutter / application CH0 / APT channel 1 / SH05R /
KSC101 68800777 / firmware 1.0.7 / KEH3 middle bay 192.168.1.19:40305.
Hub serial/firmware remain unknown. config/shutter.ethernet.toml is unchanged:
Manual-only, continuous-duty load, 2 s OFF rest, separately permitted persistent
Manual preparation; native mode/settings/EEPROM permissions stay disabled.
VCP and KEH3 external USB OUT output remain unavailable. Identity/status bit 0
does not measure blade position, key contact, readiness or native activity.

Public DiamondGUI owner names/status fields remain contracts. Retired probe/SDK/
notebook-wrapper paths remain absent; historical reports/evidence are retained.
Current instructions: README.md, docs/python-api.md, docs/gui.md, docs/cutover.md.
Manufacturer/source contracts: docs/INTERFACE.md and docs/sources.md.

## Physical evidence and authority

E200 / TEST-227: two real visible-WebUI cycles on the exact setup above passed
at their recorded pre-review source. Manual ON 0x2001 -> OFF 0x2000, 0.748307 s
between readbacks; then 1 s host hold after 28.177088 s OFF. Active Release refused,
timed pulse disabled during ON, settings 2000/2000 ms/count 5 unchanged. Final
Manual/OFF/no fault at 2026-11-07T01:10:10.710233 UTC, then released/no handle.
Raw record: records/webui-modern-hardware-live.json; source/artifact hashes and
scope: records/webui-modern-hardware-validation.json. This is not current live
state or physical validation of the review's owner/GUI changes.

E202: user reports "I did not observe both cycles". Complete E200 two-cycle
blade motion remains unverified; failed motion is not inferred. Separate human
report: records/webui-modern-hardware-observation.json. E191/E192 records an
earlier single cycle whose opening/return closed was independently reported.
Neither establishes optical timing/extinction calibration.

All prior cycle allowances are consumed. No further ON, mode/settings/EEPROM,
trigger-I/O, driver, network or other-device operation is authorized by them.
The current repository review grants no new device operation.

## Requirements

Human criteria remain in PROJECT.md. PASS applies only to its method/configuration/
revision. E204 revalidates software, not the dated physical records.

| ID | Short criterion / source | Method/evidence | Result |
| --- | --- | --- | --- |
| REQ-201 | uv / SDK independence | TEST-201; E204 locked source/wheel | PASS software; USB deployment unqualified |
| REQ-202 | Exact identity/routes | TEST-202; E204, historical E200 | PASS software; hub identity unknown |
| REQ-203 | Framing/communication | TEST-203; E204 | PASS software; current physical revision UNTESTED |
| REQ-204 | Modes/load limits | TEST-204; E203/E204 guards | PASS software; native modes/other loads unqualified |
| REQ-205 | Freshness/deadlines | TEST-205; E204 | PASS tested cases; arbitrary same-type reply ordering unresolved |
| REQ-206 | Ownership/cancellation | TEST-206; E204 | PASS software; native 250 ms target UNTESTED |
| REQ-207 | Ambiguity/cleanup | TEST-207; E203/E204 | PASS software; optical safety unqualified |
| REQ-208 | Docked KEH3 | TEST-208/220; E200 historical | Selected route historical PASS; broader topology/recovery open |
| REQ-209 | Physical/local/TTL/interlocks | TEST-209; E191/E192/E202 | PARTIAL historical qualitative observation; broader physical acceptance UNTESTED |
| REQ-210 | Drivers/persistence/endurance | TEST-210; approved campaign required | BLOCKED: inventory, hardware/window and calibration |
| REQ-211 | External DiamondGUI | TEST-211; E185 last recorded external check | FAIL historical page check: 3 owner/factory PASS, 26 page FAIL; not rerun here |
| REQ-212 | Reproducible delivery | TEST-212; E204/E205 | PASS software/docs; physical deployment incomplete |
| REQ-213 | Controller reference review | TEST-213; E161/E162 | Historical source review PASS |
| REQ-214 | QMI reference review | TEST-214; E163 | Historical source review PASS |
| REQ-215 | Ethernet notebooks/naming | TEST-215; E204 static checks | PASS static; saved execution historical |
| REQ-216 | Explicit USB inventory | TEST-216; E169/E170/E204 | Software/history only; USB open failed historically |
| REQ-217 | Bounded Ethernet diagnosis | TEST-217; E172/E178 | Historical exact-controller read PASS; hub qualification open |
| REQ-218 | Earlier review/delivery | TEST-218; E168 | Historical scoped PASS |
| REQ-219 | Earlier API slimming | TEST-219; E178/E204 | Historical review/current software PASS |
| REQ-220 | Exact Ethernet ON/OFF | TEST-220; E181 | Historical controller cycle PASS; its optics unobserved |
| REQ-221 | Repository manuals | TEST-221; E179/E193/E205 hashes | PASS five unchanged PDFs; local SH05R PDF still missing |
| REQ-222 | Earlier manual/package review | TEST-222; E182/E204 | Historical source review/current software PASS |
| REQ-223 | Earlier holistic delivery | TEST-223; E183-E187 | Historical repository delivery PASS |
| REQ-224 | Earlier WebUI flow | TEST-224; E188-E192 | Historical scoped controller flow PASS; E192 one observed blade cycle |
| REQ-225 | Manufacturer-reference functions | TEST-225; E193/E194 | PARTIAL; display/trigger/Key/Ready contracts BLOCKED; native bench work UNTESTED |
| REQ-226 | Minimalist presentation | TEST-226; E196/E204 | Historical visual/current software PASS; no new visual/physical bench run |
| REQ-227 | Modern real WebUI cycles | TEST-227; E198-E202 | Historical selected controller flow PASS; complete two-cycle blade observation unverified |
| REQ-228 | Follow-up holistic review (derived) | TEST-228; E203-E206 | PASS scoped repository review; implementation published, docs/evidence in this checkpoint |

## Next action and external dependencies

No repository implementation gap remains for this scoped review. Staged hashes
are checked before final checkpoint publication and remote parity afterward.
Further implementation testing is needed only after a source change or new failure.

For full GUI parity, obtain manufacturer-confirmed KSC101 MMI 0x0520/trigger 0x0523
payload layouts and Key/Ready mapping with firmware applicability. The existing
APT model table conflicts with motor-specific details; do not guess or use SDKs.
Then implement through the same APT owner and revalidate before an approved bench test.

For physical/deployment acceptance, provide a separate approved commissioning
handoff: current setup/protection, exact allowed commands/limits/window, calibrated
optical method/results, hub identity/topology and intended external DiamondGUI
page/mapping restoration. Software cannot establish those physical facts or
authorize restoring another checkout. Driver/reboot/endurance work needs an
all-instrument inventory and its own downtime/rollback window. These gaps keep
the full project BLOCKED; they do not negate scoped repository-review results.
