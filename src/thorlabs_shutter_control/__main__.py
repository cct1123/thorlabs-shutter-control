"""Explicit configured-target CLI. No automatic hardware discovery or startup I/O."""

import argparse
import json
import sys
import time
from dataclasses import asdict

from . import ShutterHub, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Direct KSC101 owner; optical state is independent"
    )
    parser.add_argument(
        "--config",
        help="TOML path (GUI: config/shutter.ethernet.toml; other commands: shutters.local.toml)",
    )
    parser.add_argument("--target", help="Exact configured logical name")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check-config", "identify", "status", "safe-off"):
        commands.add_parser(command)
    gui = commands.add_parser("gui", help="Open the localhost WebUI without connecting")
    gui.add_argument("--port", type=int, default=9860, help="Localhost HTTP port (default: 9860)")
    discover = commands.add_parser(
        "discover", help="Explicit informational inventory; never opens or selects a controller"
    )
    discover.add_argument(
        "--vcp", action="store_true", help="List COM ports instead of D2XX devices"
    )
    manual = commands.add_parser("manual", help="Select Manual; stays selected at power-up")
    manual.add_argument(
        "--source-inhibited",
        action="store_true",
        help="Compatibility option; no longer required for Manual selection",
    )
    pulse = commands.add_parser("pulse", help="Bounded hold on a continuous-duty qualified load")
    pulse.add_argument("--seconds", required=True, type=float)
    args = parser.parse_args(argv)
    hub = None
    original = None
    try:
        if args.command == "discover":
            from .transport import list_d2xx_devices, list_vcp_ports

            rows = list_vcp_ports() if args.vcp else list_d2xx_devices()
            print("\n".join(rows) if rows else "(none)")
            print(
                "Discovery is informational only; configure an explicit serial and route. "
                "Controller model, serial and firmware are verified on connection before control.",
                file=sys.stderr,
            )
            return 0
        config_path = args.config
        if config_path is None:
            config_path = (
                "config/shutter.ethernet.toml" if args.command == "gui" else "shutters.local.toml"
            )
        configs = load_config(config_path)
        if args.command == "check-config":
            print(json.dumps([asdict(c) for c in configs], indent=2))
            return 0
        hub = ShutterHub(configs)
        if args.command == "gui":
            from .gui import run

            gui_hub, hub = hub, None  # GUI owns both output cleanup and communication release.
            run(gui_hub, port=args.port)
            return 0
        if args.target is None:
            raise ValueError("--target is required; no first-device selection")
        # Validate public pulse arguments before opening a transport.
        if args.command == "pulse":
            hub.validate_pulse(args.target, args.seconds)
        connection = hub.connect(args.target)
        action = {
            "status": hub.get_status,
            "safe-off": hub.safe_state,
        }
        if args.command == "identify":
            result = connection.identity
        elif args.command == "pulse":
            hub.safe_state(args.target)  # Explicit OFF preparation is part of this output command.
            selected = next(c for c in configs if c.name == args.target)
            time.sleep(selected.policy.min_off_s)
            result = hub.pulse(args.target, args.seconds)
        elif args.command == "manual":
            result = hub.set_operating_mode(args.target, "manual")
        else:
            result = action[args.command](args.target)
        print(json.dumps(asdict(result), indent=2))
    except (Exception, KeyboardInterrupt) as exc:
        original = exc
        print(f"Unconfirmed: {str(exc) or type(exc).__name__}", file=sys.stderr)
        for note in getattr(exc, "__notes__", []):
            print(note, file=sys.stderr)
    finally:
        if hub is not None:
            try:
                hub.close()
            except BaseException as exc:
                print(
                    f"Communication release incomplete: {str(exc) or type(exc).__name__}",
                    file=sys.stderr,
                )
                original = original or exc
    return 1 if original else 0


if __name__ == "__main__":
    raise SystemExit(main())
