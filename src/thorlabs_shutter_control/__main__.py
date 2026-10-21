"""Launch the passive GUI using project settings; no command-line options."""

import sys
from threading import Event

from werkzeug.serving import make_server

from . import config
from .controller import ShutterError, ShutterHub


def main() -> int:
    try:
        if type(config.PORT) is not int or not 1 <= config.PORT <= 65535:
            raise ValueError("PORT must be an integer between 1 and 65535.")
        hub = ShutterHub(
            config.SERIAL_NUMBERS,
            kinesis_dir=config.KINESIS_DIR,
            slots=config.SLOTS,
            ethernet_endpoints=config.ETHERNET_ENDPOINTS,
        )
    except ValueError as exc:
        print(f"Invalid project config: {exc}", file=sys.stderr)
        return 1

    from .gui import create_app

    result = 0
    try:
        stop_requested = Event()
        app = create_app(hub, on_shutdown=stop_requested.set)
        # Handle one request at a time, finishing the shutdown response before exit.
        with make_server("127.0.0.1", config.PORT, app.server, threaded=False) as server:
            server.timeout = 0.5
            print(f"Shutter control: http://127.0.0.1:{server.server_port}/", flush=True)
            while not stop_requested.is_set():
                server.handle_request()
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
