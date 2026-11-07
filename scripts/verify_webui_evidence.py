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
    sample = json.loads(raw) if isinstance(raw, str) else raw
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


def inspect_legacy(path, record):
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


def inspect_modern(path, record):
    """Validate saved real-UI evidence; missing physical tests cannot become PASS."""
    events = record["events"]
    names = [event["action"] for event in events]

    def event(name, *, latest=False):
        matches = [item for item in events if item["action"] == name]
        require(bool(matches) and (latest or len(matches) == 1), f"Missing or duplicate {name}")
        return matches[-1]

    connected = event("connect-after-fix")
    check_feedback(connected["sample"], "off")
    settings = event("read-settings-after-fix")
    settings_at = check_feedback(settings["sample"], "off")
    baseline = event("read-settings")["sample"]["cycle_parameters"]
    require(settings["sample"]["cycle_parameters"] == baseline, "Device cycle settings changed")
    polled = event("poll-after-fix")
    require(
        check_feedback(polled["sample"], "off") > settings_at, "Polling did not advance readback"
    )
    require(polled["notice"] == settings["notice"], "Polling erased the operator message")
    before = event("live-readback")
    require(before["notice"] != event("read-settings")["notice"], "Baseline finding absent")

    final = event("final-manual-off", latest=True)
    final_at = check_feedback(final["sample"], "off")
    released = event("released-read", latest=True)["sample"]
    require(
        "Disconnected; no device feedback was requested."
        in event("released-read", latest=True)["notice"],
        "Released Read incorrectly claims device feedback",
    )
    require(
        released["connection"] == "disconnected"
        and released["has_device"] is False
        and released["error"] is None,
        "Final communication release not confirmed",
    )
    require(
        released["feedback"]["electrical_state"] == "unknown",
        "Released UI must not claim live electrical feedback",
    )
    controls = names.count("manual-on") + names.count("timed-pulse")
    require(
        names.count("manual-on") <= 1 and names.count("timed-pulse") <= 1, "Duplicate cycle action"
    )
    require(controls <= 2, "Recorded cycle budget exceeded")
    authority = record.get("authority", {})
    if controls:
        require(authority.get("confirmed") is True, "New physical authority not confirmed")
        require(controls <= authority["max_manual_cycles"], "Approved cycle budget exceeded")
    complete = names.count("manual-on") == names.count("timed-pulse") == 1
    checks = [
        "exact identity/route",
        "real cycle readback unchanged",
        "fresh polling",
        "operator notice retained",
        "final Manual/OFF",
        "released/unknown feedback",
    ]
    if complete:
        on_event, off_event = event("manual-on"), event("manual-off")
        on = check_feedback(on_event["sample"], "on")
        off = check_feedback(off_event["sample"], "off")
        require(0 < (off - on).total_seconds() <= 5, "Manual ON/OFF exceeded the5s window")
        connected_at = check_feedback(connected["sample"], "off")
        require((on - connected_at).total_seconds() >= 2, "Initial OFF rest absent")
        require(on_event["pulse_enabled"] is False, "Timed pulse remained enabled during ON")
        guard = event("active-release-refusal")
        require("Stop / OFF" in guard["notice"], "Active release guard absent")
        require(guard["sample"]["has_device"] is True, "Active Release dropped the owner")
        require(
            guard["sample"]["requested_state"] == "on" and guard["sample"]["error"] is None,
            "Active Release refusal changed the output request or latched a fault",
        )
        pulse = event("timed-pulse")
        click = datetime.fromisoformat(pulse["click_started_at_utc"].replace("Z", "+00:00"))
        require((click - off).total_seconds() >= 2, "OFF rest before timed pulse absent")
        pulse_at = check_feedback(pulse["sample"], "off")
        require(final_at >= pulse_at > off, "Final OFF observation precedes the control sequence")
        after_settings = event("read-settings-after-control")["sample"]
        require(
            after_settings["cycle_parameters"] == baseline,
            "Settings changed during the control sequence",
        )
        require("1-second host hold completed" in pulse["notice"], "Timed hold not completed")
        require(released["requested_state"] == "off", "Final output request was not OFF")
        checks += [
            "visible ON/OFF within5s",
            "pulse disabled during ON",
            "active release refused",
            "second cycle1s host hold",
            "2s OFF rests",
        ]
    return {
        "requirement_id": "REQ-227",
        "result": "PASS selected real WebUI/control evidence consistency"
        if complete
        else "PARTIAL: real read-only checks passed; both control cycles not demonstrated",
        "scope": "Saved observations; no hardware access or independent capture authentication",
        "evidence": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "checks": checks,
        "recorded_cycles": controls,
        "optical_observation": record["optical_observation"],
        "timing_scope": "Controller/host timestamps, not calibrated optical timing",
    }


def inspect(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("requirement_id") == "REQ-227":
        return inspect_modern(path, record)
    return inspect_legacy(path, record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "evidence", nargs="?", type=Path, default=ROOT / "records/webui-final-live.json"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.evidence)
    result = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8", newline="\n")
    print(result, end="")
    return 2 if report["result"].startswith("PARTIAL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
