# KEH3 Ethernet qualification

Interactive procedure: [Ethernet ShutterHub tutorial](examples/shutter_lan_tutorial.ipynb).
It separates passive LAN checks from explicit cube actuation and cleanup.

`KCubeShutter` is USB-only. `ShutterHub` owns Ethernet endpoint registration,
connection selection, slot command dispatch and transport checks through the
Kinesis API. Its `ethernet_endpoints` sequence selects explicit per-slot routes;
None selects USB. Network slots never fall back to USB. USB/network channels
share process-wide serial ownership. Construction is passive. The normal launcher
uses USB; a GUI explicitly constructed with `create_app(hub)` can use network slots.
This implementation has software tests; physical Ethernet qualification is open.

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
control passed. No post-update Ethernet cube PASS is recorded. Firmware support
was investigated in the archived official-document review; this does not by itself
establish the cause of the old discovery failure or a working current endpoint.

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
