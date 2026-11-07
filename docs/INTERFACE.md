# Manufacturer command and state traceability

Sources: [register](sources.md), APT Issue42.1 (SRC-007), KSC101 operating manual
HA0368T RevD (SRC-002), KEH3 RevE (SRC-003), exact KSC101 Kinesis1.14.60 C/.NET
programmer references (SRC-008), and KSC101 RevF UI manual (SRC-010, reference
only, never a runtime dependency). Manufacturer documents define the contract;
SDK enum values and raw wire values must not be interchanged.

The generic APT status-bits layout on p128 does not list KSC101 in the protocol's
model command table. Its use here additionally rests on the exact KSC101 SDK
mask definition (SRC-008) and recorded real firmware-1.0.7 exchanges (E178).
Other firmware needs separate compatibility evidence; offline tests cannot add it.

| Operation | Request / reply / command | Contract | Application API |
| --- | --- | --- | --- |
| Identity | 0x0005 / 0x0006 | APT pp49-50; payload84; exact model/serial/firmware/one channel | connect, identify_device |
| Operating mode | 0x04C1 / 0x04C2; set0x04C0 | APT pp184-185; 1 manual, 2 single, 3 auto, 4 triggered | get_status; set_operating_mode permits policy-qualified modes; deployed profile Manual only |
| Cycle settings | 0x04C3 set / 0x04C4 request / 0x04C5 reply | APT pp186-187; payload14: uint16 channel1, uint32 on_ms/off_ms/count. RevF pp31-32: 100..10000 ms, 0..1000000 cycles | get/set_cycle_parameters; gated Manual/OFF writes, exact readback |
| Cycle-only storage | 0x04B9 | APT p99; payload4: uint16 channel1, uint16 message0x04C3; no ACK | set_cycle_parameters(persist=True), separate permission; restart verification outstanding |
| Identify LEDs | 0x0223 | APT p43; short header channel1; no ACK | blink_identify, no output write |
| Interlock requirement | 0x04C7 / 0x04C8 | APT pp188-189; 1 required, 2 not required; query only | get_status |
| Electrical output feedback | 0x0429 / 0x042A | APT p128: channel uint16 + status uint32; exact KSC101 GetStatusBits: mask0x1 enabled1/disabled0 | get_status; output-command readback |
| Raw solenoid-state reply | 0x04CC / 0x04CD | APT pp190-191 uses1/2; actual1.0.7 returned0; retain unmodified byte, no automatic enum conversion | get_solenoid_state_reply |
| Output command | 0x04CB, channel1, value1 ON/value2 OFF | APT pp190-191; RevF pp29-30 Open/Close or Start/Stop; values stay1/2 even though .NET feedback Closed=0 | set_solenoid Manual; start qualified native modes; safe_state Stop/OFF; D2XX or docked KEH3 |
| Enable alias | 0x0210 | APT p44/p190; can operate output | enable_device refuses; never initialization |
| Fault / disconnect | 0x0080, 0x0081 / 0x0002 | APT pp46-47; retain complete fault bytes, invalidate session | errors; never interpreted as closed |
| USB initialization | FTDI API calls | SRC-001 pp28-29; 115200,8N1, RTS/CTS; 50ms before/after purge, bridge reset, RTS asserted | explicit USB connect only |

APT uses a six-byte little-endian header, destination high bit for payload,
PC address0x01 and controller0x50. Payload bound255 (SRC-001 p34). Known reply
forms/lengths/addresses/channels are checked before acceptance. Status payload
is exactly6 bytes and channel1. Firmware bytes20/21/22 of a full identity frame
are minor/interim/major; normalized version is major.interim.minor.
The current Ethernet endpoint has actual identity/status evidence for address0x50;
this does not identify the hub or qualify other firmware/topologies. The exact
192.168.1.19:40305/68800777/1.0.7 SH05R setup now has actual ON/OFF evidence
(E181); the same0x04CB1/2 messages use that verified TCP route.
KEH3 Rev E section 4.3/Figure 17 routes left/middle/right bays to ports
40304/40305/40306 (rear view); port 40303 is management. APT Issue 42.1 p28
explicitly separates the command protocol from its transport. Docked bay writes
therefore use the same frames and owner checks. This defines the transport/command contract; E181 separately verifies selected-controller
ON/OFF. Hub identity/recovery and other topologies remain unqualified. VCP and KEH3 external
USB OUT control remain refused.

KSC101 .NET SolenoidStates is Closed0/Open1; OperatingStates is Active1/Inactive2.
The C SolenoidStates enum instead uses Closed2/Open1. Active can mean waiting for
a trigger or running a cycle, so output OFF cannot determine operating Inactive.
Normal feedback leaves operating_state unknown. shutter_state is optical and
also stays unknown without an independent measurement. interlock_enabled retains
the existing application's requirement-configuration meaning, not continuity.

Trigger configuration and general enable/disable are not exposed as setup
operations. Cycle writes require explicit permission/source assertion and
Manual/OFF; EEPROM needs separate opt-in and cannot claim ACK/persistence.
Mode changes are remembered at power-up
(SRC-002 p20); a real change requires policy.allow_persistent_mode_changes.
The KSC-specific trigger description takes precedence over generic T-Cube cycle
text; no TTL behavior is qualified by software readback.
For Triggered priming only count0 level-control is accepted, with explicit
continuous permission. No trigger-I/O configuration or native activity sensor
is implemented. See the [feature matrix and unresolved KSC101 layouts](gui.md#manufacturer-reference-and-implemented-functions).

There is one single-flight session per owned connection. Queries request new
replies; SDK caches/polling are not used. APT has no transaction ID, so
response_after_request_no_transaction_id describes provenance rather than proving
arbitrary delayed-reply freshness. Timeouts, unexpected/duplicate replies and
malformed data quarantine the session. Ordinary writes also refuse a quarantined
session. A qualified protective OFF can use known transmit alignment, but a
partial/unknown-count write blocks every further frame, including cleanup.

Real control confirmation allows a transient output bit: repeated fresh status
requests share the original deadline, without resending ON/OFF. Trigger->Manual
requires explicit source_inhibited=True and policy mode permission; OFF/deactivate
is sent and confirmed before Manual. Docked KEH3 control is supported through
this same path. VCP and external USB OUT remain restricted. See
[Ethernet validation](ethernet-assessment.md), [SH05R manual](sources.md) SRC-009.
