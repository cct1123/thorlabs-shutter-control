# Shutter controller report

## Result

REQ-100 / E135 reviews and validates the accumulated USB/LAN work, fixes stale
route reconnection after a failed rescan, and separates private notebook results
from the shared template. Published in focused implementation and documentation
commits, 66ebe49 and 5bae2a4; origin/main's exact hash was verified (E136 / TEST-146).

REQ-099 / E134: the normal GUI now has one **Discover** action for USB and KEH3
Ethernet. Per-shutter connection type/endpoint/apply controls and the separate LAN
range/scan block are removed. Historical changes remain in [records](../records/RECORDS.md).

## Operation and configuration

Run `uv run shutter-control`. Startup is passive. Click Discover, choose a device
from a shutter's labelled serial/route list, then Connect. The detected route is
applied automatically to the released panel. No manual transport or IP entry is
needed. Connect/output commands stay explicit. Retained handles cannot be replaced;
full broad scanning requires released process handles. Skipped/failed transports
warn while other results remain selectable. Close competing owners for a full scan.

[config.py](../src/thorlabs_shutter_control/config.py) provides startup defaults:

| Parameter | Default |
| --- | --- |
| LAN_SCAN_START_IP | 192.168.1.0 |
| LAN_SCAN_END_IP | 192.168.1.255 |
| LAN_SCAN_MAX_ADDRESSES | 256 (integer1..256) |
| LAN_SCAN_OPEN_TIMEOUT_MS | 100 ms (integer50..1000) |

GUI Discover uses these defaults directly. Explicit Python API scan
arguments can override config defaults; the size limit still applies. Restart the
GUI after file edits. Vendor scanning probes port40303 and enumerates documented
KEH3 ports40304..40307, accepting type68 serials with matching TCPIP routes. Native
calls have no hard host deadline. No KEH6 LAN mapping or USB fallback is assumed.

KCubeShutter is USB-only; ShutterHub owns routes and dispatch. Setters send commands
and return None; getters read feedback separately. Manual Open/Close preserve mode
and enable state. Mode, readiness and TTL preparation remain application checks.
Users manage the physical interlock externally. Shutdown attempts Close/release
for every retained handle; native hangs and browser closure do not guarantee
physical shutdown. Guides: [GUI](../docs/gui.md), [API](../docs/python-api.md),
[architecture](../docs/architecture.md), [tutorials](../docs/examples/README.md).

## Validation and cleanup

TEST-145: source and extracted-wheel suites each **251 passed, 1 skipped**
(optional real SDK). Lint/format, package source/CSS parity, fake API simulation,
notebook/doc/link/privacy checks PASS. The stale-selection regression failed
before correction and passes afterward. E134 browser fake-SDK simulation verified combined
USB/LAN discovery, automatic route on explicit Connect, mixed connections,
retained-handle locking and cleanup. The removed controls are absent from actual
Dash layout/callbacks. Partial USB/LAN failures preserve successful results and
clear stale choices. Source hashes and methods:
[current evidence](../records/lan-publication-review-validation.json),
[prior browser evidence](../records/unified-discovery-validation.json).

![Simplified discovery, software simulation](../docs/assets/gui-unified-discovery.png)

No real network/device operation occurred. Local notebook results, environment,
historical images/records and the [supervisor HTML](supervisor-notebook.html) remain
preserved. Old screenshots of manual transport forms are historical E130/E131
artifacts. The executed LAN notebook is preserved byte for byte in ignored
`inputs/private/notebooks/`; its shared template has blank settings and cleared
outputs. Verified generated caches, package scratch and the unreferenced supervisor
preview are pruned. Restart GUI once to load this update.

## Physical evidence and remaining limits

E128 / TEST-138 observed a real KEH3/KSC101 explicit-endpoint LAN discovery,
identity, Connect and passive release: discovery0.844s, release0.953s outside the
restricted sandbox. A restricted run hung in native Disconnect; the environment
cause remains unproven. The user also reports successful LAN notebook execution;
the preserved outputs report discovery, identity, Open/Close feedback and release.
Independent blade observations and timing were not supplied.

Live range scanning, current GUI bench paths, Ethernet actuation/timing,
KEH6/multiple real pairs, external electrical TTL, physical loss recovery and
calibrated exposure/shutdown remain untested. Historical USB evidence does not
qualify changed paths. The active-low no-cable expectation failure remains
unresolved. [LAN evidence](../docs/ethernet-assessment.md),
[hardware procedure](../docs/HARDWARE_VALIDATION.md) and [TTL results](../records/ttl-summary.json)
preserve these boundaries. Software completion does not establish physical or
calibrated acceptance.
