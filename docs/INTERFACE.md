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

KCubeShutter has no Ethernet argument/property/path. A private shared Kinesis
implementation supplies lifecycle/getters/setters to USB cubes and hub-owned
channels; ShutterHub owns all network endpoint selection and command dispatch.
Only explicit documented KEH3 cube endpoints are accepted; no KEH6 network map
or hub IP/firmware configuration is introduced.

## Communication and feedback

| Operation | SDK contract |
| --- | --- |
| Discovery | KCubeShutter filters FTDI USB entries; ShutterHub registers LAN entries, builds once, polls CheckForConnectionChanges for asynchronous identities, and filters TCPIP/comspec per slot |
| LAN range discovery | ScanEthernetRange(start, end, 40303, open_timeout_ms) finds host addresses; register their KEH3 ports40304–40307 and poll matching type68 TCPIP identities. Default inclusive range192.168.1.0–255, maximum256 addresses; no retained process handles |
| Connect | CreateKCubeSolenoid, Connect, settings initialization, StartPolling, identity check; no operating-feedback request |
| USB health | IsConnected true, USBConnected Connected or Connecting, CommsStatus OK |
| Ethernet health | ShutterHub owns endpoint/provider checks; its network channel requires IsConnected and CommsStatus OK |
| Status | RequestStatus, RequestOperatingMode, RequestOperatingState, optional trigger request, then cached getters |
| Identity | GetDeviceInfo; identify_device does not invoke the SDK's flashing IdentifyDevice operation |
| Release | Attempt StopPolling then Disconnect even when stopping polling fails |

Headless USB can remain Connecting while IsConnected/CommsStatus and actual reads
work; Connecting alone is never accepted as readiness. Disconnected/unknown or
communication errors fault the wrapper. Operating modes normalize Manual/SingleToggle/
AutoToggle/Triggered to manual/single/auto/triggered. Operating state0 is undefined and reported as unknown; it is never treated as Inactive. A request/wait does not establish cache age.
get_status() includes operating/TTL readback; get_operating_status() requests
only operating feedback, and get_trigger_config() requests only TTL settings.
get_cached_status() performs no I/O and is for display only, never output
authorization. GUI actions explicitly read selected-panel feedback after commands;
periodic refresh updates operating feedback while TTL settings are labelled last read.

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
or process. It contributes only to informational interlock_ready metadata; it
does not authorize output or override key/identity/communication checks. Raw bits and
interlock_enabled remain separate from operator_interlock_confirmed/interlock_ready.
These values remain available to Python callers. GUI Open/Arm do not gate on
interlock feedback or confirmation; users manage the physical interlock externally.

## Outputs and timing

Close: SetOperatingState(Inactive) only; operating mode is preserved.
Open: SetOperatingState(Active) only; operating mode and enable state are preserved.
Enable: explicit enable_device() -> EnableDevice. Disarm: Inactive -> Manual.
Setters return None and perform no prerequisite/status requests, feedback waits,
readback or automatic recovery. SDK write errors latch a fault. The caller owns
readiness and verification; the GUI performs explicit reads outside the setter.
A returned setter call cannot prove Inactive was applied before the next write.
Shutdown sends Close then releases; it does not verify physical closure.

Default polling/getter wait250ms; GUI refresh request1s. Native calls may block.
Setters have no programmed wait or feedback timeout. Settings initialization uses
the configured timeout. Host waits and snapshots are not optical measurements.

## TRIG1/TRIG2

| Contract | Exact members |
| --- | --- |
| Settings | RequestTriggerConfigParams/GetTriggerConfigParams/SetTriggerConfigParams |
| Properties | Trigger1Mode/Trigger1Polarity/Trigger2Mode/Trigger2Polarity |
| Direction enums | Disabled=0, TrigIN_GPI=1, TrigOUT_GPO=10 |
| Polarity enums | TriggerHigh=1, TriggerLow=2 |
| Arm | EnableDevice, Triggered, Active; no implicit readback |
| Disarm | Inactive then Manual commands; Close alone preserves mode; no implicit readback |

The GUI checks Closed/Inactive/Manual before Apply and Arm and reads back Apply
settings. Arm enables the channel, selects Triggered and sends Active. The main
Trigger Start instead preserves enable state/mode and sends only Active, after
Inactive/Closed feedback and an actual input-settings read. Both require a key
enabled indication. Direct API setters do not
perform those application checks. The hardware manual describes5V
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
