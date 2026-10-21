# Optional hardware diagnostic helpers

Use the [three-stage practical procedure](../HARDWARE_VALIDATION.md) for future
bench sessions and the [production GUI](../../README.md#launch-and-operate) or
[hardware tutorials](../examples/README.md) to carry it out. These older helper
filenames retain historical numbering; running every file is not a test plan.

| New procedure | Existing diagnostic building blocks |
| --- | --- |
| 1. Connect/read | `stage_0.py` bench-form audit; `stage_1.py` USB discovery; `stage_2.py` structured passive connection |
| 2. One functional cycle | `stage_3.first_close`; `stage_4.open_close_pair` |
| 3. GUI/cleanup | `stage_5.shutdown_case`; `stage_6` actual Dash callback helpers |

The helpers keep their existing APIs and stricter record/prior-evidence contracts.
In particular, Stage 2's structured runner requires a complete selected-serial
record and matching enumeration; Stage 3/4 require reviewed prior evidence.
These are optional diagnostic contracts, not prerequisites for the normal GUI,
passive tutorial or simplified procedure. The incomplete
[old bench form](../../records/hardware-bench.json) is not a routine-use gate.

## Select a diagnostic when needed

Imports, defaults and `--help` are offline. Live actions must be selected:

```powershell
uv run --locked python docs/hardware_tests/stage_1.py --discover
uv run --locked python docs/hardware_tests/stage_2.py --help
```

Stage 1 discovery enumerates USB identities without Connect. Stage 2's passive
cycle reads identity/status/trigger settings and attempts
`disconnect(close_shutter=False)` without output or configuration commands.
Retain the object if release fails; there is no automatic retry.

Stage 3/4 separate reported feedback from independent observations. Stage 5 checks
shutdown from Closed or, with an explicitly supplied approved positive hold, from
Open. Stage 6 exercises actual GUI callback responses, refresh without replay,
release/reconnect and global cleanup. No disabled control is forced. A normal
Ctrl+C test uses the server's owning terminal; browser closure is not shutdown.

`READBACK_PASS` establishes electronic evidence, not observed blade motion or
calibrated timing. Existing [bench results](../../records/hardware-validation.json)
remain valid within their recorded configuration/scope. The removed dedicated
repeatability stage stays removed; Ethernet, three-pair, TTL, physical faults and
timing are separate targeted work, not the next mandatory helper numbers.

## Both trigger ports disconnected

`ttl_unconnected.py` tests one verified controller with IO1/TRIG1 and IO2/TRIG2
connected to nothing. Release any GUI/Kinesis handle first. Existing source
protection, normal interlock and actuation authority must apply. Help/imports
are passive. Set `SHUTTER_SERIAL` locally using the
[launch example](../../README.md#launch-and-operate). This explicit command
configures and may actuate hardware:

```powershell
New-Item -ItemType Directory -Force inputs/private | Out-Null
uv run --locked python docs/hardware_tests/ttl_unconnected.py $env:SHUTTER_SERIAL --ports-unconnected --armed-seconds 1 --record inputs/private/ttl-new-run.json
```

Checks: disabled/output settings readback, Arm refusal without an input, each input
alone at high/low polarity, then restoration/release. A bounded read window allows
feedback to settle without reissuing Arm. Active-low can Open immediately. On a
failure, the run stops and attempts Disarm/Close, original settings restoration
while Closed and release. No automatic replay. `--port 2` selects an independent
IO2 investigation. The record must be new and its parent directory must exist; keep it private.
The added windows are limited to2s here.

E082 actual results: both high cases stayed Closed; both low cases also reported
Closed, contrary to the manual-based Open expectation even after the read window.
Low-position checks are FAIL. Manual Open/Close passed separately. Configuration,
priming, Disarm, restoration and release passed. See
[TTL results](../../records/ttl-summary.json). External pulses, pin voltage and
independent blade/timing measurements remain untested.

## Software-only regression

```powershell
uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
```

The excluded `tests/test_sdk.py` can enumerate real hardware. The default suite
uses test doubles and does not establish physical performance or session readiness.
