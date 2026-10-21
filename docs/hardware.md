# Hardware configuration and evidence

[README](../README.md) | [Interface](INTERFACE.md) | [Acceptance procedure](HARDWARE_VALIDATION.md)

Current qualified branch: computer USB -> KEH3 left bay -> KSC10168800777 -> SH05R.
The cube reports hardware3, firmware1.0.7. Kinesis1.14.60.27990 with the FTDI USB
interface is used on Windows x64/Python3.12.7. No COM port is assigned.

USB identity/status/reconnect, Open/Close and normal shutdown have actual bench
readback evidence. The user independently confirmed the five-cycle SDK sequence.
The redesigned production GUI was exercised in the real browser without a new
physical observer. Readback, human observation and calibrated timing remain
separate evidence. See [results](../records/hardware-validation.json).

Three-pair operation, electrical TTL response, physical fault injection and
calibrated exposure/shutdown timing remain unvalidated. Historical Ethernet tests
found the hub120100261 at192.168.1.19:40303 but no responding left-bay cube before
the cube firmware update; post-update cube Ethernet qualification is still open.

Use manufacturer-approved supply, docking, cabling and shutter compatibility.
Power down before changing interlock/shutter wiring. Do not infer installed
supply rating or pin voltage from software success. Unmeasured fields remain
explicitly incomplete in [the bench record](../records/hardware-bench.json).

Primary references: [KSC101 manual, HA0368T RevD](https://media.thorlabs.com/contentassets/e92d618c92c94cea9096b3f231859611/etn017648-d02.pdf)
(sections3-4 for setup, physical interlock, key and modes), and
[KEH3 manual, DOC-103012, section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351)
for hub connections and Ethernet endpoint mapping. Their instructions describe
equipment requirements, not additional operating authorization.
