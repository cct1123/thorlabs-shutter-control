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
        "--verified-interlock",
        metavar="SERIAL",
        help="Confirm normal physical interlock/protection for this selected serial, this run only",
    )
    parser.add_argument(
        "--open-seconds", type=float, required=True, help="Approved hold in seconds"
    )
    args = parser.parse_args()
    if not math.isfinite(args.open_seconds) or args.open_seconds <= 0:
        parser.error("--open-seconds must be a finite positive number")
    if args.verified_interlock is not None and args.verified_interlock != args.serial:
        parser.error("--verified-interlock must match the selected serial")

    shutter = KCubeShutter(args.serial)
    if args.verified_interlock:
        shutter.confirm_interlock(args.serial)
    with ExitStack() as cleanup:
        # Release even a partially connected handle. Never Close an unverified target.
        cleanup.callback(shutter.disconnect, close_shutter=False)
        shutter.connect()
        cleanup.callback(shutter.close_shutter)  # Connect verified identity/feedback.
        print("Identity:", shutter.identify_device())

        # This first intentional output command also disarms a prior TTL mode.
        print("Initial Close:", shutter.close_shutter().shutter_state)

        # The driver checks the key/interlock and confirms preparation before Open.
        print("Open:", shutter.open_shutter().shutter_state)
        sleep(args.open_seconds)
        print("Close:", shutter.close_shutter().shutter_state)
        # ExitStack attempts Close then release, including on errors or Ctrl+C.
        # If cleanup also fails, Python retains the original exception chain.

    print("Cleanup completed with controller feedback. Verify physical closure.")


if __name__ == "__main__":
    main()
