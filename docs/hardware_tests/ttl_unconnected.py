"""Explicit no-cable TTL checks on one KSC101; imports and --help are offline.

Both IO1/TRIG1 and IO2/TRIG2 must be unconnected. Active-low can OPEN immediately.
Reports controller feedback only, not pin voltage, external edges or blade timing.
Original trigger settings are restored while Closed; no persist/EEPROM call.
"""

import argparse
import json
import math
import time
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from thorlabs_shutter_control import KCubeShutter, ShutterError, TriggerConfig


def snapshot(status):
    return dict(asdict(status), ttl_armed=status.ttl_armed)


def require_closed(status):
    if (
        status.connection != "connected"
        or status.shutter_state != "closed"
        or status.operating_mode != "manual"
        or status.operating_state != "inactive"
    ):
        raise ShutterError(f"Expected Closed/Inactive/Manual: {status}")


def run_matrix(controller, *, armed_seconds, emit, ports=(1, 2)):
    """Caller owns a verified connected target and its final Close/release.

    No retries. Restore original settings even after a failed expectation.
    Window is an added host hold, not a physical exposure bound.
    """
    if (
        isinstance(armed_seconds, bool)
        or not isinstance(armed_seconds, (int, float))
        or not math.isfinite(armed_seconds)
        or not 0 < armed_seconds <= 2
    ):
        raise ValueError("This bench procedure requires an added armed hold in (0, 2] seconds.")
    if (
        not isinstance(ports, (tuple, list))
        or not ports
        or any(type(port) is not int or port not in (1, 2) for port in ports)
        or len(set(ports)) != len(ports)
    ):
        raise ValueError("Select each input port at most once: 1 and/or 2.")
    original = controller.get_trigger_config()
    emit("original_config", asdict(original))

    def restore():
        controller.disarm_triggers()
        require_closed(controller.get_operating_status())
        controller.configure_triggers(original)
        restored = controller.get_trigger_config()
        emit("restored_config", asdict(restored))

    with ExitStack() as cleanup:
        cleanup.callback(restore)
        controller.disarm_triggers()
        require_closed(controller.get_operating_status())
        # Unloaded outputs: settings/readback only. No measured voltage claim.
        for mode, polarity in (("disabled", "high"), ("output", "high"), ("output", "low")):
            config = TriggerConfig(mode, polarity, mode, polarity)
            controller.configure_triggers(config)
            if controller.get_trigger_config() != config:
                raise ShutterError("Configuration readback mismatch")
            require_closed(controller.get_status())
            emit("configuration_pass", asdict(config))

        for port in ports:
            for polarity in ("high", "low"):
                fields = {"trig1_mode": "disabled", "trig2_mode": "disabled"}
                fields.update({f"trig{port}_mode": "input", f"trig{port}_polarity": polarity})
                config = TriggerConfig(**fields)
                controller.configure_triggers(config)
                expected = "closed" if polarity == "high" else "open"
                case = {"port": port, "polarity": polarity, "expected": expected}
                emit("input_start", case)
                try:
                    ready = controller.get_status()
                    if not ready.is_closed_manual or not ready.key_enabled:
                        raise ShutterError("Verify Closed/Manual and key before Arm")
                    controller.arm_triggers()
                    status = controller.get_status()
                    emit("armed_feedback", dict(case, status=snapshot(status)))
                    started = time.monotonic()
                    # Arm feedback can precede the next position update. Allow
                    # one bounded window of reads, without reissuing Arm/Active.
                    while time.monotonic() - started < armed_seconds:
                        if (
                            status.connection != "connected"
                            or status.ttl_armed is not True
                            or status.trigger_config != config
                            or not status.key_enabled
                        ):
                            raise ShutterError(f"Armed readiness changed: {status}")
                        time.sleep(min(0.1, armed_seconds))
                        status = controller.get_status()
                        emit("settling_feedback", dict(case, status=snapshot(status)))
                    if (
                        status.connection != "connected"
                        or status.ttl_armed is not True
                        or status.shutter_state != expected
                        or status.trigger_config != config
                        or not status.key_enabled
                    ):
                        raise ShutterError(f"Disconnected-input expectation failed: {status}")
                    emit(
                        "input_pass",
                        dict(case, elapsed_s=time.monotonic() - started, status=snapshot(status)),
                    )
                finally:
                    controller.disarm_triggers()
                    closed = controller.get_operating_status()
                    emit("disarmed_feedback", dict(case, status=snapshot(closed)))
                    require_closed(closed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial")
    parser.add_argument("--ports-unconnected", action="store_true", required=True)
    parser.add_argument("--armed-seconds", type=float, required=True)
    parser.add_argument("--port", type=int, choices=(1, 2), action="append")
    parser.add_argument("--record", type=Path, required=True, help="New JSON evidence file")
    args = parser.parse_args()
    if not math.isfinite(args.armed_seconds) or not 0 < args.armed_seconds <= 2:
        parser.error("--armed-seconds must be in (0, 2] for this bench procedure")
    if args.record.exists():
        parser.error("Refusing to overwrite an existing evidence file")
    if args.port and len(set(args.port)) != len(args.port):
        parser.error("Do not repeat a port")
    record = {
        "test": "TEST-091",
        "serial": args.serial,
        "ports_unconnected": "human-reported",
        "added_armed_hold_s": args.armed_seconds,
        "ports": args.port or [1, 2],
        "physical_observation": "UNTESTED",
        "external_edges_voltage_timing": "UNTESTED",
        "result": "IN_PROGRESS",
        "events": [],
    }

    def save():
        args.record.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def emit(action, data):
        record["events"].append(
            {"utc": datetime.now(timezone.utc).isoformat(), "action": action, "data": data}
        )
        save()
        print(action, json.dumps(data), flush=True)

    controller = KCubeShutter(args.serial)
    save()  # Persist scope before SDK access.
    try:
        with ExitStack() as cleanup:
            cleanup.callback(controller.disconnect, close_shutter=False)
            status = controller.connect()

            def close_verified():
                controller.close_shutter()
                closed = controller.get_operating_status()
                emit("final_closed", snapshot(closed))
                require_closed(closed)

            cleanup.callback(close_verified)  # Verified identity only.
            emit("connected", dict(identity=controller.identify_device(), status=snapshot(status)))
            run_matrix(
                controller, armed_seconds=args.armed_seconds, emit=emit, ports=args.port or (1, 2)
            )
        record["result"] = "READBACK_PASS"
        return 0
    except BaseException as exc:
        record["result"] = "FAIL"
        record["error"] = repr(exc)
        raise
    finally:
        record["released"] = not controller.get_status().has_device
        save()


if __name__ == "__main__":
    raise SystemExit(main())
