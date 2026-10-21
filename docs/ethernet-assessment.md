# KEH3 Ethernet

[GUI](gui.md#ethernet-lan-configuration) | [API](python-api.md) | [Hardware](hardware.md)

ShutterHub owns TCPIP discovery, exact endpoint/provider validation and command
dispatch. KCubeShutter is USB-only. USB and LAN use the same serial ownership
registry; network routes never fall back to USB. Construction/startup is passive.

## Setup and discovery

Use the hub's actual configured IPv4 address on a reachable network, approved
power/docking/shutter wiring and normal physical interlock. Release other owners.
Follow [KEH3 manual section4.3](https://media.thorlabscms.cn/globalassets/items/k/ke/keh/keh3/doc-103012.pdf?v=0129060351),
including USB IN disconnected for Ethernet. This application does not configure
IP addresses, firmware, firewall or hub power.

| Port on the same hub IP | Target |
| --- | --- |
| 40303 | Hub management/discovery |
| 40304 / 40305 / 40306 | Left / middle / right cube bay |
| 40307 | USB OUT device |

Only KEH3 cube endpoints40304..40307 are accepted. Do not infer KEH6 mappings or
cube identity from a responding management port.

GUI Discover combines USB, configured routes and one shared scan using config.py's
LAN_SCAN settings. The bounded inclusive scan probes40303, registers discovered
hosts' cube endpoints, builds once and polls CheckForConnectionChanges/GetDeviceList(68).
Only exact TCPIP endpoints and valid KSC101 serials are returned. Release all
process-owned handles for broad scanning; failed/skipped transports warn while
successful results remain. Native calls may exceed timeout; an empty result does
not prove absence. Connect is separate and applies the selected detected route.

Configured-route Python discovery registers endpoints, builds once and polls until
each LAN route has an identity or the controller timeout expires (default5s,
100ms between polls). It does not require a USB cable. Without slots, supplied
endpoint/serial lists determine count; omitted routes are USB only when requested
by that configuration. See the [LAN notebook](examples/shutter_lan_tutorial.ipynb).

## Evidence and limitations

[Retained observations](../records/hardware-evidence.json) include one real
KEH3/KSC101 explicit-route discovery, identity, Connect and communication-only
release: discovery0.844s and release0.953s outside the restricted agent sandbox.
A restricted comparison hung in native Disconnect; its cause remains unknown.
The user reports successful LAN notebook operation, with feedback saved privately.

Those observations do not qualify the current baseline, live range scanning,
Ethernet blade motion, calibrated timing, multiple pairs or physical fault recovery.
Use explicit getters after commands; GUI/procedures own readiness and sequencing.
Close still targets a retained faulted handle, without rebind or transport fallback.
Communication release is not independently verified closure.
