"""Real GUI callback lifecycle checks; no automatic server or device launch."""

import math
import time


def callback_payload(dependency, action, serial, counters):
    """Construct Dash's documented callback request from actual dependencies."""
    changed = action + (".n_intervals" if action == "refresh" else ".n_clicks")
    counters[changed] = counters.get(changed, 0) + 1
    outputs = []
    for output in dependency["output"].strip(".").split("..."):
        component, prop = output.rsplit(".", 1)
        outputs.append({"id": component, "property": prop})
    states = []
    for state in dependency["state"]:
        name = state["id"]
        if name.startswith("serial-"):
            value = serial if name == "serial-1" else None
        else:
            value = "high" if "polarity" in name else ("input" if "trig1" in name else "output")
        states.append(dict(state, value=value))
    return {
        "output": dependency["output"],
        "outputs": outputs,
        "inputs": [
            dict(item, value=counters.get(item["id"] + "." + item["property"], 0))
            for item in dependency["inputs"]
        ],
        "state": states,
        "changedPropIds": [changed],
    }


def closed_gui_lifecycle(call, serial):
    """Exercise passive startup/unused slots, discovery, Close/release/reconnect.

    Returns with slot1 verified reported Closed and connected, so the caller
    must deliver one normal terminal Ctrl+C and verify release/reconnect.
    Open tests are never forced through disabled controls. No physical PASS.
    """
    result = {"stage": 6, "serial": serial, "physical_status": "UNTESTED", "steps": []}

    def check(action, expected):
        response = call(action)
        result["steps"].append({"action": action, "response": response})
        for component, properties in expected.items():
            for key, value in properties.items():
                if response.get(component, {}).get(key) != value:
                    raise ValueError(f"{action}: unexpected {component}.{key}")
        return response

    disconnected = {f"connection-{i}": {"children": "Disconnected"} for i in (1, 2, 3)}
    first = check("refresh", disconnected)
    if any(first[f"open-{i}"]["disabled"] is not True for i in (1, 2, 3)):
        raise ValueError("Startup Open must be disabled")
    check("discover", disconnected)
    current = check(
        "connect-1",
        {
            "connection-1": {"children": "Connected"},
            "connection-2": {"children": "Disconnected"},
            "connection-3": {"children": "Disconnected"},
        },
    )
    if serial not in current["identity-1"]["children"]:
        raise ValueError("GUI selected identity mismatch")
    result["open_disabled"] = current["open-1"]["disabled"]
    result["safeguards"] = current["safeguards-1"]["children"]
    closed = {"shutter-state-1": {"children": "Closed"}}
    check("close-1", closed)
    for _ in range(3):
        check("refresh", closed)
    check("disconnect-1", {"connection-1": {"children": "Disconnected"}})
    check("connect-1", {"connection-1": {"children": "Connected"}})
    check("close-1", closed)
    result["closed_lifecycle"] = "READBACK_PASS"
    result["open_subcases"] = "BLOCKED" if result["open_disabled"] else "NOT_EXECUTED"
    result["sigint_subcase"] = "PENDING_CALLER_INTERRUPT_FROM_CLOSED"
    return result


def open_close_gui(call, *, open_seconds):
    """Test enabled Open, hold and Close; any failure attempts global shutdown.

    Caller owns a verified, connected, Closed slot1; this function neither
    confirms interlock nor starts a server. Never forge a disabled Open action.
    """
    if (
        isinstance(open_seconds, bool)
        or not isinstance(open_seconds, (int, float))
        or not math.isfinite(open_seconds)
        or open_seconds <= 0
    ):
        raise ValueError("Finite positive approved Open hold required")
    result = {"physical_status": "UNTESTED", "steps": []}
    try:
        ready = call("refresh")
        result["steps"].append({"action": "refresh", "response": ready})
        if (
            ready["connection-1"]["children"] != "Connected"
            or ready["shutter-state-1"]["children"] != "Closed"
            or ready["open-1"]["disabled"] is not False
        ):
            raise ValueError("GUI Open is not ready")
        opened = call("open-1")
        result["steps"].append({"action": "open-1", "response": opened})
        if opened["shutter-state-1"]["children"] != "Open":
            raise ValueError("GUI did not report Open")
        start = time.monotonic()
        time.sleep(open_seconds)
        result["added_open_hold_s"] = time.monotonic() - start
        closed = call("close-1")
        result["steps"].append({"action": "close-1", "response": closed})
        if closed["shutter-state-1"]["children"] != "Closed":
            raise ValueError("GUI did not report Closed")
        for _ in range(3):
            refreshed = call("refresh")
            result["steps"].append({"action": "refresh", "response": refreshed})
            if refreshed["shutter-state-1"]["children"] != "Closed":
                raise ValueError("Refresh changed Closed feedback")
        result["status"] = "READBACK_PASS"
        return result
    except BaseException as exc:
        try:
            call("shutdown-all")
        except BaseException as cleanup:
            exc.add_note(f"GUI shutdown also failed: {cleanup}")
        raise
