# Python API

[README](../README.md) | [Architecture](architecture.md) | [Interface](INTERFACE.md)

Exports: KCubeShutter, ShutterHub, ShutterStatus, TriggerConfig and ShutterError.
Import/construction is passive. SDK loading occurs on explicit discovery/connection.
`KCubeShutter` accepts USB devices only. Ethernet endpoints belong to `ShutterHub`.

## Construction and confirmation

```python
from thorlabs_shutter_control import KCubeShutter, config

# Set SERIAL_NUMBERS in config.py first.
c = KCubeShutter(config.SERIAL_NUMBERS[0], timeout=5.0, polling_ms=250)
```

| Argument | Contract |
| --- | --- |
| serial_number | Optional eight-digit KSC101 serial starting68, as str or int; normalized to str internally; changing an owned target is refused |
| kinesis_dir | Optional SDK path; otherwise `config.KINESIS_DIR` (no environment lookup) |
| timeout | Finite0.5..60s, at least two polling intervals; settings initialization wait only, not an end-to-end deadline |
| polling_ms | Integer100..1000ms; default250 |

Confirmation requires the same explicitly selected serial and no retained handle.
It is object/serial scoped, survives ordinary reconnect within that session,
clears on retargeting and does not transfer to another object/process. It changes
no hardware interlock setting. Positive SDK indication or this explicit evidence
is informational metadata. No project command or example gates on interlock
feedback or confirmation. Users manage the physical interlock externally; the GUI
checks identity/communication, key and operating feedback.

## Connection and manual control

`connect()` initializes communication/polling and verifies the selected identity.
Its returned snapshot contains connection metadata, not newly requested operating
feedback. Use a getter when you need that feedback. Undefined operating state `0`
is reported as `unknown`; it does not prevent connection or imply Inactive.

```python
verified = False
try:
    status = c.connect()
    verified = True
    print(c.identify_device())
    c.close_shutter()
    print(c.get_shutter_state())
finally:
    c.disconnect(close_shutter=verified)
```

The example authorizes normal output cleanup for the selected bench. For a purely
passive diagnostic use disconnect(close_shutter=False), which leaves output/mode
unchanged. Do not substitute safe_shutdown for communication-only release.

| Method | Behavior |
| --- | --- |
| discover() | Return KSC101 identities; no Connect or output command |
| connect(serial_number=None) | Discover/select, claim serial, initialize settings/polling and verify identity; return metadata without operating-feedback requests |
| identify_device() | Return serial_number/description from GetDeviceInfo; no display-flashing IdentifyDevice call |
| get_status() | Fresh full operating/TTL snapshot; read failures latch a fault |
| get_operating_status() | Fresh operating/safeguard feedback only; no TTL settings requests |
| get_trigger_config() | Fresh TTL settings only; no operating-status requests |
| get_cached_status() | Last display observation without I/O; current fault/disconnection takes precedence |
| close_shutter() | Send Inactive only; preserve mode; return None |
| open_shutter() | Send Active only; preserve mode/enable state; return None |
| enable_device() | Explicit SDK channel enable; no mode/state command or feedback; return None |
| set_operating_state(state) | Send active or inactive only; return None |
| set_operating_mode(mode) | Send manual, single, auto or triggered only; return None |
| get_shutter_state() | Request position only: open, closed or unknown |
| get_operating_state() | Request operation only: active, inactive or unknown |
| get_operating_mode() | Request mode only: manual, single, auto, triggered or unknown |
| get_status_bits() | Request raw status bits only |
| disconnect(close_shutter=True) | Request Close then release; False releases communication only |
| safe_shutdown() | Best-effort Close command and release; no closure readback |

**Setters send commands. Getters request feedback.** Setters perform no status
requests, prerequisite reads, sleeps, retries, result readback or automatic
recovery. They validate arguments and the locally retained handle/fault state,
then issue vendor writes. Repeated calls send repeated commands. Native SDK calls
can still block or raise. Successful return means only that the SDK call returned.

```python
c.disarm_triggers()               # Explicit Inactive/Manual preparation.
print(c.get_operating_status())    # Establish the intended baseline first.
c.enable_device()                 # Explicit setup once when needed.
c.open_shutter()                  # Active only; returns None.
print(c.get_shutter_state())       # Separate position request/read.
c.close_shutter()                 # Write, returns None.
print(c.get_operating_status())    # Explicit operating snapshot if wanted.
```

Active follows the selected mode: Manual opens, Single starts one cycle, Auto
starts cycling, and Triggered primes trigger behavior. Inactive requests closure
without selecting Manual. Use explicit mode setup when needed; Open/Close never
repeat EnableDevice. The GUI manual Open requires Manual and assumes an enabled
controller. Arm remains a compound Enable/Triggered/Active command. See the
[official KSC101 example](https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/Kinesis/KCube/KSC101/KSC101_pythonnet.py),
which enables once during setup before toggling Active/Inactive.

Direct API callers own sequencing, physical interlocks and any required
verification. Hardware interlocks remain intact. The GUI performs its own explicit
readiness reads and reads the selected panel again after commands. Setters clear
cached observations; a sent command never fabricates a successful observation.
Getter snapshots normalize undefined operating enums to `unknown`. Communication
and SDK exceptions still latch faults; Close remains available after faults.

Context manager: entering calls connect, exiting attempts safe_shutdown after the
body, including body errors. A failed __enter__ does not run __exit__; connect
itself attempts passive release and retains the object/claim on failed release.
For identity-gated output cleanup on partial connections, see the staged helpers.

## Status

ShutterStatus is immutable. All values are SDK feedback, not independent sensing.

