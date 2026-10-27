# KSC101 interface contract

[API](python-api.md) | [Hardware](hardware.md) | [Ethernet](ethernet-assessment.md)

Use Windows x64, Kinesis .NET Framework assemblies and Python.NET. The retained
bench configuration used Python3.12.7, Python.NET3.1 and Kinesis1.14.60.27990 with
KSC101 firmware1.0.7. The current software baseline still needs bench qualification.

Official references: [Kinesis](https://www.thorlabs.com/software-pages/Motion_Control),
[vendor examples](https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python),
[KSC101 manual sections3-4](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf),
[KEH3 manual section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351).

## Transport and feedback

| Operation | Contract |
| --- | --- |
| USB | KSC101 eight-digit68 serial, FTDI transport; no COM port |
| KEH3 Ethernet | Hub40303; left/middle/right40304/40305/40306; USB OUT40307; exact TCPIP endpoint/provider required |
| Discovery | Register LAN entries, BuildDeviceList once, refresh CheckForConnectionChanges, enumerate type68 identities |
| Range scan | ScanEthernetRange(start,end,40303,open_timeout_ms) returns host-address strings; bounded inclusive range; no owned handles |
| Connect | CreateKCubeSolenoid, Connect, settings initialization, StartPolling, GetDeviceInfo identity validation; no output/mode writes |
| USB health | IsConnected plus USBConnected Connected/Connecting and CommsStatus OK |
| LAN health | IsConnected, CommsStatus OK and exact TCPIP endpoint/provider |
| Feedback | RequestStatus/OperatingMode/OperatingState, optional trigger request, then named getters without added sleeps |
| Identity | GetDeviceInfo; no display-flashing IdentifyDevice call |
| Release | Attempt StopPolling and Disconnect even if stopping polling fails |

Connecting alone is insufficient readiness. Undefined operation0 is unknown.
Operating modes normalize Manual/SingleToggle/AutoToggle/Triggered to
manual/single/auto/triggered. A request/getter pair does not establish cache age;
the returned value may precede the request. SDK polling remains enabled.
Cached snapshots support display and selection of read breadth, not output
authorization. The GUI always requests feedback before checking readiness.
Its settings comparison uses the SDK getter; write acknowledgement/freshness is
not established by that comparison.

## Commands and physical interlock

Open/Close request Active/Inactive only; enable and mode are preserved. Explicit
EnableDevice enables the channel. Disarm requests Inactive then Manual. Setters
return None without readiness reads, sleeps or verification; SDK exceptions latch
faults. Close/release remain available after faults. Shutdown requests Close and
releases without independently proving closure.

Key feedback is separate from the physical interlock. Status bit0x1000 is a positive
interlock indication; a clear bit stays unknown. The recorded jack/key matrix did
not establish a software continuity signal. Users manage the physical circuit;
GUI Open/Arm do not use interlock feedback as a gate.

## TRIG1/TRIG2

| Item | Vendor members |
| --- | --- |
| Read/write | RequestTriggerConfigParams/GetTriggerConfigParams/SetTriggerConfigParams |
| Properties | Trigger1Mode/Trigger1Polarity/Trigger2Mode/Trigger2Polarity |
| Directions | Disabled=0, TrigIN_GPI=1, TrigOUT_GPO=10 |
| Polarity | TriggerHigh=1, TriggerLow=2 |
| Arm | EnableDevice, Triggered, Active |
| Disarm | Inactive, Manual |

GUI Apply/Arm require Closed/Inactive/Manual; Apply checks readback and Arm reads
actual input settings. Main Trigger Start preserves mode/enable state and requires
Inactive/Closed plus key/input feedback. Driver methods perform no such reads.
The manual describes5V TTL and disconnected input LOW; active-low can open without
a cable. Electronic no-cable low-position expectations failed on both ports; no
workaround is applied. No explicit EEPROM persistence call is made, and power-cycle
persistence, pin voltage/edges and optical timing remain unmeasured.
