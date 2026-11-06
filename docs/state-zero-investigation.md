# KSC101 firmware 1.0.7 state-zero investigation

6 November 2026; actual controller 68800777, hardware 3, one channel,
192.168.1.19:40305, KEH3 middle bay. All new operations were read-only. No
simulator, SDK runtime, output/enable/mode write, priming, setting or reset was used.

## Exact KSC101 API reference

The KSC101 Kinesis .NET API defines separate enums:

| API enum | Values | Meaning |
| --- | --- | --- |
| SolenoidStatus.SolenoidStates | Closed=0, Open=1 | Controller-indicated solenoid state |
| SolenoidStatus.OperatingStates | Active=1, Inactive=2 | Operating command/state; mode-dependent behavior |
| SolenoidStatus.OperatingModes | Manual=1, SingleToggle=2, AutoToggle=3, Triggered=4 | Operating mode |

Zero is documented as Closed in the .NET feedback enum. The KSC101 C header and
older APT state table instead enumerate Open/ON=1, Closed/OFF=2. These are
different representations; the .NET enum alone does not establish a universal
raw 0x04CD mapping across firmware. The earlier conclusion that zero was entirely
undocumented was incomplete.

Documentation was extracted from the validly Thorlabs-signed local Kinesis
installer 1.14.60.0. No installer, SDK, DLL or driver was executed or installed.
Exact paths, hashes and provenance are in
[API-reference findings](../records/ksc101-api-reference-findings.json), SRC-008.

- [Exact KSC101 SolenoidStatus numeric enums](../inputs/reference/state-zero/kinesis-1.14.60/dotnet-api/a08484.html).
- [Exact KSC101 GetStatusBits output mask](../inputs/reference/state-zero/kinesis-1.14.60/dotnet-api/a08488_a33fd41ba3b79a5078c4609d804c51376.html).
- [Exact KSC101 GetOperatingState behavior](../inputs/reference/state-zero/kinesis-1.14.60/dotnet-api/a08488_a17ec982fd4d4ce12229bb09fe9671aa2.html).

These ignored local files are manufacturer reference artifacts, not runtime dependencies.

The actual 0x04CD response is `cd0401000150`: channel 1, value 0. Identity, mode
and interlock queries succeed. The mode is Triggered, and the user independently
reported the display says solenoid OFF. This matches documented Closed=0 feedback,
but does not establish optical closure or other firmware behavior.

## Independent actual status query

The legacy status-update request 0x0480 received no reply within 5 s; the session
was closed and that request was not repeated. On a new identity-verified session,
status-bits request `290401005001` returned `2a0406008150010000200000`:

- response 0x042A, exactly six payload bytes;
- channel 1, status bits 0x00002000;
- output bit 0 is clear.

APT Issue 42.1 p128 defines the channel-word/status-dword layout. The exact
KSC101 GetStatusBits API defines mask 0x00000001 as enabled=1/disabled=0; no
TCube-only extrapolation is needed. Its SDK getter is cached, whereas our direct
protocol query explicitly requests a new reply. The 0x2000 bit is documented as
unused and is not interpreted as an interlock/key readiness bit.
No new ON test was authorized or performed.

## Notebook repair

The current shared ShutterHub explicitly requests fresh status bits for normal
status and output confirmation. The ambiguous 0x04CD scalar is no longer part of
the normal query path: get_solenoid_state_reply returns it only when explicitly
requested, without guessing an enum. This removes the prior firmware-specific
zero-acceptance branch and the separate notebook state decoder. operating_state
remains unknown; electrical OFF is not evidence of operating Inactive/unprimed.

All clients use one ShutterStatus schema with nested identity and feedback.
feedback.status_bits preserves raw bits and feedback.electrical_state uses bit0;
feedback.shutter_state remains optical unknown. This investigation was read-only.
The later docked-KEH3 control implementation and current limits are described in
[the Ethernet assessment](ethernet-assessment.md); these historical read-only
observations do not validate physical ON/OFF.
Wrong reply lengths/channels, malformed data and timeouts remain errors.

The source/API review's current real runs are recorded separately in
records/source-review-live-notebook-*.json. Earlier E176/E177 successful notebook3
artifacts remain valid for their own source hashes and former field names only.
Restart an existing kernel after source changes.

The original user-executed notebook 3 was copied to ignored inputs/private/notebooks
before repair. The pre-review notebooks and all original output are preserved as hash-identified
backups; revised notebooks use the canonical owner and save new read-only runs. Static verification
now inventories saved output without deleting or requiring removal of hardware
evidence. Saved output does not count as a new execution of a notebook.

## Sources and reproducible evidence

- [Official Thorlabs solenoid header](https://github.com/Thorlabs/Motion_Control_Examples/blob/main/C%2B%2B/Kinesis/TCube/TSC001/Thorlabs.MotionControl.TCube.Solenoid.h), manufacturer-authored TCube-family API; enum and SC_GetStatusBits comments. Exact git blob 3b80326f066667f0826077a85c55c90929d34ec8, SHA256 1b8eddfd0a6d9ddd4d2f612980bc9b6977f46b465931c1e6644cb8f3e8f150c9.
- [APT manufacturer protocol](https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol_v40.pdf) and the registered Issue 36/42.1 copies in [sources](sources.md). Older APT tables do not define raw zero; SRC-008 supplies the exact .NET feedback enum.
- [Actual raw state and timed-out status-update capture](../records/state-zero-hardware-investigation.json).
- [Actual independent status-bits capture](../records/state-zero-statusbits-investigation.json).
- [Human observation/context and notebook backup](../records/state-zero-investigation-context.json).
- [Historical KSC101 ON/OFF bit evidence](../records/hardware-evidence.json), ttl/manual_positive_control; not current physical qualification.
