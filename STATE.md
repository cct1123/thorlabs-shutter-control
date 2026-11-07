# Engineering state

## Active manufacturer-style APT WebUI

REQ-225 / TEST-225: PARTIAL; supported software paths validated, full GUI parity
BLOCKED on KSC101-specific display/trigger wire contracts and Key/Ready feedback.
E193/D061: RevF GUI is reference only. Four mode selectors, Open/Start and
Close/Stop, timing/count, Settings and Identify use the canonical APT owner.
Cycle edits/storage and native modes have separate permission/qualification gates;
the real SH05R TOML remains unchanged, Manual-only with settings writes disabled.
MMI/trigger layouts conflict with KSC101 applicability text; disabled controls and
Unknown lamps disclose the gap instead of guessing motor layouts or using an SDK.

E194: 201 source + 201 isolated installed-wheel tests PASS; Python/CSS parity,
lint/format/locked install/import/help PASS, six notebooks static PASS.
Browser review at1100px desktop/390px phone was disconnected, no device command;
responsive selector and scrolling Settings header corrected, zero console warnings/errors.
Evidence: records/webui-apt-validation.json and desktop/settings/phone screenshots.
Native timing, priming, Identify flash, settings persistence and the revised
panel's physical operation remain UNTESTED. Old E191/E192 qualify their exact
historical Manual cycle only. No new live output/configuration authority exists.
The new passive preview is at127.0.0.1:9860 (owned exec session14309, final source
started with -B; no device connection).
Earlier9857 server was not taken over. Recheck transient state before future work.

Implementation checkpoint: ab80236. Next: publish documentation/evidence;
full parity resumes only with a trustworthy
manufacturer KSC101 display/trigger/status contract and separately approved tests.

## Latest single-cycle follow-up (6 November 2026, local date)

E191 / REQ-224: exactly one newly authorized1s host-hold cycle completed through
the visible WebUI timed button. Fresh initial identity68800777/1.0.7, Manual/OFF
and interlock requirement true; configured OFF rest observed. Successful existing
owner pulse returned Manual/OFF0x2000/no fault. Release then Read confirmed
disconnected/has_device=false/requestedOFF. No second cycle or mode change.
Evidence: records/webui-one-second-cycle.json, webui-one-second-off.jpg and
webui-one-second-validation.json (source/artifact hashes and timing scope).
The WebUI remains open at127.0.0.1:9857 (owned exec session3080), with no device
handle/claim. Recheck its actual state before future work; do not issue more ON.
E192: user confirms "Yes, it opened and returned closed". Qualitative blade motion
PASS for this exact cycle by independent human report. No extinction/detector or
optical-timing calibration is established. Follow-up: records/webui-one-second-observation.json.
The1s setting is host hold after internal ON readback, not calibrated optical exposure.

## Latest actual WebUI validation (6 November 2026)

REQ-224 / TEST-224: PASS for the selected actual WebUI/controller workflow.
The user confirmed the unchanged protected SH05R setup. Visible browser actions
used the production owner/TCP at 192.168.1.19:40305, KSC10168800777/1.0.7;
no simulator, injected transport or direct callback substitute. Two short ON/OFF
cycles total (baseline and corrected), plus explicit OFF/rest-guard checks.
The final live read was Manual/OFF/no fault; Release then Read showed disconnected,
has_device=false and requestedOFF. The test server on9857 was stopped after
release; the separate8050 listener was left alone. No further actuation is planned.

E188 exposed default-port collision, unknown feedback after GUI Connect and a
first-ON rest-timer bug. E189 fixes gui --port, fresh feedback on WebUI Connect,
OFF-rest timing beginning at fresh OFF rather than a failed ON attempt, and a
remaining-wait message. First ON after the rest now succeeds; immediate ON during
rest is refused with1.66s remaining, followed by fresh OFF/no fault. Already-Manual
selection remained a read-only no-op. Library connect remains identity-only.

Evidence: records/webui-baseline-live.json, webui-final-live.json, the two JPEGs,
webui-live-validation.json (runtime/config/artifact hashes), webui-evidence-validation.json
and webui-package-validation.json. scripts/verify_webui_evidence.py checks saved
observations without operating or simulating hardware. Passive compile/lint/format,
lock, exact wheel parity, isolated install/import/help and invalid-port checks PASS.
No simulated-device tests ran in this campaign. The previous160+160 full suite is
historical for its recorded revision; affected full fault/deadline/cancellation
regressions are not claimed as newly revalidated by this selected happy path.
E190: the user reports "I did not observe the blade". Independent blade motion
and optical closure remain UNTESTED; controller readback results are unchanged.
Follow-up: records/webui-observation-followup.json. No additional actuation.

## Previously delivered holistic review

Updated 6 November 2026. **REQ-223 repository review/delivery COMPLETE.
Full physical/deployment qualification remains BLOCKED.**
That prior review performed no device operation; E188/E189 above are the separately
authorized current live WebUI work. No driver, firmware or network setting changed.

## Current architecture and configuration

