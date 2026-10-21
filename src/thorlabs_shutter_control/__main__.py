"""Launch the passive GUI using project settings; no command-line options."""

import sys

from . import config
from .controller import ShutterError, ShutterHub


def main() -> int:
    try:
        if type(config.PORT) is not int or not 1 <= config.PORT <= 65535:
            raise ValueError("PORT must be an integer between 1 and 65535.")
        hub = ShutterHub(config.SERIAL_NUMBERS, kinesis_dir=config.KINESIS_DIR, slots=config.SLOTS)
    except ValueError as exc:
        print(f"Invalid project config: {exc}", file=sys.stderr)
        return 1

    from .gui import create_app

    result = 0
    try:
        app = create_app(hub)
        # One process/operator owns all slots. Reloaders must not duplicate handles.
        app.run(host="127.0.0.1", port=config.PORT, debug=False, use_reloader=False, threaded=False)
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
