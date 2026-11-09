# Engineering state

## Current checkpoint

8 November 2026. REQ-274 / TEST-274 documentation refresh COMPLETE (E256).
README now leads with launch/operation and links to detailed contracts. Setup
documents current CLI effects/defaults/shutdown, and the notebook guide no longer
describes a removed source-confirmation flag. No runtime/configuration/notebook
cell change. User follow-up "commit push" authorizes publication to origin/main,
including the three prior local review commits. Git history identifies the final
documentation commit; equality with the remote main ref is the publication check.
Documentation commit: f45f77b. Publication is BLOCKED: automatic approval review
rejected git push origin main as sensitive external egress to the default branch,
requiring explicit approval of the payload/destination and prior commits (E258).
No push ran. This local handoff checkpoint is an additional publication commit.
Prior REQ-273 review is complete: runtime ddda81d, docs/evidence 7c2f4d4,
checkpoint 5a6ae37 (D094/E254/E255).
The broader engineering project remains BLOCKED on the independent physical,
manufacturer-contract and external-integration gaps below. No hardware/lab-network
I/O, existing-owner/server change or external checkout edit is part of publication.

391 source + 391 isolated-wheel tests PASS, zero failures/errors/skips; all 41
verifier inputs match records/docs-refresh-direct-validation.json. Documentation
audit: records/docs-refresh-audit.json. Historical evidence is retained.
The prior review reproduced three regressions before fixes (E254 / D094):
retained output faults were suppressed after successful shutdown OFF; the GUI
re-enabled an unusable hardware-disconnect control; empty-text CLI interruptions
lost their exception name. All are fixed;165 affected tests and full verification pass.

Architecture: controller/protocol/transport are the three core layers, with
package exports, CLI and Dash GUI. One exact-target shared owner controls
identity/route claims, deadlines, readback, faults and cleanup. Removed convenience
methods/status fields require the migration in docs/python-api.md.

Explicit Stop/OFF clears faults only after fresh OFF/interlock verification.
Reads and automatic cleanup/shutdown retain faults; shutdown also reports them
after successful OFF and still attempts other targets. Failed verification
retains the journal. A poisoned stream needs deliberate Release/Connect before
another explicit Stop. Source confirmation is no longer required for settings,
native Start or mode selection. Hardware disconnect is protected and API-only;
the unusable GUI control and callback are removed. No optical state is inferred.

REQ-270 status flags remain software PASS; REQ-271 full Key/Ready/actual native
Activity remains PARTIAL/BLOCKED. interlock_status_bit/channel_enabled_bit decode
reported0x1000/0x80000000 from existing0x042A replies with the electrical timestamp;
they never authorize output or establish key/readiness/optical/native activity.
Host-only/disconnected values are None. Full contract: docs/status-readback.md.

REQ-272 standalone Shutdown GUI server is included in combined wheel validation.
The localhost listener drains accepted callbacks, then runs output cleanup and
release. Embedded create_app() omits it. Pending requests can delay exit; it is
not an emergency Stop. No existing server was stopped/restarted by this review.

## Status-capability evidence and remaining implementation gap

E250 / TEST-268 static reference review is historical; E252 / TEST-270 implements
the documented flags. Exact vendor API exposes KeyEnabled/OperatingState but
neither API declarations nor RevF manual p29 supplies verified raw mappings for
Key/Ready/actual native state. Saved firmware1.0.7 raw0x04CD value0 conflicts with
legacy Active1/Inactive2 decoding. Static reflection-only inspection of extracted
vendor wrapper getters delegates to native accessors and does not resolve the
protocol mapping. No installer, vendor function, constructor or SDK runtime ran.
Provenance/replay: records/status-readback-{native-reference,reference-replay}.json.

## Current working configuration

Default GUI: uv run shutter-control gui from repository root, tracked
config/shutter.ethernet.toml, localhost9860. Explicit --config/--port overrides
remain. Startup is passive; no automatic selection, connect, takeover or replay.
Other CLI commands default to shutters.local.toml.

Exact configured target: shutter / SH05R / KSC10168800777 / firmware1.0.7 /
KEH3 middle192.168.1.19:40305. Hub identity remains unknown. Configuration is
not a claim of current physical state; no live state was queried this session.

- min_off_s=0.0: no extra software OFF pause for this profile.
- qualified_modes=manual/single/auto/triggered: no default-profile Manual-only gate.
  Custom profiles still enforce their own configured activation modes.
- Mode selection: no software source confirmation or separate mode permission;
  persistent-mode legacy field/CLI confirmation option accepted for compatibility.
  Selection still requires electrical OFF/interlock, sends/verifies OFF first,
  then confirms requested mode/OFF/interlock; actual mode changes persist.
- Native Start requires cycle/load checks, no prior
  pending Start and explicit Stop. allow_continuous_cycles=false/max_cycle_count1;
  Triggered priming remains blocked unless its independent conditions are met.
- Settings and EEPROM permissions remain false. Interlock/OFF checks, identity,
  ownership and protocol ambiguity checks remain; explicit verified Stop/OFF can reset faults.
