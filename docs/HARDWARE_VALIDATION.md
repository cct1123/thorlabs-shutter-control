# Hardware commissioning

[Hardware/evidence](hardware.md) | [Interface](INTERFACE.md) | [Notebooks](examples/README.md)

Software tests establish routing/control flow, not physical performance. Use this
procedure only with appropriate authority for the selected bench and action.
Establish target serial/shutter mapping, one owner, manufacturer-approved wiring,
normal physical interlock, independently blocked/disabled source, approved hold
and an independent shutdown action before operating.

## Connect and read

Use GUI Discover/select/Connect or the appropriate notebook's passive cells.
Confirm exact serial and USB/LAN route. Request identity and operating feedback.
Pass requires matching identity and successful communication/reads. Preserve
unknown values; operating state0 is not Inactive. Stop on wrong identity or errors.
For a passive LAN check, skip all output/mode cells and release without Close.

The current getters add no Python settling sleep and may expose values received
before the request. Qualify request-to-response age and settings readback on the
intended USB/LAN topology under the approved bench conditions. Record whether a
response can be associated with its request/write; an SDK value or a 100 ms GUI
refresh alone does not establish that association. Until demonstrated, record
freshness and write acknowledgement as UNTESTED rather than infer them from the
software checks. Do not use the GUI cadence as an exposure or shutdown bound.

## One functional cycle

Proceed only within approved operating conditions. Explicitly Disarm to
Inactive/Manual, read Closed/Inactive/Manual, then Enable when setup is needed.
Check key/feedback before Open. Request Open, read feedback, observe the actual
blade/optical state, hold for the approved added duration, then Close/read/observe.
Setters returning successfully is insufficient evidence of motion or closure.
Host waits and feedback latency do not establish a maximum exposure or calibration.

## GUI and cleanup

Exercise the production selection, mode, readiness, action and error displays on
the intended topology. Stop/Close before mode changes. Check normal Close/release,
reconnect, global cleanup and launcher shutdown. Close failure must remain visible;
failed release must retain the owner/object for recovery. Verify physical closure
independently. A closed browser tab is not shutdown; native calls can block.

## Record the result

Keep exact revision, Python/SDK/firmware, topology, private serial/address/bay,
commands, expected/observed feedback, independent observation, durations in seconds,
errors and cleanup outcome. Mark PASS/FAIL/UNTESTED separately for software,
controller readback and physical observation. Store unredacted data privately.

[Retained evidence](../records/hardware-evidence.json) includes prior USB/motion
observations and one passive KEH3 LAN connection. Current baseline qualification,
range scans, Ethernet output/timing/recovery, multi-pair/KEH6, electrical TTL and
calibrated timing remain open. Active-low no-cable position checks failed on both
ports; keep that failure visible. Arm may open immediately. Dedicated loss/fault
or calibration tests require their own documented conditions and authorization.
