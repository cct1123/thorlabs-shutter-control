# KEH3 Ethernet qualification

The Python driver accepts an explicit `ethernet_endpoint` for passive qualification.
The GUI/CLI remain USB-focused. The selected TCPIP provider/endpoint is checked
before and during connection; the driver never silently falls back to USB.
USB and Ethernet share serial ownership within the process.

The official [KEH3 manual, section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351)
maps one IP address to separate endpoints:

| Endpoint | Function |
| --- | --- |
| `IP:40303` | Hub |
| `IP:40304` | Left bay |
| `IP:40305` | Middle bay |
| `IP:40306` | Right bay |
| `IP:40307` | USB OUT |

The manual requires USB IN disconnected for Ethernet operation. Do not move or
redock a powered cube to diagnose routing. Historical tests used192.168.1.19;
recheck the actual address before a later session rather than copying it blindly.

## Observed result

Before the KSC101 update, the hub120100261/firmware1.1.2 responded over Ethernet,
but left-bay KSC10168800777/firmware1.0.6 did not return an identity. Kinesis also
listed only the hub with USB absent. TCP acceptance on40304 was insufficient.

The cube was later updated to1.0.7; USB identity mismatch was repaired and USB
control passed. No post-update Ethernet cube PASS is recorded. Firmware support
was investigated in the archived official-document review; this does not by itself
establish the cause of the old discovery failure or a working current endpoint.

## Next passive check

Release all existing handles, close competing applications, and use an explicitly
authorized LAN-only arrangement. Select the actual left-bay endpoint:

```python
from thorlabs_shutter_control import KCubeShutter

cube = KCubeShutter("68800777", ethernet_endpoint="192.168.1.19:40304")
try:
    print(cube.discover())
    print(cube.connect())
    print(cube.identify_device())
    print(cube.get_status())
finally:
    cube.disconnect(close_shutter=False)
```

Require TCPIP transport, matching endpoint/serial, known operating feedback and
successful passive release. Stop after a failed identity/read; preserve the same
object if release fails. Do not run this alongside the live USB owner. Ethernet
actuation, timing and recovery remain unvalidated. [Historical evidence](../records/archive/README.md)
contains the raw responses and firmware investigation.
