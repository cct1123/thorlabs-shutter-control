"""Lesson 2: connect to one real controller and read its reported state.

Run after the passive connection stage has been approved:
    uv run --locked python docs/examples/02_connect_and_read_status.py SERIAL

Replace SERIAL with the eight-digit identity you recorded in lesson 1.
This lesson makes no explicit output writes. Its final disconnect deliberately
leaves the existing output/mode unchanged; it does not close an open shutter.
Keep the independent beam block/source disable in place.
"""

import argparse

from thorlabs_shutter_control import KCubeShutter, ShutterError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial", help="Actual KSC101 serial, eight digits beginning with 68")
    args = parser.parse_args()
    shutter = KCubeShutter(args.serial)

    try:
        # Connect starts communication/polling and checks the returned identity.
        # It does not select Manual mode or enable the output.
        shutter.connect()
        print("Identity:", shutter.identify_device())

        status = shutter.get_status()
        if status.error:
            raise ShutterError(status.error)
        print("Connection:", status.connection)
        print("Reported shutter position:", status.shutter_state)
        print("Operating mode / state:", status.operating_mode, "/", status.operating_state)
        print("Key / interlock enabled:", status.key_enabled, "/", status.interlock_enabled)
        print("TTL armed:", status.ttl_armed)
        print("TRIG1/TRIG2 settings:", status.trigger_config)
        # These are controller reports, not independent optical measurements.
    finally:
        # Passive release is intentional in this lesson only. It is NOT a safe
        # shutdown. The later actuation lessons close/disarm before releasing.
        shutter.disconnect(close_shutter=False)


if __name__ == "__main__":
    main()
