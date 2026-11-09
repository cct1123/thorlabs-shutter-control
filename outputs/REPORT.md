# Reviewed shutter-control system

8 November 2026. REQ-273 / TEST-273 software review validated:391 source and391
isolated-wheel tests PASS, zero failures/errors/skips. REQ-273 is COMPLETE for
software/local publication: runtime/configuration/tests/tutorial commit ddda81d,
documentation/evidence commit 7c2f4d4, then this final checkpoint/audit stage.
Full physical/deployment acceptance remains BLOCKED. No hardware/lab-network
I/O, existing-owner/server operation, external checkout edit or push occurred.

## Resulting behavior

Run `uv run shutter-control gui` from the repository root after
`uv sync --locked --extra gui`. It loads config/shutter.ethernet.toml on
127.0.0.1:9860. Config/port overrides remain. Startup is passive; selection and
Connect are explicit. Release closes communication without output commands.
Stop/Release the existing owner before deliberate restart and browser reload.

The configured setup is SH05R / KSC10168800777 / firmware1.0.7 / KEH3 middle
192.168.1.19:40305. Hub identity is unknown; configuration does not establish
present physical state. controller/protocol/transport form the three core layers;
Python, CLI, Dash GUI and tutorials use the same owner without an SDK runtime.
External consumers need the [API/schema migration](../docs/python-api.md#status-schema-migration).

| Operation | Current contract |
| --- | --- |
| Mode selection | Manual/Single/Auto/Triggered without source confirmation or separate mode permission; changes persist; fresh OFF/interlock, Stop and readback remain |
| Activation | Tracked profile allows all four modes; cycle/load/OFF/interlock/ownership/fault checks remain; custom qualified_modes still apply |
| Triggered priming | Requires cycles0 and continuous-cycle permission, false in the tracked profile |
| Settings/EEPROM | Separate permissions remain false in the tracked profile; writes require Manual/OFF/interlock and exact readback; no source checkbox |
| OFF interval | Tracked min_off_s=0; custom positive intervals remain enforced; every ON attempt invalidates prior rest |
| Manual ON / pulse | Continuous-duty load required; ordinary ON has no automatic shutoff; pulse has a host hold at most50s, GUI1s; neither is calibrated exposure |
| Fault reset | Explicit Stop/OFF clears fault/journal only after fresh OFF/interlock; failed verification, reads and automatic cleanup retain faults |
| Shutdown | Standalone button drains accepted requests, attempts output cleanup and release; retained faults produce failure even after OFF; embedded apps omit the button |
| Hardware disconnect | Protected Python API only; ordinary GUI Release remains passive |
| Status | Dated electrical output and literal interlock/channel flags; host Native request is separate from actual native activity |

## Review findings and pruning

Three before-fix regressions failed as expected; fixes pass165 affected tests:

- Shutdown could return successfully while retaining a prior output fault after
  OFF. It now aggregates that fault and still cleans remaining targets.
- Rendering re-enabled the disabled hardware-disconnect button, whose required
  source assertion no longer existed in the GUI. Removed its widget, action and
  callback dispatch; the protected Python API remains covered by regressions.
- Empty-text CLI interruptions produced an empty diagnostic. They now include
  the exception type, including KeyboardInterrupt.

Reconciled stale source-confirmation/mode-permission descriptions in the README,
configuration, GUI help, API, interface, architecture, cutover and setup guides.
Updated notebook4's current policy description and marked old screenshots and
physical tests as historical. Saved notebook outputs and metadata are unchanged.
Pruning also integrates the earlier reviewed convenience-API/status reduction
and shared GUI field builder. Historical evidence and unrelated artifacts remain.
Fourteen historical JPEG captures retain their original .png filenames for
capture/hash references; the audit lists this non-critical archival limitation.

## Validation and evidence

Command: `uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix repo-review-final-`

Source/wheel software suites each pass 391 tests. Lock/lint/format, exact Python/CSS
wheel parity, passive import/help/config, negative lock checks and static tutorial
checks PASS. All 41 verification input hashes match. Real localhost tests cover
standalone shutdown without an instrument. Software transports do not prove real
wiring, optical behavior or native driver timing. No new visual browser check ran.

- [Integrated verification](../records/repo-review-final-direct-validation.json)
- [Source tests](../records/repo-review-final-offline-tests.xml), [wheel tests](../records/repo-review-final-wheel-tests.xml)
- [Before-fix reproductions](../records/repo-review-reproduction-tests.xml), [affected regressions](../records/repo-review-fixed-tests.xml)
- [Documentation/manual/notebook audit](../records/repo-review-audit.json)
- [Durable findings and decisions](../records/RECORDS.md#e254---repository-review-validation--test-273)

Older validation campaigns retain their exact revisions and conditions. E252's
389+389 status result and E253's391-source shutdown result are included in this
new integrated verification; their old input hashes are not current validation.

## Remaining acceptance gaps

REQ-270's documented flag decoding passes software tests. The full vendor
Key/Ready/actual native Activity request REQ-271 remains PARTIAL/BLOCKED. Reported
masks0x1000/0x80000000 do not establish key position, readiness or interlock
continuity; raw0x2000 is not repurposed as such a flag. Host-only/disconnected
values remain None; retained healthy-refusal readings keep their original date.
Manufacturer-confirmed firmware-specific raw definitions or an existing passive
capture paired with vendor states are required. See the
[status contract and exact resumption condition](../docs/status-readback.md).

E239's last approved1s Manual pulse ended with Manual/OFF/interlock and release
on its recorded revision; its cycle allowance is consumed and blade motion was
unobserved. Earlier E191/E192 records one human-observed cycle. Neither establishes
calibrated timing/extinction or validates the current zero-pause/all-mode profile.
Native modes/triggered priming/settings/storage, MMI/trigger layouts, hub identity/
recovery, USB driver/reboot/endurance and external DiamondGUI migration remain
open. The last external check E185 failed26 page cases; that checkout was neither
changed nor revalidated. [STATE.md](../STATE.md) preserves the exact dependencies.
