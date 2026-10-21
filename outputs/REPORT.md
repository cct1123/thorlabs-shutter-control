# Current baseline report

## Result

REQ-101 establishes the current USB/LAN system as the sole maintained baseline.
The GUI requires ShutterHub. Unused operator-confirmation metadata and the direct
single-controller GUI adapter are removed. USB/LAN routes, four modes, TTL settings,
explicit commands, identity/ownership and cleanup remain.

Removed numbered hardware diagnostics, duplicate script tutorials, supervisor
deliverables, superseded captures and incremental development records. Current
guides, two notebooks and focused software regressions remain. Historical evidence
is recoverable in Git and a hash-verified private archive; no compatibility
workflows or migration adapters are maintained.

## Operation

Install Kinesis and run uv sync --locked, then uv run shutter-control. Edit
config.py for optional panel/SDK/LAN-scan defaults. Discover, select a labelled
device and Connect. Use approved mode/output actions, then Shut down GUI & devices.
Startup is passive; full LAN scanning needs released process handles. Native
calls may block. See [README](../README.md), [GUI](../docs/gui.md) and [API](../docs/python-api.md).

## Validation and limitations

REQ-102 / TEST-151 rewrites all tests/doubles as15 essential cases in3 modules
plus1 fixture:405 lines, down from2486. Source and extracted wheel each15 passed,
0 skipped; lint/format and package/source parity PASS. Scope: normal USB/LAN/TTL,
identity, retained ownership, cleanup, GUI/launcher and both notebook cycles, plus
selected operational failures. This is representative functional coverage, not
exhaustive validation. Production source/CSS is unchanged. The real-SDK opt-in
test, preview helper and speculative/fuzz/internal check matrices are removed.
[Current test evidence](../records/tests-validation.json) records the result.

TEST-148/149 record the original runtime baseline's delivery and pruning; their
test suite has been superseded. The original cleanup dropped109 to43 files and
about2.32MB to0.54MB. [Evidence index](../records/RECORDS.md) and
[baseline evidence](../records/baseline-validation.json) retain that scope.
Implementation77ede6a and pruned baseline d1453d3 are pushed and origin/main's
exact hash verified. This final checkpoint is marked baseline-2026-10-21.
No actual hardware/network discovery or actuation is performed for this cleanup.

[Physical evidence](../records/hardware-evidence.json) retains prior USB observations,
passive one-pair LAN communication and unresolved no-cable active-low TTL failures.
Current GUI/USB, live range scans, Ethernet output/timing/recovery, KEH6/multiple
pairs, electrical TTL and calibrated optical/shutdown timing remain unqualified.
Software completion does not establish physical acceptance.
