# Manufacturer command and state traceability

Source IDs and revisions: [sources](sources.md). Implemented commands are traced
to SRC-001 Issue 36; the KSC101 applicability table includes the shared solenoid
commands. Later Issue 42.1 was inspected online as a cross-check. Actual firmware
support is still a commissioning result, not established by an allowlist alone.

| Function | APT message(s) | SRC-001 printed pages | Meaning / implementation |
| --- | --- | --- | --- |
| Identity | 0x0005 / 0x0006 | 52-53 | 84-byte payload; serial, model, firmware, HW revision, channel count |
| Mode | 0x04C1 / 0x04C2; set 0x04C0 | 187-188 | Channel 1; 1 Manual, 2 Single, 3 Auto, 4 Trigger; Manual transition requires explicit persistent-mode policy permission |
| Interlock requirement | 0x04C7 / 0x04C8 | 191-192 | 1 required, 2 disabled; query only, never bypass or reconfigure |
| Solenoid electrical state | 0x04CC / 0x04CD; set 0x04CB | 193-194 | Channel 1; 1 ON, 2 OFF; state readback is not blade feedback |
| Fault | 0x0080 / 0x0081 | 49-50 | Raw complete message retained; rich form includes command, code and text |
| Disconnect notification | 0x0002 | 49 | Invalidates session, never means shutter closed |
| USB initialization | FTDI calls | 28-29 | 115200, 8N1, 50 ms before/after purge, bridge reset, RTS/CTS, RTS asserted |

APT header: little-endian message word, two parameter bytes or payload length,
destination byte (bit 7 marks payload), source byte. Direct USB controller address
0x50, PC address 0x01; these addresses are not assumed for KEH3. Identity firmware
bytes in the full frame are 20 minor, 21 interim, 22 major; the normalized version
is major.interim.minor. One protocol channel is distinct from application CH.

SRC-002 sections 3.4 and 4 explain key, physical interlock, local modes and trigger
authority. SRC-002 p20 establishes that the last used mode is remembered at power-up.
Mode changes require `allow_persistent_mode_changes`; selecting an already Manual
mode sends no mode write. No code disables the physical interlock, primes triggers
or sends EEPROM/startup-configuration commands. `interlock_enabled` in feedback means
the reported requirement setting; it is not measured circuit continuity.

Cycle configuration, trigger configuration, status-bit interpretations and key
feedback are deliberately unavailable until applicability, attached shutter limits
and qualification are resolved. SRC-001's generic triggered-cycle description
differs from SRC-002's KSC101 level/priming behavior; no TTL behavior is released
by inference from the older T-Cube description.

Solenoid ON/OFF is electrical. Optical mapping and load limits require SRC-004
and an independent observed setup. The code cannot establish optical closure or
physical timing from a command or reply.

SRC-001 p34 limits data packets to 255 bytes for the supported protocol revision.
Receive headers must match the known reply/fault form and length before a payload
is awaited. After a partial/unknown-count write, no cleanup frame is appended to
the potentially misaligned transmit stream; explicit protected recovery is required.
