# KEH3 Ethernet qualification

Interactive procedure: [Ethernet ShutterHub tutorial](examples/shutter_lan_tutorial.ipynb).
It separates passive LAN checks from explicit cube actuation and cleanup.

`KCubeShutter` is USB-only. `ShutterHub` owns Ethernet endpoint registration,
connection selection, slot command dispatch and transport checks through the
Kinesis API. Its `ethernet_endpoints` sequence selects explicit per-slot routes;
None selects USB. Network slots never fall back to USB. USB/network channels
share process-wide serial ownership. Construction is passive. The normal launcher
uses `config.py`'s `ETHERNET_ENDPOINTS` (empty defaults to USB); an embedded GUI
can also use `create_app(hub)` with configured network slots.
The GUI Discover action combines USB and LAN discovery; no per-card transport
controls or separate LAN block remain. LAN_SCAN_* settings in config.py supply
range/timeout defaults. Select a labelled serial and Connect to apply its detected
route automatically. One shared scan serves all panels. Retained handles block
broad scanning; partial results and diagnostics remain available. Range scanning
is software/browser tested only; E128 physical evidence is explicit-endpoint scope.
One real KEH3/KSC101 LAN discovery, identity, connection and passive release check
now passes (E128 / TEST-138). Ethernet actuation, timing and recovery remain open.

With network endpoints supplied and `slots` omitted, the hub creates only enough
slots for those endpoints/serials; it does not add implicit USB slots. LAN-only
discovery registers the explicit TCPIP endpoints, calls `BuildDeviceList`, then
polls `CheckForConnectionChanges` and reads matching KSC101 entries. TCPIP identity
discovery is asynchronous; one immediate list read can be empty. Polling stops
when all configured network endpoints have identities or the controllers' discovery
deadline expires (default 5 s, 100 ms poll interval). Registration/rebuild occurs
once per discovery, not on every poll. Native SDK calls may exceed that deadline.
The rebuild is required for Ethernet too; it does
not mean a USB cable/device is required. Explicit `None` routes select USB.
No USB cable or USB-discovered cube is required for the LAN-only software path.
The GUI uses `discover_available()` for a unified list; `discover_by_slot()`
remains the explicit-route API. See [GUI LAN configuration](gui.md#ethernet-lan-configuration).

The [official Python KSC101 example](https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/Kinesis/KCube/KSC101/KSC101_pythonnet.py)
shows the cube's creation/connection API with normal device-list discovery.
The repository's [Ethernet-specific .NET example](https://github.com/Thorlabs/Motion_Control_Examples/blob/main/C%23/Benchtop/BBD30X/BBD30X_Ethernet/Program.cs)
uses ScanEthernetRange, manual registration, BuildDeviceList, then typed serial
enumeration. Our optional bounded range scan finds hub addresses before deriving
the documented KEH3 cube endpoints. It is a BBD example, not
proof that a KEH3 cube route works. Skipping BuildDeviceList was an incorrect
interpretation of the no-USB requirement and has been corrected.

The official [KEH3 manual, section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351)
maps one IP address to separate endpoints for **KEH3**:

| Endpoint | Function |
| --- | --- |
| `IP:40303` | Hub |
| `IP:40304` | Left bay |
| `IP:40305` | Middle bay |
| `IP:40306` | Right bay |
| `IP:40307` | USB OUT |

The manual requires USB IN disconnected for Ethernet operation. Do not move or
redock a powered cube to diagnose routing. Use the actual approved bench address;
the documentation address below is fictional.

## Observed result

Before the KSC101 update, the hub (alias HUB_A)/firmware1.1.2 responded over Ethernet,
but left-bay KSC101 (alias CONTROLLER_A)/firmware1.0.6 did not return an identity. Kinesis also
listed only the hub with USB absent. TCP acceptance on40304 was insufficient.

The cube was later updated to1.0.7; USB identity mismatch was repaired and USB
control passed. After reboot, Kinesis displayed both devices; subsequent Python
investigation isolated missing asynchronous connection-change refreshes.

E128 / TEST-138: corrected ShutterHub discovered the selected cube in 0.844 s,
connected, verified its serial and TCPIP endpoint, then released communication
without Close in 0.953 s. This live check ran outside the restricted agent sandbox.
A restricted comparison connected/read successfully but blocked in native TCPIP
Disconnect and its helper was interrupted. That environment difference is an
observation, not proof of the underlying native cleanup cause. The restricted
readback was closed/unknown operating state/triggered; no mode/output was changed.
Passive communication PASS does not establish readiness for Open/Arm or physical
blade/optical sensing. Firmware support was investigated in the archive; no old
failure is retrospectively assigned a firmware or hardware root cause.

## Next passive check

Release all existing handles, close competing applications, and use an explicitly
authorized LAN-only arrangement. Select the actual left-bay endpoint:

```python
from thorlabs_shutter_control import ShutterHub

serial = 68000001  # Replace with the actual selected cube identity.
hub = ShutterHub([serial], slots=1, ethernet_endpoints=["192.0.2.10:40304"])
try:
    print(hub.discover())
    hub.connect(0, serial)
    print(hub.identify_device(0))
    print(hub.get_status(0))
finally:
    hub.disconnect(0, close_shutter=False)
```

Require TCPIP transport, matching endpoint/serial, known operating feedback and
successful passive release. Stop after a failed identity/read; preserve the same
object if release fails. Do not run this alongside the live USB owner. Ethernet
actuation, timing and recovery remain unvalidated. [Historical evidence](../records/archive/README.md)
describes private retention of the raw responses and firmware investigation.

KEH6 USB/software slot support does not qualify its Ethernet route. This driver
still accepts only the documented KEH3 cube range40304..40307; no KEH6 bay-port
mapping or LAN success is inferred from removing the software slot cap.

## Command handling

For separately authorized operation, use the same slot API: `hub.open_shutter(0)`,
`hub.close_shutter(0)`, `hub.arm_triggers(0)` and `hub.disarm_triggers(0)`.
`hub.configure_triggers(0, config)` writes port settings. Setters return None;
request feedback separately with `hub.get_shutter_state(0)`,
`hub.get_operating_status(0)` or `hub.get_trigger_config(0)`.
The driver does not perform prerequisite reads, waits or automatic recovery.
The GUI/controlled procedures own those application checks.

Hub routing checks SDK provider/comspec metadata before ordinary network writes;
getter health checks also require IsConnected/CommsStatus. A route change faults
rather than selecting a different endpoint. Close/Inactive can still be attempted
on the retained handle after a fault. Shutdown attempts every slot and releases
handles despite failures, without asserting physical closure. Native calls can
still block; physical timing, actuation and recovery are not established by tests.
