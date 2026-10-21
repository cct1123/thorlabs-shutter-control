# Historical evidence archive

hardware-2026-10-20.zip preserves136 original files: dated diagnostic responses,
firmware/interlock/sequence evidence, GUI/shutdown traces, earlier project/state/
report checkpoints, superseded plans and acquisition scripts. Original bytes are
preserved. manifest.json lists each member's size and SHA256; the adjacent
.zip.sha256 file hashes the whole ZIP. No vendor installer or installed runtime
is bundled. Historical files are reference data, not current operating authority.

Verify before extraction:

```powershell
Get-FileHash records/archive/hardware-2026-10-20.zip -Algorithm SHA256
Get-Content records/archive/hardware-2026-10-20.zip.sha256
python -m zipfile -l records/archive/hardware-2026-10-20.zip
```

| Evidence | ZIP member |
| --- | --- |
| Full E001-E078/D records | records/RECORDS.md |
| Firmware1.0.7/identity repair | records/firmware-post-usb-2026-10-20.json |
| Four-state interlock/key matrix | records/interlock-four-state-comparison-2026-10-20.json |
| Five-cycle raw/user observation | records/sdk-five-cycles-2s-2026-10-20.json and sdk-five-cycles-observation-2026-10-20.json |
| Stage5 shutdown | records/stage5-confirmed-hardware-2026-10-20.json |
| Stage6 Ctrl+C closure/release | records/stage6-confirmed-server-2026-10-20.json and stage6-post-shutdown-2026-10-20.json |
| Redesigned GUI/browser run | records/gui-ux-summary-2026-10-20.json, gui-ux-hardware-2026-10-20.json and gui-ux-browser-motion-2026-10-20.json |
| Original human criteria/checkpoints | PROJECT.md, STATE.md, outputs/REPORT.md |
| Superseded command/firmware/development reviews | docs/COMMAND_REVIEW.md, docs/KSC101_FIRMWARE_UPDATE_REVIEW.md, docs/DEVELOPMENT_PLAN.md |

Filename-only continuations above have the same records/ prefix. Inspect/extract
historical material outside the active document tree; do not run old acquisition
scripts as current procedures. Current interpretation is in
[hardware-validation.json](../hardware-validation.json) and [STATE.md](../../STATE.md).
