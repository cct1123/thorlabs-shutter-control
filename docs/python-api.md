# Python API

```python
from thorlabs_shutter_control import ShutterHub, load_config

hub = ShutterHub(load_config("shutters.local.toml"))  # passive
try:
    hub.connect("beam")                 # identity only; exact configured route
    sample = hub.get_status("beam")     # dated electrical replies, optical unknown
finally:
    hub.close()                         # communication only
```

Run scripts with `uv run --locked python your_script.py`. There are no legacy
KCubeShutter, LANDiscovery, SDK-folder arguments or dynamic slot/discovery APIs.

After physical qualification and within the approved operating window:

```python
hub.set_manual_mode("beam")   # changed modes persist: requires separate policy opt-in
hub.open_shutter("beam")      # qualified continuous-duty manual ON, with readback
hub.close_shutter("beam")     # priority qualified OFF, with electrical readback
hub.pulse("beam", 0.5)        # requested host hold, not measured optical exposure
hub.cancel("beam")           # reaches the active owner and attempts qualified OFF
hub.shutdown_outputs()        # attempts every connected target, aggregates failures
```

Optical open/close names are allowed only with an independently established load
mapping. `set_solenoid(target, bool)` uses the same policy boundary. No public
output method bypasses it. Invalid arguments/modes fail before output writes;
nonfinite durations fail before any I/O. Unsupported cycles/TTL are unavailable.
`enable_device()` rejects explicitly because the protocol aliases channel enable
to solenoid output. It must not act as a harmless setup call.
`validate_pulse(target, duration)` checks the same duration/load constraints as
`pulse()` without connecting or accessing hardware; the CLI uses it before opening
a transport. Finite exposure/duty loads remain unavailable for both ON and pulse.

SRC-002 p20 specifies that the last used mode is remembered across power cycles.
Changing to Manual therefore requires `allow_persistent_mode_changes = true` in
the reviewed qualification policy, in addition to electrical OFF and the preserved
interlock requirement. The default is false. An already Manual/OFF controller is
queried without a mode write. A refused opt-in is not an ambiguous write and does
not itself latch a fault. No separate EEPROM command is sent.

`ShutterStatus` retains the DiamondGUI owner schema. Requested state,
`feedback.electrical_state`, and timestamped human optical observations are
separate. `feedback.shutter_state` stays unknown without a live independent
sensor. `transition_confirmed` is false. Interlock mode is the controller's
configuration, not proof of contact continuity; key/channel/status-bit fields
stay unknown where this driver does not have an established interpretation.

APT has no transaction identifiers. Freshness says
`response_after_request_no_transaction_id`, which describes receive provenance,
not a write acknowledgement or arbitrary network-delay immunity. No SDK cache
is involved. A query timeout/cancellation, duplicate reply or conflicting frame
poisons the session; it is never retried or reused for successful results.
After a short or unknown-count write, transmit alignment is also unknown. That
connection refuses every subsequent frame, including OFF, so a cleanup frame
cannot become part of the incomplete command. Independently protect the source
and restore the controller under the documented recovery procedure. Receive-only
failures and complete-but-late writes still allow a qualified OFF attempt; their
uncertain readback cannot confirm optical closure.

After any ambiguous output, ON remains locked out even after release/reconnect
or a new process. Normal successful OFF does not clear an existing fault. With
the source independently inhibited, optical closure independently observed and
the controller locally restored to Manual/OFF with interlocks intact:

```python
hub.recover("beam", source_inhibited=True, optical_closed=True,
            evidence="operator observation record with setup and timestamp")
```

Recovery reopens only the exact route, verifies identity/firmware and fresh
OFF/Manual/interlock replies, records the human observation and clears the
persistent uncertainty marker. It never sends ON or replays a trigger cycle.
The physical observation remains a dated record, not a continuing optical sensor.

Names and configured integer application channels are accepted. CH never means
APT channel: KSC101 protocol channel is always 1. `connection_snapshot()` is
host metadata only. `identify_device()` and `get_status()` perform explicit I/O.
