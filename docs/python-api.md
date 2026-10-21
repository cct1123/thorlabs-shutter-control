# Python API

[README](../README.md) | [Architecture](architecture.md) | [Interface](INTERFACE.md)

Exports: KCubeShutter, ShutterHub, ShutterStatus, TriggerConfig, ShutterError,
LanDevice and LanDiscovery. Imports/construction are passive. KCubeShutter is USB
only; ShutterHub owns slots and Ethernet. Use hub methods for owned network channels.

## Construction

```python
from thorlabs_shutter_control import KCubeShutter, ShutterHub, config

c = KCubeShutter(config.SERIAL_NUMBERS[0], timeout=5.0, polling_ms=250)
hub = ShutterHub(slots=3)  # Empty, unselected panels; no discovery or connection.
```

Serials are eight digits beginning68, as strings or integers; internally they are
strings. None means unselected. timeout is finite0.5..60s and at least two polling
intervals; polling_ms is an integer100..1000. kinesis_dir defaults to config.KINESIS_DIR.
timeout applies to settings initialization and asynchronous LAN identity polling,
not to a blocking native call or total address-range scan.

ShutterHub accepts serial_numbers, slots, kinesis_dir and ethernet_endpoints.
Default slots: max(3, serial count) for USB, or max(serial count, endpoint count)
when routes are supplied. An explicit positive count must fit both lists.
None endpoints select USB; LAN endpoints must be IPv4:40304..40307 for KEH3.
Distinct USB controllers may be injected with controllers= for embedded/test use,
without other hub options. Network channels belong to their creating hub.

## Connection and manual control

Connect discovers and verifies identity without enabling or changing outputs.
Its returned snapshot is connection metadata; explicitly request operating feedback.
Hub connect(slot, serial) requires a selected serial; slots are zero-based.

```python
verified = False
try:
    c.connect()
    verified = True
    print(c.identify_device())
    c.disarm_triggers()  # Explicit Inactive, then Manual commands.
    if not c.get_operating_status().is_closed_manual:
        raise RuntimeError("Expected Closed/Inactive/Manual before Enable.")
    c.enable_device()
    c.open_shutter()
    print(c.get_shutter_state())
    c.close_shutter()
    print(c.get_shutter_state())
finally:
    c.disconnect(close_shutter=verified)
```

This example operates hardware and assumes approved conditions/source protection.
For communication-only checks, disconnect(close_shutter=False) releases without
Close or mode changes. Do not replace it with safe_shutdown.

| Method | Contract |
| --- | --- |
| discover() | Return matching KSC101 serials; no Connect/output |
| connect(serial_number=None) | Use explicit/preselected serial or the sole discovered USB device; validate identity and retain ownership |
| identify_device() | Read serial/description; does not flash the device display |
| get_status() | Request operating/TTL feedback; return a fault snapshot on read failure |
| get_operating_status() | Request operating/key/interlock feedback without TTL; return a fault snapshot on read failure |
| get_cached_status() | Last observation without I/O; current fault/disconnection takes precedence |
| get_shutter_state(), get_operating_state(), get_operating_mode(), get_status_bits() | Request the named feedback only |
| open_shutter(), close_shutter() | Request Active/Inactive only; preserve mode/enable state |
| enable_device() | Explicit channel enable |
| set_operating_state(state) | active or inactive |
| set_operating_mode(mode) | manual, single, auto or triggered |
| disconnect(close_shutter=True) | Attempt Close when requested, then communication release |
| safe_shutdown() | Close/release without closure readback |

Setters return None, invalidate display observations and perform no prerequisite
reads, sleeps, retries, readback or automatic recovery. SDK errors latch faults.
Callers own readiness, sequencing and verification; the GUI performs explicit
application checks. Close/release remain available after faults. Native calls can
block. A returned command does not establish physical state.

