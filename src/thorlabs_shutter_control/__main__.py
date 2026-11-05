"""Explicit configured-target CLI. No automatic hardware discovery or startup I/O."""

import argparse
import json
import sys
from dataclasses import asdict

from . import ShutterHub, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Direct KSC101 owner; optical state is independent"
    )
    parser.add_argument("--config", default="shutters.local.toml")
    parser.add_argument("--target", help="Exact configured logical name")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("check-config", "identify", "status", "safe-off", "gui"):
        commands.add_parser(command)
    discover = commands.add_parser(
        "discover", help="Explicit informational inventory; never opens or selects a controller"
    )
    discover.add_argument(
        "--vcp", action="store_true", help="List COM ports instead of D2XX devices"
    )
    commands.add_parser("manual", help="Select Manual; changed modes are remembered at power-up")
    for name in ("keh3-analyze", "keh3-probe"):
        sub = commands.add_parser(
            name, help="Candidate identity diagnostics; never qualifies a route"
        )
        sub.add_argument("--destination", type=lambda value: int(value, 0), required=True)
        if name == "keh3-analyze":
            sub.add_argument(
                "--capture", required=True, help="Raw binary RX capture, at most 4096 bytes"
            )
        else:
            sub.add_argument(
                "--query-authorized",
                action="store_true",
                help="Operator confirms a bounded identity-query bench authorization",
            )
    pulse = commands.add_parser("pulse", help="Bounded hold on a continuous-duty qualified load")
    pulse.add_argument("--seconds", required=True, type=float)
    args = parser.parse_args(argv)
    hub = None
    original = None
    try:
        if args.command == "discover":
            from .discovery import list_d2xx_devices, list_vcp_ports

            rows = list_vcp_ports() if args.vcp else list_d2xx_devices()
            print("\n".join(rows) if rows else "(none)")
            print(
                "Discovery is informational only; configure an explicit serial and route. "
                "Controller model, serial and firmware are verified on connection before control.",
                file=sys.stderr,
            )
            return 0
        configs = load_config(args.config)
        if args.command in ("keh3-analyze", "keh3-probe"):
            from pathlib import Path

            from .keh3 import CAPTURE_LIMIT, KEH3Probe, analyze_capture

            selected = next((c for c in configs if c.name == args.target), None)
            if selected is None:
                raise ValueError("--target must name one exact configured KEH3 controller")
            if args.command == "keh3-analyze":
                with Path(args.capture).open("rb") as stream:
                    raw = stream.read(CAPTURE_LIMIT + 1)
                report = analyze_capture(selected, raw, destination=args.destination)
            else:
                report = KEH3Probe(
                    selected, destination=args.destination, authorized=args.query_authorized
                ).run()
            print(json.dumps(asdict(report), indent=2))
            return 0 if report.verdict == "candidate-controller-match-hub-unverified" else 2
        if args.command == "check-config":
            print(json.dumps([asdict(c) for c in configs], indent=2))
            return 0
        hub = ShutterHub(configs)
        if args.command == "gui":
            from .gui import run

            gui_hub, hub = hub, None  # GUI owns both output cleanup and communication release.
            run(gui_hub)
            return 0
        if args.target is None:
            raise ValueError("--target is required; no first-device selection")
        # Validate public pulse arguments before opening a transport.
        if args.command == "pulse":
            hub.validate_pulse(args.target, args.seconds)
        hub.connect(args.target)
        action = {
            "identify": hub.identify_device,
            "status": hub.get_status,
            "safe-off": hub.safe_state,
            "manual": hub.set_manual_mode,
        }
        result = (
            hub.pulse(args.target, args.seconds)
            if args.command == "pulse"
            else (action[args.command](args.target))
        )
        print(json.dumps(asdict(result), indent=2))
    except (Exception, KeyboardInterrupt) as exc:
        original = exc
        print(f"Unconfirmed: {exc}", file=sys.stderr)
        for note in getattr(exc, "__notes__", []):
            print(note, file=sys.stderr)
    finally:
        if hub is not None:
            try:
                hub.close()
            except BaseException as exc:
                print(f"Communication release incomplete: {exc}", file=sys.stderr)
                original = original or exc
    return 1 if original else 0


if __name__ == "__main__":
    raise SystemExit(main())