Device -> byte transport -> APT Session -> KSC101 driver -> ShutterHub ->
Python / CLI / GUI / notebooks. One owner, exact identity/route selection,
bounded single-flight I/O, persistent ambiguity and explicit protected recovery.
No candidate connection manager, SDK backend, automatic retry/fallback or ON replay.
DiamondGUI method/status names are retained public contracts, not duplicate backends.

The configured target is shutter, application CH 0, KSC101 serial 68800777,
firmware allowlist 1.0.7, KEH3 middle bay 192.168.1.19:40305. APT channel is 1;
management port 40303 is unused. Hub serial/firmware are explicitly unknown.
config/shutter.ethernet.toml records the user-selected SH05R commissioning policy;
all notebooks load it through docs/examples/shutter_config.py. The generic
config/shutters.example.toml uses the same logical name and fictional identity,
with no write policy. Ignored local configuration/backups remain private.

D2XX and docked KEH3 use the same Manual/load/interlock/ownership checks. VCP
and KEH3 external USB OUT remain read-only. A protected Trigger-to-Manual change
requires explicit source_inhibited=True and persistent-mode policy permission,
sends OFF first, then confirms Manual/OFF. Interlock readback is configuration,
not measured contact continuity. Optical state is never inferred from output bits.

## Previous review validation (historical revision)

E183 / TEST-223: 160 source + 160 isolated installed-wheel tests PASS, zero
failures/errors/skips. Locked dependencies/build/install/import/help, source-wheel
parity, lint/format, missing/outdated lock refusal and passive config checks PASS.
All six notebooks PASS static schema/syntax/link checks; no hardware cells run.
records/direct-validation.json contains current source/config/tutorial hashes;
all inputs matched exact staged Git blobs before stage 1. E184 verifies 113 local
Markdown targets, four unchanged manuals, and JSON/XML evidence readability.
E186's final review manifest verifies 112 current local links, the wheel's current
README, six preserved notebook backups and absence of all 59 scoped cleanup targets.

Fixed incidental read-only shutdown OFF, unselected GUI Release affecting all
routes, and rest timing beginning before electrical OFF readback. Read-only faults
remain visible without actuation. Prior output/mode attempts retain explicit
cleanup obligations; passive close never sends OFF. Verification removes its own
successful disposable environment and retains failed-run diagnostics.

Stage 1: b9b2309 runtime, regression fixes, examples, migration/API/operator docs.
Stage 2: 2297162 manufacturer manuals, source/state interpretation and preserved
hardware evidence. Stage 3: c6f6661 final review/checkpoint and cleanup record.
E187 verifies all three stages published to origin/main at c6f6661, matching local
HEAD with a clean working tree. This follow-up checkpoint preserves that observed
result; final remote parity is checked again after its publication.
Publication is explicitly authorized by the current user request in PROJECT.md.

E185 supersedes the old unavailable-checkout assumption: the external DiamondGUI
checkout exists. Its 3 passive owner/factory tests PASS; all 26 isolated page tests
FAIL because the existing dirty shutter page is entirely commented out. Its
metadata still uses the old logical key and left-bay port 40304. No external
source/configuration was changed; restoring those edits is a separate user choice.
See records/diamondgui-current-integration.json and diamondgui-current-tests.xml.

## Historical hardware evidence and validity

E181 records one real SH05R ON/OFF cycle on 68800777/1.0.7 at the exact middle-bay
endpoint: OFF/Manual preparation, 2 s initial OFF pause, one ON with 1 s host hold,
priority OFF and release. Readback 0x2000 -> 0x2001 -> 0x2000; host ON-to-OFF
dispatch 1.0569156 s. Final recorded Manual/OFF, no journal fault and released
socket/claims. The user reported: "I did not observe it". Independent blade motion,
optical closure/timing and present transient state remain unknown.

This review changed controller/GUI code and normalized reviewed text to LF;
E181's hashes identify its historical revision, not the current package. Its
recorded physical result is preserved; current software tests do not requalify
physical operation. No repeat cycle is requested or planned. All six pre-normalized
notebook snapshots/outputs are preserved privately with hashes in
records/holistic-normalization.json. Existing earlier backups remain intact.

KSC101 Rev D, KEH3/KEH6 Rev E and APT Issues 36/42.1 are unchanged under
docs/manuals.
SRC-009 identifies the previously reviewed SH05R manual online; a local unchanged
SH05R PDF is still missing. E179's historical documentation ID collision is
resolved by current REQ-221; E181 is the exact control result, E182 the previous
manual/package review. Do not rewrite historical records to imply new tests.

## Requirements

Human criteria remain in PROJECT.md. PASS is scoped to its stated method/revision.

