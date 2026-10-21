# Practical hardware test procedure

[Bench evidence](../records/hardware-validation.json) | [Interface](INTERFACE.md) |
[Examples](examples/README.md) | [Diagnostic helpers](hardware_tests/README.md)

## What the bench taught us

The working configuration is **computer -> USB -> KEH3 left bay -> KSC101
(alias CONTROLLER_A), firmware 1.0.7 -> SH05R**, using Kinesis 1.14.60.27990 on Windows x64.
Historical USB identity/status/reconnect, Open/Close, production shutdown and real
GUI actions worked on their recorded revisions. Current mode controls and
launcher shutdown have software validation and need affected bench checks. The user confirmed five physical Open/2-second hold/Close/2-second hold
cycles. Later GUI/shutdown runs established electronic feedback and cleanup;
they did not independently measure blade motion or exposure timing.

| Experience | Use this lesson next time |
| --- | --- |
| Searching for a COM port led nowhere | This USB path uses Kinesis/FTDI; discover the controller serial instead. |
| USB reported `Connecting` despite successful reads | Judge the combined identity, `IsConnected`, `CommsStatus` and responses. One SDK label is insufficient. |
| Firmware 1.0.6 returned a mismatched hardware serial | The official 1.0.7 update repaired USB identity. Never conceal a mismatch with a software alias; firmware work is separate maintenance. |
| Repeated interlock reads and jack/key changes did not resolve readiness | The jack matrix established no software continuity signal. Preserve unknown; key feedback is separate. Users manage the physical circuit externally; no software interlock gate. |
| Mode/status interpretation delayed useful tests | Auto is a valid mode. Undocumented operating value `0` does not mean Inactive. Use documented commands and verify the resulting state. |
| Ethernet initially found only the hub | A responding hub/port does not prove cube communication. E128 now validates one KEH3/KSC101 passive LAN connection after asynchronous SDK refresh was fixed; actuation/timing remain untested. |
| Actual GUI actions exposed issues that helper stages missed | Exercise the production path early, including refresh, reconnect and cleanup. |

The old process split related checks across too many stages, repeatedly asked for
unchanged facts, and made a complete bench form a routine prerequisite. Replace
that with three stages, one short result record, and intervention only for a
specific unresolved dependency.

## Three stages for commissioning or a relevant change

Before starting, establish the target serial/shutter mapping, one controller owner,
normal physical interlock, independently blocked/disabled source, approved hold
and independent shutdown action. Reuse established authorization within its scope;
recheck changed or transient conditions. Installation/firmware checks belong to
configuration changes, not every session.

### 1. Connect and read

Discover once, select the intended serial, connect and read identity/status.
**Pass:** identity matches; communication and requested reads succeed. Record raw
unknown values honestly. Reading needs no mode/output change or complete old
bench form. Stop on wrong identity or failed communication before motion.

Use the GUI's Discover/Connect, or the passive tutorial:

```powershell
uv run --locked python docs/examples/02_connect_and_read_status.py $env:SHUTTER_SERIAL
```

### 2. Close, then one Open/hold/Close

Read status first. With verified identity, send explicit Disarm and require
Closed/Inactive/Manual before enabling the channel once as needed. This avoids
enabling while a retained Active state is still selected.
Command Open, require Open/Active/Manual, hold for the
approved interval, then Close and require Closed/Inactive/Manual. The qualified
bench used a **2-second added hold**; this is not a universal limit or calibrated
exposure. One cycle is sufficient for this functional check.

**Pass scope:** matching feedback establishes the software/device path; independent
blade observation establishes physical operation. Record which was obtained;
without observation, physical agreement stays untested. No fixed cycle-count or
soak stage is required. Repeat only to answer a specific question.

### 3. Use the GUI and finish cleanly

Check the selected controller/state, one Open/Close interaction, refresh without
replay, and release/reconnect. Reuse Stage 2's cycle if it ran through the GUI.
Unused slots should stay disconnected. Finish Closed with **Close & disconnect
all** to retain the server, or **Shut down GUI & devices** to release and exit the
launcher. Normal terminal **Ctrl+C** also attempts cleanup. Verify release and
server exit when requested. For
commissioning, reconnect once to check identity/Closed, then release.
**Pass:** expected UI feedback, no replay/duplicate owner, closure feedback and
successful cleanup; retain any physical-observation limit from Stage 2.

Browser closure does not stop the controller. Test shutdown *from Open* only as a
targeted shutdown regression with applicable authority/protection; it was already
exercised on this bench, and is not a routine-session requirement.

## Routine use of the unchanged, qualified bench

**Connect/read -> Close baseline -> operate as needed -> Close and release.**

No commissioning rerun, repeated passive-connect cycles, firmware check, complete
bench form or approval between ordinary commands. A status-only task ends with
passive release and needs no Open/Close cycle. Use the
[normal GUI launcher](../README.md#launch-and-operate). Users manage the physical
interlock externally; software confirmation is optional informational metadata.

On failure, stop the sequence; do not automatically replay commands. Attempt
Close/cleanup on a verified target and use independent recovery if needed. After
an unverified failed connection, use passive release. Failed release retains
ownership: preserve the handle/error instead of creating another owner.

## Separate tests, only when their capability is needed

| Test | Question and current limit |
| --- | --- |
| Ethernet | E128 / TEST-138 passed one KEH3/KSC101 explicit-endpoint discovery, identity, Connect and passive release. Hub 40303; left/middle/right bays 40304/40305/40306. Follow the [passive Ethernet note](ethernet-assessment.md); range scanning, current GUI bench operation and Ethernet actuation/timing remain unqualified. |
| Three controllers | Do three real mappings operate independently and all clean up? Single-pair success does not qualify this; REQ-023 remains open. |
| TTL | Actual no-cable configuration/Arm/Disarm passed, but both active-low position checks failed (still reported Closed). See [E082 results](../records/ttl-summary.json). External signals/voltage remain untested; REQ-031 stays open. Arm can open immediately. |
| Loss/recovery | Does a specifically authorized Closed-state communication-loss test fault and recover correctly? Physical injection remains untested, REQ-006. |
| Physical timing/shutdown | Does independent observation/instrumentation establish blade state and any required timing? Host waits/readback are insufficient; remaining REQ-005/007 evidence is still needed. |

These are separate acceptance gaps, not gates before routine single-pair USB use.
Do not change firmware, wiring, network settings or triggers as an incidental test.
Revalidate the affected path after relevant changes.

Record only what makes the result reproducible: date/test purpose, code revision,
serial/transport and changed configuration, action/hold, expected versus observed
feedback, independent observation if any, errors and final release outcome.
Label results PASS/FAIL/UNTESTED with their scope. Keep raw logs when useful for
diagnosis. Historical records/helper filenames retain old stage numbers in the
[archive](../records/archive/README.md); this procedure supersedes that sequence
without altering its evidence.
