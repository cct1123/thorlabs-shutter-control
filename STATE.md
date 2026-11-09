# Engineering state

## Current checkpoint

2026-11-08 REQ-251 / TEST-251 final combined review: COMPLETE software/publication (E235).
The project remains BLOCKED for full physical/deployment acceptance; the review
is a separate software/publication scope. The user retains the three core modules
and authorizes the reviewed changes to be committed and pushed. No new device
operation, policy expansion, running-owner change or external application edit.

D085/E231 fixes queued stale replies behind a full receive buffer and concurrent
WebUI Release after ON/Start. It preserves passive ordinary close and all load,
interlock, identity, ownership, deadline and uncertainty protections. Redundant
release checking moves to the owner; cycle-duty checks share one repetition guard.
The GUI command-exposure work (REQ-250; D084/E230) is integrated; its
desktop/phone passive preview is complete and stopped. A subsequent fault-notice
regression keeps persistent owner faults visible in both notices, including polls;
readable electrical data cannot hide lockout or authorize output.

E234: 341 source + 341 isolated-wheel tests PASS, zero failures/errors/skips.
Lock/lint/format/package parity/import/help/passive config and six static notebooks
PASS. All 39 verifier input hashes match. Evidence: records/final-review-
{direct-validation,audit}.json and source/wheel XMLs. No hardware was operated.
Detailed earlier campaigns remain in records/RECORDS.md and their JSON/XML
artifacts; old campaign summaries are removed from this compact checkpoint.

## Architecture and fixed configuration

Device -> transport -> APT Session -> KSC101 driver -> ShutterHub -> Python/CLI/
WebUI/notebooks. One owner; no SDK backend, compatibility connection manager,
automatic retry/fallback, automatic startup connection or ON replay.

Canonical target: shutter / application CH0 / APT channel 1 / SH05R /
KSC101 68800777 / firmware 1.0.7 / KEH3 middle bay 192.168.1.19:40305.
Hub serial/firmware remain unknown. config/shutter.ethernet.toml records:
Manual-only output activation, continuous-duty load, 2 s OFF rest, separately
permitted protected selection of all four modes; native Start/priming and
settings/EEPROM permissions stay disabled.
VCP and KEH3 external USB OUT output remain unavailable. Identity/status bit 0
does not measure blade position, key contact, readiness or native activity.

Public DiamondGUI owner names/status fields remain contracts. Retired probe/SDK/
notebook-wrapper paths remain absent; raw historical evidence is retained and
superseded review documents remain available in Git history.
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
revision. Final software evidence is E234; dated physical records retain their own scope.
Older campaign counts and structural metrics below refer to their recorded revisions.

| ID | Short criterion / source | Method/evidence | Result |
| --- | --- | --- | --- |
| REQ-248 | Controller readability/docstrings (derived; PROJECT.md 8 November) | TEST-248; D082/E228; 86/86 coverage, AST/public signatures, source/wheel | PASS software: 255 source + 255 wheel |
| REQ-246 | Logical controller ordering (derived; PROJECT.md 8 November request) | TEST-246; D080/E226; AST equivalence and source/wheel checks | PASS software: 255 source + 255 wheel |
| REQ-244 | Controller duplication pruning (derived; PROJECT.md 8 November approval) | TEST-244; D078/E224; query count/refusals, 128-case mode parity, source/wheel | PASS software: 255 source + 255 wheel |
| REQ-242 | Happy-path GUI pruning (derived; PROJECT.md 8 November request) | TEST-242; D077/E223; callback/owner refusals, source/wheel checks, metrics | PASS software: 255 source + 255 wheel; 15.4% fewer GUI lines |
| REQ-241 | Dataclass simplification (derived; PROJECT.md 8 November approval) | TEST-241; D075/E221; metrics, snapshot isolation and source/wheel checks | PASS software: 251 source + 251 wheel; external schema migration required |
| REQ-240 | VCP duplicate-read pruning (derived; PROJECT.md 8 November request) | TEST-240; E220 byte-buffer checks; final E234 integration | PASS software; prior concurrent-lint blocker resolved |
| REQ-239 | Protocol pruning (derived; PROJECT.md 8 November approval) | TEST-239; D074/E219; predicate/write comparison and targeted/source/wheel tests | PASS software: 41 targeted, 251 source + 251 wheel; no device I/O |
| REQ-238 | Transport logic simplification (derived; PROJECT.md 8 November approval) | TEST-238; D073/E218; TCP loopback, exact bay mapping, public owner route guards and source/wheel verification | PASS software: 250 source + 250 wheel; no device I/O |
| REQ-237 | Protocol helper cleanup (derived; PROJECT.md 8 November explicit request) | TEST-237; D072/E217; retained-helper/query AST checks and source/wheel verifier | PASS software: 250 source + 250 wheel; no device I/O |
| REQ-236 | Controller helper cleanup (derived; PROJECT.md 8 November) | TEST-236; D071/E216; exact scoped delta and source/wheel regressions | PASS software: 250 source + 250 wheel |
| REQ-235 | Protocol organization (derived; PROJECT.md 8 November request) | TEST-235; D070/E214; existing protocol regressions and source/wheel verifier | PASS software: 250 source + 250 wheel; no device I/O |
| REQ-234 | Controller organization (derived; PROJECT.md 8 November) | TEST-234; D069/E213; structural equivalence and source/wheel verification | PASS software; 250 source + 250 wheel |
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
| REQ-221 | Repository manuals | TEST-221; E179/E193/E205; final E234 integrity audit | PASS integrity: four local PDFs, Issue 36 retained in Git; local SH05R PDF still missing |
| REQ-222 | Earlier manual/package review | TEST-222; E182/E204 | Historical source review/current software PASS |
| REQ-223 | Earlier holistic delivery | TEST-223; E183-E187 | Historical repository delivery PASS |
| REQ-224 | Earlier WebUI flow | TEST-224; E188-E192 | Historical scoped controller flow PASS; E192 one observed blade cycle |
| REQ-225 | Manufacturer-reference functions | TEST-225; E193/E194 | PARTIAL; display/trigger/Key/Ready contracts BLOCKED; native bench work UNTESTED |
| REQ-226 | Minimalist presentation | TEST-226; E196/E204 | Historical visual/current software PASS; no new visual/physical bench run |
| REQ-227 | Modern real WebUI cycles | TEST-227; E198-E202 | Historical selected controller flow PASS; complete two-cycle blade observation unverified |
| REQ-228 | Follow-up holistic review (derived) | TEST-228; E203-E206 | PASS scoped repository review; implementation published, docs/evidence in this checkpoint |
| REQ-230 | Cowork slimming (derived; PROJECT.md 8 November) | TEST-230; D065/E209; current E210 | PASS software; six runtime modules, two scripts |
| REQ-229 | GUI mode selection (derived; PROJECT.md 8 November request) | TEST-229; D064/E208; records/gui-mode-selection-direct-validation.json | PASS software: 116 focused, 236 source + 236 wheel; live mode change UNTESTED |
| REQ-231 | Three-module core (derived; PROJECT.md 8 November) | TEST-231; D066/E210; core-migration source/wheel, metadata regressions, links | PASS software: 250 source + 250 wheel; physical revision UNTESTED |
| REQ-233 | Transport organization (derived; PROJECT.md 8 November request) | TEST-233; E215; transport-organization source/wheel and contract regressions | PASS software: 250 source + 250 wheel; no device I/O |
| REQ-245 | APT42 command coverage audit (PROJECT.md 8 November) | TEST-245; E225; full per-ID source/manual matrix | PASS audit; complete command implementation NOT demonstrated |
| REQ-249 | Clear documented shutter commands (PROJECT.md 8 November) | TEST-249; D083/E229; literal frames, owner/error cases, source/wheel | PASS software: 293 + 293; new hardware operations UNTESTED |

