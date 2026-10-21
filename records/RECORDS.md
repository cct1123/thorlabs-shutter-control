# Baseline evidence and decisions

## D038 - Current baseline, REQ-101

Source: user request quoted in PROJECT.md. The current USB/LAN system becomes the
only maintained baseline, with no compatibility adapters or alternate old workflows.
Remove obsolete staged diagnostics, duplicate scripts, supervisor reports, old
screenshots and incremental development records. Keep the two notebooks, current
tests, current guides and compact [physical evidence](hardware-evidence.json).

Historical intent, checkpoints and records are recoverable at Git5ab1f91 and in
hash-verified ignored inputs/private/baseline-5ab1f91. The private executed LAN
notebook and .venv are preserved. These archives are provenance, not active code.

## E138 / TEST-148 - Integrated software baseline

Expected: current USB/LAN/GUI/TTL/identity/ownership/error/cleanup/notebook contracts
pass with source and extracted wheel; removed single-controller GUI adapter and
operator-confirmation API are absent. No real SDK/network/device operation.
Observed: source217 passed,1 optional real-SDK skip; extracted wheel217 passed,
1 skipped. Wheel import origin verified under its extracted directory; all6
packaged Python/CSS files match source bytes. Ruff lint/format PASS. Three fake
controllers complete Manual/TTL/readback/cleanup; every handle released. The new
GUI boundary regression rejects direct-controller construction and missing serial
before device I/O. Remaining callback tests cover all modes, TTL, discovery,
partial failure, stale choices, identity, ownership and fault/interrupt cleanup.
The2 notebooks run12 fake scenarios, including errors/interrupts/passive release.

Tests removed with deleted diagnostics/scripts/confirmation/repetition explain the
251-to217 count change; no current-contract test was dropped to conceal a failure.
The first updated GUI test run exposed its helper supplying no selected serial;
callers now submit explicit selections as the actual GUI does. Scan fixtures use
the current vendor host-address contract. The USB notebook's superseded repeat
exercise is removed; its original template is archived privately.

Commands: .venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider --tb=short;
Ruff check/format --check --no-cache .; uv build --wheel --offline --out-dir
tmp/baseline-package; extracted-wheel PYTHONPATH import plus full pytest;
python -B -X utf8 tests/simulated_demo.py --api. Scope: fake SDK and actual callback
HTTP, no new browser/bench operation. [Machine evidence](baseline-validation.json).

## E139 / TEST-149 - Baseline tree and documentation

Expected: no obsolete files/compatibility paths/dangling references; current docs
and snippets agree; private evidence/environment remain; package matches source;
generated scratch is pruned. Prior tree:109 tracked files,2,323,179 bytes.
Observed:68 removed files,43 maintained files after2 consolidated evidence files,
about0.54MB (about77% smaller by working-file bytes). Only2 documentation assets
remain.16 Markdown files,2 cleared notebooks/15 code cells, local links/anchors
and5 Python snippets check successfully; no obsolete symbols/references remain.
All46 archived files match their original hashes. The executed LAN notebook hash
remains unchanged and ignored; .venv is present. No private identities were found
in maintained public text. Detailed deletion inventory/hashes are private; Git
history is preserved. Physical qualification remains incomplete.

Exact generated cleanup targets are resolved inside the workspace, checked for
reparse points/tracked contents and inventoried before removal. Final checks and
source/package/archive hashes are in baseline-validation.json. Focused commits,
normal push/remote equality and the baseline marker follow after cleanup.
