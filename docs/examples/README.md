# Current notebooks

[USB tutorial](shutter_open_close_tutorial.ipynb) covers one selected cube: settings,
identity, explicit Disarm/Closed/Enable setup, Open/hold, Close, feedback, API call
duration and release. Run cells in order; Open can remain active while paused.

[LAN tutorial](shutter_lan_tutorial.ipynb) uses ShutterHub with an explicit KEH3
cube serial/bay endpoint. It separates passive discovery/identity from deliberate
Manual setup and one Open/hold/Close cycle. For communication-only work, skip
operation cells and run release; that path sends no Close or mode command.

Use the project .venv kernel, restart after source/config changes, and exclude
other owners. Set local serial/address and approved hold; shared templates have
blank local identities/cleared outputs. Imports/settings are passive, later cells
can actuate real hardware. Users establish normal physical interlock and independent
source protection. Always finish release; preserve the same object if release fails.
Cleanup attempts do not prove physical closure or bound a native hang.

API call durations, host waits and controller feedback do not establish optical
state or calibration. Current physical limits and prior notebook observations are
in [hardware evidence](../hardware.md). Preserve executed copies/results in ignored
inputs/private/notebooks; keep public examples free of actual device identifiers.
Tests execute these notebooks only against fake devices. Developer simulation is
separate: `uv run --locked python -B tests/simulated_demo.py --api`.
