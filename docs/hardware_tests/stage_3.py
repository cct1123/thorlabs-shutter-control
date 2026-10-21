"""Prepared first-Close helper. Importing/running this file never accesses hardware.

Use software controllers until a separately reviewed physical launch. The caller
retains the controller, bench record, prior-stage evidence and authority.
"""

import json
import math
import time
from dataclasses import asdict
from datetime import datetime, timezone

from stage_2 import selection_gaps, validate_feedback


def _motion_cycle(record, serial, controller, prior_review, *, stage, open_seconds=None):
    result = {
        "stage": stage,
        "serial": serial,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "status": "BLOCKED",
        "physical_test_status": "UNTESTED",
        "scope": "reported feedback only; independent observations and review required",
    }
    gaps = selection_gaps(record, serial)
    if gaps:
        return dict(result, gaps=gaps)
    if not (
        isinstance(prior_review, dict)
        and prior_review.get("stage") == stage - 1
        and prior_review.get("serial") == serial
        and prior_review.get("physical_test_status") == "PASS"
        and prior_review.get("reviewed") is True
        and isinstance(prior_review.get("evidence"), str)
        and prior_review["evidence"].strip()
    ):
        return dict(result, reason="Reviewed physical prior-stage PASS evidence required")
    if stage == 4:
        if (
            isinstance(open_seconds, bool)
            or not isinstance(open_seconds, (int, float))
            or not math.isfinite(open_seconds)
            or open_seconds <= 0
        ):
            return dict(result, reason="Finite positive approved added Open hold required")
        result["added_open_hold_s"] = open_seconds
    if controller.serial_number not in (None, serial):
        return dict(result, reason="Do not retarget another controller owner")
    initial = controller.get_status()
    if initial.has_device or initial.connection != "disconnected":
        return dict(result, reason="Resolve existing/faulted controller before a new cycle")

    verified = False
    errors = []
    interrupted = None
    phase = "connect"

    def capture(label, status, expected=None):
        result[label] = asdict(status)
        if expected is None:
            validate_feedback(status, serial)
        elif (
            status.connection != "connected"
            or not status.has_device
            or status.serial_number != serial
            or type(status.key_enabled) is not bool
        ):
            raise ValueError(f"{label}: unhealthy/unknown target feedback")
        if (
            expected is not None
            and (status.shutter_state, status.operating_state, status.operating_mode) != expected
        ):
            raise ValueError(f"{label}: expected {expected}")
        return status

    try:
        controller.connect(serial)
        phase = "pre-motion status"
        capture("connected", controller.get_status())
        phase = "identity"
        result["identity"] = controller.identify_device()
        if result["identity"].get("serial_number") != serial:
            raise ValueError("Identity readback does not match selected serial")
        phase = "pre-motion status"
        capture("pre_motion", controller.get_status())
        verified = True
        phase = "initial Disarm / Close"
        controller.disarm_triggers()
        capture(
            "initial_close", controller.get_operating_status(), ("closed", "inactive", "manual")
        )
        if stage == 4:
            phase = "enable channel"
            controller.enable_device()
            phase = "Open"
            ready = controller.get_operating_status()
            if not ready.is_closed_manual or not ready.key_enabled:
                raise ValueError("Open refused: key or baseline not verified")
            controller.open_shutter()
            opened = capture(
                "open", controller.get_operating_status(), ("open", "active", "manual")
            )
            if not opened.key_enabled:
                raise ValueError("Open feedback lacks enabled key")
            phase = "added Open hold"
            time.sleep(open_seconds)
            phase = "Close"
            controller.close_shutter()
            capture("close", controller.get_operating_status(), ("closed", "inactive", "manual"))
        phase = "final feedback"
        capture("final", controller.get_status(), ("closed", "inactive", "manual"))
    except BaseException as exc:
        errors.append(f"{phase}: {type(exc).__name__}: {exc}")
        if not isinstance(exc, Exception):
            interrupted = exc
    finally:
        result["cleanup_close_authorized"] = verified
        try:
            # Never request output through an unverified target's retained handle.
            controller.disconnect(close_shutter=verified)
            result["communication_release"] = "COMPLETED"
        except BaseException as exc:
            errors.append(f"cleanup: {type(exc).__name__}: {exc}")
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


def first_close(record, serial, controller, stage_2_review):
    """One first Close plus guarded Close/release; no Enable or Open command."""
    return _motion_cycle(record, serial, controller, stage_2_review, stage=3)
