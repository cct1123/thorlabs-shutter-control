# Source register and contract gaps

Retrieved 2026-11-04. Manufacturer documents are reference data, not operating
authorization. Original downloads/extracted text are in ignored inputs/reference;
their exact SHA-256 values below identify the inspected documents.

| ID | Document / revision | Origin and inspected sections | Applicability / result |
| --- | --- | --- | --- |
| SRC-001 | Thorlabs Host-Controller Communications Protocol, Issue 36, 17 April 2023, 421 pages | [Manufacturer entry point](https://www.thorlabs.com/Software/Motion%20Control/APT_Communications_Protocol.pdf); inspected [manufacturer-authored mirror](https://raw.githubusercontent.com/amsikking/thorlabs_KSC101/master/APT_Communications_Protocol.pdf). Sections 2-5, KSC101 command table p12, p49-53 and p187-194 | Direct USB framing/solenoid contract. Main URL currently returns HTML. Older revision; actual firmware applicability still needs qualification. Issue 42.1, 9 September 2025, was [cross-checked online](https://device.report/m/b2a6badd7c00b3042ba383e291667e7eab10746c14c4f92cea45fc480c7304ed); not a new physical result |
| SRC-002 | KSC101 operating manual HA0368T Rev D, June 2023 | [Manufacturer PDF](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf), sections 3.3-3.4, 4.3-4.5, 6.3, appendices A/C | Load interface, modes, key/interlock and trigger warning. Trigger applicability is KSC-specific; no generic T-Cube assumptions |
| SRC-003 | KEH3/KEH6 manual DOC-103012 Rev E, 22 January 2026 | [Manufacturer PDF](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf), sections 1.2, 3 and 4.2-4.3, Figure 17 | KEH3 port map and USB/Ethernet restrictions established. Direct framing, management identity, firmware and external-route contract unresolved |
| SRC-004 | Actual attached shutter manual/specification | [Manufacturer shutter entry point](https://www.thorlabs.com/optical-shutters) | MISSING: current attached model, wiring, continuous/duty/exposure/switch limits, physical OFF mapping. Prior SH05R evidence is historical, not current qualification |
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
configuration remain unavailable. SRC-002 p20 says mode changes are automatically
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
