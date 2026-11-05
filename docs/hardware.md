# Device, route and driver matrix

| Route | Python dependency | Native / OS requirement | Current validation | Rollback |
| --- | --- | --- | --- | --- |
| Direct USB, exact serial, D2XX | optional ftd2xx 1.3.8 (pywin32 on Windows) | Matching official FTDI D2XX native DLL and device driver/binding; retains FTDIBUS dependence | Simulated protocol/initialization only; actual driver and firmware UNTESTED | Restore inventoried signed package/binding during all-instrument downtime |
| Direct USB, exact VCP | optional pyserial 3.5 | Existing FTDI VCP binding and exact COM assignment; retains FTDI dependence | Read-only commissioning; bridge reset equivalence unresolved | Restore original COM/binding/package from inventory |
| KEH3 left/middle/right | standard Python networking would suffice if wire contract confirmed | Exact hub identity, host, firmware and bay required; USB IN disconnected in Ethernet mode | Unavailable: management identity, framing/initialization/addresses unresolved; no socket opened | Keep route unavailable; independent source protection |
| KEH3 external USB OUT | unresolved | Requires its own supported-device/routing contract | Unavailable independently of cube bays | No inferred fallback |
| TTL | unavailable | Actual shutter rating, electrical thresholds/polarity/priming and source ownership | UNTESTED; conflicting generic/KSC descriptions; prior active-low issue historical | Inhibit trigger/source independently under approved procedure |

No driver, firmware, IP address or persistent setting was changed. No connected
device was enumerated. Previous observations of KSC101 firmware 1.0.7, SH05R and
one KEH3 route in `records/hardware-evidence.json` apply only to their recorded
revision/setup and do not establish the present hardware configuration.

The rewrite is independent of Thorlabs applications and SDK DLLs at the Python
runtime level. Neither optional USB transport eliminates the FTDI driver. No
claim is made about resolving the FTDIBUS crash mechanism. Only independently
validated hub Ethernet could establish host FTDI avoidance for those routes.

Continuous-duty manual operation requires documented shutter compatibility,
wiring, OFF mapping and recovery interval at the shared owner boundary. Finite
exposure/duty loads remain disabled. No attached shutter specification has been
confirmed for this rewrite. Do not infer safe limits from controller capability.
