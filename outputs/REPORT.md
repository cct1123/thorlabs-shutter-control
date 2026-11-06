# Holistic review and migration delivery

6 November 2026. **Package review PASS; integrated deployment remains blocked.**
The package has one shared owner and direct APT driver for Python, CLI, GUI and
six real Ethernet notebooks. The review performed no device operation.

## Defects corrected

| Finding | Correction | Evidence |
| --- | --- | --- |
| GUI shutdown could send OFF after a read-only session when a write policy existed | Cleanup depends on prior output/mode attempts; read-only faults are reported without actuation | E183 owner regressions, with/without policy and fault |
| Release with no selected GUI target could disconnect every route | All six controls require an exact configured name before dispatch | E183 Flask callback cases for missing/unknown targets |
| Minimum OFF rest started at command dispatch | Start rest after fresh electrical OFF readback | E183 delayed-transition regression; early ON refused |
| Candidate connection manager, analyzer/probe CLI and gated example duplicated current workflows | Removed superseded paths; one owner, TOML configuration and static notebook verification | [Migration replacements](../docs/cutover.md) |
| Generic config target and notebook-guide API differed from current usage | Consistent shutter name; guide uses shutter_config.SHUTTER | Static/passive setup and CLI checks |
| Current guides cited the manual-copy record as the live ON/OFF result | Corrected links to E181 and separated historical/current validation | E184 documentation audit |
| External DiamondGUI checkpoint incorrectly said its checkout was unavailable | Live inspection found a commented-out page and stale metadata; documented current deployment failure without altering the separate dirty checkout | E185: 3 owner/factory PASS, 26 page FAIL |
| Verification accumulated disposable environments | Remove successful-run work; retain failed-run diagnostics; avoid subprocess Python/Ruff caches | Successful full verification and scoped cleanup manifest |

The DiamondGUI public method/status surface remains intact. No SDK backend,
constructor shim, implicit transport fallback, command retry or ON replay remains.
Runtime Python shrank from 1,702 to 1,588 lines relative to 9d486b3: 114 net lines
removed (6.7%), including the superseded candidate path.
Electrical output, operating state and optical observation stay separate. VCP and
KEH3 external USB OUT control remain unavailable; writes require the reviewed
load policy and Manual/interlock/identity/ownership checks.

## Final software evidence

**160 source tests + 160 isolated installed-wheel tests PASS**, with zero failures,
errors or skips. Locked dependencies, lint/format, clean build/install/import/help,
source-wheel parity, negative lock cases and passive configuration validation pass.
All six notebooks pass schema/syntax/link checks without executing their cells.
Tests use software byte transports and localhost; they establish no physical result.

Commands:

```powershell
uv run --locked --offline --group dev --extra gui python scripts/verify.py
uv run --locked --offline --group notebooks python scripts/verify_notebooks.py
```

All verification input hashes matched the staged Git blobs. Reviewed changed text
was normalized to the repository's LF policy, with six byte-exact notebook backups
and saved outputs retained privately. Four manufacturer PDFs remain unchanged and
match their registered SHA-256 values. 112 local Markdown targets exist; all
reviewed JSON/XML evidence parses. See [E183/E184](../records/RECORDS.md),
[source/wheel manifest](../records/direct-validation.json),
[source tests](../records/offline-tests.xml), [wheel tests](../records/wheel-tests.xml),
[static notebook checks](../records/notebook-validation.json),
[manual integrity](../records/manuals-verification.json) and
[normalization/backups](../records/holistic-normalization.json).
The [final review manifest](../records/holistic-review.json) records the current
package PASS and external integration FAIL together.

## Cleanup and delivery

Stage 1: b9b2309, runtime migration, owner/GUI fixes, examples and operator/API docs.
Stage 2: 2297162, manufacturer manuals, source/state interpretation and historical
evidence. The final checkpoint/cleanup commit and remote synchronization are
recorded in STATE.md and the engineering delivery record.

Only inventoried generated cache/test/build paths are removed. The environment,
current wheel, manuals, records, private notebook backups, reference originals and
runtime ownership state are preserved. Investigation scripts, source preimages
and ambiguous temporary history remain available. Logical byte totals do not
measure physical disk savings because caches and environments can share hardlinks.
See [cleanup inventory/results](../records/holistic-cleanup.json).
Cleanup removed 59 targets, including 178,212 generated files from the main
inventory (5,317,497,320 logical bytes); all removals completed without failure.

## Historical hardware evidence and remaining limits

[E181](../records/ethernet-control-live.json) records one real SH05R cycle on
KSC101 68800777, firmware 1.0.7, KEH3 middle bay 192.168.1.19:40305: protected
OFF/Manual preparation, 2 s initial OFF pause, one ON with a 1 s host hold,
priority OFF and release. Electrical bits were 0x2000 -> 0x2001 -> 0x2000;
ON-to-OFF host dispatch was 1.0569156 s. Final recorded state was Manual/OFF.
The user did not observe blade motion. This is historical evidence for its recorded
hashes; the review changed controller/GUI code and did not repeat or requalify
physical operation. Present state, independent optical closure/timing, key/contact
continuity, local/TTL behavior, hub identity/recovery, other topology, native
250 ms dispatch, driver persistence, reboot and endurance remain unverified.
A manufacturer design mapping is not an independent optical measurement.

The four repository manuals cover KSC101, KEH3/KEH6 and APT Issues 36/42.1;
[the SH05R source](../docs/sources.md) was reviewed online earlier, but its unchanged
local PDF is still missing. The external DiamondGUI checkout is present and dirty:
3 passive owner/factory tests PASS, but 26 page tests FAIL because its shutter
page is entirely commented out. Its metadata still selects the old name and
port 40304. No external edits were made. See [current integration findings](../records/diamondgui-current-integration.json)
and [failing page tests](../records/diamondgui-current-tests.xml). The historical
29-case PASS is superseded. In-repo owner/schema, CLI and GUI tests pass. [STATE.md](../STATE.md) records the exact human dependency
and resumption conditions. The full engineering project is BLOCKED, not COMPLETE.
