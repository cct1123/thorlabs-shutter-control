# Python API and integration

[README](../README.md) · [Getting started](getting-started.md) · [Architecture](architecture.md)

The public package exports `KCubeShutter`, `ShutterHub`, `ShutterStatus`, `TriggerConfig` and
`ShutterError`. Importing or constructing controllers/a hub does not connect
hardware. Hardware access remains on hold pending explicit validation approval.

## Minimal example

This example is for an **approved hardware setup with one attached KSC101**.
It requests real motion; first-time users can run the equivalent software-only
lifecycle with `uv run --locked python docs/examples/simulated_demo.py --api`.

```python
from thorlabs_shutter_control import KCubeShutter

with KCubeShutter() as controller:
    print(controller.identify_device())
    print(controller.get_status().shutter_state)
    controller.open_shutter()
    controller.close_shutter()
```

Entering the context calls `connect()` and returns the same controller. Exiting
attempts Close and disconnect, including when the body raises an exception.
The example's success is controller feedback, not independent proof of motion.

## Construct and configure

```text
KCubeShutter(
    serial_number=None,
    *,
    kinesis_dir=None,
    timeout=5.0,
    polling_ms=250,
)
```

| Argument / public attribute | Meaning and accepted values |
| --- | --- |
| `serial_number: str \| None` | Actual eight-digit ASCII serial beginning with `68`. `None` selects the sole discovered KSC101 on first connect. The attribute retains the selected serial after disconnect. |
| `kinesis_dir: str \| Path \| None` | SDK folder. If omitted, use `KINESIS_DIR`, then the `Thorlabs/Kinesis` directory beneath `ProgramFiles`. Only one SDK installation may be loaded per Python process. |
| `timeout: float` | Feedback/settings wait in seconds; finite `0.5..60`, default `5.0`. At least two polling intervals. It does not bound every native SDK call or the whole Open operation. |
| `polling_ms: int` | Polling interval in milliseconds; `100..1000`, default `250`. Boolean values are rejected. |

Invalid serial/timing values raise `ValueError` at construction. Configure these
attributes through the constructor and select a different device through
`connect(serial_number=...)` after disconnecting. Direct mutation of attributes
does not reconfigure an active vendor connection or rerun constructor validation.

## Methods

Hardware side effects below apply to the real backend. In the documentation demo,
the same methods reach only the existing test fixture.

| Method | Purpose, arguments and state requirements | Return | Important failures |
| --- | --- | --- | --- |
| `discover()` | Load the SDK and enumerate KSC101 USB identities, sorted by serial. No connection/output write; normally used before connect. | `list[str]`; empty when none found | `ShutterError` for unsupported OS, SDK loading or discovery failure |
| `connect(serial_number=None)` | Optional serial overrides selection. Discovers again; requires the selected device or exactly one device if selection is unset. Initializes settings, starts polling, verifies the returned serial matches selection and reads status without explicit enable/mode/output writes. Repeated connect to a healthy same-device handle returns status. | `ShutterStatus` | `ShutterError` for duplicate ownership in this process, invalid/absent/ambiguous identity, selection change while a handle exists, latched fault, initialization/polling/communication failure; attempts release after partial connection |
| `identify_device()` | Read identity from an active, healthy vendor connection. Does not call the vendor's display-flashing Identify command. | `dict[str, str]` with `serial_number` and `description` | `ShutterError`; identity-read failures latch a fault |
| `get_status()` | Return reported feedback if connected and not faulted; callable while disconnected. Communication/status failures become a fault snapshot with unknown state. | Immutable `ShutterStatus` | Device-read errors are captured in `status.error` rather than raised |
| `open_shutter()` | Requires connected/non-faulted status and enabled key/interlock reports. Requests Manual Open after verified preparation; returns immediately if already reporting Open/Active/Manual with safeguards enabled. | `ShutterStatus` reporting Open on success | `ShutterError` for connection/safeguard refusal, feedback timeout or SDK failure; failed command sequence attempts Inactive and latches a fault |
| `close_shutter()` | Requires a retained handle, including after a fault. Requests Inactive, verifies Closed/Inactive before Manual, then verifies Closed/Inactive/Manual. Operating feedback is independent of TTL settings reads. | `ShutterStatus` reporting Closed on success | `ShutterError` if no handle or closure cannot be verified; failure latches a fault |
| `disconnect(*, close_shutter=True)` | Default: attempt Close, stop polling and release. `False` explicitly releases communication without changing output. No handle: returns without an operation. | `None` | `ShutterError` for incomplete shutdown; release is attempted despite a Close failure, and a failed release retains the handle for retry |
| `safe_shutdown()` | Same as `disconnect(close_shutter=True)`. Available for normal shutdown and recovery attempts. | `None` | Same shutdown errors as `disconnect()` |
| `with controller:` | `__enter__()` connects and returns the controller; `__exit__()` attempts shutdown and does not suppress the body's exception. | Controller on entry; exit returns `False` | Entry can raise `ShutterError`. Shutdown error is raised if the body succeeded, or attached as a note to an existing body exception. |

