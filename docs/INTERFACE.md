# KSC101 interface contract

[API](python-api.md) | [Hardware](hardware.md) | [Ethernet](ethernet-assessment.md)

## Device and transport

The qualified USB branch is computer -> KEH3 left bay -> KSC101 (alias CONTROLLER_A) -> SH05R.
Kinesis identifies the cube by its eight-digit serial beginning68 through FTDI;
there is no COM-port dependency. Kinesis1.14.60.27990 .NET Framework assemblies
are loaded lazily using Python.NET3.1 on Python3.12.7 x64. Cube firmware1.0.7
repaired the old hardware-info serialMISMATCHED_ID versus descriptorCONTROLLER_A mismatch.
No software serial alias was added. Installed supply/wiring details not observed
remain incomplete in the bench record.

The SDK namespace is `Thorlabs.MotionControl.KCube.SolenoidCLI`; exact members
come from the installed KSC101-specific .NET API/help, not a different motion
controller's trigger example. Official references:
[Kinesis distribution](https://www.thorlabs.com/software-pages/Motion_Control),
[Thorlabs Python examples](https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python),
[KSC101 manual HA0368T RevD, sections3-4](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf),
[KEH3 manual section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351).
Static excerpts/checksums and bench investigations are preserved in the archive.

## Communication and feedback

| Operation | SDK contract |
| --- | --- |
| Discovery | BuildDeviceList/GetDeviceList(68); experimental explicit Ethernet checks provider/comspec |
| Connect | CreateKCubeSolenoid, Connect, settings initialization, StartPolling, identity check, status requests |
| USB health | IsConnected true, USBConnected Connected or Connecting, CommsStatus OK |
| Ethernet health | Selected TCPIP provider/comspec unchanged, IsConnected true, CommsStatus OK |
| Status | RequestStatus, RequestOperatingMode, RequestOperatingState, optional trigger request, then cached getters |
| Identity | GetDeviceInfo; identify_device does not invoke the SDK's flashing IdentifyDevice operation |
| Release | Attempt StopPolling then Disconnect even when stopping polling fails |

Headless USB can remain Connecting while IsConnected/CommsStatus and actual reads
work; Connecting alone is never accepted as readiness. Disconnected/unknown or
communication errors fault the wrapper. Operating modes normalize Manual/SingleToggle/
AutoToggle/Triggered to manual/single/auto/triggered. Operating state0 stays invalid;
only Active/Inactive is accepted. A request/wait does not establish cache age.

## Key and physical interlock

The manual describes a current-carrying physical interlock separately from the
key enable switch. SDK header bit0x1000 is treated as a positive interlock
indication; a clear bit is **unknown**, not a proven disabled physical circuit.
Four human-labelled Auto-mode tests showed0x2000 when key enabled and0 when key
disabled, with no jack-related difference. No replacement mask or independent
software jack-continuity report was established.

`confirm_interlock(serial)` records verified normal physical circuit/protection
for the explicitly selected object/serial before connection. It performs no SDK
or hardware write, clears on retargeting, and does not transfer to another object
or process. Unknown SDK readiness may use this evidence; a known negative report,
key failure, wrong identity or communication fault is not overridden. Raw bits and
interlock_enabled remain separate from operator_interlock_confirmed/interlock_ready.

## Outputs and timing

Close: SetOperatingState(Inactive) -> verify Closed/Inactive ->
SetOperatingMode(Manual) -> verify Closed/Inactive/Manual.
Open: require readiness/non-Triggered -> establish Close baseline -> EnableDevice ->
SetOperatingState(Active) -> verify Open/Active/Manual with readiness.
Failed Open attempts Inactive and latches the error. Cleanup is best effort.

Default polling250ms; feedback timeout5s per wait stage; GUI refresh request1s.
Native calls can block beyond these waits. Host sleeps, reported transitions and
shutdown call durations are not calibrated blade/exposure measurements.

## TRIG1/TRIG2

| Contract | Exact members |
| --- | --- |
| Settings | RequestTriggerConfigParams/GetTriggerConfigParams/SetTriggerConfigParams |
| Properties | Trigger1Mode/Trigger1Polarity/Trigger2Mode/Trigger2Polarity |
| Direction enums | Disabled=0, TrigIN_GPI=1, TrigOUT_GPO=10 |
| Polarity enums | TriggerHigh=1, TriggerLow=2 |
| Arm | Close baseline, EnableDevice, Triggered, Active; confirm arming/readback |
| Disarm | Same verified Inactive-before-Manual sequence as Close |

Apply requires Closed/Inactive/Manual; readback must match. Arm uses the current
device settings and needs at least one input. The hardware manual describes5V
TTL and a disconnected input as LOW; active-low priming can open with no cable.
The driver reports configuration/priming, not measured pin voltage or raw edges.
No explicit PersistSettings/EEPROM call is made; power-cycle persistence has not
been measured. E082 tested configuration/priming/Disarm on actual USB hardware
with both ports disconnected. Each input/high stayed Closed, but input/low also
stayed reported Closed despite Triggered/Active and matching settings after a
bounded read window. This fails the manual-based Open expectation; cause remains
unknown. A separate Manual Open/Close control passed. Settings were restored and
handles released. [Raw-result index](../records/ttl-summary.json). External edges,
output voltage and independent physical/timing behavior remain unqualified;
the active-low safety warning still applies.
