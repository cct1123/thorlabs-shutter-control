# Python API and integration

[README](../README.md) · [Getting started](getting-started.md) · [Architecture](architecture.md)

The public package exports `KSC101Controller`, `ShutterStatus` and `ShutterError`.
Importing or constructing a controller does not connect hardware.

## Minimal example

This example is for an **approved hardware setup with one attached KSC101**.
It requests real motion; first-time users can run the equivalent software-only
lifecycle with `uv run --locked python docs/examples/simulated_demo.py --api`.

```python
from thorlabs_shutter_control import KSC101Controller

with KSC101Controller() as controller:
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
KSC101Controller(
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
| `connect(serial_number=None)` | Optional serial overrides selection. Discovers again; requires the selected device or exactly one device if selection is unset. Initializes settings, starts polling and reads status without explicit enable/mode/output writes. Repeated connect to a healthy same-device handle returns status. | `ShutterStatus` | `ShutterError` for invalid/absent/ambiguous identity, selection change while a handle exists, latched fault, initialization/polling/communication failure; attempts release after partial connection |
| `identify_device()` | Read identity from an active, healthy vendor connection. Does not call the vendor's display-flashing Identify command. | `dict[str, str]` with `serial_number` and `description` | `ShutterError`; identity-read failures latch a fault |
| `get_status()` | Return reported feedback if connected and not faulted; callable while disconnected. Communication/status failures become a fault snapshot with unknown state. | Immutable `ShutterStatus` | Device-read errors are captured in `status.error` rather than raised |
| `open_shutter()` | Requires connected/non-faulted status and enabled key/interlock reports. Requests Manual Open after verified preparation; returns immediately if already reporting Open/Active/Manual with safeguards enabled. | `ShutterStatus` reporting Open on success | `ShutterError` for connection/safeguard refusal, feedback timeout or SDK failure; failed command sequence attempts Inactive and latches a fault |
| `close_shutter()` | Requires a retained device handle. Attempts Inactive then Manual, even after a prior fault; waits for Closed/Inactive/Manual feedback. | `ShutterStatus` reporting Closed on success | `ShutterError` if no handle or closure cannot be verified; failure latches a fault |
| `disconnect(*, close_shutter=True)` | Default: attempt Close, stop polling and release. `False` explicitly releases communication without changing output. No handle: returns without an operation. | `None` | `ShutterError` for incomplete shutdown; release is attempted despite a Close failure, and a failed release retains the handle for retry |
| `safe_shutdown()` | Same as `disconnect(close_shutter=True)`. Available for normal shutdown and recovery attempts. | `None` | Same shutdown errors as `disconnect()` |
| `with controller:` | `__enter__()` connects and returns the controller; `__exit__()` attempts shutdown and does not suppress the body's exception. | Controller on entry; exit returns `False` | Entry can raise `ShutterError`. Shutdown error is raised if the body succeeded, or attached as a note to an existing body exception. |

There are no `open()` or `close()` aliases. Use `open_shutter()` and
`close_shutter()` in integrations.

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
| `error` | `str \| None` | Latched diagnostic message, or `None` |

On a fault snapshot, shutter/operating state and mode become `unknown`, and
key/interlock become `None`; identity and handle presence can remain available.
Kinesis owns polling/cache freshness. These values are not a calibrated or
independent optical measurement.

## Explicit connection and error handling

For approved hardware operation, this is the equivalent explicit lifetime:

```python
from thorlabs_shutter_control import KSC101Controller, ShutterError

controller = KSC101Controller()
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
If release itself fails, `has_device` remains true so cleanup can be retried.
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

Call it inside `with KSC101Controller() as controller:` for an approved setup.
This helper closes after acquisition errors; the outer context also attempts
shutdown if Open fails. If both acquisition and Close fail, Python retains the
acquisition exception as context for the Close error. Log the full exception chain.
The software-only demo is a useful place to try such orchestration first.

Use one owner per device, keep vendor types out of experiment code, and do not run
the vendor GUI or another controller process against the same KSC101. Per-instance
locking only serializes that object's synchronous calls. The class has no async
API or cross-process ownership mechanism. Do not use the demo's process-wide SDK
patch in a program that also controls real hardware.

Default polling is 250 ms and feedback waits are 5 s per stage. Calls can block
longer inside the SDK. This interface is for manual/laboratory orchestration,
not precise exposure timing. See [architecture](architecture.md#timing-and-ownership).
