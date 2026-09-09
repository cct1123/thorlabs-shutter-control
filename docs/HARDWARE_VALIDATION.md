# Ordered hardware validation — awaiting human approval

This procedure has NOT been executed. REQ-003 through REQ-008 remain BLOCKED.
HARDWARE_READY means the software candidate and procedure are ready for review;
it does not establish physical performance or authorize device access.
Proceed in order after approval, recording each result before the next stage.
No firmware changes, safeguard bypasses, or hazardous-beam tests are included.

## 0. Establish the bench configuration before USB communication

Record actual controller serial/firmware, exact shutter model and its official
manual, power-supply model/rating/polarity, shutter cable, USB connection, existing
key/interlock arrangement, external triggers, initial output/mode/physical state,
and the operator and independent observation method. Values not available stay
UNKNOWN and block any step that depends on them. Firmware can be transcribed
from the normal display or existing vendor records; do not flash it.

The operator must confirm the beam source is disabled or independently blocked,
the shutter is not the sole protective barrier, and movement cannot expose people
or damage equipment/samples. Observe blades safely or use a documented independent
detector; never look into an optical beam. Record the approved physical shutdown
method. Keep this configuration throughout all tests, including fault injection.

Check compatibility against the actual shutter manual and the
[KSC101 manual, HA0368T Rev D](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf),
sections 3.3–3.4 and Appendix C. The controller specifies regulated 15 V, 1 A;
that is not a measurement of the bench supply. Any setup/power changes belong
to the operator and manufacturer sequence: power down before changing shutter/
interlock cabling; do not hot-plug the supply. Record initial motion if power-up
is necessary. Preserve safeguards and control external trigger sources through
the bench's existing approved procedure; do not rewire an interlock.

Record Windows/Python architecture, source/build hashes, uv version, installed
Kinesis version/path, .NET/runtime and USB-driver readiness. The ignored extracted
SDK is not a driver installation. Use Python 3.12 x64 and matching Kinesis x64;
the prior SDK audit used 1.14.60.27990. Close competing control applications;
use one owner and one operator. No simulator should impersonate the real device.
Before repeated motion, establish the model's duty-cycle/thermal limits and a
per-state dwell of at least 1 s, increased to meet its manual. Record the approved
dwell; an unknown limit does not authorize a 20-cycle run.

## 1. Environment and discovery — no output command

Prepared PowerShell commands, to execute AFTER approval:

```powershell
Set-Location C:\projects\thorlabs-shutter-control
$uv = 'C:\Users\ctcheung\.local\bin\uv.exe'
$env:KINESIS_TEST_DIR = $null
& $uv --cache-dir .uv-cache sync --locked
& $uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
& $uv --cache-dir .uv-cache run --locked shutter-control --help
$env:KINESIS_DIR = Read-Host 'Verified Kinesis installation folder'
& $uv --cache-dir .uv-cache run --locked shutter-control --list
```

The final command is the **first hardware-interface action**: load official SDK,
`DeviceManagerCLI.BuildDeviceList()`, then `GetDeviceList(68)`. No Connect, Enable,
mode or state writes. Compare the serial with the physical label; never use a
sample/test identity. Empty, ambiguous or mismatched discovery stops progress
for diagnosis. Do not retry with output commands. The optional SDK pytest also
enumerates and is unnecessary before this explicit discovery. Record TEST-003.

## 2. Connection, identity, status and passive release — no output command

Select the actual discovered serial and start a Python REPL:

```powershell
$env:KSC101_SERIAL = Read-Host 'Actual KSC101 serial matching label and discovery'
& $uv --cache-dir .uv-cache run --locked python
```

Execute the block once. Review the result and independently check for any motion,
then repeat twice for three connection cycles:

```python
import os
from thorlabs_shutter_control import KSC101Controller
c = KSC101Controller(os.environ["KSC101_SERIAL"])
try:
    print(c.connect())
    print(c.identify_device())
    print(c.get_status())
finally:
    c.disconnect(close_shutter=False)
```

First connection sequence: discovery again, `CreateKCubeSolenoid(serial)`,
`Connect(serial)`, settings-initialization check/wait, `StartPolling(250)`, polling
check, `GetDeviceInfo`, 500 ms initial wait, health/status requests and getters.
Identity reads `GetDeviceInfo`; release calls `StopPolling` then `Disconnect`.
No explicit output, enable or mode writes. SDK side effects/startup motion remain
observations to validate, not guarantees inferred from call names.

Do NOT use `with c`, default `disconnect()`, or `safe_shutdown()` in this phase:
they attempt Close. Compare identity, mode, key/interlock and state against the
bench/display; note unsupported/unknown feedback and health changes. No busy
connection should remain after release. If release fails, retain the same `c`
for diagnosis/cleanup; do not replace it or create another owner. Record TEST-003
and TEST-005; stop before actuation if feedback/configuration is ambiguous.

## 3. First Close — first intentional output-changing action

After stages 0–2 pass, execute individually in the REPL, recording independent
observation after Close:

```python
print(c.connect())
print(c.close_shutter())
print(c.get_status())
```

**May physically move the shutter.** First write: `SetOperatingState(Inactive)`,
then `SetOperatingMode(Manual)` and wait for reported Closed/Inactive/Manual.
This establishes the closing path before requesting Open; it does not enable
first. Already closed is a baseline, not an observed transition. If Close cannot
establish its reported state, stop and diagnose; do not add Enable experimentally.
Record TEST-004/005.

