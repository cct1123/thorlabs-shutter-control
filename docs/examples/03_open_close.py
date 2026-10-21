"""Lesson 3: close, open briefly, then close one real shutter.

Run only after manual actuation and the chosen dwell have been approved:
    uv run --locked python docs/examples/03_open_close.py SERIAL --open-seconds SECONDS

Use an actual serial and a positive dwell within the shutter's approved limits.
The sleep duration is an added hold, not a maximum opening time: vendor calls
and physical travel add latency. Observe the shutter independently.
"""

import argparse
import math
from contextlib import ExitStack
from time import sleep

from thorlabs_shutter_control import KCubeShutter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial", help="Actual serial recorded in lesson 1")
    parser.add_argument(
        "--open-seconds", type=float, required=True, help="Approved hold in seconds"
    )
    args = parser.parse_args()
    if not math.isfinite(args.open_seconds) or args.open_seconds <= 0:
        parser.error("--open-seconds must be a finite positive number")

    shutter = KCubeShutter(args.serial)
    with ExitStack() as cleanup:
        # Release even a partially connected handle. Never Close an unverified target.
        cleanup.callback(shutter.disconnect, close_shutter=False)
        shutter.connect()
        cleanup.callback(shutter.close_shutter)  # Connect verified identity.
        print("Identity:", shutter.identify_device())

        # Establish Inactive/Manual before enabling a possibly retained Active state.
        shutter.disarm_triggers()
        ready = shutter.get_operating_status()
        print("Initial Close:", ready.shutter_state)
        if not ready.is_closed_manual or not ready.key_enabled:
            raise RuntimeError("Verify Closed/Manual and key before Open")
        shutter.enable_device()  # Explicit setup only after the baseline read.
        shutter.open_shutter()
        print("Open:", shutter.get_operating_status().shutter_state)
        sleep(args.open_seconds)
        shutter.close_shutter()
        print("Close:", shutter.get_operating_status().shutter_state)
        # ExitStack attempts Close then release, including on errors or Ctrl+C.
        # If cleanup also fails, Python retains the original exception chain.

    print("Close command sent and connection released. Verify physical closure.")


if __name__ == "__main__":
    main()
