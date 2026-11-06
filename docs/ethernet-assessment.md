# KEH3 Ethernet Manual ON/OFF

Docked-bay control is implemented through the canonical ShutterHub/TCP/APT path.
The earlier blanket ban was an implementation restriction, not a manufacturer
prohibition. APT Issue42.1 section2.1 explicitly separates command framing from
transport. KEH3 DOC-103012 RevE section4.3/Figure17 assigns per-bay ports and
requires USB IN disconnected. KSC101's solenoid command is0x04CB, channel1,
value1 ON/value2 OFF (APT pp190-191). There is no USB/SDK fallback.

The exact selected controller at192.168.1.19:40305, middle bay, KSC10168800777,
firmware1.0.7/hardware3, has actual ON/OFF validation with the user-confirmed SH05R
and protected source/isolated trigger setup. The user requests this controller
at this endpoint; matching its exact live model/serial/firmware/channel count is
the selection authority. Hub serial/firmware remain unknown and are not reported
as verified. Management40303 is not used or programmed.

The same APT requests/commands and strict session/ownership/deadline logic apply
to USB and docked Ethernet. No command is automatically replayed. Output readback
polls fresh0x042A replies within the original deadline to allow a physical transition;
it never retries a failed query or resends the output command. The exact KSC101
API defines output mask0x1. Optical blade position is not inferred from it.

Manual is selected explicitly. A protected Trigger->Manual transition needs
source_inhibited=True plus policy permission for remembered mode changes. It sends
OFF/deactivate, confirms output clear, selects Manual and verifies Manual/OFF.
Ordinary ON/OFF never changes mode implicitly or primes a trigger. Interlock bypass,
EEPROM, trigger/cycle parameters and network settings are not exposed.

[The real notebook6 result](../records/ethernet-control-live.json) records one ON,
one1s added hold, priority OFF and release. Readback0x2000->0x2001->0x2000;
ON-to-OFF dispatch1.0569156s is a host observation, not optical exposure calibration.
Final controller Manual/OFF; handles/claims released. Source and policy are captured
in [the configuration](../config/shutter.ethernet.toml) and [manual register](sources.md).

Other occupied/empty/swapped bay/firmware combinations, shared-hub loss, hub
identity/recovery/persistence, independent optics and endurance remain separate
acceptance work. The implementation permits documented docked bays with exact
controller config and load policy; only this middle-bay setup has current physical
command evidence. VCP and external USB OUT control remain unavailable.