## 4. One Open, then Close — intentional actuation

Run `print(c.open_shutter())`, independently verify Open, hold for the approved
dwell, then `print(c.close_shutter())` and independently verify Closed. Sample
`print(c.get_status())` in each stable state. Open sends Inactive then Manual,
waits for Closed/Inactive/Manual, then sends `EnableDevice()` and
`SetOperatingState(Active)` and waits for Open/Active/Manual with key/interlock
enabled. Thus one Open call may first close an existing state.

Record commands, physical transitions, status agreement, elapsed times and errors
(TEST-004/005). One opening and one closing must be observed; return values alone
cannot pass. Abort on mismatch or unexpected motion.

## 5. Normal shutdown and reconnect — intentional actuation

From independently confirmed Closed, call `c.safe_shutdown()` and verify release.
Reconnect, open once, then call `c.safe_shutdown()` while open. Independently
observe closure and record shutdown latency/residual state. Reconnect once more,
read identity/status, and call `c.safe_shutdown()` to leave a released closed
baseline. All shutdown calls attempt Inactive/Manual and may move the shutter.
Require closure and release before GUI/repetition tests (TEST-003/007).
Exit the REPL with `exit()` only after successful cleanup.

## 6. Dash and Ctrl+C — intentional actuation

```powershell
& $uv --cache-dir .uv-cache run --locked shutter-control --serial $env:KSC101_SERIAL
```

Open http://127.0.0.1:8050. Check passive initial UI with Open/Close disabled;
Discover, verify/select serial, Connect, verify identity/status/safeguards. Click
Close, then Open, observe over several refreshes with no replay, then Close.
Click Close & disconnect; verify closure/release. Reconnect, Open, then press
Ctrl+C in the server terminal; independently verify closure and server exit.
Open/Close/Close & disconnect and connected-server Ctrl+C can actuate. Closing
a browser tab is not shutdown. Record TEST-008/007 and ensure ownership is released.

## 7. Repeated operation — intentional actuation

After single transitions, shutdown and GUI tests pass, reconnect in the REPL.
Repeat the stage 4 Open/Close pair **20 times**, using the recorded approved
per-state dwell. Number every pair; independently verify each opening and closure
before advancing. Record timestamps, observations and errors; stop on the first
discrepancy, overheating sign or limit violation. End with `c.safe_shutdown()`.
A 20-call counter is not evidence of 20 physical cycles. Record TEST-004/005.
Do not increase rate or count to diagnose a failure.

## 8. Controlled communication loss — may affect output; no intended opening

Only after normal operation/shutdown passes, reconnect and independently confirm
Closed. With the source disabled/independently blocked, the operator disconnects
USB only. Repeatedly query `c.get_status()` and record time to Fault/Unknown; do
not assume immediate detection. If no fault appears within the agreed observation
window (initially 10 s), stop as FAIL and leave Open uncalled. After a latched
fault is observed, call `c.open_shutter()` once: expect rejection with no output
command. The 10 s window is a test criterion, not a vendor timeout guarantee.

Call `c.safe_shutdown()` while USB remains disconnected: expect visible shutdown
failure and unknown closure, with release attempted. Independently record position.
Reconnect USB, retry cleanup if a handle remains, explicitly connect/read identity/
status, verify no unsolicited opening, Close, then shut down. USB removal/
restoration and shutdown/recovery may change output. If cleanup hangs, keep the
beam independently blocked and use the approved bench shutdown method.

Repeat this CLOSED-state case through Dash: Connect, Close, remove USB, wait for
Fault/Unknown and disabled Open, Close & disconnect, reconnect USB, cleanup/
reconnect as needed, Close & disconnect, exit server. Record TEST-006/007/008.
Never remove power/interlock/shutter wiring as fault injection. An existing
disabled key/interlock state may be checked for Open refusal only if the approved
bench setup permits it; mark unavailable cases BLOCKED and do not bypass it.

## Evidence, stop rules and completion

For each TEST record operator/observation method, UTC time, source/build hashes,
Python/uv/SDK/firmware, serial, shutter, supply, cabling, trigger/key/interlock,
initial/final states, dwell, expected/observed results, latency in seconds and
PASS/FAIL/INCONCLUSIVE. Preserve errors and label human-reported observations.
Detector readings need units and arrangement. Never mark unexecuted steps PASS.

On unexpected motion, uncertain state, failed closure, error or lost observer:
stop, keep the independent beam block/source disable, and use the agreed physical
shutdown procedure. Software Close is best effort only when appropriate. Do not
blindly reconnect/retry Open. Diagnose before resuming at the affected earlier gate.

Normal safe_shutdown requests Inactive then Manual, waits for controller-reported
Closed/Inactive/Manual, stops polling and disconnects. It attempts release even
after closure failure and surfaces errors; failed release retains the handle for
retry. It does not restore a previous trigger/auto mode. Vendor timeouts/cache
freshness, forced termination, USB/power loss or a hung native call prevent any
guarantee of physical closure. Independent protection is required throughout.

Update STATE.md and records after each stage. If code/configuration changes,
invalidate affected results, rerun relevant software tests and repeat affected
physical gates plus a final connected GUI open/close/shutdown check on that exact
revision. COMPLETE requires current PASS evidence for every requirement; unresolved
or unavailable physical checks remain BLOCKED.
