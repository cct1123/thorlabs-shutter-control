# Hardware tutorials

For an interactive walkthrough, open
[shutter_open_close_tutorial.ipynb](shutter_open_close_tutorial.ipynb). Separate
cells cover settings, validation, controller/error cleanup, connection, initial
Close, Open/hold, Close, optional repetition, and disconnect. Run them in order
with the project `.venv` kernel. Successful steps keep the connection active;
Open leaves the shutter open until Close. Each hardware step attempts cleanup
on errors/Ctrl+C. Always finish with Disconnect. Repetition is disabled by default.
Restart the kernel after controller or configuration changes.

These five scripts use real hardware. `--help` and imports are passive. Match each
serial to the physical shutter and establish independent source protection, normal
interlock, ownership and operating limits before running an output example.

| Script | Effect |
| --- | --- |
| [01_discover.py](01_discover.py) | USB enumeration only |
| [02_connect_and_read_status.py](02_connect_and_read_status.py) | Connect/read and communication-only release; no Close or mode change |
| [03_open_close.py](03_open_close.py) | Initial Close, Open, approved added hold, Close and cleanup |
| [04_three_shutters.py](04_three_shutters.py) | Connect three distinct serials, establish Closed, operate sequentially, attempt all-slot cleanup |
| [05_ttl_control.py](05_ttl_control.py) | Configure TRIG1 input/high and TRIG2 disabled/high, explicitly Arm, wait, Disarm/Close and release |

Example on the qualified single-pair bench, after normal interlock/protection
have been verified:

```powershell
uv run --locked python docs/examples/01_discover.py
uv run --locked python docs/examples/02_connect_and_read_status.py $env:SHUTTER_SERIAL
uv run --locked python docs/examples/03_open_close.py $env:SHUTTER_SERIAL --open-seconds 2
```

Users manage the physical interlock externally. There is no software interlock
gate or confirmation flag. The lessons explicitly check identity, connection, key
and operating state before Open/Arm; driver setters only send commands.

Examples4/5 remain unqualified on three actual devices/electrical trigger inputs.
Supply actual serials and explicitly approved `--open-seconds` or `--armed-seconds`;
there is no default actuation duration. These waits start after feedback and are
not maximum exposure bounds. The TTL example can open immediately on an active
input. Read [the interface contract](../INTERFACE.md) before using it.

The actuation examples use ExitStack to register passive release before Connect,
and Close only after connection identity verification succeeds. All registered
callbacks are attempted despite failures, with normal Python exception chaining.
A failed identity plus failed release never authorizes Close of the unverified
target. Release alone does not prove closure. Follow the
[three-stage procedure](../HARDWARE_VALIDATION.md); the
[optional diagnostic helpers](../hardware_tests/README.md) retain structured
operation/release results for investigations, rather than a mandatory sequence.

Developer-only simulation is separate: `uv run --locked python tests/simulated_demo.py --api`.
It uses fictional software devices and cannot prove wiring, physical motion or timing.
