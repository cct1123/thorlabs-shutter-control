"""Lesson 5: configure TRIG1 as an active-high input and arm a real shutter.

Run only after TTL wiring, source levels, timing and actuation are approved:
    uv run --locked python docs/examples/05_ttl_control.py SERIAL --armed-seconds SECONDS

This changes settings: TRIG1=input/high, TRIG2=disabled/high. Before running,
verify that TRIG1 is connected to the approved TTL source at its inactive LOW
level. An active HIGH input can open immediately on Arm. A disconnected input
is documented LOW; changing to active-low can open with no cable.
"""

import argparse
import math
from contextlib import ExitStack
from time import sleep

from thorlabs_shutter_control import KCubeShutter, TriggerConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial", help="Actual serial recorded in lesson 1")
    parser.add_argument(
        "--armed-seconds",
        type=float,
        required=True,
        help="Approved armed window in seconds; allow for command latency",
    )
    args = parser.parse_args()
    if not math.isfinite(args.armed_seconds) or args.armed_seconds <= 0:
        parser.error("--armed-seconds must be a finite positive number")

    shutter = KCubeShutter(args.serial)
    with ExitStack() as cleanup:
        cleanup.callback(shutter.disconnect, close_shutter=False)
        shutter.connect()
        cleanup.callback(shutter.disarm_triggers)  # Only after verified Connect.
        print("Identity:", shutter.identify_device())
        shutter.disarm_triggers()  # Apply requires reported Closed/Inactive/Manual.

        # 'input' receives the external signal. 'high' means HIGH requests Open.
        # Disable TRIG2 here; this lesson does not use it as an input or output.
        config = TriggerConfig(
            trig1_mode="input",
            trig1_polarity="high",
            trig2_mode="disabled",
            trig2_polarity="high",
        )
        shutter.configure_triggers(config)  # Apply settings; this does not arm.
        print("Device settings readback:", shutter.get_trigger_config())

        # Arm selects Triggered and primes Active. The signal now controls position.
        ready = shutter.get_status()
        if not ready.is_closed_manual or not ready.key_enabled:
            raise RuntimeError("Verify Closed/Manual and key before Arm")
        shutter.arm_triggers()
        status = shutter.get_status()
        print("Armed:", status.ttl_armed, "Reported position:", status.shutter_state)
        # Armed=True can coexist with Closed when the signal is inactive.
        # This program does not generate pulses or measure input voltage.
        sleep(args.armed_seconds)

        shutter.disarm_triggers()
        print("Disarm / Close:", shutter.get_operating_status().shutter_state)
        # ExitStack attempts Disarm/Close and release on errors or Ctrl+C,
        # preserving chained failures without writing through an unverified target.

    print("Disarmed and released with controller feedback; verify physical closure.")
    # Port settings remain configured. No explicit persist/EEPROM command is made.


if __name__ == "__main__":
    main()