| ID | Source / short criterion | Method / evidence | Current result |
| --- | --- | --- | --- |
| REQ-201 | Objective: uv and SDK independence | TEST-201; E183 source/clean-wheel imports/help | PASS software; USB native deployment unqualified |
| REQ-202 | Exact identity and routes | TEST-202; E183 regressions; E170/E172 historical reads | PASS software; historical middle-bay identity; hub identity open |
| REQ-203 | Communication/framing | TEST-203; E183 framing/status tests; E181 historical control | PASS software; physical requalification open |
| REQ-204 | Modes and load limits | TEST-204; E183 policy/transition/rest regressions | PASS software; other modes/loads unqualified |
| REQ-205 | Freshness/deadlines | TEST-205; E183 stale/late/partial/quarantine tests | PASS tested cases; arbitrary same-type reply ordering unresolved |
| REQ-206 | Ownership/cancellation | TEST-206; E183 process/concurrency/priority tests | PASS software; native 250 ms target UNTESTED |
| REQ-207 | Ambiguity and cleanup | TEST-207; E183 faults/read-only/output obligation tests | PASS software; optical safety UNTESTED |
| REQ-208 | Direct KEH3 control | TEST-208/220; E181 exact middle-bay cycle; E183 routes | Historical selected-controller command/readback PASS; broader topology/recovery open |
| REQ-209 | Physical/local/TTL/interlocks | TEST-209; E191/E192 selected cycle, broader approved procedure required | PARTIAL: user-observed blade opening/return closed PASS for E191; local/TTL/contact behavior and optical calibration UNTESTED |
| REQ-210 | Drivers/persistence/endurance | TEST-210; approved deployment campaign required | BLOCKED: hardware, inventory and downtime/window |
| REQ-211 | DiamondGUI integration | TEST-211; E185 inspected current external suite | FAIL external page: 3 owner/factory PASS, 26 page FAIL; commented page/stale metadata |
| REQ-212 | Reproducible delivery | TEST-212; E183 source/wheel parity; E184 docs/manual hashes | PASS software; physical deployment incomplete |
| REQ-213 | Controller reference review | TEST-213; E161/E162 | Historical source review PASS |
| REQ-214 | QMI discovery review | TEST-214; E163 | Historical source review PASS |
| REQ-215 | Exact Ethernet notebooks/name | TEST-215; E183 six static/passive checks | PASS software; saved hardware outputs are historical |
| REQ-216 | Explicit D2XX/VCP inventory | TEST-216; E183 offline; E169/E170 native history | PASS software/enumeration history; USB open failed historically |
| REQ-217 | Bounded Ethernet diagnosis | TEST-217; E172/E178 historical live reads | Historical exact-controller read PASS; hub qualification open |
| REQ-218 | Earlier review/commit | TEST-218; E168 and checkpoint 9d486b3 | Historical scoped PASS |
| REQ-219 | Earlier source/API slimming | TEST-219; E178 | Historical scoped PASS; current software revalidated in E183 |
| REQ-220 | Exact Ethernet ON/OFF | TEST-220; E181 | PASS recorded controller cycle/release only; optics unobserved; current physical revision UNTESTED |
| REQ-221 | Repository manuals | TEST-221; E179/E184 hash checks | PASS four unchanged copies; local SH05R PDF missing |
| REQ-222 | Earlier manual/package review | TEST-222; E182 | Historical scoped PASS; current software revalidated in E183 |
| REQ-223 | Holistic review, prune, naming, staged push (derived) | TEST-223; E183-E187 and holistic-review/publication manifests | PASS prior scoped repository delivery; external deployment blockers documented |
| REQ-224 | Actual WebUI user flow, fixes and scripts | TEST-224; E188/E189, E191/E192 and passive checks | PASS selected WebUI/controller path and E192 human-observed opening/return closed; calibrated optics and full fault matrix open |
| REQ-225 | Manufacturer-style APT panel (derived; PROJECT.md active request) | TEST-225; E193/E194, feature matrix in docs/gui.md | PARTIAL: supported software paths and passive browser PASS; display/trigger I/O and Key/Ready contracts BLOCKED; new physical functions UNTESTED |

## Short plan and human action required

The supported APT WebUI implementation is validated; staged publication is next.
Full GUI functionality needs one specific external contract: manufacturer-confirmed
KSC101 MMI0x0520/trigger0x0523 payload fields/lengths/units/enums and Key/Ready status
mapping, including firmware applicability. Existing APT42.1 detail conflicts with
its model table (SRC-010); software checks cannot resolve the hardware contract.
Return the authoritative layouts/reference or packet evidence under a separately
approved capture procedure. Then implement those fields through the same APT
owner and rerun framing/settings/browser tests before any approved bench test.
No extra physical command is planned. Keep the external dirty integration intact until its
intended restoration/mapping is agreed. Full-project BLOCKED is not validated
deployment completion.

For the broader deployment, provide one approved commissioning handoff: the exact
current setup, independent source protection, allowed commands/rated limits and
window, independent blade/optical observation method (timing in seconds with clock/
detector calibration if required), hub identity/topology, and the intended
DiamondGUI page/configuration restoration decision. E181 establishes controller bits only; software cannot supply
these physical observations or decide whether to restore the externally edited page. Return
the agreed procedure/limits and measured results with units or explicit initial
state confirmation. Then revalidate affected software integration and perform only
the specifically authorized physical tests, recording fresh revision/configuration
and calibration validity. Driver/reboot/endurance work needs its own approved
all-instrument downtime/window. BLOCKED is not full-project completion.
