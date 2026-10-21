"""One explicitly supplied controller's shutdown/reconnect case; no auto launch."""

import math
import time
from dataclasses import asdict
from datetime import datetime, timezone


def shutdown_case(controller, serial, *, open_seconds=None):
    """Connect/Close, optionally Open/hold, then shutdown itself must close.

    No bypass of controller Open guards; no prompt or test retry. The caller
    retains the object and must separately authorize hardware and hold limits.
    Successful return is reported-data evidence, not independent blade proof.
    """
    result = {
        "stage": 5,
        "serial": serial,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "case": "closed_shutdown" if open_seconds is None else "open_shutdown",
        "physical_status": "UNTESTED",
        "errors": [],
        "status": "BLOCKED",
    }
    if controller.serial_number not in (None, serial):
        return dict(result, reason="Controller belongs to another selected serial")
    if open_seconds is not None and (
        isinstance(open_seconds, bool)
        or not isinstance(open_seconds, (int, float))
        or not math.isfinite(open_seconds)
        or open_seconds <= 0
    ):
        return dict(result, reason="Finite positive approved Open hold required")
    before = controller.get_status()
    if before.has_device or before.connection != "disconnected":
        return dict(result, reason="Resolve retained/faulted owner before this case")
    verified = False
    interrupted = None
    phase = "connect"
    start = time.monotonic()
    try:
        status = controller.connect(serial)
        result["connected"] = asdict(status)
        phase = "identity/status"
        result["identity"] = controller.identify_device()
        status = controller.get_status()
        if (
            result["identity"].get("serial_number") != serial
            or status.serial_number != serial
            or status.connection != "connected"
            or not status.has_device
            or status.shutter_state not in ("open", "closed")
            or status.operating_state not in ("active", "inactive")
            or status.operating_mode not in ("manual", "single", "auto", "triggered")
        ):
            raise ValueError("Target/status not verified")
        verified = True
        phase = "initial Close"
        closed = controller.close_shutter()
        result["initial_close"] = asdict(closed)
        if (
            closed.connection,
            closed.shutter_state,
            closed.operating_state,
            closed.operating_mode,
        ) != ("connected", "closed", "inactive", "manual"):
            raise ValueError("Initial Closed/Inactive/Manual not verified")
        if open_seconds is not None:
            phase = "Open"
            result["open"] = asdict(controller.open_shutter())
            if (
                result["open"]["connection"],
                result["open"]["shutter_state"],
                result["open"]["operating_state"],
                result["open"]["operating_mode"],
            ) != ("connected", "open", "active", "manual"):
                raise ValueError("Open feedback not verified")
            result["added_open_hold_s"] = open_seconds
            phase = "Open hold"
            time.sleep(open_seconds)
        # Do not explicitly Close here: finally must test shutdown from Open.
    except BaseException as exc:
        result["errors"].append(f"{phase}: {type(exc).__name__}: {exc}")
        if not isinstance(exc, Exception):
            interrupted = exc
    finally:
        release_start = time.monotonic()
        try:
            if verified:
                controller.safe_shutdown()
                result["cleanup_method"] = "safe_shutdown"
            else:
                controller.disconnect(close_shutter=False)
                result["cleanup_method"] = "passive_release"
            released = controller.get_status()
            if released.has_device or released.connection != "disconnected":
                raise ValueError("Shutdown did not return disconnected/no handle")
            result["release"] = "COMPLETED"
        except BaseException as exc:
            result["errors"].append(f"shutdown/release: {type(exc).__name__}: {exc}")
            result["release"] = "UNCONFIRMED"
            if interrupted is None and not isinstance(exc, Exception):
                interrupted = exc
        result["shutdown_call_s"] = time.monotonic() - release_start
        result["elapsed_s"] = time.monotonic() - start
    result["status"] = "ERROR" if result["errors"] else "READBACK_PASS"
    result["retain_controller_for_diagnosis"] = bool(result["errors"])
    if interrupted is not None:
        interrupted.add_note(str(result))
        raise interrupted
    return result