| REQ-250 | GUI command exposure (PROJECT.md 8 November) | TEST-250; D084/E230 callback/desktop/phone evidence; E234 integration | PASS software/layout: 140 targeted; final 341 source + 341 wheel |
| REQ-251 | Combined review and publication (PROJECT.md 8 November) | TEST-251; D085/E231/E234; regressions, source/wheel/docs and remote verification | PASS software/docs/publication; E235 |

## Next action and external dependencies

E235: reviewed implementation/docs/evidence committed as 2bc53e2 and pushed to
origin/main; remote HEAD equality verified. The final checkpoint records this
observed publication. Next engineering work is the separate physical/deployment
campaign; no further source change is required by REQ-251.
No device I/O is part of publication. The active earlier application environment
was not synced or restarted because shutter-control.exe is in use; validation
uses --no-sync and an isolated installed wheel. Deploy only after the existing
owner has stopped outputs and released communication; then install/restart and
reload deliberately, without takeover or automatic connection.

External DiamondGUI consumers require the version-2 flat status migration in
docs/python-api.md before upgrading. E185 remains a dated failed page/mapping
check; the external checkout was not inspected, changed or revalidated here.
Complete physical/driver/reboot/endurance acceptance only under the separately
approved setup and limits described below. Existing cycle authority is consumed.

## Human action required

1. Known: E234 validates the final combined software checkout. E200's two-cycle
   allowance is consumed; E202 leaves complete two-cycle blade observation
   unverified. The latest owner/GUI revision has software validation only.
2. Blocked: software inspection cannot establish present source protection,
   trigger isolation, interlock condition or blade motion, nor grant actuation
   authority. AGENTS.md Physical action and human intervention requires that
   authority for the specific conditions.
3. Needed: confirm the same SH05R / KSC101 68800777 / KEH3 middle bay
   192.168.1.19:40305 is independently source-protected, external triggers
   isolated, key/interlock intact, and approve one new Manual WebUI cycle while
   observing the blade. Permit fresh identity/Manual/OFF checks, at least 2 s
   confirmed OFF rest, one existing 1 s host-held pulse, final fresh Manual/OFF
   and release. No mode/settings/EEPROM writes or further cycles. If the initial
   state is not Manual/OFF, stop before the pulse and report it.
4. Return: setup/window confirmation and approval; during the run, report
   whether the blade visibly opened and returned closed. This qualitative
   observation does not establish optical timing or extinction calibration.
5. Next: check the local owner's identity/released state without takeover,
   launch/reload reviewed code only when released, then use visible WebUI
   controls with raw evidence. If release is uncertain, stop for owner resolution.
   On ambiguity, no retry; use the existing bounded OFF cleanup, retain unknown
   optical state, and rely on the independent source protection.

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
