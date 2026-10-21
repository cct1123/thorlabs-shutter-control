"""CLI entry point. Only --list performs SDK discovery without a GUI button click."""

import argparse
import sys

from .controller import ShutterError, ShutterHub


def main() -> int:
    parser = argparse.ArgumentParser(description="Local control of KSC101 shutters")
    parser.add_argument(
        "--serial",
        action="append",
        default=[],
        help="Preselect a serial; repeat for distinct devices in panel order",
    )
    parser.add_argument(
        "--slots", type=int, help="Number of panels (default: at least 3, growing to fit serials)"
    )
    parser.add_argument("--kinesis-dir", help="Kinesis SDK folder (or set KINESIS_DIR)")
    parser.add_argument(
        "--verified-interlock",
        action="append",
        default=[],
        metavar="SERIAL",
        help="Confirm normal interlock/protection for this preselected serial, this session only",
    )
    parser.add_argument(
        "--list", action="store_true", help="List USB devices; no connection/actuation"
    )
    parser.add_argument("--port", type=int, default=8050, help="Local GUI port (default: 8050)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    try:
        hub = ShutterHub(args.serial, kinesis_dir=args.kinesis_dir, slots=args.slots)
        for serial in args.verified_interlock:
            if serial not in args.serial:
                raise ValueError("--verified-interlock requires the same explicit --serial.")
            next(c for c in hub.controllers if c.serial_number == serial).confirm_interlock(serial)
    except ValueError as exc:
        parser.error(str(exc))
    if args.list:
        try:
            serials = hub.discover()
            print("\n".join(serials) if serials else "No KSC101 devices discovered.")
            return 0
        except ShutterError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    from .gui import create_app

    result = 0
    try:
        app = create_app(hub)
        # One process/operator owns all slots. Reloaders must not duplicate handles.
        app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False, threaded=False)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            hub.safe_shutdown()
        except ShutterError as exc:
            print(str(exc), file=sys.stderr)
            result = 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
