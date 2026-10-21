"""Lesson 1: find the USB serial numbers of real KSC101 controllers.

Run from the repository root, after discovery has been approved:
    uv run --locked python docs/examples/01_discover.py

Discovery talks to Kinesis/USB. It does not connect to a shutter or command its
output. Match each printed serial to a physical controller label before lesson 2.
"""

import argparse

from thorlabs_shutter_control import KCubeShutter


def main():
    # --help exits here without loading Kinesis or accessing USB.
    argparse.ArgumentParser(description=__doc__).parse_args()

    # Constructing the Python object does not communicate with hardware.
    shutter = KCubeShutter()

    # This is the first hardware operation: ask Kinesis for type-68 USB devices.
    serials = shutter.discover()
    if not serials:
        print("No KSC101 found. Check the approved power/USB setup; do not continue.")
        return

    print("KSC101 serial numbers:")
    for serial in serials:
        print(f"  {serial}")
    print("Record which physical shutter belongs to each serial.")
    # No device handle was opened, so there is nothing to disconnect.


if __name__ == "__main__":
    main()