- Timed pulse cap50s; GUI pulse1s. Ordinary Manual ON has no automatic shutoff.
- Healthy refusals retain only previous same-connection dated feedback with its
  original timestamp and explicit historical label; faults/disconnects/new
  connections do not reuse it. No extra I/O is done by refusal handling.

## Current validation

E256 / TEST-274: uv run --locked --offline --group dev --extra gui python -B
scripts/verify.py --record-prefix docs-refresh-
391 source + 391 isolated installed-wheel tests PASS, zero failures/errors/skips.
Locked dependencies, Ruff lint/format, exact wheel Python/CSS parity, passive
import/help/config, missing/outdated lock rejection and static tutorials PASS.
All 41 hashed inputs match; see records/docs-refresh-direct-validation.json.
The tests use simulated transports and localhost only, including real localhost
server shutdown. No browser screenshot or physical validation is claimed.

records/docs-refresh-audit.json checks current local links/anchors, packaged
README, passive CLI help/configuration and input parity: 131 local links and
10 heading anchors PASS across 22 Markdown documents. No notebook cells,
manuals or runtime/configuration files changed. Prior records/repo-review-audit.json
preserves the E254 manual/notebook audit against review base 174d23b. E254's
README/tutorial-guide hashes are historical after this refresh; E256 supplies
current input evidence. Earlier E252/E253 results remain historical.

## Current requirement map

Human criteria: PROJECT.md. PASS is limited to the recorded method/configuration;
source changes do not revalidate old physical measurements or consumed authority.

| ID | Criterion | Method/evidence | Current result |
| --- | --- | --- | --- |
| REQ-274 | Refresh README/setup/tutorial documentation | TEST-274; E256; links/anchors, passive examples, packaged README and source/wheel | COMPLETE documentation/software;391+391 |
| REQ-273 | Whole-repository review, pruning and staged commits | TEST-273; D094/E254/E255; source/wheel/audit and Git history | COMPLETE software/local publication;391+391 |
| REQ-272 | Standalone GUI shutdown | TEST-272; D093/E253; current E256 source/wheel | PASS software;391+391 integrated |
| REQ-270 | Implement documented status flags | TEST-270; D092/E252; literal/fake/GUI/source/wheel | PASS software;389+389 |
| REQ-271 | Full Key/Ready/actual native Activity | TEST-271; E252; manufacturer/raw-mapping comparison | PARTIAL/BLOCKED; no guessed mapping |
| REQ-269 | Remove source checklist; verified explicit Stop resets fault | TEST-269; D091/E251; records/gui-fault-reset-tests.xml | PASS software;389 tests; running owner unchanged |
| REQ-267 | Review/fix integrated consistency | TEST-267; D090/E249; full source/wheel/static tutorials | PASS software;370+370 |
| REQ-264 | Remove default Manual-only activation gate | TEST-264; E247/E249; profile-based native simulations | PASS software; physical native behavior untested |
| REQ-265 | Remove separate mode permission | TEST-265; E247/E249; false/true legacy flags, Stop/readback | PASS software |
| REQ-266 | Remove interlock/electrical-OFF prerequisites | PROJECT.md annotated request | DECLINED, not implemented; prerequisites retained |
| REQ-263 | Remaining software guardrail audit | TEST-263; E246; static/passive inventory | PASS historical audit; E247/E249 supersede mode restrictions |
| REQ-262 | Remove extra software OFF pause | TEST-262; E245/E249; zero-pause profile/fake clock | PASS software |
| REQ-261 | Diagnose0.94s Manual ON refusal | TEST-261; E248 alias for duplicate E244 diagnosis; fake clock | PASS diagnosis; GUI feedback loss fixed E249; tracked pause now zero |
| REQ-260 | Remove mode source confirmation | TEST-260; E243/E249; unchecked GUI selection | PASS software |

## Earlier requirements and evidence

The following results are historical scoped checkpoints, preserved for
traceability. Their test counts/revisions are not current full-system validation;
E256 is the current complete software result. E244 refers to code reduction;
E248 aliases the older Manual ON diagnosis that also used E244 by mistake.

