"""Lesson 4: use three real KSC101s through KEH3 USB, one shutter at a time.

Run only after the three-controller mapping and each dwell have been approved:
    uv run --locked python docs/examples/04_three_shutters.py S1 S2 S3 --open-seconds T

Replace S1/S2/S3 with distinct actual serials in the order you want to use them.
Replace T with a dwell acceptable for ALL three shutters. Commands are sequential,
not synchronized. Keep independent protection/observation for every shutter.
"""

import argparse
import math
from contextlib import ExitStack
from time import sleep

from thorlabs_shutter_control import ShutterHub


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serials", nargs=3, metavar="SERIAL", help="Three distinct actual serials")
    parser.add_argument(
        "--open-seconds", type=float, required=True, help="Approved hold in seconds"
    )
    args = parser.parse_args()
    if not math.isfinite(args.open_seconds) or args.open_seconds <= 0:
        parser.error("--open-seconds must be a finite positive number")

    # The hub creates one independent KCubeShutter for each serial; no connection yet.
    hub = ShutterHub(args.serials)
    with ExitStack() as cleanup:
        for shutter in hub.controllers:
            cleanup.callback(shutter.disconnect, close_shutter=False)
        for slot, serial in enumerate(args.serials):
            # Python slot numbers start at 0; printed shutter numbers start at 1.
            hub.connect(slot, serial)
            shutter = hub.controllers[slot]
            cleanup.callback(shutter.close_shutter)  # Only a verified connection.
            print(f"Shutter {slot + 1}:", shutter.identify_device())
            shutter.enable_device()  # Explicit one-time channel setup.
            shutter.disarm_triggers()  # Establish Manual/Inactive before opening any.

        for number, shutter in enumerate(hub.controllers, start=1):
            try:
                ready = shutter.get_operating_status()
                if not ready.is_closed_manual or not ready.key_enabled:
                    raise RuntimeError("Verify Closed/Manual and key before Open")
                shutter.open_shutter()
                print(f"Opening shutter {number}:", shutter.get_operating_status().shutter_state)
                sleep(args.open_seconds)
            finally:
                # Close this shutter before the loop can open the next one.
                shutter.close_shutter()
                print(f"Closing shutter {number}:", shutter.get_operating_status().shutter_state)
        # ExitStack closes verified targets and releases every handle despite
        # callback failures. A failed identity never authorizes an output command.


if __name__ == "__main__":
    main()
