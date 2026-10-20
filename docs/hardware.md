# Hardware and validation status

[README](../README.md) · [Setup](getting-started.md) · [Interface notes](INTERFACE.md)

The intended system is up to three Thorlabs KSC101 K-Cube Solenoid Controllers
through a KEH3 USB hub, each driving a compatible Thorlabs optical shutter, with
manufacturer-approved power/cabling and a USB-connected control computer.
**No physical configuration has yet passed acceptance.** The current
state is **AWAITING_HUMAN_REVIEW**, with REQ-003–008 blocked.
Three-panel software support does not establish KEH3 USB compatibility at the
bench. KEH3 Ethernet control is outside the implementation; hardware access
remains on hold.

Thorlabs' [current KSC101 product page](https://www.thorlabs.com/k-cube-r-solenoid-controller?tabName=Overview),
verified on 2026-10-20, explicitly lists KEH3 as a compatible hub for up to three
controllers. It provides power and USB 2.0 communications through one host USB
connection; the stated combined cube-load limit is 4.6 A. This is manufacturer
compatibility evidence ([E018](../records/RECORDS.md#e018)), not a measurement of
the installed bench. Supply/load ratings and every physical acceptance gate
still require verification under the existing hold.

## What is established

| Item | Established evidence | Still required |
| --- | --- | --- |
| Controllers | Human-supplied targets: three KSC101s through KEH3 USB | Each actual identity/serial, firmware, availability and shutter/panel mapping |
| Optical shutters | Human-supplied compatible Thorlabs shutters | Each exact model, compatibility, feedback capability and operating limits |
| Hub, power and cables | KEH3 USB is the requested topology | Actual hub variant/identity, approved supply/docking/USB arrangement, each shutter cable and power-up procedure |
| Software | Windows x64 / Python 3.12 software tests; historical Kinesis 1.14.60.27990 SDK load and contract inspection | Installed vendor runtime/USB driver readiness on the bench computer |
| GUI and API | Software tests and actual browser operation against the test fixture | Physical motion, feedback, reconnect, faults and shutdown through the GUI/API |

Historical enumeration found zero devices ([E002](../records/RECORDS.md#e002)).
That is not a current device check or proof of a wiring/driver fault. No hardware
was accessed during the readiness audit or this documentation pass.

## Connection overview

```mermaid
flowchart LR
    P[Windows computer with Kinesis] <-->|USB| H[KEH3: intended, unverified]
    V[Manufacturer-approved hub supply] -->|Power| H
    H --> C[Up to three KSC101 cubes]
    C -->|One compatible shutter per cube| S[Optical shutters]
    I[Existing key / interlock arrangements] -. safeguards .-> C
```

This is a functional topology, **not a wiring diagram or pinout**. Supply, shutter,
trigger and interlock details must be checked against the actual equipment and
manufacturer instructions. The physical configuration is still unknown.
The hub arrangement needs its own KEH3 manual and supply/docking checks; a single
cube's supply specification below does not establish the hub supply requirements.

The [KSC101 manual, HA0368T Rev D](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf)
is the project's recorded hardware reference: setup/interlocks in §§3.3–3.4,
operating modes in §4.3, specifications in Appendix C. The previously inspected
manual specifies a regulated 15 V supply rated 1 A; this does not identify or
validate the installed supply, connector polarity or shutter compatibility.
Use the actual model's manual before making connections. Preserve all existing
interlocks and follow the approved power-down procedure for cable changes.

## Vendor software

Install the official [Thorlabs Kinesis software](https://www.thorlabs.com/software-pages/Motion_Control)
appropriate to the Windows/Python bitness, including its runtime dependencies and
USB drivers. The controller explicitly loads .NET Framework through
[Python.NET](https://pythonnet.github.io/pythonnet/python.html).

The inspected SDK was **1.14.60.27990 x64**. Its administrative extraction is
ignored/local and absent from a fresh clone; it is not a USB-driver installation.

`uv sync` installs Python dependencies only. The loader expects the Kinesis folder
to contain DeviceManagerCLI, GenericMotorCLI and KCube.SolenoidCLI assemblies with
their vendor dependencies. Choose a nonstandard folder with `KINESIS_DIR` or
`--kinesis-dir`; restart Python before selecting a different SDK installation.
See [INTERFACE.md](INTERFACE.md) for the precise assembly names and vendor sources.

## From simulation to physical acceptance

```mermaid
flowchart LR
    A[Install] --> B[Simulate]
    B --> C[Test]
    C --> R[Review + bench checks]
    R -. approval .-> D[Connect + verify identity]
    D -. pending .-> E[Observe physical operation]
    style R fill:#fff4d6,stroke:#a67824
    style D fill:#fff4d6,stroke:#a67824
    style E fill:#fff4d6,stroke:#a67824
```

The software path has been exercised. Every physical stage is still pending;
the diagram is an overview, not authorization or a substitute for the
[ordered validation procedure](HARDWARE_VALIDATION.md). That procedure starts
with bench facts and safeguards, then discovery and passive connection/identity/
release, first Close, individual Open/Close, shutdown/reconnect, GUI/Ctrl+C,
approved-dwell repetition, and closed-state USB-loss/recovery. The multi-controller
stage additionally verifies three serial/shutter/panel mappings, unaffected
neighbors during individual operations/reconnect, and all-controller shutdown.

Acceptance needs independent observation, comparison with reported state, approved
operating/dwell limits and observed shutdown. No physical timing, optical transmission
or calibration result has been established.

## Shutdown and operating limits

Open/Close select Manual mode; successful Close reports Manual/Inactive and does
not restore the prior mode. The manual describes mode persistence across power
cycles. Initialization, polling and preparation feedback before Enable still need
bench validation. See [interface notes](INTERFACE.md) for the command sequence.

Normal per-controller cleanup attempts Close then release. Hub/GUI/CLI shutdown
attempts every slot sequentially and continues after reported failures, identifying
each failed slot/serial. There is no total latency guarantee: a hung vendor call
can prevent later attempts. Abrupt power/USB/process failure also prevents a
closure guarantee. Keep the independent beam block/source
disable, approved observation method and physical shutdown method required by
the hardware procedure. No firmware change or safeguard bypass is authorized.

## Hardware photographs

No project-owned or user-provided bench photos are available. No vendor imagery
has been copied into the repository; use the linked official manual for identification.
Future user-supplied photos would make this guide more useful:

| Photo to add | Useful caption content |
| --- | --- |
| Overall controller/shutter setup | Identify the KSC101, actual shutter, USB link and supported supply; show cable routing |
| Controller connections with power off | Identify shutter, power and USB connections without implying an unverified pinout |
| Shutter model label and mounting | Establish the actual model/orientation; omit private inventory or serial information where needed |

Add captions and record the verified configuration when these photos become available.
