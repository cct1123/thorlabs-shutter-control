"""Check recorded real-browser observations without accessing hardware or simulating it.

Run: uv run --locked python scripts/verify_webui_evidence.py
This checks saved evidence consistency; it does not execute a new live test or
independently authenticate where an observation came from.
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_feedback(raw, state):
    sample = json.loads(raw)
    require(sample["serial_number"] == "68800777", "Wrong configured controller")
    require(sample["endpoint"] == "192.168.1.19:40305", "Wrong Ethernet route")
    require(sample["identity_verified"] is True, "Controller identity unverified")
    identity = sample["identity"]
    require(
        (identity["model"], identity["serial_number"], identity["firmware"], identity["channels"])
        == ("KSC101", "68800777", "1.0.7", 1),
        "Unexpected real controller identity",
    )
    feedback = sample["feedback"]
    require(feedback["operating_mode"] == "manual", "Manual mode not confirmed")
    require(feedback["interlock_enabled"] is True, "Interlock requirement not confirmed")
    require(feedback["electrical_state"] == state, f"Expected electrical {state}")
    require(bool(feedback["status_bits"] & 1) == (state == "on"), "Output bit disagrees")
    require(sample["error"] is None, "Owner reports a fault")
    require(feedback["shutter_state"] == "unknown", "Electrical output inferred optical state")
    require(sample["transition_confirmed"] is False, "Physical transition inferred")
    require(
        sample["feedback_freshness"] == "response_after_request_no_transaction_id",
        "Missing fresh-query provenance",
    )
    return datetime.fromisoformat(feedback["electrical_observed_at"])


def inspect(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    connected = check_feedback(record["connect"], "off")
    sequence = record["sequence"]
    require(
        [entry["action"] for entry in sequence] == ["first-on-after-connect", "off"],
        "Unexpected final user sequence",
    )
    on = check_feedback(sequence[0]["visibleResult"], "on")
    off = check_feedback(sequence[1]["visibleResult"], "off")
    require((on - connected).total_seconds() >= 2, "Configured OFF rest not observed")
    require(off > on, "OFF observation must follow ON")
    guards = record["guard_sequence"]
    check_feedback(guards[0]["visibleResult"], "off")
    require("ON was not dispatched." in guards[1]["visibleResult"], "OFF-rest refusal absent")
    check_feedback(guards[2]["visibleResult"], "off")
    check_feedback(record["final_manual_off"], "off")
    released = json.loads(record["released_status"])
    require(
        released["connection"] == "disconnected"
        and released["has_device"] is False
        and released["requested_state"] == "off"
        and released["error"] is None,
        "Final ownership release or OFF request not confirmed",
    )
    return {
        "requirement_id": "REQ-224",
        "result": "PASS recorded WebUI evidence consistency",
        "scope": "Saved observations only; no new hardware action or simulator",
        "evidence": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "checks": [
            "exact identity/route",
            "fresh OFF",
            "first ON",
            "OFF",
            "rest refusal",
            "release",
        ],
        "optical_observation": record["optical_observation"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "evidence", nargs="?", type=Path, default=ROOT / "records/webui-final-live.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.evidence), indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8", newline="\n")
    print(result, end="")


if __name__ == "__main__":
    main()
