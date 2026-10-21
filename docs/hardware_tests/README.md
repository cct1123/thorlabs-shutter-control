# Hardware test tools

Current authority: the user enabled GUI/hardware and requested autonomous Stage5/6.
Administrative holds are removed. Actual target is USB68800777 through KEH3 to
KSC101/SH05R. Firmware1.0.7; normal physical interlock and independent source
block retained. [STATE.md](../../STATE.md) is the current checkpoint.

## Discovery and passive reads

Defaults and --help are offline; live actions are explicitly selected:

```powershell
uv run --locked python docs/hardware_tests/stage_0.py
uv run --locked python docs/hardware_tests/stage_1.py --preflight
uv run --locked python docs/hardware_tests/stage_1.py --discover
uv run --locked python docs/hardware_tests/stage_2.py --preflight --serial 68800777
uv run --locked python docs/hardware_tests/stage_2.py --connect --serial 68800777
```

Stage0 reads the local bench JSON and reports factual gaps. Stage1 --discover
loads Kinesis and enumerates USB identities without connecting. Its standalone
check_discovery(record, enumerator) additionally compares a complete expected
bench record; enumeration alone never proves physical mapping.

Stage2 --connect requires a complete selected-serial record and matching
Stage1 enumeration, then runs one passive_cycle. It captures identity, status and
trigger readback, and always attempts disconnect(close_shutter=False). No Close,
Enable, mode or configuration command is sent. Interlock unknown is preserved as
unknown, not failed continuity; it cannot by itself authorize motion. Factual
record gaps return INCOMPLETE, not an administrative hold or physical PASS.
No automatic retry. Retain the object if release fails.

## Motion helpers

Importing/running helper files does not connect or actuate automatically.
Stage3 first_close and Stage4 open_close_pair accept a caller-retained controller,
complete record and reviewed prior physical-stage evidence. They record reported
feedback separately from independent observations. For current bench readiness:

```python
from thorlabs_shutter_control import KCubeShutter

c = KCubeShutter("68800777")
# Only after normal physical interlock/source protection have been verified:
c.confirm_interlock("68800777")
```

This is session/selected-serial evidence and performs no SDK access or interlock
write. Retargeting clears it. The SDK reading remains unknown. A known negative,
locked key, unhealthy communication or wrong identity still inhibits Open.

## Stages 5 and 6

stage_5.shutdown_case(c, serial, open_seconds=None) connects, verifies target and
status, establishes Closed/Inactive/Manual, then safe_shutdown closes/releases.
With an explicitly approved finite positive open_seconds, it Opens and holds
before safe_shutdown itself must Close; no explicit intervening Close masks that
case. Failed unverified connection uses passive release. Operation/cleanup errors
are both preserved; interrupts propagate after cleanup. Result READBACK_PASS is
electronic evidence; physical_status stays UNTESTED without new observation.

stage_6.closed_gui_lifecycle(call, serial) checks actual callback responses for
passive startup, disconnected unused slots, discovery, selected identity, Close,
refresh, release and reconnect. stage_6.open_close_gui(call, open_seconds=2)
requires enabled Open on a connected Closed slot, then checks Open/hold/Close and
three refreshes without replay. It attempts global shutdown on failure.
callback_payload builds the actual Dash request from served dependencies;
changedPropIds selects the single action. No disabled control is forced.

Normal server Ctrl+C is delivered from its owning terminal, not browser-tab
closure or force-kill. Verify Close/Inactive/Manual during safe_shutdown, released
handles, server exit and a fresh passive reconnect. The current run used the
production CLI with log-only wrappers around Open/Close/hub shutdown. See
[combined evidence](../../records/hardware-validation.json).
Added holds start after reported Open; they are not calibrated exposure or
maximum shutdown times. The current Stage5/6 tests require no human prompts;
new independent physical observations are not invented.

## Start the enabled GUI

```powershell
uv run --locked shutter-control --serial 68800777 --verified-interlock 68800777
```

Startup is passive. Connect enables Open when current key/communication/identity
checks and interlock readiness pass. The GUI displays unknown (operator verified).
Close & disconnect all and normal terminal Ctrl+C attempt closure/release.

Stage7 remains removed by the user. Three-pair, TTL, physical loss/recovery and
Ethernet cube acceptance are separate unexecuted scope, not software-test PASS.

## Software-only regression

```powershell
uv run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
```

tests/test_sdk.py can enumerate actual hardware; the excluded suite uses fake
SDKs and establishes software behavior only. Existing dated failure records are
historical evidence, not active administrative restrictions.
