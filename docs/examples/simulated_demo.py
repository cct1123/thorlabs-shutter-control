"""Documentation demo using the existing software-only pytest rig.

Run from a source checkout after `uv sync --locked`. This is not a production
backend or an installed console command. The real SDK loader is replaced for
the entire demo, including cleanup; no Kinesis DLL or USB device is accessed.
"""

import argparse
import runpy
from contextlib import contextmanager
from pathlib import Path

import pytest

from thorlabs_shutter_control import ShutterError
from thorlabs_shutter_control.gui import create_app


@contextmanager
def simulated_controller(*, empty=False):
    """Reuse the test fixture, including its virtual clock and fictional identity."""
    fixture_file = Path(__file__).resolve().parents[2] / "tests" / "conftest.py"
    fixture = runpy.run_path(str(fixture_file))["rig"]
    with pytest.MonkeyPatch.context() as patch:
        # This source-checkout helper deliberately depends on the test fixture.
        rig = fixture.__wrapped__(patch)
        if empty:
            rig.serials.clear()
        try:
            yield rig.controller
        finally:
            rig.controller.safe_shutdown()


def main():
    parser = argparse.ArgumentParser(description="SIMULATION ONLY: documentation demo")
    parser.add_argument("--api", action="store_true", help="Print a simulated API lifecycle")
    parser.add_argument("--empty", action="store_true", help="Simulate zero discovered devices")
    parser.add_argument("--port", type=int, default=8050, help="Local GUI port (default: 8050)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    print("SIMULATION ONLY — test fixture; no hardware access.", flush=True)
    try:
        with simulated_controller(empty=args.empty) as controller:
            if args.api:
                print("Discovered:", controller.discover())
                with controller:
                    print("Identity:", controller.identify_device())
                    print("Initial:", controller.get_status().shutter_state)
                    print("Open:", controller.open_shutter().shutter_state)
                    print("Close:", controller.close_shutter().shutter_state)
                print("After cleanup:", controller.get_status().connection)
            else:
                app = create_app(controller)
                app.run(
                    host="127.0.0.1",
                    port=args.port,
                    debug=False,
                    use_reloader=False,
                    threaded=False,
                )
    except KeyboardInterrupt:
        pass
    except ShutterError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