There are no `open()` or `close()` aliases. Use `open_shutter()` and
`close_shutter()` in integrations.

## TRIG1/TRIG2 TTL

`TriggerConfig(trig1_mode="input", trig1_polarity="high", trig2_mode="output",
trig2_polarity="high")` is immutable. Modes are `disabled`, `input`, `output`;
polarities are `high`, `low`. Invalid values raise `ValueError` before hardware
access. These defaults describe a proposed configuration, not measured device
settings. Importing or constructing it performs no hardware operation.

| Method / status | Behavior |
| --- | --- |
| `get_trigger_config()` | Request and read vendor settings; returns `TriggerConfig`. Read errors latch a fault. No voltage or input-level measurement. |
| `configure_triggers(config)` | Require healthy Closed/Inactive/Manual feedback, apply both ports and wait for matching readback. Returns the reported configuration; mismatch or SDK failure latches a fault. Does not arm or explicitly persist settings. |
| `arm_triggers()` | Require healthy feedback, key/interlock and at least one configured input. Close/disarm first, enable, select Triggered, then prime Active. Wait for Triggered/Active with safeguards and unchanged configuration. Failure attempts Disarm/Close and latches a fault. Already armed returns feedback without another output write. |
| `disarm_triggers()` | Same closure operation as `close_shutter()`: attempt Inactive and Manual, verify Closed/Inactive/Manual. Remains available with a retained faulted handle. |
| `status.trigger_config` | Reported settings, or `None` when disconnected/faulted or omitted from command feedback. `get_status()` and connect request settings; they do not apply defaults. |
| `status.ttl_armed` | `True` for healthy Triggered/Active feedback; `False` for Manual or Inactive; otherwise `None`. An armed shutter can report Closed while its input is inactive. Faults invalidate this readout. |

Manual `open_shutter()` refuses Triggered mode until explicitly disarmed. Close
and default shutdown disarm and leave Manual selected; port settings are retained.
Closed/Inactive feedback is required before selecting Manual: forcing Manual
while a cube is still primed Active could open it. Failed Inactive/feedback skips
the mode change, reports uncertainty and still permits handle release/all-slot
cleanup. Failure cannot establish physical closure/disarming. `disconnect(close_shutter=False)`
still explicitly leaves the device's output/mode unchanged; it is not safe cleanup.

Open/Close/Disarm feedback waits sample operating state without reading TTL
settings, so a settings-read error cannot block disarming. Their returned snapshot
may omit `trigger_config`; use `get_status()` or `get_trigger_config()` for settings.
A prior fault remains latched until successful disconnect/reconnect.

For an **approved TTL bench only**, after connection and identity checks:

```python
from thorlabs_shutter_control import TriggerConfig

controller.disarm_triggers()
controller.configure_triggers(TriggerConfig("input", "high", "output", "high"))
print(controller.get_trigger_config())
try:
    controller.arm_triggers()  # May open immediately if an input is active.
    print(controller.get_status().ttl_armed)
finally:
    controller.disarm_triggers()  # The owning context/hub must also clean up.
```

