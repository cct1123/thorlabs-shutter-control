# Engineering state

## Active holistic review (6 November 2026)

REQ-223 / TEST-223 (derived from PROJECT.md holistic review): IN PROGRESS.
The user now authorizes staged commits and push of the reviewed migration.
No new hardware action is authorized or needed for this software review.
Baseline software verification: 144 source + 144 isolated-wheel tests pass.
Review findings to reproduce: qualified read-only GUI shutdown can actuate OFF;
GUI Release without a target can release every route; OFF-rest accounting starts
before electrical OFF is observed. Prior runtime-dependent PASS results are
historical until affected software checks are rerun; E181 remains evidence only
of its recorded hardware configuration/revision, not a current optical result.
E183: fixes pass 160 source + 160 isolated-wheel tests and all six static notebooks.
Current software evidence is records/direct-validation.json. Runtime hashes have
changed since E181; its actual cycle remains historical, not a requalification.
Next: commit the runtime stage, publish manuals/evidence in a separate commit,
finish scoped artifact cleanup and the final checkpoint/report, then push.

Updated6 November2026. **Exact Ethernet ON/OFF PASS (REQ-220/E181); broader
physical deployment qualification remains open.** No current command/handle/claim.

## Current controller and configuration

shutter, CH0; KSC10168800777, firmware1.0.7, hardware3, one protocol channel.
KEH3 middle bay192.168.1.19:40305, management40303 unused. User confirmed power/
Ethernet/USB IN disconnected and currentSH05R/safe setup in response to blocked
source/isolated-trigger question. Hub serial/firmware remain unknown metadata.
Tracked config/shutter.ethernet.toml is the shared exact-controller/load policy;
docs/examples/shutter_config.py loads it. Ignored shutters.local.toml now mirrors
that Ethernet policy; its former USB config is preserved under inputs/private.

## Actual completed control test

User authority in PROJECT.md covers explicit OFF/Manual preparation and one1s
added ON hold,2s OFF pause, finalOFF/Manual/release on this one controller only.
At2026-11-06T21:26:03.171963+00:00 preparation verified Triggered/OFF, sent
cb0401025001 then c00401015001, confirmed Manual/OFF and released, with ON forbidden.
At2026-11-06T21:26:53.535384+00:00 a fresh real Jupyter kernel ran notebook6:
OFF/pause, exactly onecb0401015001 ON, positive fresh bit0,1s added hold, priority
cb0401025001 OFF and fresh clear bit. Observed0x2000->0x2001->0x2000. ON-to-OFF
host dispatch1.0569156s is not calibrated optical exposure. Final Manual/OFF,
no error/journal fault; socket/claims released. Fresh post-release CLI confirmed
same identity/Manual/OFF0x2000 and no fault. No simulator, SDK or injected
transport was used for these operations. No repeat cycle is planned.

User independent-observation answer: "I did not observe it". Blade motion,
optical closure and timing remain UNTESTED. Source protection is human-reported;
interlock requirement is configuration, not a measured contact-continuity test.
Manual selection is remembered; no automatic Trigger restoration. No other
controller, trigger/cycle/network/EEPROM, firmware/driver/security setting changed.

Evidence: records/ethernet-control-manual-preparation.json,
records/ethernet-control-live.json (all real frames, hashes and saved notebook6),
records/ethernet-control-final-status.json; D059/E181 in records/RECORDS.md.

## Resulting architecture and boundaries

Transport -> APT Session -> KSC101 -> ShutterHub -> Python/CLI/GUI/notebooks.
Docked KEH3 and qualified D2XX use the same exact identity, load policy, Manual/
interlock requirement, ownership/deadline/uncertainty/cleanup path. VCP/external
USB OUT control remain unavailable. No scan, fallback, retry or ON replay.
A protected Trigger->Manual transition needs explicit source_inhibited=True and
policy mode permission, sends OFF before Manual and confirms final mode/output.
Normal ON/OFF never changes mode or primes triggers. CLI pulse explicitly prepares
OFF/rest before balanced hold/OFF. Fresh output polling uses the existing total
budget; it never resends the command or retries a failed query. TCP supplies send
count before Session's lateness check; partial/unknown writes still forbid every
further frame. Output/operating/optical meanings and raw0x04CD stay separate.
Context release is passive; explicit qualified cleanup and protected recovery
retain original failures and cleanup outcomes. Failed close retains resources.

## Current software and concurrent documentation evidence

Final integrated144 source +144 exact installed-wheel tests PASS, no failures/
errors/skips. Locked build/clean dependency/install/import/help, source-wheel
parity, lint/format, negative locks and all6 schema/syntax/link checks PASS.
Current runtime/config/notebook hashes match the real sessions and final manifests.
Current code has additional protocol/route/policy regressions from the concurrent
manual/package review; software transports are not physical evidence.

Repository manual copies (REQ-221, E179) are preserved unchanged under docs/manuals:
KSC101 RevD, KEH3/KEH6 RevE and APT Issues36/42.1. Index and registered hashes are
retained. E179's old TEST-220 identifier belongs to documentation, now disambiguated
as REQ-221; this live control work is E181/REQ-220. REQ-222/E182 concerns the separate
manual/package consistency review, which itself sends no hardware commands. Its
source review does not negate this independently authorized live result. The SH05R
primary manual was inspected online; direct download timed out, no local hash
claimed (SRC-009, records/sh05r-manual-reference.json). Do not invent a missing copy.