Snapshot getters report failed reads in `connection` and `error`; inspect those
fields before using the values. Narrow getters such as `get_trigger_config()`
raise `ShutterError` on read failure. Requested feedback uses a fixed wait followed
by SDK getters; it does not guarantee a known response age. `has_device` means a
driver handle is retained, including after failed disconnect, rather than healthy
communication or demonstrated shutter motion.

The context manager connects on entry and attempts safe_shutdown on exit. Failed
entry performs passive connection cleanup; failed release retains the object/claim.

## Status and TTL

ShutterStatus is immutable. It includes connection, has_device, serial_number,
description, shutter_state, operating_state, operating_mode, key_enabled,
interlock_enabled, trigger_config, error and status_bits. Undefined enums normalize
to unknown. A clear interlock bit is unknown; users verify the physical circuit.
is_closed_manual summarizes Closed/Inactive/Manual. ttl_armed reflects reported
Triggered/Active, not position. Feedback is not independent optical sensing.

```python
from thorlabs_shutter_control import TriggerConfig

settings = TriggerConfig(
    trig1_mode="input", trig1_polarity="high", trig2_mode="disabled", trig2_polarity="high"
)
c.configure_triggers(settings)
print(c.get_trigger_config())
```

Directions: disabled/input/output. Polarity: high/low. configure_triggers only
writes; get_trigger_config reads. arm_triggers explicitly enables, selects
Triggered and requests Active; disarm_triggers sends Inactive then Manual.
These direct methods do not read readiness. Arm may open immediately; see
[GUI prerequisites](gui.md#trigger-settings) and [hardware limits](hardware.md).

## Hub discovery and routing

discover_available() returns (routes, warnings): serial -> endpoint, None for USB.
It combines USB, configured-route discovery and one config-based LAN scan. Failed
transports warn without hiding successful results. It changes no slot route.
discover() returns a flat list for configured routes; discover_by_slot() groups
matching lists after one discovery. Snapshots can omit retained handles; GUI
identity/cleanup retention is separate.

scan_lan(start_address=None, end_address=None, open_timeout_ms=None) uses
config.LAN_SCAN_START_IP/END_IP/OPEN_TIMEOUT_MS when omitted. Explicit arguments
override those defaults; LAN_SCAN_MAX_ADDRESSES limits every scan to1..256.
Bounds must be IPv4 strings in ascending order; timeout is an integer50..1000ms.
The SDK scans hub port40303, registers hosts' KEH3 ports40304..40307, builds once
and refreshes asynchronous TCPIP identities. Result: LanDiscovery(hub_addresses,
controllers), with LanDevice(serial_number, endpoint). No device Connect/output
occurs. Release all process-owned handles before broad scanning.

configure_slot(slot, ethernet_endpoint=endpoint) passively selects a LAN route;
omitting the endpoint selects USB. A changed route replaces only a released
channel, clears its serial and retains SDK folder/timeout/poll settings. Same
route is a no-op. Failed-release handles forbid replacement. The endpoint tuple
is read-only. There is no transport fallback or inferred KEH6 LAN mapping.

Hub command/getter methods take slot first; their device contracts match the table
above. safe_shutdown attempts every slot, aggregates failures and preserves
interrupts after cleanup attempts. Successful communication release is not closure.

## Embedded GUI

```python
from thorlabs_shutter_control.gui import create_app

app = create_app(hub)  # A ShutterHub is required, including for one panel.
```

The host owns its server and cleanup. An optional on_shutdown callback enables
cooperative server shutdown after successful hub cleanup; it must not block.

GUI Connect calls the driver's `connect()` and then `hub.get_status(slot)` for a
full operating/TTL snapshot. GUI Apply TTL reads the operating prerequisite,
writes settings, then checks one full snapshot for read errors and actual TTL
agreement. Each action returns that snapshot to the GUI callback for display,
avoiding a second result read. See [GUI feedback timing](gui.md#feedback-timing).

Direct Python `connect()` still returns connection metadata only; it does not
automatically request operating or TTL feedback. Setters still return None and
perform no implicit readback. Use explicit getters and application checks as in
the examples above. The GUI optimization does not change those driver contracts.
