"""CLI entry point. Only --list performs SDK discovery without a GUI button click."""

import argparse
import sys

from .controller import KSC101Controller, ShutterError


def main() -> int:
    parser = argparse.ArgumentParser(description="Local KSC101 manual shutter control")
    parser.add_argument("--serial", help="Eight-digit KSC101 serial number; otherwise discover")
    parser.add_argument("--kinesis-dir", help="Kinesis SDK folder (or set KINESIS_DIR)")
    parser.add_argument(
        "--list", action="store_true", help="List USB devices; no connection/actuation"
    )
    parser.add_argument("--port", type=int, default=8050, help="Local GUI port (default: 8050)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    try:
        controller = KSC101Controller(args.serial, kinesis_dir=args.kinesis_dir)
    except ValueError as exc:
        parser.error(str(exc))
    if args.list:
        try:
            serials = controller.discover()
            print("\n".join(serials) if serials else "No KSC101 devices discovered.")
            return 0
        except ShutterError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    from .gui import create_app

    app = create_app(controller)
    result = 0
    try:
        # One process, one controller, one operator. Reloaders must never duplicate ownership.
        app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False, threaded=False)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            controller.safe_shutdown()
        except ShutterError as exc:
            print(str(exc), file=sys.stderr)
            result = 1
    return result


if __name__ == "__main__":
    raise SystemExit(main())
