# Physical acceptance procedure — not yet executed

Requirements REQ-003 through REQ-008 remain blocked. Software doubles and SDK
enumeration do not demonstrate shutter motion. Record actual observations under
the TEST IDs below in `records/RECORDS.md`; never mark an unexecuted step PASS.

## Preconditions and information needed

An operator must make the actual KSC101 and compatible shutter available on this
computer and supply/confirm:

- Controller serial number and exact shutter model.
- Power-supply model and output rating; wiring/configuration consistent with the
  manufacturer manuals for this controller and shutter.
- Existing key/interlock state and any external trigger connections. Preserve
  safety mechanisms; do not add a bypass or change powered interlock or shutter cabling.
- Beam source disabled or independently blocked, no exposed hazardous beam, and
  movement unable to expose people or damage equipment/samples. The shutter
  under test must not be the sole protective barrier.
- A safe means of independently observing blade movement/closure. Do not look
  into an optical beam. If a detector is used, record its arrangement and actual
  readings; counts from software alone are not physical observations.

Then verify the supported Kinesis installation/USB driver and record Python, SDK,
firmware, and application source fingerprint. Close competing device applications.
Resolve the confirmed shutter's duty-cycle limits before repeated operation. The
proposed run is 20 manual open/close cycles, at least 1 second dwell in each state,
in the safe configuration above; revise the dwell upward if its documentation
requires it. Start with single open and close checks before that run.

The user's engineering launch authorizes routine engineering work. Per AGENTS.md,
actual actuation also requires known operating conditions and appropriate authority.
Confirm those conditions and the intended sequence with the operator before the
first physical operation. No firmware changes are included.

## Expected results and evidence

| Test | Procedure | Expected result / evidence |
| --- | --- | --- |
| TEST-003 | Run `shutter-control --list`; compare serial to label. Connect and call `identify_device`; perform three software disconnect/reconnect cycles. | Correct identity every time; no explicit Open on connect; independently note any startup motion. Default disconnect closes. No leaked/busy connection on reconnect. |
| TEST-004 | Call `open_shutter`, observe physical opening; call `close_shutter`, observe physical closing. Then run the agreed 20 cycles with approved dwell. | Every transition observed physically; tally commands and independent observations, errors, and timestamps. Record any mismatch and stop on it. |
| TEST-005 | Compare `get_status` before/after each single transition and during a stable state. | Reported position/mode consistent with observation. Document unavailable or ambiguous feedback and update GUI labeling if needed. |
| TEST-006 | In the independently safe configuration, first confirm closed; disconnect USB only and attempt status and Open. Reconnect USB and recover through explicit disconnect/connect. Inspect an existing disabled safeguard state only if the operator's setup permits it. | Faults visible, position becomes unknown, further Open rejected after a fault, recovery deliberate. Record actual detection latency and unexpected motion. Do not assume unplugging USB closes the shutter. Never change interlock wiring as an injected fault. |
| TEST-007 | In the safe configuration, open then call `safe_shutdown`; repeat using Ctrl+C while the GUI server owns the open shutter. | Independent closure observed before completion; connection released. Record failures, shutdown latency, residual state. Validate communication-loss shutdown failure reporting while the beam stays independently blocked. |
| TEST-008 | Run Dash; Discover, Connect, Open, Close, Close & disconnect, reconnect, and repeat the safe communication-loss case. | Correct identity/status/messages, controls use the same controller methods, no Open replay during refresh, physical transitions independently observed. Browser-tab closure alone is not shutdown. |

Each record must identify operator/observation method, source fingerprint, serial,
shutter model, supply, firmware/SDK versions, key/interlock/trigger configuration,
expected result, observed result, and PASS/FAIL/INCONCLUSIVE. Label operator-reported
observations as such. Record optical measurements with units if used.

## Stop and recovery

On unexpected motion, uncertain state, an error, or failed closure: stop the
sequence, maintain the independent beam block/source disable, and use the bench's
approved physical shutdown procedure. Attempt software Close only while communication
and configuration make it appropriate. A failed close is never evidence of closure.
Reconcile state and cause before reconnecting/restarting tests.

Complete the project only after the integrated final run passes on the recorded
configuration and all physical evidence is linked from STATE.md and the report.
