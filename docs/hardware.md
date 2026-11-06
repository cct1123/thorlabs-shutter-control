# Device, route and driver matrix

| Route | Python dependency | Native / OS requirement | Current validation | Rollback |
| --- | --- | --- | --- | --- |
| Direct USB, exact serial, D2XX | optional ftd2xx 1.3.8 (pywin32 on Windows) | Matching official FTDI D2XX native DLL and device driver/binding; retains FTDIBUS dependence | Simulated protocol/initialization only; actual driver and firmware UNTESTED | Restore inventoried signed package/binding during all-instrument downtime |
| Direct USB, exact VCP | optional pyserial 3.5 | Existing FTDI VCP binding and exact COM assignment; retains FTDI dependence | Read-only commissioning; bridge reset equivalence unresolved | Restore original COM/binding/package from inventory |
| KEH3 left/middle/right | Python standard-library TCP | Exact controller/host/bay; USB IN disconnected | Actual middle-bay 68800777/1.0.7 identity/status readback; SH05R Manual ON/OFF controller readback PASS (E181); independent optics and hub recovery unvalidated | Independent source protection; qualified OFF best effort; release communication |
| KEH3 external USB OUT | unresolved | Requires its own supported-device/routing contract | Unavailable independently of cube bays | No inferred fallback |
| TTL | unavailable | Actual shutter rating, electrical thresholds/polarity/priming and source ownership | UNTESTED; conflicting generic/KSC descriptions; prior active-low issue historical | Inhibit trigger/source independently under approved procedure |

No driver, firmware or IP address was changed. Explicit Manual selection was
authorized/performed and is remembered at power-up; no other persistent setting
was programmed. The earlier native inventory and USB open failure are recorded in STATE.md. Previous observations of KSC101 firmware 1.0.7, SH05R and
one KEH3 route in `records/hardware-evidence.json` apply only to their recorded
revision/setup and do not establish the present hardware configuration.

The rewrite is independent of Thorlabs applications and SDK DLLs at the Python
runtime level. Neither optional USB transport eliminates the FTDI driver. No
claim is made about resolving the FTDIBUS crash mechanism. The actual TCP read/control path does not load host FTDI libraries. The selected
SH05R ON/OFF controller readback passes; hub recovery/independent optics/other
configurations remain separate.

Continuous-duty manual operation requires documented shutter compatibility,
wiring, OFF mapping and recovery interval at the shared owner boundary. Finite
exposure/duty loads remain disabled. No attached shutter specification has been
bench-qualified for this revision. PROJECT.md records the user's SH05R selection;
SRC-009 supplies the load document reference. Do not infer safe limits from
controller capability or confuse manufacturer design mapping with measured closure.
