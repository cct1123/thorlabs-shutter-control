# Combined review and delivery

8 November 2026. REQ-251 / TEST-251: **COMPLETE, software/publication scope** (D085/E231/E234).
Full physical and external deployment acceptance remains **BLOCKED**.
Implementation/docs/evidence published as `2bc53e2`; remote HEAD equality
verified (E235). The separate active hardware campaign remains uncommitted.

The reviewed v2 package retains three core modules: controller.py owns validated
configuration, device commands, policy and ownership; protocol.py owns APT
framing/deadlines; transport.py owns explicit routes and byte I/O. GUI and CLI
remain separate entry points. Retired modules have no compatibility wrappers.

The review fixes three demonstrated flaws:

- A stale reply queued behind 4096 bytes of unsolicited events could satisfy a
  new query. Queries now drain every arrived chunk before dispatch, within the
  original deadline. Queued replies and incomplete tails are refused; continuous
  traffic times out. This does not solve arbitrary delayed replies without APT
  transaction IDs.
- WebUI Release could check an idle snapshot, wait for the lock, then close a
  connection after another callback started output. Its pending ON/Start check
  now runs under the same owner lock as release. Ordinary close remains passive.
- Generic success notices could hide a persistent owner fault. Fault lockout now
  remains visible in both main and Settings notices, including polls and Release.
  Readable electrical data still cannot clear lockout or authorize output.

Release checking has one canonical owner implementation. Cycle-duty/count
checks share one repetition branch. The preceding pruning removes retired core
modules, duplicate notebook verification, unsupported GUI placeholders and obsolete
review documents. Historical evidence and notebook outputs are retained; Issue 36
is preserved byte-for-byte in Git history while Issue 42.1 remains local.

The combined GUI exposes documented channel/bay/LED reads, guarded LED settings,
interlock enforcement, update requests/raw events and explicit hardware disconnect
through ShutterHub. Last-read/request labels do not claim optical feedback or
streaming acknowledgement. The UI retains one exact-target dispatch path. E230 records passive desktop/phone
layout checks; the final review also inspected the four saved screenshots.

Version 2 uses a flat ShutterStatus. Repository consumers/tutorial source are
migrated; saved notebook outputs remain historical. External DiamondGUI still
needs the documented schema and route/page migration before deployment.

**341 source + 341 isolated-wheel tests PASS**, zero failures/errors/skips.
All 39 verifier input hashes match. Source and installed-wheel checks use
software transports, saved observations and localhost loopback only. They check
identity/routing, interlocks/load policy, native permissions, cancellation,
partial writes, cleanup/recovery, lock contention, GUI callbacks, dependency lock,
lint/format, package parity, passive import/help/config and six static notebooks.
No live controller was contacted; no running owner was restarted or taken over.

Evidence:

- [Three pre-fix failures](../records/final-review-reproductions.xml),
  [passing protection regressions](../records/final-review-regressions.xml).
- [Final source/wheel verifier](../records/final-review-direct-validation.json),
  [source tests](../records/final-review-offline-tests.xml),
  [wheel tests](../records/final-review-wheel-tests.xml).
- [Documentation/artifact audit](../records/final-review-audit.json),
  [observed publication](../records/final-review-publication.json),
  [decisions and observations](../records/RECORDS.md), [checkpoint](../STATE.md).

The selected SH05R / 68800777 / 1.0.7 / KEH3 middle-bay configuration retains
Manual-only output activation, 2 s OFF rest, protected persistent mode selection,
and disabled native Start/priming/settings/EEPROM permissions. Interlock disable,
unverified motor/MMI/trigger layouts, automatic ON replay and route fallback
remain excluded. Electrical readback does not establish blade position or optical
timing. Previous physical cycle allowances are consumed.

The existing shutter-control.exe remains in use; its environment was not synced.
The reviewed wheel must be deployed deliberately after stopping/releasing the
existing owner. Calibration, new physical validation, hub identity/topology,
driver/persistence/endurance work and external DiamondGUI cutover remain open.
See [operation/API](../docs/python-api.md), [GUI](../docs/gui.md),
[cutover](../docs/cutover.md) and [physical acceptance](../docs/HARDWARE_VALIDATION.md).
