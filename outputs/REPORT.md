# Follow-up holistic review

REQ-228 / TEST-228: repository implementation, validation and generated cleanup
PASS. Implementation 460286f is pushed with remote parity verified; this checkpoint
delivers final documentation and evidence. Full hardware/deployment acceptance remains
blocked on the explicit gaps below. No device operation occurred in this review.

## Findings and fixes

| Supported finding | Final behavior | Evidence |
| --- | --- | --- |
| ON could leave an old OFF timer reusable when no ON poll followed | Every ON attempt invalidates prior rest; fresh external OFF starts a new interval | E203 baseline failure; E204 regression |
| An earlier output session could cause OFF during a later read-only shutdown | Confirmed-safe release retires output history; unresolved/faulted work remains protected | Healthy/faulted reconnect regressions |
| Protected recovery retained an old ON request/cleanup obligation | Verified recovery clears stale requests without output | Recovery/passive-shutdown regression |
| Cycle edits ignored recorded duty limits | Timing/count/duty checks precede I/O; exact duty boundary accepted | Negative/positive policy regressions |
| Mode/settings writes could pass despite disabling interlock requirement | Readback must retain the requirement; failure faults/retains uncertainty and attempts protective cleanup | Both write paths fault-tested |
| Explicit mode Stop retained an old native Start request | Requested state reflects the explicit OFF | Native-to-Manual regression |
| GUI drafts/assertions survived disconnect/reconnection | Target/generation scope clears old state; polling preserves same-connection edits | GUI callback regressions |
| Verification omitted a frozen real fixture and trusted pytest exit alone | Fixture hashed; failed/skipped/empty required suites refused and totals retained | Provenance/report regressions |

Removed duplicated GUI callback test plumbing in favor of one helper. Replaced
repeated checkpoint/report history with current conclusions and links to durable
records. Existing public owner/status names and the explicit raw diagnostic are
retained contracts, not duplicate backends. SDK/probe/notebook-wrapper runtime
paths were already removed and remain absent. No live policy/configuration or
external DiamondGUI source was changed.

## Validation and cleanup

**228 source + 228 isolated installed-wheel tests PASS**, zero failures/errors/
skips. Locked build/install/import/help/config checks, lint/format, exact Python/
CSS parity and frozen-fixture provenance PASS. All six notebooks PASS static
schema/syntax/link checks; no device cell ran. The source/fault suite uses software
fixtures and localhost loopback and establishes no physical qualification.

Baseline evidence records 8 failing owner cases and 4 failing GUI cases before the
fixes. Final and baseline artifacts are separate. Command:

```powershell
uv run --locked --offline --group dev --extra gui python -B scripts/verify.py --record-prefix followup-review-
uv run --locked --offline --group dev --group notebooks --extra gui python -B scripts/verify_notebooks.py
```

Removed **32 verified generated cache/pytest directories, 699 files / 174667 bytes**.
Every absolute target was checked for workspace containment, links, unchanged
contents and tracked files before native PowerShell deletion. No tracked file
was deleted. Environments, local config, manuals, reference tooling, real records,
backups and runtime state were preserved. Ambiguous tmp history was retained.

Evidence: [validation manifest](../records/followup-review-validation.json),
[source/wheel checks](../records/followup-review-direct-validation.json),
[static notebooks](../records/followup-review-notebooks.json),
[cleanup inventory/results](../records/followup-review-cleanup.json),
[records](../records/RECORDS.md).

## Migration and physical validity

Restart the released WebUI owner and reload the browser before using the reviewed
source. The previously running 9860 preview uses pre-review code; it was last
observed released after E200 and was not polled or replaced here. There is no
automatic takeover or background hardware connection. See [cutover](../docs/cutover.md).

E200's two real Manual WebUI/controller cycles remain PASS at their recorded
source/configuration; final Manual/OFF was followed by release. E202's user report,
"I did not observe both cycles", leaves complete two-cycle blade motion unverified.
The original raw capture and hashes remain intact; the human follow-up is separate.
E191/E192's earlier individually observed cycle does not calibrate optics.

Current owner/GUI changes have software validation only. Native timing/priming,
EEPROM restart persistence, local/TTL/interlock behavior, optical calibration and
broader driver/hub deployment are not newly qualified. Display/trigger-I/O and
Key/Ready need trustworthy KSC101-specific contracts. The external DiamondGUI
page/mapping failure is the historical E185 result and was not rechecked here.
These remain visible in [STATE.md](../STATE.md) and the
[physical acceptance plan](../docs/HARDWARE_VALIDATION.md).
