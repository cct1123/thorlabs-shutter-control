# Ordered hardware validation — awaiting human approval

This procedure has NOT been executed. REQ-003 through REQ-008 remain BLOCKED.
The three-KSC101/KEH3 USB extension below is also unexecuted. Hardware access
remains on hold; software implementation is not authorization to begin these steps.
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
For three-cube operation, record those facts separately for each cube/shutter,
assign fixed labels Shutter 1–3, and map each physical label to one GUI panel and
serial. Also record the actual KEH3 variant/identity, its official manual,
approved hub supply/docking arrangement and host USB path. The standalone KSC101
supply specification does not establish the hub supply specification. Ethernet
is outside this procedure and implementation.

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
# Run from the repository root after approval.
$uv = (Get-Command uv -ErrorAction Stop).Source
$env:KINESIS_TEST_DIR = $null
& $uv --cache-dir .uv-cache sync --locked
& $uv --cache-dir .uv-cache run --locked pytest -q -p no:cacheprovider --ignore=tests/test_sdk.py
& $uv --cache-dir .uv-cache run --locked shutter-control --help
$env:KINESIS_DIR = Read-Host 'Verified Kinesis installation folder'
& $uv --cache-dir .uv-cache run --locked shutter-control --list
```

The final command is the **first hardware-interface action**: load official SDK,
`DeviceManagerCLI.BuildDeviceList()`, then `GetDeviceList(68)`. No Connect, Enable,
mode or state writes. Compare every expected serial with its physical label;
three expected KSC101 identities are valid for the hub configuration. Never use a
sample/test identity. Missing, unexpected or mismatched identities stop progress
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
from thorlabs_shutter_control import KCubeShutter
c = KCubeShutter(os.environ["KSC101_SERIAL"])
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
Repeat the individual stages for each identified cube before combined operation;
keep other shutters independently confirmed Closed, with their outputs uncommanded.

## 3. First Close — first intentional output-changing action

After stages 0–2 pass, execute individually in the REPL, recording independent
observation after Close:

```python
print(c.connect())
print(c.close_shutter())
print(c.get_status())
```

**May physically move the shutter.** First write: `SetOperatingState(Inactive)`,
verify Closed/Inactive, then `SetOperatingMode(Manual)` and verify Closed/Inactive/Manual.
This establishes the closing path before requesting Open; it does not enable
first. Already closed is a baseline, not an observed transition. If Close cannot
establish its reported state, stop and diagnose; do not add Enable experimentally.
Record TEST-004/005.

## 4. One Open, then Close — intentional actuation

Run `print(c.open_shutter())`, independently verify Open, hold for the approved
dwell, then `print(c.close_shutter())` and independently verify Closed. Sample
`print(c.get_status())` in each stable state. Open sends Inactive, verifies
Closed/Inactive, then selects Manual and verifies Closed/Inactive/Manual before `EnableDevice()` and
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

Open [localhost:8050](http://127.0.0.1:8050). Check passive initial UI with Open/Close disabled;
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

For KEH3, do not remove a powered cube or change docking/power/interlock wiring as
fault injection. A host USB removal affects the shared connection. Use only the
operator-approved USB path and procedure, with every shutter independently
confirmed Closed and the beam independently blocked. The combined case follows.

## 9. Three-controller KEH3 USB acceptance — intentional actuation after prior gates

Run only after stages 0–8 have passed for the three identified cubes in the
recorded configuration and the operator has approved combined operation. Record
each result under the existing physical TEST-003–008, including the slot/serial
subcase. This is a prepared procedure, not physical validation evidence.

1. Repeat discovery once and compare all three distinct serials with the stage-0
   physical shutter/panel mapping. Launch the GUI using all three actual serials:

   ```powershell
   $serial1 = Read-Host 'Actual KSC101 serial mapped to Shutter 1'
   $serial2 = Read-Host 'Actual KSC101 serial mapped to Shutter 2'
   $serial3 = Read-Host 'Actual KSC101 serial mapped to Shutter 3'
   & $uv --cache-dir .uv-cache run --locked shutter-control --serial $serial1 --serial $serial2 --serial $serial3
   ```

2. Confirm passive startup, then Connect the first panel. In a still-disconnected
   second panel select the first panel's serial and attempt Connect: it must be
   refused without a second connection or output command. Restore the correct
   distinct selections and Connect the remaining panels individually. Verify all
   identities, reported states, safeguards and initial physical states; record
   any motion during connection.
3. Establish independently confirmed Closed for every shutter. For Shutter 1,
   then 2, then 3, perform one Open/Close pair with that shutter's approved dwell.
   Independently observe all three shutters: only the selected shutter may move;
   the other two must remain Closed with healthy, unchanged identities/status.
   Stop on a wrong mapping, unexpected neighbor motion, or feedback mismatch.
4. From Closed, Close & disconnect one panel and reconnect that same serial.
   Verify the other two retain their own healthy connections and do not move.
   Repeat for each panel, checking identity again after every reconnect.
5. Use only a combination of open shutters permitted by the stage-0 limits and
   combined-operation approval. Click **Close & disconnect all** and independently
   verify closure/release of every connected shutter. Record each shutter's
   closure latency and final state, plus total cleanup time. Repeat with terminal
   Ctrl+C from an approved open-state combination. Do not infer simultaneous
   closure or a maximum latency from software timeouts; cleanup is sequential.
   If the permitted dwell cannot accommodate the test, leave that case BLOCKED.
6. Return all shutters to independently confirmed Closed. Apply the approved
   shared host-USB loss case from stage 8. Record each panel's Fault/Unknown
   detection latency and Open refusal. Request **Close & disconnect all** while
   USB is absent; expect errors identifying affected slots, with no later slot
   skipped merely because an earlier attempt reported an error. Do not deliberately
   hang an SDK call: a hung call can prevent reaching later slots. Restore the
   approved USB connection, retry retained-handle cleanup, then reconnect and
   recheck each identity/physical state before final Close & disconnect all.

The shared-USB case does not prove isolation from an individual cube failure.
An individual fault case requires a separate manufacturer-permitted, explicitly
approved method; otherwise record it as BLOCKED and retain the software-test
evidence only. Do not remove hub power or a powered cube to create such a fault.
End with all shutters independently confirmed Closed and all handles released.

## Stage 10 — TTL acceptance (pending)

**Not authorized for execution.** TEST-034 / REQ-031 extend the existing physical
gates; software TEST-033 cannot establish these results. Obtain explicit TTL
launch approval after stages 0–9 are satisfied for the intended configuration.

1. Record each actual KSC101/shutter/firmware/SDK, port wiring, source model,
   approved levels and electrical compatibility from matching manuals. Record
   input/output directions and polarity before connecting signal cables. Never
   connect two driving outputs. Preserve the independent source disable/beam block,
   observation/recovery method and per-shutter/combined dwell limits. Do not infer
   electrical thresholds from other K-Cube models.
2. Connect passively and compare reported settings with independently established
   vendor settings. Observe initial physical state. Disarm/Close and independently
   confirm closure. Apply each approved port configuration only from
   Closed/Inactive/Manual; compare both readback fields for both ports. Record
   whether vendor settings are cached and how freshness is established.
3. For one shutter at a time with the others disarmed/closed, set its input to the
   approved inactive level, Arm, and confirm Triggered/Active with physical Closed.
   Drive the approved active level for the allowed dwell, observe opening, return
   inactive, observe closure. Record pin voltage in V, source/scope arrangement,
   timing in seconds and uncertainty where applicable. Repeat approved cases for
   TRIG1 and TRIG2, high and low polarity; leave unapproved wiring cases BLOCKED.
   An open input is documented LOW: active-low can open immediately when primed.
   Do not deliberately disconnect a trigger cable while armed to test this warning.
4. With only approved levels/states, test Disarm/Close while the input is active.
   Independently verify closure and that further input changes do not reopen it.
   Check Manual/Inactive readback and manual Open refusal while Triggered. For
   outputs, observe the approved load with a suitable instrument and compare
   reported direction/polarity against actual output behavior.
5. Repeat per shutter, verify no neighbor changes, then use only the approved
   combined state to test Close & disconnect all and terminal Ctrl+C while armed.
   Observe every closure and record per-shutter/total latency and final modes.
   Validate approved communication-loss/recovery cases as in stages 8–9. Do not
   force a hung SDK call or change powered hub/shutter/interlock cabling.
6. Finish with independently confirmed Closed and all handles released. Record
   settings/mode persistence across any separately approved power-cycle test;
   this program makes no explicit EEPROM write, but that does not prove volatility.

Stop on unexpected motion, stale/mismatched feedback or failed disarming. Keep
independent protection and use the agreed physical recovery; do not keep arming.

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

Normal safe_shutdown requests Inactive, verifies Closed/Inactive before selecting
Manual, then verifies Closed/Inactive/Manual, stops polling and disconnects.
Closure waits use operating feedback independently of trigger-settings reads.
It attempts release even
after closure failure and surfaces errors; failed release retains the handle for
retry. Disconnect is attempted even after a StopPolling interruption; errors and
the interruption remain visible. It does not restore a previous trigger/auto mode. Vendor timeouts/cache
freshness, forced termination, USB/power loss or a hung native call prevent any
guarantee of physical closure. Hub shutdown attempts each slot sequentially,
continues after reported errors/interruption and preserves slot/serial diagnostics.
No end-to-end latency or physical closure guarantee exists. Independent protection
is required throughout.

Update STATE.md and records after each stage. If code/configuration changes,
invalidate affected results, rerun relevant software tests and repeat affected
physical gates plus a final connected GUI open/close/shutdown check on that exact
revision. COMPLETE requires current PASS evidence for every requirement; unresolved
or unavailable physical checks remain BLOCKED.
