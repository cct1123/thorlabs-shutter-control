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

The [current download page](https://www.thorlabs.com/software-pages/Motion_Control)
lists Kinesis 1.14.60 and notes a transition toward XA. Kinesis is used here because
the official KSC101 example and inspected KSC101 SDK directly establish support.
No assertion is made about KSC101 support in XA. Revisit the choice if official
device-specific support changes.

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

The program does not persist settings, alter trigger wiring, bypass safeguards,
or write firmware. Selecting Manual for explicit shutter operations is a runtime
mode change; it is not restored on shutdown, so timed/triggered output stays disarmed.

## Manufacturer documentation and unresolved configuration

[KSC101 manual, HA0368T Rev D, June 2023](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf):
sections 3.3-3.4 cover setup and interlocks, 4.3 covers operating modes, and
Appendix C lists specifications. This file contains legacy APT software material;
it is used for hardware context, while Kinesis calls come from the current SDK.

The manual specifies a regulated 15 V supply rated 1 A and cautions against
changing the interlock connection while powered. These are manufacturer details,
not observations of this bench. Exact shutter model, supply, serial, firmware,
key/interlock arrangement, optical environment, and physical feedback remain unknown.
Do not infer a compatible configuration from a successful DLL call.
