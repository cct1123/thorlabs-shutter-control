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
| Operating mode | 0x04C1 / 0x04C2; set0x04C0 | APT pp184-185; 1 manual, 2 single, 3 auto, 4 triggered | get_status; persistent-mode permission allows protected set_operating_mode for all four; qualified_modes separately gates activation |
| Cycle settings | 0x04C3 set / 0x04C4 request / 0x04C5 reply | APT pp186-187; payload14: uint16 channel1, uint32 on_ms/off_ms/count. RevF pp31-32: 100..10000 ms, 0..1000000 cycles | get/set_cycle_parameters; gated Manual/OFF writes, exact readback |
| Cycle-only storage | 0x04B9 | APT p99; payload4: uint16 channel1, uint16 message0x04C3; no ACK | set_cycle_parameters(persist=True), separate permission; restart verification outstanding |
| Identify LEDs | 0x0223 | APT p43; short header channel1; no ACK | blink_identify, no output write |
| Interlock requirement | set0x04C6; 0x04C7 / 0x04C8 | APT pp188-189; query, or enable requirement only; no disable API | get_status; guarded require_interlock |
| Electrical output feedback | 0x0429 / 0x042A | APT p128: channel uint16 + status uint32; exact KSC101 GetStatusBits: mask0x1 enabled1/disabled0 | get_status; output-command readback |
| Raw solenoid-state reply | 0x04CC / 0x04CD | APT pp190-191 uses1/2; actual1.0.7 returned0; retain unmodified byte, no automatic enum conversion | get_solenoid_state_reply |
| Output command | 0x04CB, channel1, value1 ON/value2 OFF | APT pp190-191; RevF pp29-30 Open/Close or Start/Stop; values stay1/2 even though .NET feedback Closed=0 | set_solenoid Manual; start qualified native modes; safe_state Stop/OFF; D2XX or docked KEH3 |
| Enable alias | 0x0210; query0x0211/0212 | APT pp44-45/p190; SET can operate output | Typed driver encoder and owner get_channel_enabled; enable_device refuses; canonical owner ON/OFF remains0x04CB |
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
The flat status schema omits unavailable activity/key/blade feedback.
interlock_required records requirement configuration, not continuity. Human
optical_closed_at/evidence remain separate from electrical output readback.