The KSC101 manual describes 5 V TTL and an open/disconnected input as LOW.
Active-low can therefore open immediately on arming with no cable. Verify source,
polarity, direction and independent beam protection before any approved arming.
No live TTL test is authorized here. See [interface](INTERFACE.md#ttl-interface)
and the pending [physical procedure](HARDWARE_VALIDATION.md#stage-10--ttl-acceptance-pending).
Readback uses vendor-maintained data after a request and polling delay; real SDK
cache freshness, electrical behavior and priming semantics remain unvalidated.

## Three controllers with ShutterHub

`ShutterHub(serial_numbers=(), *, kinesis_dir=None, controllers=None)` constructs three independent
controllers. Supply up to three distinct serials to preselect slots in order;
remaining slots stay unselected. Construction never discovers or connects devices.
The `controllers` attribute is a tuple in panel order. The GUI uses this hub for
separate serial selections, connections, statuses, and Open/Close controls.

For existing controllers, use `ShutterHub(controllers=[...])` with one to three
distinct objects. Configure those objects directly; serial numbers or an SDK
directory cannot also be supplied to the hub when injecting controllers.

| Hub method / attribute | Behavior |
| --- | --- |
| `discover()` | One passive USB enumeration supplies choices for all slots; no connection or output write. |
| `connect(slot, serial_number)` | Connect an explicit serial in zero-based slot `0`, `1` or `2`; reject invalid slots and duplicate retained ownership. Returns that controller's `ShutterStatus`. |
| `controllers[slot]` | The existing `KCubeShutter` API for independent identification, status, Open, Close and individual shutdown. |
| `safe_shutdown()` | Attempt every controller in order, including after reported failures. Aggregate ordinary errors into one `ShutterError` with slot/serial context; re-raise an interruption after the remaining attempts. |
| `lock` | Reentrant lock used to serialize a complete GUI action/status snapshot with hub shutdown. Integrations own their operation/lifetime coordination. |

The following example is for an **approved, validated three-shutter bench**.
Its final cleanup requests real closure. The environment variables must contain
three actual serials mapped to the physical shutters; no hardware execution is
authorized by this documentation:

```python
import os

from thorlabs_shutter_control import ShutterHub

serials = [os.environ[f"KSC101_SERIAL_{index}"] for index in range(1, 4)]
hub = ShutterHub(serials)
try:
    for slot, controller in enumerate(hub.controllers):
        controller.connect()  # Uses the serial preselected during construction.
        print(slot + 1, controller.identify_device())
    # Use hub.controllers[slot].open_shutter()/close_shutter() only as approved.
finally:
    hub.safe_shutdown()  # Attempts cleanup of all slots, including partial setup.
```

KEH3 USB is the intended three-cube transport, with physical validation pending.
There is no hub Ethernet setup or synchronized actuation API. The hub does not
make multiple shutter operations simultaneous. Shutdown is sequential; neither
the per-controller timeout nor this loop establishes a total latency bound.
A hung vendor call can prevent later shutdown attempts. Independently protect
and observe every shutter, and preserve all reported errors.

## Status fields

`ShutterStatus` is a frozen dataclass. Treat each result as a snapshot and request
a new one when needed. Its default constructor represents a disconnected device.

| Field | Type / typical values | Meaning |
| --- | --- | --- |
| `connection` | `str`: `disconnected`, `connected`, `fault` | Wrapper connection/fault state; default `disconnected` |
| `has_device` | `bool`, default `False` | A vendor handle is retained; this alone does not establish healthy communication |
| `serial_number` | `str \| None` | Selected identity; may remain populated while disconnected |
| `description` | `str \| None` | Vendor description read on connection |
| `shutter_state` | `str`: `open`, `closed`, `unknown` | Normalized controller-reported position; default `unknown` |
| `operating_state` | `str`, default `unknown` | Lowercase vendor state, typically `active` or `inactive` |
| `operating_mode` | `str`, default `unknown` | Lowercase vendor mode; successful manual commands report `manual` |
| `key_enabled` | `bool \| None` | Reported key state; `None` means unknown |
| `interlock_enabled` | `bool \| None` | Reported interlock flag; `None` means unknown |
| `trigger_config` | `TriggerConfig \| None` | Vendor settings when requested; omitted in operating-only command feedback, disconnected or fault snapshots |
| `ttl_armed` (property) | `bool \| None` | Reported Triggered/Active priming, distinct from position; unknown on faults |
| `error` | `str \| None` | Latched diagnostic message, or `None` |

On a fault snapshot, shutter/operating state and mode become `unknown`, and
key/interlock become `None`; identity and handle presence can remain available.
Kinesis owns polling/cache freshness. These values are not a calibrated or
independent optical measurement.

## Explicit connection and error handling

For approved hardware operation, this is the equivalent explicit lifetime:

```python
from thorlabs_shutter_control import KCubeShutter, ShutterError

controller = KCubeShutter()
try:
    print("Available:", controller.discover())
    controller.connect()
    status = controller.get_status()
    if status.error:
        raise ShutterError(status.error)
    print("Connected:", controller.identify_device())
    print("Open:", controller.open_shutter().shutter_state)
    print("Close:", controller.close_shutter().shutter_state)
except ShutterError as error:
    print(f"Shutter operation failed: {error}")
finally:
    try:
        controller.safe_shutdown()
    except ShutterError as error:
        print(f"Shutdown incomplete; physical closure unverified: {error}")
```

`ShutterError` subclasses `RuntimeError`; its message includes operation context
and usually the underlying vendor error. The context manager is preferable when
you want cleanup failures automatically attached to an original exception.
Application code must decide how to stop the larger experiment after failure;
printing a message alone is not a physical recovery method.

## Shutdown and faults

Close/cleanup are attempts, not an independent guarantee that the blade closed.
`disconnect(close_shutter=False)` leaves output unchanged and is deliberately
different from normal shutdown. It is used by the first passive connection stage
in the [hardware procedure](HARDWARE_VALIDATION.md).

A successful Close after an earlier fault can return a Closed snapshot without
clearing the latched fault: subsequent `get_status()` remains Fault and Open is
blocked until disconnect/reconnect. Resolve the cause and verify the bench before
resuming operation. A successful release clears the prior fault only when cleanup
has no new errors; repeated cleanup with no handle preserves a failed-close message.

If an Open sequence fails, it attempts Inactive, records physical state as
unverified and raises. Shutdown still attempts release after a Close error.
An interruption during recovery also leaves a latched fault. Release attempts
Disconnect even when StopPolling is interrupted; it reports errors and re-raises
the interruption after cleanup, preserving serial ownership if release failed.
If release itself fails, `has_device` remains true so cleanup can be retried.
Its serial ownership claim remains held too; creating another controller object
cannot bypass a retained handle. Successful release or cleanup after a failed
connection frees the claim. A factory failure that creates no handle also frees it.
Power loss, USB loss, forced process termination and hung native calls do not
provide guaranteed software cleanup.

## Integrate into an experiment

Depend on this small API at the orchestration boundary. Pass an already connected
controller into your experiment function and keep ownership/cleanup outside it:

```python
def acquire_with_shutter(controller, acquire):
    """Caller owns connection and shutdown; acquire is the experiment's callback."""
    controller.open_shutter()
    try:
        return acquire()
    finally:
        controller.close_shutter()
```

Call it inside `with KCubeShutter() as controller:` for an approved setup.
This helper closes after acquisition errors; the outer context also attempts
shutdown if Open fails. If both acquisition and Close fail, Python retains the
acquisition exception as context for the Close error. Log the full exception chain.
The software-only demo is a useful place to try such orchestration first.

Use one owner per device, keep vendor types out of experiment code, and do not run
the vendor GUI or another controller process against the same KSC101. Per-instance
locking serializes that object's synchronous calls; the process-wide registry
rejects a second owner of the same serial, and shared SDK discovery/creation is
serialized. The class has no async API or cross-process ownership mechanism.
Do not use the demo's process-wide SDK
patch in a program that also controls real hardware.

Default polling is 250 ms and feedback waits are 5 s per stage. Calls can block
longer inside the SDK. This interface is for manual/laboratory orchestration,
not precise exposure timing. See [architecture](architecture.md#timing-and-ownership).