Prior E178 slimming/read-only evidence retains its original hashes/fields. Every
pre-review notebook and user output is backed up via source-review-notebook-backups.json;
pre-control5/6 are also preserved privately. No unrelated dirty work, external
DiamondGUI source, driver or dependency was changed; no commit/push. The external
DiamondGUI checkout is absent, so its historical29 integration cases are not a
current PASS; local method/schema/CLI/GUI regressions pass.

## Requirements and scoped acceptance

Human criteria remain in PROJECT.md. PASS is restricted to the stated method/
configuration. Missing physical criteria below are not hidden by software success.

| Requirement | Source / criterion | Validation / evidence | Current result |
| --- | --- | --- | --- |
| REQ-201 | Objective; uv/SDK independence | TEST-201: locked clean wheel/import/help; E178 | PASS offline; native drivers unqualified |
| REQ-202 | Identity and route requirements | TEST-202: E168 offline; E170 USB; E172 Ethernet middle-bay identity | PASS actual KSC101 identity on 40305; USB open FAIL; hub/full route qualification missing |
| REQ-203 | Communication/framing | TEST-203/220, E181 actual0x2000/0x2001/0x2000 and current142-case regressions | PASS selected read/control; operating/optical state remain unknown |
| REQ-204 | Modes/load constraints | TEST-204/220, E181 protected OFF->Manual and one SH05R ON/OFF | PASS selected Manual + software; other modes/loads unqualified |
| REQ-205 | Freshness and deadlines | TEST-205: stale/late quarantine, total and separate cleanup budgets; E178 software | PASS tested cases; arbitrary same-type reply ordering unresolved |
| REQ-206 | Ownership and priority cancellation | TEST-206: process claims, concurrent routes, query/hold cancellation; E178 software | PASS offline; native 250 ms target UNTESTED |
| REQ-207 | Ambiguity and cleanup | TEST-207: partial writes, lockout/recovery, all-target cleanup; E178 software | PASS offline; optical safety UNTESTED |
| REQ-208 | Direct KEH3 control | TEST-208/220, E181 exact middle-bay68800777/1.0.7 | PASS selected controller commands/readback; other topology/hub recovery/optics open |
| REQ-209 | Physical/local/TTL/interlock behavior | TEST-209: actual setup and approved physical procedure | BLOCKED: setup/ratings and authorization |
| REQ-210 | Drivers, persistence and endurance | TEST-210: inventory/rollback, reconnect/reboot/coexistence | BLOCKED: hardware and approved downtime/window |
| REQ-211 | DiamondGUI owner integration | TEST-211: 29 focused owner/factory/page tests; E168 historical; local owner-schema regression current | External checkout unavailable; full integration UNTESTED |
| REQ-212 | Delivery and reproducibility | TEST-212: lock, source/wheel parity, docs/links/hashes; E178 | PASS software; actual load documentation absent |
| REQ-213 | User-selected controller reference | TEST-213: pinned read-only comparison; E161/E162 | PASS source review; no hardware acceptance transferred |
| REQ-214 | User QMI discovery investigation | TEST-214: pinned source investigation; E163 | PASS source review only |
| REQ-215 | Exact Ethernet notebooks/generic name | TEST-215/220, all6 static/passive + actual notebook6 E181; prior1/2/3 E178 | PASS current structure and real ON/OFF6; prior output/backups retained |
| REQ-216 | Explicit D2XX/VCP discovery | TEST-216: offline E166/E168; native metadata E169/E170 | PASS enumeration; shutter absent from D2XX descriptor list but present in Windows PnP |
| REQ-217 | KEH3 diagnostic preparation and authorized live follow-up | TEST-217: software E178; actual identity/status E172/E178 | PASS read diagnostics; hub verification/operation BLOCKED |
| REQ-218 | Comprehensive review/simplification/commit (derived) | TEST-218: reproduced regressions, full source/wheel/integration, final diff; E168 | PASS software; delivered in the local checkpoint commit |
| REQ-219 | PROJECT.md source/API review, 6 November (derived) | TEST-219: E178 historical source contract/reduction and live reads; current software revalidated in E182 | PASS for E178's scope/revision; current counts/hashes are in E182; no new hardware evidence |
| REQ-220 | Latest exact Ethernet ON/OFF request | TEST-220/E181: real OFF/Manual, one1s ON/OFF, release and fresh CLI | PASS implementation/controller readback; user did not observe blade motion |
| REQ-221 | PROJECT.md repository documentation request, 6 November (derived; disambiguates historical E179 ID collision) | TEST-221: current hash/visibility recheck; E179 originally TEST-220 | PASS repository copies: KSC101, KEH3/KEH6, APT Issues 36 and 42.1; SH05R manual reviewed online, local PDF missing |
| REQ-222 | PROJECT.md manual consistency/package validation, 6 November (derived) | TEST-222: source review, literal bytes/route/policy/transition regressions, source/wheel/static notebooks; E182 | PASS software:144 source +144 wheel, six static notebooks; no new device operation |

## Next action and human dependency

The requested exact-controller Ethernet implementation/test is satisfied. No
further actuation is requested or planned. Use the reviewed API/notebook6 only
within an approved protected-source setup; saved output is not continuing state.
Broader qualification needs independent observed blade motion/optical calibration,
normal key/interlock/local/TTL/fault behavior, other occupied/empty/swapped routes,
hub identity/recovery, native dispatch and reboot/endurance evidence. Current
readback cannot supply those measurements. Obtain their exact limits/physical
window before future tests; do not repeat this cycle just to fill missing optics.
The full project is not marked COMPLETE while those broader requirements remain.
