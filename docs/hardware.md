# Hardware configuration and evidence

[README](../README.md) | [Interface](INTERFACE.md) | [Acceptance procedure](HARDWARE_VALIDATION.md)

![KSC101 controller and SH05R shutter](assets/ksc101-sh05r.webp)

Manufacturer product photo: [Thorlabs](https://www.thorlabs.com/optical-shutters);
illustrates the device pair, not the test bench.

Published identities below are aliases. Current qualified branch: computer USB -> KEH3 left bay -> KSC101 (alias CONTROLLER_A) -> SH05R.
The cube reports hardware3, firmware1.0.7. Kinesis1.14.60.27990 with the FTDI USB
interface is used on Windows x64/Python3.12.7. No COM port is assigned.

USB identity/status/reconnect, Open/Close and normal shutdown have actual bench
readback evidence. The user independently confirmed the five-cycle SDK sequence.
The redesigned production GUI was exercised in the real browser without a new
physical observer. Readback, human observation and calibrated timing remain
separate evidence. See [results](../records/hardware-validation.json).

Three-pair operation, electrical TTL response, physical fault injection and
calibrated exposure/shutdown timing remain unvalidated. Historical Ethernet tests
found only the hub, with no responding left-bay cube before
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

## KEH6 and larger USB installations

The [KEH6](https://www.thorlabs.com/item/KEH6) provides six cube bays; Thorlabs also
describes USB OUT hub linking in its [hub overview](https://www.thorlabs.us/newgrouppage9.cfm?objectgroup_ID=16708).
Software addresses each KSC101 serial through Kinesis and does not detect or
restrict a USB hub model. KEH6 USB compatibility is therefore expected, not a new
bench result. Existing USB evidence is one KSC101/SH05R on KEH3 only.

Use `--slots N`, or pass enough distinct serials to expand the default beyond
three. No app-defined count cap is imposed. Installed cube count must respect
actual hub/power/USB limits; increasing N also increases sequential refresh and
cleanup latency. Six/nine-device software tests do not qualify physical power,
connections, timing or optical operation. Ethernet maps in the separate guide
are KEH3-specific; KEH6 LAN endpoints have not been qualified or generalized.
