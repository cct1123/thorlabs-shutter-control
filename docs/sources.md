# Source register and contract gaps

Initial retrieval 2026-11-04; later sources are dated below. Manufacturer documents
are reference data, not operating authorization. Unchanged controller/hub manuals
and both inspected APT protocol revisions are now included under
[docs/manuals](manuals/README.md) for offline reference (verified 2026-11-06).
Original downloads/extracted text remain in ignored inputs/reference; their exact
SHA-256 values below identify the inspected documents. See the
[verification manifest](../records/manuals-verification.json) for local paths,
page counts, byte counts and origins.

| ID | Document / revision | Origin and inspected sections | Applicability / result |
| --- | --- | --- | --- |
| SRC-001 | Thorlabs Host-Controller Communications Protocol, Issue 36, 17 April 2023, 421 pages | [Manufacturer entry point](https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf); inspected [manufacturer-authored mirror](https://raw.githubusercontent.com/amsikking/thorlabs_KSC101/master/APT_Communications_Protocol.pdf). Sections 2-5, KSC101 command table p12, p49-53 and p187-194 | Direct USB framing/solenoid contract. Main URL currently returns HTML. Older revision; actual firmware applicability still needs qualification. Issue 42.1, 9 September 2025, was [cross-checked online](https://device.report/m/b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed); not a new physical result |
| SRC-002 | KSC101 operating manual HA0368T Rev D, June 2023 | [Manufacturer PDF](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf), sections 3.3-3.4, 4.3-4.5, 6.3, appendices A/C | Load interface, modes, key/interlock and trigger warning. Trigger applicability is KSC-specific; no generic T-Cube assumptions |
| SRC-003 | KEH3/KEH6 manual DOC-103012 Rev E, 22 January 2026 | [Manufacturer PDF](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf), sections 1.2, 3 and 4.2-4.3, Figure 17 | KEH3 port map and USB/Ethernet restrictions established. Direct framing, management identity, firmware and external-route contract unresolved |
| SRC-004 / SRC-009 | Current SH05R, user-confirmed6 November2026; Thorlabs TTN264481-D02 RevA | [Manufacturer-authored manual mirror](https://oxxius.ru/upload/iblock/6c6/hl12m6ms8y6qlnttgzhww6040mysz7ym/TTN264481_D02.pdf), pp3,5-7 | NativeKSC101 compatibility and normally-closed design; continuous native holding supported. Independent optics remain unmeasured |
| SRC-005 | QMI revision 7b02875043985abd6366d902c1cf32af240a6881, 28 October 2026 | [Pinned implementation](https://github.com/QuTech-Delft/QMI/tree/7b02875043985abd6366d902c1cf32af240a6881/qmi/instruments/thorlabs), apt_protocol.py, apt_packets.py, kdc101.py, LICENSE.md | Reference for separation and framing only. Does not establish KSC101 or KEH3 support; no QMI runtime dependency or copied code |
| SRC-006 | Local thorlabs-control revision d70f2a6e8f494516a3aed169f33bcf6775fdd982, inspected 5 November 2026 | C:/repo/thorlabs-control; devices/ksc101.py, devices/keh3.py, link.py, deadline.py, apt/frames.py, transport modules and source/traceability guides | User-selected implementation reference only. Independently adopted timing/header/partial-write concepts and verified automatic mode persistence against SRC-002 p20. No code copied, runtime dependency or hardware qualification transferred. See controller-reference-review.md |

## Original document hashes

| Artifact | SHA-256 |
| --- | --- |
| apt.pdf (Issue 36) | 96668e05c353269d59390d3e00e4e7237c881707b3a947057dd08ead13191966 |
| ksc101.pdf | b51ac9ca1aa53b02b554dfd5b1c0bd4b99d73e4ba092e47170a64a3f4bab34f5 |
| keh3.pdf | c768e4e3f2317ae29f7bfcdf8b18f750d7adc688d324c55550cdfa9a31a0489b |
| qmi-apt_protocol.py | 74ae0a1b386bbb1a23c78a10078c7ddd75daa5454195ef370d3fe0c6638283c7 |
| qmi-apt_packets.py | 748081dbac898b7fff203a4a3467774420f6813893d5ebe026c408f1c1e59597 |
| qmi-kdc101.py | 6927240d7ef3d8910cb32202e9cb17018010e668256066fa8ab8d93a28fdeb88 |
| qmi-license.md | d619bbc76b6a5beec0b104d78844fa3307e7637e3019aa06b8a92ed429d09ac6 |

## QMI reference and deviations

QMI uses the MIT OSS license; its copyright/permission notice must accompany
copies or substantial portions. This rewrite is independently implemented and
does not copy QMI code. The license is retained in THIRD_PARTY_NOTICES.md for
reference. Consult the upstream license for any later reuse.

This implementation differs by using an incremental bounded decoder, preserving
unrelated messages/fault frames, end-to-end monotonic deadlines, single-flight
queries, cancellation and permanent session quarantine after ambiguity. It does
not copy QMI's fixed response sleeps, indefinite timeout default or clearing of
old traffic as an assertion of freshness.

## Unresolved contracts

KEH3 follow-up SRC-007: manufacturer-authored APT Issue 42.1 (9 September 2025,
443 pages), retrieved from the reference project's
[mirror](https://raw.githubusercontent.com/JovanMarkov96/Thorlabs_Motion_Control/master/docs/manuals/APT_Communications_Protocol.pdf).
SHA-256 b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed.
The full text provides no KEH3/40303-specific contract. Official example repository
tree snapshots (Motion_Control_Examples and Light_Control_and_Manipulation_Examples)
were also inspected; exact tree IDs/hashes are recorded in records/keh3-validation.json.
See docs/keh3-offline-validation.md for the bounded findings and remaining questions.

The generic protocol describes triggered cycling while the KSC101 manual
describes logic-level operation with priming. TTL, cycle starts and EEPROM
configuration require the separate qualification gates described in SRC-010 below;
trigger-I/O configuration remains unavailable. SRC-002 p20 says mode changes are automatically
remembered at power-up; they now require separate policy permission. APT has no
transaction IDs; even a post-request
reply cannot distinguish an arbitrarily delayed same-type unsolicited reply
from the current one. Quarantine prevents known timed-out requests from being
reused, but firmware ordering and new-connection buffer behavior need manufacturer
confirmation/bench evidence. This is an open acceptance limitation.

USB D2XX initialization follows SRC-001. VCP cannot express its bridge-reset call
and remains read-only commissioning. No alternative USB stack, endpoint routing,
OS crash fix, optical feedback interpretation or finite exposure protection is
claimed from simulation.

## SRC-007 - State-zero investigation, 6 November 2026

Manufacturer APT Issue 42.1 pp190-191 and earlier SRC-001 enumerate only
solenoid ON=1/OFF=2; no firmware-1.0.7 definition of legacy 0 was found. The
[official manufacturer-authored TCube solenoid SDK header](https://github.com/Thorlabs/Motion_Control_Examples/blob/main/C%2B%2B/Kinesis/TCube/TSC001/Thorlabs.MotionControl.TCube.Solenoid.h)
defines the same enum and status bit0 as output enabled/disabled. Exact official
Git blob 3b80326f066667f0826077a85c55c90929d34ec8, SHA256
1b8eddfd0a6d9ddd4d2f612980bc9b6977f46b465931c1e6644cb8f3e8f150c9.
This is a solenoid-family reference, not an exact KSC101 firmware contract.
Current real KSC101 status0x2000 plus the user's OFF/Trigger display and historical
same-controller 0x2001 ON/0x2000 OFF observations support the read-only output-bit
interpretation; they do not qualify new ON/control behavior. No SDK binary is used.
See [state-zero investigation](state-zero-investigation.md) for raw packets,
bounded initial source searches. Its initial conclusion about undocumented zero
is superseded by the exact KSC101 .NET reference in SRC-008 below.

## SRC-008 - Exact KSC101 Kinesis API reference, 6 November 2026

Thorlabs Kinesis installer 1.14.60.0, local file
C:/Users/HFNV/Downloads/thorlabs_kinesis_setup_27990_x64.exe; Authenticode Valid,
signer Thorlabs, Inc. SHA256
298c4cc03a6c3b4d5c174964ae9193d13baca63dab10c1595b4e9ad5d914ff05.
Documentation only was extracted; installer/SDK/DLLs/drivers were not executed
or installed. Provenance and inspected artifact hashes are in
[ksc101-api-reference-findings.json](../records/ksc101-api-reference-findings.json).

| Exact reference | Finding | SHA-256 |
| --- | --- | --- |
| KSC101 .NET SolenoidStatus class, a08484.html | SolenoidStates Closed=0/Open=1; OperatingStates Active=1/Inactive=2 | add82aed2829c80b0047923d62d6e66ac6bb133a7093d0429d10b4fc7ab4300c |
| KSC101 .NET GetStatusBits, a08488_a33fd41ba3b79a5078c4609d804c51376.html | Mask 0x00000001 output enabled=1/disabled=0; SDK getter cached | cf20d5625aaae5eab3b2081e461b394b2ca213658183a47859c76afd545da72b |
| Thorlabs.MotionControl.KCube.Solenoid.h | C API Open=1/Closed=2, a different representation | 528c5e92604710c258e5e67326ddeb7a8c9add2b297bd1d903e60ff02ef60445 |

These exact KSC101 references correct the earlier broad claim that zero was
undocumented and replace TCube-only support for the output-bit interpretation.
They do not prove a universal raw 0x04CD enum across firmware or optical position.
See [the investigation](state-zero-investigation.md) for source links and live data.

## SRC-009 - SH05R load manual, 6 November 2026

Thorlabs SH05R/SH05R/M User Guide TTN264481-D02 Rev A, 24 February 2022,
15 PDF pages. Reviewed the manufacturer-authored
[PDF mirror](https://oxxius.ru/upload/iblock/6c6/hl12m6ms8y6qlnttgzhww6040mysz7ym/TTN264481_D02.pdf)
online: printed pp2-7 (PDF pages4-9). It recommends KSC101/SC10 control,
describes a normally closed design, and specifies continuous steady-state
operation at20 C within its electrical limits. Timing depends on the driver;
SC10 measurements are not KSC101 calibration. The connector's position-feedback
signal is distinct from output enable. This supports the native-driver load
policy's design assumptions, not present wiring, optical closure or performance.
The configured2 s OFF pause is a commissioning choice, not a manufacturer minimum.

The direct mirror download timed out; the web PDF extraction supplied the inspected
manufacturer text. No local SH05R PDF hash is claimed. Existing downloaded
manufacturer documents and their hashes remain unchanged. Inspection metadata
is in [sh05r-manual-reference.json](../records/sh05r-manual-reference.json).


The [actual Manual/OFF preparation](../records/ethernet-control-manual-preparation.json)
and [one ON/OFF cycle](../records/ethernet-control-live.json) are separate from those
source facts. APT/SRC-007 section2.1 gives transport independence, pp190-191
command0x04CB ON1/OFF2; KEH3/SRC-003 section4.3 gives per-bay routing. The exact
192.168.1.19:40305/68800777/1.0.7 path now has real command/readback evidence.
The configured2s OFF pause is a commissioning choice, not a rated minimum.
No custom voltage, EEPROM, trigger configuration or interlock bypass was used.

## SRC-010 - KSC101 Kinesis UI manual, 6 November 2026

User-supplied [official ETN017648-D03 PDF](https://media.thorlabs.com/globalassets/items/k/ks/ksc/ksc101/etn017648-d03.pdf?v=0918071407)
retrieved as HA0368T Rev F, September 2026, 41 pages / 26,149,045 bytes.
Unchanged local [PDF](manuals/KSC101_Kinesis_UI_Manual_HA0368T_Rev_F.pdf), SHA-256
007d604c718378b3b8b6bc6f46876f00f91c6a4e4d839c2a175681ac3c122597.
Inspected sections4.3,5.2,6.2-6.3 and visually rendered GUI/settings pp28/31.
The manual/screenshot are design references, not instructions to run vendor
software or permission for physical operations. No Kinesis/SDK runtime is used.

RevF pp28-30 define four modes, Open/Close or Start/Stop, On/Off durations,
Key Enabled/Is Ready/Error/Open lamps, Settings and Identify. pp31-33 specify
cycle On/Off100..10000 ms, count0..1000000 (0 continuous), display brightness,
timeout/dimming and two trigger-port modes/polarities. Section4.3 describes
level-trigger priming, unlike the generic APT solenoid cycling prose. The GUI's
motor Jog/Home keyboard list does not define shutter commands and was omitted.

APT Issue42.1 pp43,99,184-190 supplies the implemented raw Identify, cycle-only
storage, mode/cycle query/set and ON/OFF frames. Cycle commands use channel1
and integer milliseconds. The application's conservative100..10000 ms bound
follows the KSC101 manual rather than the inconsistent generic timing upper
bound prose. NoEEPROM ACK exists; success is only a storage request, with later
restart/readback verification required. Current hardware qualification remains
Manual-only; software contracts do not qualify native timing, priming or storage.

Unresolved: the protocol's model table lists KSC101 for MMI0x0520 and trigger
0x0523, but detailed sections name motor KST/KDC/KBD families and contain motor
positions/velocities and conflicting lengths. That is insufficient to implement
KSC101 display/trigger configuration. No confirmed Key/Ready mapping was found.
Those controls stay disabled/Unknown; no motor-layout guess or SDK fallback.
A newer official APT URL attempt returned1313-byte HTML, not a PDF; it is not
used as protocol evidence. The [WebUI matrix](gui.md#manufacturer-reference-and-implemented-functions)
and records/webui-apt-validation.json distinguish implemented software paths,
passive browser checks and unresolved physical/wire-contract acceptance.
