# KEH3 Ethernet SDK assessment

Checked 2026-10-20. Scope: official documentation, static SDK/package inspection
and current-source review only. No SDK was imported or initialized; no USB or
network device discovery, connection, configuration or actuation occurred.

**Kinesis is the best-supported incremental path.** Thorlabs explicitly documents
KEH3 Ethernet operation in Kinesis, including multiple attached cubes. Its SDK
provides Ethernet scanning and manual transport registration. XA now supports
KSC101 and contains Ethernet support, but the exact KEH3 discovery/configuration
contract in the Python package is not established by the inspected sources.
Neither route has been physically validated here.

## Evidence and remaining uncertainty

| Layer | Finding | Limit |
| --- | --- | --- |
| KEH3 | Official manual DOC-103012 Rev E, January 22, 2026, sections 4.2–4.3.1, documents Ethernet with Kinesis and multiple cubes | Installed hub/cube firmware and actual three-serial enumeration unknown |
| Kinesis SDK | `DeviceManagerCLI.ScanEthernetRange(startIPAddress, endIPAddress, portNo, openTimeout)`, `CreateManualDeviceEntry(comSpec)`, `DeleteManualDeviceEntry(comSpec)`, `GetManualDeviceEntries()` and `GetTransportInfo(serialNo)` are documented | Inspected API help is an older official example artifact; verify installed-version behavior and endpoint-string grammar before implementation |
| KSC101 Kinesis | Official Python example uses `KCubeSolenoid.CreateKCubeSolenoid(serial)` and `Connect(serial)` | Example is not a three-KSC101 Ethernet demonstration |
| XA | Official Python SDK 1.9.1.28941 lists KSC101, includes `products/ksc101.py` and its factory mapping | KSC101 support does not alone prove this topology |
| XA Ethernet | Bundled native DLL contains `TLMC_DiscoverEthernetDeviceInfo`; changelog describes Ethernet fixes; Python device information includes `device`, `transport`, `parent_device` | Public Python `SystemManager` exposes no dedicated Ethernet scan method; native discovery signature/settings schema must be verified from matching C SDK documentation |

The hub manual describes one IP with separate ports routing to bays. USB IN must
be disconnected for Ethernet operation. Static addressing and DHCP are supported;
the shipped static address is 192.168.0.200. These are documented defaults, not
this bench's settings. Section 6 identifies a firmware caveat when identical cube
types are not all displayed. Do not flash firmware automatically. The text
extraction of Figure 17 lists the ports, but its physical port-to-bay diagram was
not visually verified during this review; do not hard-code that mapping from
this assessment.

## Proposed Kinesis changes

1. In `controller.py`, add explicit optional Ethernet endpoint configuration,
   retaining USB as the default and passive object construction. At an explicit
   Discover/Connect action, register the configured transports under `_sdk_lock`,
   build the device list, and retain type-68 filtering. Use the vendor-returned
   communication specification or verified installed-SDK grammar; do not invent
   an `IP:port` syntax from the BBD example. Prefer a configured hub over a broad
   network scan. Verify whether registering the hub enumerates all bays or each
   bay needs registration.
2. Keep one `KCubeShutter` per physical serial. Validate identity after connecting;
   never equate a bay index with a stable shutter identity. Preserve the existing
   process-wide serial ownership across USB and Ethernet, so the same physical
   cube cannot be opened twice via different transports or IP aliases.
3. Replace `_check_connection()`'s unconditional `USBConnected` requirement with
   documented transport-aware health checks. Retain communication-error detection,
   latched faults and unknown state on failure. Merely deleting the USB check is
   insufficient without validating Ethernet loss detection and feedback age.
4. Manage SDK transport entries at shared-hub scope: remove only entries created
   by this process after their last user releases them, including partial failures.
   One slot disconnecting must not invalidate another slot's transport.
5. Pass endpoint configuration through `ShutterHub` and CLI. Show transport/hub
   identity in status; retain existing three-panel action/cleanup behavior and
   the controller/GUI boundary. Leave GUI startup and serial preselection passive.
6. Add software tests for registration lifecycle, wrong identity, endpoint errors,
   duplicate serials across transports, independent devices, shared hub loss,
   stale feedback and all-slot cleanup after failures/interrupts. Later extend
   bench acceptance to cable loss, reconnect and independently observed closure.

Existing solenoid operations are candidates for reuse through Kinesis; their
Ethernet feedback/error behavior must still be revalidated. No backend change is
implemented by this assessment.

## XA alternative

XA would require a larger driver change. Its inspected Python interface uses
`SystemManager.instance()`, `startup(settings_file_name=None)`, `get_device_list()`
and `open_device_as(device_id, transport, operating_mode, Ksc101)`. Pass the
discovered transport descriptor; no literal Ethernet descriptor is established
here. Verify native discovery or startup settings against matching SDK headers
before writing a binding. Never call startup as an incidental import/test.

Map `get/set_solenoid_state`, `get/set_solenoid_operating_mode`, enable state,
status requests/items and error codes into the current public interface. XA's
On/Off state vocabulary differs from the current Kinesis operating-state flow;
confirm key/interlock and physical feedback semantics rather than translating
names mechanically. Preserve close-before-release and per-slot fault handling;
close all handles before shared manager shutdown. In this package,
`Device.parent_device_id` returns `_device_id`, although the constructor stores
`_parent_device_id`; use discovery information to check parent mapping instead.

If Ethernet is the only new requirement, extend Kinesis first. Consider XA for
a separately authorized migration after its discovery and safeguard contracts
are settled. Retain the hardware hold for either path.

## Official references

- [KEH3/KEH6 manual, DOC-103012 Rev E](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351), especially sections 4.2, 4.3, 4.3.1 and 6. The current product page identifies this manual.
- [Controller hub product page](https://www.thorlabs.com/k-cube-r-controller-hubs).
- [Kinesis Ethernet example and API help](https://github.com/Thorlabs/Motion_Control_Examples/tree/3ef959523e2be48d57704af964f7a2c24547b722/C%23/Benchtop/BBD30X/BBD30X_Ethernet). Its BBD-specific commands are not a KSC101 contract.
- [Official KSC101 Python example](https://github.com/Thorlabs/Motion_Control_Examples/blob/3ef959523e2be48d57704af964f7a2c24547b722/Python/Kinesis/KCube/KSC101/KSC101_pythonnet.py).
- [Official XA Python SDK 1.9.1.28941](https://pypi.org/project/thorlabs-xa/1.9.1.28941/). The source archive changelog records KSC101 support in 1.7.0 on September 18, 2026; the older GitHub changelog currently stops at 1.6.1.

Inspected artifacts are under `tmp/ethernet-research`; wheel SHA-256:
`48f0405cd094689ca790691b3fc174ae4f9271b9e97c786f1e984e606830fa2f`.
Kinesis API CHM SHA-256:
`dfa52c72df9c0c9859bd29a9cfb9efe7a29e33787f9b4ddec0e720704de29b7d`.
Downloads were inspected as data,
not installed or loaded.
