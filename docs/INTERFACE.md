# KSC101 interface notes

## Chosen interface

Use the official Kinesis .NET assemblies through Python.NET, following
[Thorlabs' Python KSC101 example](https://github.com/Thorlabs/Motion_Control_Examples/blob/d85b2014d12018028c3eba1f724f42e94d3c47bf/Python/Kinesis/KCube/KSC101/KSC101_pythonnet.py)
and [Thorlabs' C# discovery example](https://github.com/Thorlabs/Light_Control_and_Manipulation_Examples/blob/main/C%23/KSC101/Initialize_and_Open/Program.cs).
Discovery filters device type 68. Example serial numbers are never treated as
the user's device identity. Import and GUI startup do not connect hardware.

The vendor examples establish available methods, not a complete recovery or
physical-validation policy. This project adds selection checks, serialization,
fault handling, feedback waits, and cleanup around them.

The [download page](https://www.thorlabs.com/software-pages/Motion_Control), inspected
on 2026-09-09 during E001, listed Kinesis 1.14.60 and a transition toward XA.
The current [KSC101 product page](https://www.thorlabs.com/k-cube-r-solenoid-controller?tabName=Overview),
verified on 2026-10-20 ([E018](../records/RECORDS.md#e018)), explicitly advertises
USB control with Kinesis or XA. This implementation uses Kinesis because the
official KSC101 example and inspected SDK establish its API contract. XA support
is a manufacturer claim; an XA backend has not been implemented or tested here.

Required assemblies: `Thorlabs.MotionControl.DeviceManagerCLI.dll`,
`Thorlabs.MotionControl.GenericMotorCLI.dll`, and
`Thorlabs.MotionControl.KCube.SolenoidCLI.dll`, with their vendor native dependencies.
Load only one SDK directory in a Python process. See
[Python.NET's runtime/assembly guidance](https://pythonnet.github.io/pythonnet/python.html).

## Observed API contract

Verified by reflection against official SDK build `1.14.60.27990`, without
connecting a controller. The native `Thorlabs.MotionControl.KCube.Solenoid.h`
shipped with that SDK corroborates state meanings and the interlock status bit.

| Purpose | Kinesis member / meaning |
| --- | --- |
| Discover | `BuildDeviceList`, `GetDeviceList(68)` |
| Connect | `CreateKCubeSolenoid`, `Connect`, settings initialization, `StartPolling` |
| Identity | `GetDeviceInfo().SerialNumberText`, `.Description` |
| Health | `IsConnected`, `USBConnected` (`Connected`), `CommsStatus` (`OK`, `Timeout`, `Error`) |
| Mode | `SetOperatingMode(Manual)`; other modes include timed and triggered operation |
| Command | `SetOperatingState(Active/Inactive)`; Active opens in Manual, Inactive closes |
| Reported position | `GetSolenoidState()` (`Open` / `Closed`), distinct from operating state |
| Safeguards | `Status.KeyEnabled`; `GetStatusBits() & 0x1000` is the documented interlock flag |
| Release | `StopPolling`, `Disconnect`; release alone is not closure |

`GetStatusBits` and the state getters expose vendor-maintained data. Polling and
`RequestStatus` request updates; the wrapper cannot attest to the age of every
field or independent physical motion. Communication health is checked before and
after sampling, and any observed fault invalidates displayed state. Hardware
tests must establish actual status/USB-loss behavior for the installed version.

Connection checks the returned identity against the selected serial; mismatch
fails before any output write and attempts release. Operating feedback is sampled
after the TTL request delay, avoiding a snapshot retained from before that wait.

Open preparation requests Inactive and verifies Closed/Inactive before selecting
Manual, then verifies Closed/Inactive/Manual before EnableDevice/Active. A successful setter alone cannot
satisfy that gate. Hardware must establish whether those reports are fresh and
represent physical position for the connected shutter; the mock cannot do so.

The program issues no explicit persist-settings or firmware calls, alters no
trigger wiring, and does not bypass safeguards. Successful Close/shutdown leaves
Manual/Inactive reported; the previous timed/triggered mode is not restored.
The manufacturer manual says the last mode is remembered across power cycles;
do not assume these runtime changes have no lasting effect or that a failed
shutdown disarmed the controller. Record actual startup/persistence behavior.

## Manufacturer documentation and unresolved configuration

The [current product page](https://www.thorlabs.com/k-cube-r-solenoid-controller?tabName=Overview)
explicitly lists KEH3/KEH6 as compatible power/communications hubs for up to
three/six KSC101 controllers. The hub uses a USB 2.0 circuit and the page limits
the combined cube load to 4.6 A. This confirms the intended KEH3 USB topology at
the manufacturer-documentation level; installed supply/load, enumeration,
identity mapping, feedback and physical closure remain unvalidated. It does not
establish an Ethernet transport for this repository.

[KSC101 manual, HA0368T Rev D, June 2023](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf):
sections 3.3-3.4 cover setup and interlocks, 4.3 covers operating modes, and
Appendix C lists specifications. This file contains legacy APT software material;
it is used for hardware context, while Kinesis calls come from the current SDK.

The manual specifies a regulated 15 V supply rated 1 A and cautions against
changing the interlock connection while powered. These are manufacturer details,
not observations of this bench. Exact shutter model, supply, serial, firmware,
key/interlock arrangement, optical environment, and physical feedback remain unknown.
Do not infer a compatible configuration from a successful DLL call.

## TTL interface

New TTL members were verified by **static official API-help inspection**, not by
loading assemblies or querying this bench. The official
[Kinesis .NET API CHM](https://github.com/Thorlabs/Motion_Control_Examples/tree/3ef959523e2be48d57704af964f7a2c24547b722/C%23/Benchtop/BBD30X/BBD30X_Ethernet)
contains the KSC101-specific `Thorlabs.MotionControl.KCube.SolenoidCLI` namespace.
Local extracted references: `a07553.html` (KCubeSolenoid), `a07565.html`
(TriggerConfigSettings), `a07549_a4682b683a86f17b04ee9fe588f7f913f.html` (OperatingModes).
The enclosing example is for BBD; its motor trigger APIs are not used here.

| Contract | Exact SDK members |
| --- | --- |
| Settings request/read/write | `RequestTriggerConfigParams()`, `GetTriggerConfigParams()`, `SetTriggerConfigParams(TriggerConfigSettings)` |
| Settings properties | `Trigger1Mode`, `Trigger1Polarity`, `Trigger2Mode`, `Trigger2Polarity` |
| `TriggerConfigSettings.TriggerPortMode` | `Disabled=0`, `TrigIN_GPI=1`, `TrigOUT_GPO=10` |
| `TriggerConfigSettings.TriggerPolarity` | `TriggerHigh=1`, `TriggerLow=2` |
| Arming | `EnableDevice()`, `SetOperatingMode(SolenoidStatus.OperatingModes.Triggered)`, `SetOperatingState(Active)` |
| Disarming | `SetOperatingState(Inactive)`, require Closed/Inactive feedback, `SetOperatingMode(Manual)`, require Closed/Inactive/Manual |

Apply requires Closed/Inactive/Manual and matches both ports against readback.
Readback requests wait one polling interval before reading cached vendor settings;
matching data does not prove response freshness or voltage at a connector. Arm
checks Triggered/Active, safeguards and configuration; physical position can be
Closed while primed. Manual Open refuses Triggered mode. Unknown enum values or
read/write errors fault the wrapper and invalidate TTL status. No fallback guesses
or explicit EEPROM/persist calls are made. Actual persistence across power cycles
must be recorded at the bench.

Manual section 3.4.1 documents bidirectional TRIG1/TRIG2, selectable active
polarity, 5 V TTL, Triggered mode and priming. A disconnected input is LOW;
active-low can open when primed. This code exposes configuration and operating
state, not raw input levels, output voltage, edge counts or calibrated timing.
Installed-SDK and physical validation remain pending under the hardware hold.