Trigger configuration and general enable/disable are not exposed as setup
operations. The explicit interlock setter only enables the requirement. Cycle writes require explicit permission/source assertion and
Manual/OFF; EEPROM needs separate opt-in and cannot claim ACK/persistence.
Mode changes are remembered at power-up
(SRC-002 p20); a real change requires policy.allow_persistent_mode_changes.
The KSC-specific trigger description takes precedence over generic T-Cube cycle
text; no TTL behavior is qualified by software readback.
For Triggered priming only count0 level-control is accepted, with explicit
continuous permission. No trigger-I/O configuration or native activity sensor
is implemented. See the [feature matrix and unresolved KSC101 layouts](gui.md#manufacturer-reference-and-implemented-functions).

There is one single-flight session per owned connection. Before dispatch, a
query drains all currently arrived chunks within its existing deadline. A queued
reply behind a full transport buffer is rejected before a new request; continuous
event traffic can exhaust the budget but cannot authorize dispatch. A remaining
partial frame is ambiguous. Queries request new
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

## Issue 42.1 command coverage audit, 8 November 2026

Historical E225 snapshot before REQ-249 implementation. The current additions
are listed in the documented-command implementation section below; the original
per-ID audit record is preserved unchanged.

**Not all listed commands are implemented.** Reference: SRC-007, Issue42.1,
9 September 2025, 443 pages, SHA256
b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed.
The TSC001/KSC101 table on pp11-12 has 36 IDs, followed by three KSC101-only
entries. GET messages are controller replies, not extra host commands. A generic
Frame encoder or recognized response length does not constitute a command API.

| Family / table IDs | Actual implementation | Manual pages |
| --- | --- | --- |
| Hardware information 0x0005/0006 | Query, decode and exact identity verification | 49-50 |
| Identify 0x0223 | LED flash request, no acknowledgement | 43 |
| Mode 0x04C0/C1/C2 | Set/query/decode all four values; activation remains policy-gated | 184-185 |
| Cycle timing/count 0x04C3/C4/C5 | Set/query/decode, using KSC101-specific 100..10000 ms bounds | 186-187 |
| Interlock 0x04C6/C7/C8 | Query/decode only; SET 0x04C6 absent | 188-189 |
| Solenoid state 0x04CB/CC/CD | ON/OFF plus raw query/reply; no invented conversion of raw firmware zero | 190-191 |
| EEPROM 0x04B9 | Cycle-parameter storage only; no EEPROM ACK or restart proof | 99 |
| Channel enable 0x0210/11/12 | SET alias deliberately refused; no request API; 0x0212 has framing validation only | 44-45, 190 |
| Automatic updates 0x0011/0012/0481 | No start/stop or typed status-update implementation; explicit status queries used | 48, 120 (table says119) |
| Hub bay 0x0065/0066 | No query/decoder; p52 describes legacy T-Cube bay identities, not a verified KEH3 management contract | 52 |
| LED indication modes 0x04B3/B4/B5 | Absent; detailed flags include motor/limit-switch concepts needing solenoid applicability review | 92-93 |
| Button parameters 0x04B6/B7/B8 | Absent; details describe motor jog/position/homing | 97-98 |
| Absolute move/completed/stop 0x0453/0464/0465 | Absent; shutter table lists them but no verified shutter-specific semantics | 80-81, 85 |
| KSC101-only SET 0x0520/0523/0526 | Absent; model table conflicts with motor-only detailed sections | 12, 134-144 |
| Disconnect/fault 0x0002/0080/0081 | Incoming events handled, raw fault data retained; host HW_DISCONNECT is not transmitted by close()/disconnect() | 46-47 |

Of the 39 table IDs, 10 are transmitted, five are queried replies, three have
inbound handlers, one is framing-only and 20 have no typed implementation.
This is a coverage inventory, not a trustworthy percentage of required KSC101
features: the applicability table itself contains contradictions. Full ID/name/
page/classification/source hashes: [audit record](../records/apt42-command-coverage.json).

The additional 0x0429/042A status-bit path is implemented but absent from the
KSC101 table. Its output-bit interpretation relies on SRC-008 and historical
firmware evidence; Issue42.1 alone does not establish the KSC101-specific mask.

### Conflicts and implementation boundaries

- p12 lists 0x0520/0523/0526 for KSC101; pp134/137/141 restrict the detailed
  layouts to motor-controller models. Their related REQ/GET IDs 0x0521/22,
  0x0524/25 and 0x0527/28 are also absent from this implementation.
- MMI prose specifies 36 data bytes while the header gives 0x1C (28). Trigger
  SET prose specifies 22 while the header gives 0x0C (12). These are not verified
  KSC101 layouts; do not guess commands merely to increase table coverage.
- p186 prints a 10000-second ON/OFF maximum. The KSC101 RevF manual p31 instead
  specifies 10000 milliseconds, matching current code. Do not expand the limit
  from the conflicting generic protocol text.
- Triggered mode selection exists; native priming supports only the KSC101
  count0 level-control subset, not the full generic edge/cycle description.
- Interlock disabling and channel-enable aliases are deliberately excluded from
  normal operation. Publishing a command does not authorize using it.

The normal connect/read/Manual ON/OFF path is implemented; complete Issue42.1
coverage is not. This audit changed no runtime code or device configuration.

## Documented-command implementation, 8 November 2026

REQ-249 implements the clear scalar/word/header layouts without adding motor
position, button, MMI or trigger-I/O payloads:

| IDs | Implementation | Reference / boundary |
| --- | --- | --- |
| 0x04C6 | require_interlock, with permission/protection, Manual/OFF and confirmed requirement | p188; sends value1 only; never bypasses interlock |
| 0x0211/0212 | get_channel_enabled boolean; reject wrong channel/unknown enum | pp44-45; not optical feedback |
| 0x0210 | Typed low-level driver output alias | p44/p190; never initialization; owner ON/OFF still uses0x04CB |
| 0x0065/0066 | get_hub_bay_reply raw byte; validate reserved byte | p52; no mapping to verified KEH3 bays/identity |
| 0x04B3/B4/B5 | LED indication mask write/read, exact RAM readback | pp92-93; channel/mask word pair; documented bits1/2/8, no shutter-state interpretation |
| 0x0011/0012 | Explicit start_updates/stop_updates | p48; no ACK, thread, implicit start or implicit stop |
| 0x0481 | Raw frame collection through get_events | Payload intentionally opaque; no motor-status layout guessed |
| 0x0002 | Explicit protected hardware disconnect plus release; incoming handling retained | p46; ordinary close()/disconnect() remain passive |

p93's request diagram prints 0x0411, inconsistent with the 0x04B4 section header
and KSC101 applicability table. The implementation uses the consistently named
0x04B4 request and never sends that motor-position request. LED flags are a raw
documented mask; no LED bit is converted into shutter position or readiness.

Existing settings permissions and firmware identity checks still apply; the live
configuration is unchanged. EEPROM remains cycle-only. Ambiguous motor/button/
MMI/trigger families and interlock disabling remain excluded. Software tests do
not qualify these new operations on real firmware. Current per-ID evidence:
[shutter-commands-coverage.json](../records/shutter-commands-coverage.json).