| Field/property | Meaning |
| --- | --- |
| connection | disconnected, connected or fault |
| has_device | Retained SDK handle, independent of communication health |
| serial_number / description | Selected identity / vendor description |
| shutter_state | open, closed or unknown |
| operating_state | active, inactive or unknown |
| operating_mode | manual, single, auto, triggered or unknown |
| key_enabled | bool or None |
| interlock_enabled | True for documented positive SDK bit, None when unverified/unavailable; clear does not prove physically disabled |
| status_bits | Raw SDK integer or None |
| operator_interlock_confirmed | Separate session verification for selected serial |
| interlock_ready | Healthy connection and positive indication, or operator evidence when reading is None; known False is not overridden |
| trigger_config | TriggerConfig or None |
| ttl_armed | True for Triggered/Active, False for Manual or Inactive, otherwise None |
| error | Latched diagnostic or None |

Faulted snapshots invalidate operating/TTL values. Identity and handle information
can remain available; release without known closure never claims physical Closed.

## TRIG1/TRIG2 TTL

```python
from thorlabs_shutter_control import TriggerConfig

c.disarm_triggers()
config = TriggerConfig(trig1_mode="input", trig1_polarity="high",
                       trig2_mode="disabled", trig2_polarity="high")
c.configure_triggers(config)
print(c.get_trigger_config())
```

This changes configuration; it requires a separately approved TTL setup.
TriggerConfig is immutable, with modes disabled/input/output and polarity high/low.
Defaults: TRIG1 input/high, TRIG2 output/high. Construction alone writes nothing.

`configure_triggers(config)` sends the validated port settings and returns None.
`get_trigger_config()` separately requests those settings. No automatic matching,
retry, prerequisite read or EEPROM persist occurs in the setter.
`arm_triggers()` sends Enable, Triggered, Active and returns None.
`disarm_triggers()` explicitly sends Inactive then Manual. Close alone preserves
the operating mode.
Callers must establish the intended baseline, input configuration and readiness
before Arm; the GUI and hardware lessons do this explicitly. Armed does not mean
Open; an inactive input may leave the blade Closed.
Active input/active-low with a disconnected LOW input may open immediately.
No raw input-voltage measurement or calibrated pulse generation is provided.

## Multiple controllers

```python
from thorlabs_shutter_control import ShutterHub

hub = ShutterHub(["68000001", "68000002", "68000003"])  # Fictional example IDs.
# Supply actual distinct identities and verify each physical interlock separately.
```

ShutterHub accepts `slots=N` for any positive integer. Without it, the count is
`max(3, len(serial_numbers), len(ethernet_endpoints))`; an explicit count must fit
both lists. Omitted serials are None; omitted endpoints are USB. `controllers=`
accepts distinct USB KCubeShutter objects only, without other hub options.
Network channels belong to their creating hub and cannot be injected elsewhere.

For Ethernet, configure explicit per-slot endpoints on the hub:

```python
hub = ShutterHub(
    [68000001], slots=1,
    ethernet_endpoints=["192.0.2.10:40304"],  # Replace fictional ID/address.
)
try:
    hub.connect(0, 68000001)
    print(hub.identify_device(0))
    print(hub.get_status(0))
finally:
    hub.disconnect(0, close_shutter=False)  # Passive release for this read-only example.
```

`ethernet_endpoints` is an immutable per-slot tuple: an IPv4 KEH3 cube endpoint
selects network transport; None selects USB. Only the documented cube ports
40304..40307 are accepted. This is software support, not physical Ethernet
qualification. No KEH6 Ethernet port map is inferred.

Hub methods use a zero-based slot first: `open_shutter(slot)`,
`close_shutter(slot)`, `set_operating_state(slot, state)`,
`set_operating_mode(slot, mode)`, `configure_triggers(slot, config)`,
`arm_triggers(slot)`, `disarm_triggers(slot)`, `enable_device(slot)`, and
`confirm_interlock(slot, serial)`.
Setters return None with no operating feedback request/wait/readback. Network
writes check local SDK routing metadata first; a changed endpoint/provider faults
and refuses ordinary output commands. Close/Inactive still attempts the retained
handle for cleanup. Commands never rebind a handle or fall back to USB.

Read methods also take a slot: `get_shutter_state`, `get_operating_state`,
`get_operating_mode`, `get_status_bits`, `get_trigger_config`, `get_status`,
`get_operating_status`, `get_cached_status`, and `identify_device`.
Discovery registers the selected endpoints, builds one list and filters matching
transports. Connect requires an explicit serial matching that slot's route.
USB KCubeShutter discovery filters FTDI entries even after network registration.
The normal launcher remains USB; `create_app(hub)` also accepts a network hub.
Use hub methods for network lifecycle/commands rather than its internal channels.

hub.safe_shutdown attempts every controller despite ordinary errors/interrupts,
then aggregates errors by slot/serial. A native hang can block later attempts.
The hub lock serializes GUI actions/snapshots; each driver also serializes calls.

A GUI built from `ShutterHub`, including a one-slot hub, requires a selected
serial for Connect. The direct `create_app(KCubeShutter(...))` convenience form
retains the driver's optional-serial connection behavior.

## Shutdown and faults

Faults latch until successful release/reconnect. Close may succeed while the old
fault remains. A failed Disconnect keeps the SDK handle and serial ownership
claim; retain the same controller for diagnosis, rather than creating another owner.
StopPolling failure does not skip Disconnect. Cleanup failures raise ShutterError;
interruptions propagate after remaining cleanup attempts and include diagnostics.

Separate process ownership is an operator responsibility. Normal CLI Ctrl+C calls
hub cleanup; browser closure, forced process kill and USB/power loss do not provide
that guarantee. Physical recovery and optical closure must be independently defined.

Ethernet is described in the [qualification note](ethernet-assessment.md). Actual
single-pair evidence and limits are in [hardware-validation.json](../records/hardware-validation.json).
