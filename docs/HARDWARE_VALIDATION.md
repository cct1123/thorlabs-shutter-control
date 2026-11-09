# Physical acceptance and scoped Ethernet commissioning

The current repository review is software-only. E239 records the last bounded
one-pulse WebUI redo, with final Manual/OFF and release; its blade motion was
unobserved. Source/configuration have changed since that run, and all recorded
cycle allowances are consumed. E200's earlier two real Manual WebUI
cycles retain their recorded source/configuration scope; E202 reports that the
user did not observe both cycles, so full two-cycle blade motion is unverified.
E191/E192 records a separate earlier individually observed cycle. No calibrated
optical timing/extinction, local/TTL/interlock or native-mode campaign is implied.
The reviewed owner rest/cleanup/interlock guards require affected physical
requalification in a fresh approved window; no repeat was performed here.

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

| Test | Requirement | Procedure / expected evidence | Recorded result / validity |
| --- | --- | --- | --- |
| TEST-220 | REQ-220 | Exact middle-bay KSC10168800777/1.0.7 and SH05R, protected source, explicit Manual, one1s ON/OFF, finalOFF and release | PASS controller command/readback only; no independent blade observation |
| TEST-227 | REQ-227 | Approved protected modern-WebUI Open/Close, active-release guard,1s host hold, final OFF/release | E200 PASS selected controller flow at its recorded revision; E202 full two-cycle independent blade motion unverified |
| TEST-255 | REQ-255 | One approved 1 s host pulse, final Manual/OFF/interlock readback and release | E239 PASS bounded electrical/WebUI flow at its recorded revision; independent blade motion unobserved; allowance consumed |
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
Explicit Stop/OFF can reset a software fault after verified OFF/interlock; it
does not establish optical closure. Passive protected recovery separately
requires protected source plus independently observed closure. Do not bypass
the interlock, change a driver or reset a hub as recovery.
