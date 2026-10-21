"""Stage-2 passive-cycle preparation and explicitly selected USB connection.

Default/--preflight is offline. --connect requires a complete bench record and
matching discovery. It reads feedback and releases without output commands.
"""

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from stage_0 import DEFAULT_RECORD, record_gaps
from stage_1 import preflight

FEEDBACK_FIELDS = (
    "shutter_state",
    "operating_state",
    "operating_mode",
    "key_enabled",
    "trigger_config",
)


def selection_gaps(record, serial):
    gaps = record_gaps(record)
    if not gaps and serial not in [pair["serial"] for pair in record["pairs"]]:
        gaps.append("Select an explicit serial from the completed bench record")
    return gaps


def validate_feedback(status, serial):
    if status.connection != "connected" or not status.has_device:
        raise ValueError(status.error or "Connection/status feedback is not healthy")
    if status.serial_number != serial:
        raise ValueError("Status identity does not match the selected serial")
    if (
        status.shutter_state not in ("open", "closed")
        or status.operating_state not in ("active", "inactive")
        or status.operating_mode not in ("manual", "single", "auto", "triggered")
        or type(status.key_enabled) is not bool
        or status.trigger_config is None
    ):
        raise ValueError("Unknown/incomplete feedback; review before another cycle or actuation")


def passive_cycle(record, serial, controller, discovery_result):
    """Capture ONE cycle using a caller-retained controller; no motion command.

    A prior discovery result is a prerequisite record, never operating authority. The
    caller must retain this same controller for diagnosis after any failure.
    """
    result = {
        "stage": 2,
        "tests": ["TEST-003 passive lifecycle subcase", "TEST-005 reported feedback only"],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "serial": serial,
        "scope": "controller-reported data; independent physical observation still required",
        "status": "BLOCKED",
        "physical_test_status": "UNTESTED",
    }
    gaps = selection_gaps(record, serial)
    if gaps:
        return dict(result, gaps=gaps)
    expected = sorted(pair["serial"] for pair in record["pairs"])
    if not (
        isinstance(discovery_result, dict)
        and discovery_result.get("status") == "MATCH"
        and discovery_result.get("expected_serials") == expected
        and discovery_result.get("observed_serials") == expected
    ):
        return dict(result, reason="A matching Stage-1 enumeration record is required")
    if controller.serial_number not in (None, serial):
        return dict(
            result, reason="Use the controller for this serial; do not retarget another owner"
        )
    # Refuse an existing/retained handle. Its cleanup remains with its prior owner.
    initial = controller.get_status()
    if initial.has_device or initial.connection != "disconnected":
        return dict(result, reason="Controller is connected/faulted; resolve it before a new cycle")
    errors = []
    interrupted = None
    phase = "connect"
    try:
        controller.connect(serial)
        connected = controller.get_status()
        result["connected_status"] = asdict(connected)
        validate_feedback(connected, serial)
        phase = "identity"
        identity = controller.identify_device()
        result["identity"] = identity
        if identity.get("serial_number") != serial:
            raise ValueError("Identity readback does not match the selected serial")
        phase = "status"
        status = controller.get_status()
        result["reported_status"] = asdict(status)
        validate_feedback(status, serial)
        if any(getattr(connected, field) != getattr(status, field) for field in FEEDBACK_FIELDS):
            raise ValueError("Feedback changed during passive connection; review before repeating")
    except BaseException as exc:
        errors.append(f"{phase}: {type(exc).__name__}: {exc}")
        if not isinstance(exc, Exception):
            interrupted = exc
    finally:
        try:
            controller.disconnect(close_shutter=False)
            result["communication_release"] = "COMPLETED"
        except BaseException as exc:
            errors.append(f"passive release: {type(exc).__name__}: {exc}")
            result["communication_release"] = "UNCONFIRMED"
            if interrupted is None and not isinstance(exc, Exception):
                interrupted = exc
    result.update(
        status="ERROR" if errors else "READBACK_CAPTURED",
        errors=errors,
        retain_controller_for_diagnosis=bool(errors),
    )
    if interrupted is not None:
        interrupted.add_note(json.dumps(result))
        raise interrupted
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD, help="Local bench JSON file")
    parser.add_argument("--serial", help="Explicit serial to validate against the record")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="Offline preparation only (default)")
    mode.add_argument(
        "--connect", action="store_true", help="One passive USB connection/read/release cycle"
    )
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "stage": 2,
                    "status": "ERROR",
                    "connection_access": "NOT_REQUESTED",
                    "error": f"Cannot read bench record: {exc}",
                },
                indent=2,
            )
        )
        return 2
    if args.connect:
        gaps = selection_gaps(record, args.serial)
        if gaps:
            result = {"stage": 2, "status": "INCOMPLETE", "gaps": gaps}
        else:
            from stage_1 import check_discovery

            from thorlabs_shutter_control import KCubeShutter

            controller = KCubeShutter(args.serial)
            discovery = check_discovery(record, controller.discover)
            result = passive_cycle(record, args.serial, controller, discovery)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "READBACK_CAPTURED" else 1
    result = preflight(record)
    result.update(stage=2, serial=args.serial, connection_access="NOT_REQUESTED")
    result["scope"] = "offline record/environment/serial checks; no passive connection executed"
    # preflight already includes record gaps; add selection only for a complete record.
    if not record_gaps(record):
        result["gaps"].extend(selection_gaps(record, args.serial))
    result["status"] = "INCOMPLETE" if result["gaps"] else "OFFLINE_CHECKS_COMPLETE"
    print(json.dumps(result, indent=2))
    return 1 if result["gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