| ID | Short criterion / source | Method/evidence | Result |
| --- | --- | --- | --- |
| REQ-259 | Implement reduction (PROJECT.md 8 November) | TEST-259; D089/E244; command order, schema/API/GUI and final source/wheel | PASS software: 359 source +359 wheel; desktop/mobile passive; no hardware operation |
| REQ-258 | Codebase reduction plan (PROJECT.md 8 November) | TEST-258; E242; E241 findings, source inventory and stage/validation review | PASS plan; subsequently implemented under REQ-259 |
| REQ-257 | Controller redundancy review (PROJECT.md 8 November) | TEST-257; E241; full source/caller inspection, fake frames, 213 regressions | PASS scoped review; candidates reported, no implementation change |
| REQ-256 | README/simple GUI launch (PROJECT.md 8 November) | TEST-256; D088/E240; defaults/overrides/passivity, real localhost smoke and source/wheel | PASS: 59 application, 355 source +355 wheel; no hardware operation |
| REQ-255 | Actual WebUI redo (PROJECT.md 8 November) | TEST-255; D087/E238/E239; software regressions, source/wheel, actual bounded browser run | PASS bounded electrical/WebUI: one pulse, final Manual/OFF/no fault/released; independent motion unobserved |
| REQ-254 | GUI electrical feedback under fault (PROJECT.md 8 November) | TEST-254; E237; callback regressions, saved actual replay, source/wheel | PASS GUI/software: 102 affected, 351 source +351 wheel; later E238 resolves controller P1 |
| REQ-253 | Remaining-issue review (PROJECT.md 8 November) | TEST-253; E236; E237/E238 follow-up regressions | Review complete; both code findings fixed in software; physical closure open |
| REQ-252 | Actual user-style WebUI debugging (PROJECT.md 8 November) | TEST-252; D086/E233; actual browser/TCP, regressions, final source/wheel | Historical electrical/software PASS; blade motion unobserved; later lockout recovery recorded by E239 |
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
| REQ-207 | Ambiguity/cleanup | TEST-207; REQ-255 interruption regressions and source/wheel; E236 pre-fix evidence | PASS software for empty-error lockout/reconnect/recovery; physical safety unqualified |
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

## Physical evidence and remaining gaps

E239 records the last bounded electrical/WebUI run on its recorded revision:
one approved1s host pulse, final Manual/OFF0x2000/interlock required/no fault at
2026-11-09T03:34:39.878424 UTC, followed by release/server stop. Camera No/unsure;
blade motion was not independently observed. Source/config have since changed;
this is historical evidence, not proof of current state or native performance.
Earlier E191/E192 records one human-observed blade cycle; none establishes
optical timing/extinction calibration. All earlier cycle allowances are consumed.

Open acceptance: independent optical/blade measurement and timing/extinction
calibration; native modes/triggered priming/settings/EEPROM physical validation;
KSC101-specific MMI/trigger layouts and Key/Ready mapping; USB driver/reboot/
endurance/deployment; hub identity; external DiamondGUI adapter/page migration.
The external checkout was not changed or revalidated. E185's failed mapping/page
check remains historical. Software permissions do not establish physical qualification.

## Next action and authorization

No further documentation/test action is required for the completed REQ-274
refresh. Commit/push to origin/main is authorized by the user's follow-up;
obtain the explicit payload/destination approval in Human action required, then
push and verify the final remote ref and clean worktree. No
hardware operation is pending. Keep previous captures and consumed cycle
allowances historical. A running owner may have older source/configuration.
Deployment requires normal Stop/Release followed by deliberate restart/reload,
with no automatic takeover; no live state was inspected here. Explicit Stop/OFF
must verify OFF/interlock to clear a live fault. Never delete ownership journals
to imitate verification. Broader physical acceptance remains BLOCKED separately.

## Human action required

Publication: f45f77b contains the validated documentation refresh; ddda81d,
7c2f4d4 and 5a6ae37 contain the earlier runtime/configuration/tests/tutorial,
documentation/evidence and review checkpoint. Automatic approval review rejected
pushing these to git@github.com:cct1123/thorlabs-shutter-control.git main as
sensitive external egress without explicit payload/destination approval (E258).
Approve publication of those four commits plus this blocked-handoff checkpoint
to that exact origin/main. No hardware authority is requested. After approval,
retry the normal push and compare remote main with HEAD; no force push.

For the active REQ-271 status gap, one precise dependency remains:
1. Known: documented status flags are implemented/tested; vendor Key/Ready/actual
   OperatingState exist but verified raw mappings are absent/conflicting (E252).
2. Blocked: source, API/manual and wrapper metadata cannot establish firmware1.0.7
   raw bytes without speculation; safe supported software work is complete.
3. Needed: manufacturer-confirmed KSC101 firmware1.0.7 request/reply byte layouts
   and bit/value definitions for KeyEnabled, Is Ready and actual OperatingState/
   ToggleCount, or an existing passive vendor capture paired with those states.
4. Return model/firmware/mode, query/reply hex, displayed-state timestamps and
   provenance. Documentation/existing captures only; no new hardware action is
   requested or authorized by this handoff.
5. Next: create literal independent fixtures, implement verified driver/owner
   mappings, then prepare a separately authorized read-only comparison.
Details: docs/status-readback.md. This dependency is distinct from broader
physical/deployment acceptance described below.

None for the REQ-274 documentation refresh. Full physical/deployment acceptance
is blocked because output bits cannot establish blade position or optical timing,
and no independent calibrated observation method/new controlled window exists.
To resume that separate work, provide the observation interface/method, required
units/calibration and an explicitly bounded setup/command/hold/cycle window.
Return the measurement capability and protected setup conditions; next action is
to prepare a concrete measurement procedure before any newly authorized motion.
Do not reuse past cycle allowances or infer closure from a disconnected GUI.
