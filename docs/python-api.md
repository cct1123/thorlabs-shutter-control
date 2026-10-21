# Python API

[README](../README.md) | [Architecture](architecture.md) | [Interface](INTERFACE.md)

Exports: KCubeShutter, ShutterHub, ShutterStatus, TriggerConfig and ShutterError.
Import/construction is passive. SDK loading occurs on explicit discovery/connection.

## Construction and confirmation

```python
from thorlabs_shutter_control import KCubeShutter

c = KCubeShutter("68800777", timeout=5.0, polling_ms=250)
# Only after normal physical interlock and independent protection are verified:
c.confirm_interlock("68800777")
```

| Argument | Contract |
| --- | --- |
| serial_number | Optional eight-digit KSC101 serial starting68; changing an owned target is refused |
| kinesis_dir | Optional SDK path; otherwise KINESIS_DIR, then Program Files/Thorlabs/Kinesis |
| timeout | Finite0.5..60s, at least two polling intervals; per feedback wait, not end-to-end deadline |
| polling_ms | Integer100..1000ms; default250 |
| ethernet_endpoint | Optional explicit IPv4 KEH3 endpoint, ports40304..40307; experimental passive qualification |

Confirmation requires the same explicitly selected serial and no retained handle.
It is object/serial scoped, survives ordinary reconnect within that session,
clears on retargeting and does not transfer to another object/process. It changes
no hardware interlock setting. Positive SDK indication or this explicit evidence
can establish readiness when SDK indication is unknown; known negative, key,
identity and communication checks remain blocking.

## Connection and manual control

```python
try:
    status = c.connect()
    print(c.identify_device())
    print(c.close_shutter())
finally:
    c.safe_shutdown()
```

The example authorizes normal output cleanup for the selected bench. For a purely
passive diagnostic use disconnect(close_shutter=False), which leaves output/mode
unchanged. Do not substitute safe_shutdown for communication-only release.

| Method | Behavior |
| --- | --- |
| discover() | Return KSC101 identities; no Connect or output command |
| connect(serial_number=None) | Discover/select, claim serial, initialize settings/polling, verify identity and known operating feedback; no explicit output/mode write |
| identify_device() | Return serial_number/description from GetDeviceInfo; no display-flashing IdentifyDevice call |
| get_status() | Full controller-reported snapshot including trigger settings; read failures latch a fault |
| close_shutter() | Attempt Inactive even after a fault, require Closed/Inactive before Manual, then verify again |
| open_shutter() | Require healthy connection/key/interlock readiness/non-Triggered mode; Close baseline, enable, Active and verify Open |
| disconnect(close_shutter=True) | Default Close then release, retaining/raising any failure; False releases communication only |
| safe_shutdown() | Default Close-and-release behavior; reports incomplete cleanup |

Already Open/Active/Manual with readiness returns feedback without replaying an
Open write. A failed Open may have actuated, so recovery attempts Inactive and
preserves a fault. Unknown enums remain errors; Numeric0 is not Inactive.
Command-return snapshots may omit trigger_config; get_status reads the full status.

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
print(c.configure_triggers(config))
print(c.get_trigger_config())
```

This changes configuration; it requires a separately approved TTL setup.
TriggerConfig is immutable, with modes disabled/input/output and polarity high/low.
Defaults: TRIG1 input/high, TRIG2 output/high. Construction alone writes nothing.

configure_triggers requires healthy Closed/Inactive/Manual and matching readback.
get_trigger_config requests existing settings. arm_triggers requires an input,
readiness and healthy status, then closes, enables, selects Triggered and primes
Active. It uses device settings, not GUI drafts. disarm_triggers is the Close
sequence. Armed does not mean Open; an inactive input may leave the blade Closed.
Active input/active-low with a disconnected LOW input may open immediately.
No raw input-voltage measurement or calibrated pulse generation is provided.

## Multiple controllers

```python
from thorlabs_shutter_control import ShutterHub

hub = ShutterHub(["68000001", "68000002", "68000003"])  # Fictional example IDs.
# Supply actual distinct identities and verify each physical interlock separately.
```

ShutterHub creates three fixed slots, padding omitted serials with None.
Explicit controllers= accepts one to three distinct objects; do not combine this
with serial_numbers/kinesis_dir options. Python hub.connect uses zero-based slots
and explicit serials. discover uses the first controller's transport, so the normal
hub/GUI is USB-focused; mixed experimental transports are not qualified.

hub.safe_shutdown attempts every controller despite ordinary errors/interrupts,
then aggregates errors by slot/serial. A native hang can block later attempts.
The hub lock serializes GUI actions/snapshots; each driver also serializes calls.

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
