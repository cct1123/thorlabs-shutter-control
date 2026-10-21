# Hardware and evidence

[README](../README.md) | [Commissioning](HARDWARE_VALIDATION.md) | [Ethernet](ethernet-assessment.md)

KSC101 drives an SH05R shutter through manufacturer-approved supply, wiring and
physical interlock. USB addresses individual cube serials directly or through
KEH3/KEH6 USB hubs. KEH6 and multiple real pairs are not qualified here; software
panel count does not establish electrical/power capacity or simultaneous timing.
Power down before redocking or changing shutter/interlock wiring.

![Manufacturer KSC101/SH05R photo](assets/ksc101-sh05r.webp)

[Photo source](https://www.thorlabs.com/optical-shutters); not a test-bench image.

## Retained observations

[hardware-evidence.json](../records/hardware-evidence.json) consolidates observations
with their original revision/configuration scope. It is not a current calibration.

| Observation | Scope |
| --- | --- |
| USB identity/status/reconnect and five Open/hold/Close cycles | Electronic feedback passed; user confirmed the physical sequence on the recorded revision |
| GUI and shutdown | Browser/USB readback and communication release passed on recorded revisions; independent shutdown timing unmeasured |
| KEH3 explicit-endpoint Ethernet | One KSC101 discovery/identity/Connect/passive release passed; no output command in that test |
| LAN notebook | User reports success; preserved output reports discovery, identity, Open/Close feedback and release |
| No-cable TTL | Configuration/priming/Disarm passed; both active-low Open expectations failed with reported Closed; cause unknown |

## Current limits

Current source changes need affected USB/GUI/cleanup bench requalification.
Live LAN range scans, Ethernet actuation/timing/recovery, KEH6/multiple actual
pairs, external electrical TTL signals, physical communication-loss recovery and
calibrated optical/exposure/shutdown timing remain unqualified. Controller
readback and API call durations do not independently establish blade position.
Software cleanup cannot bound a blocking native call; use independent protection.

Physical acceptance requires documented topology, exact local identities/versions,
approved conditions and independent observations. Keep raw bench data and executed
notebook results in ignored inputs/private; publish sanitized summaries only.
