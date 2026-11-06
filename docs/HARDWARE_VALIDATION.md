# Physical acceptance and scoped Ethernet commissioning

PROJECT.md records a bounded exact-controller SH05R commissioning authorization
for OFF/Manual preparation and one 1 s ON/OFF cycle, with a 2 s OFF pause and
independent source/trigger protection. E181 executed that one cycle: controller
ON/OFF readback PASS, final Manual/OFF and release. The user did not observe
blade motion. The broader procedures below have not been executed.
Check the applicable authorization and present conditions before any command;
the broader tests below require their own approved conditions and limits.

Before a window, record hub/controller/shutter serial/model/firmware, power and
wiring, beam/source configuration, independent protection, interlocks, initial
optical/electrical states, permitted commands, duty/frequency/exposure limits,
cycle count, cleanup and operator recovery. Do not invent numeric safe limits.
Keep one active owner and close unrelated device applications.

| Test | Requirement | Procedure / expected evidence | Current result |
| --- | --- | --- | --- |
| TEST-220 | REQ-220 | Exact middle-bay KSC10168800777/1.0.7 and SH05R, protected source, explicit Manual, one1s ON/OFF, finalOFF and release | PASS controller command/readback only; no independent blade observation |
| TEST-208 | REQ-208 | Manufacturer Ethernet contract; exact hub and each occupied/empty/swapped route; wrong hub/serial rejected; shared loss invalidates all affected data | BLOCKED |
| TEST-209 | REQ-209 | Begin with authorized identity/state reads. Establish shutter model and OFF/ON optical mapping independently. Then explicit modes/output, local controls, interlocks, loss while active, power-off/restoration and optical timing | UNTESTED |
| TEST-210 | REQ-210 | Inventory packages/loaded drivers/serial instruments and rollback. Qualify bindings, 10 reconnects, 3 reboots and representative 24-hour coexistence, finalized within actual shutter ratings | UNTESTED |

Measure software protective-request arrival -> output-frame dispatch and physical
light transmission -> verified closure separately. Initial healthy dispatch target
250 ms is not an optical tolerance. Obtain physical switching tolerances from the
actual shutter specification and measurement method; record detector/clock
calibration and uncertainty where meaningful. Software hold duration is not
calibrated exposure.

Each result records TEST/REQ ID, UTC and local timestamps, code/dependency revision,
OS/driver configuration, exact topology, requested state, complete controller
responses, independent optical observations, measured values with units and
cleanup outcome. Report PASS only for the tested configuration and criterion.
Changed firmware/routing/policy/wiring invalidates affected qualification.

On communication loss, retain unknown optical state, inhibit the independent
source under the approved procedure and inspect the shutter. Do not repeat ON.
Qualified OFF remains best effort through a retained exact D2XX/docked-KEH3 handle; lack of
readback, session poison or trigger authority prevents confirmed safe state.
Recovery is explicit and requires protected source plus independently observed
closure. Do not bypass the interlock, change a driver or reset a hub as recovery.
