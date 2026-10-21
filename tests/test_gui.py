from dataclasses import replace

import pytest

from thorlabs_shutter_control import KCubeShutter, ShutterHub
from thorlabs_shutter_control.gui import create_app


def invoke(app, action, *, serial=None, serials=None, clicks=1, ttl=None):
    key, callback = next(iter(app.callback_map.items()))
    outputs = [
        {"id": item.component_id, "property": item.component_property}
        for item in callback["output"]
    ]
    inputs = [dict(item, value=clicks) for item in callback["inputs"]]
    selected = iter(serials if serials is not None else [serial])
    states = []
    for item in callback["state"]:
        name = item["id"]
        if name == "serial" or name.startswith("serial-"):
            value = next(selected)
        else:
            value = (ttl or {}).get(
                name, "high" if "polarity" in name else ("input" if "trig1" in name else "output")
            )
        states.append(dict(item, value=value))
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": key,
            "outputs": outputs,
            "inputs": inputs,
            "state": states,
            "changedPropIds": [f"{action}.{'n_intervals' if action == 'refresh' else 'n_clicks'}"],
        },
    )
    assert response.status_code == 200, response.data
    return response.get_json()["response"]


def test_gui_runs_entire_manual_lifecycle_through_controller(rig):
    app = create_app(rig.controller)
    discovered = invoke(app, "discover")
    assert discovered["serial"]["options"] == ["68000001"]
    assert invoke(app, "connect")["connection"]["children"] == "Connected"
    assert invoke(app, "open")["shutter-state"]["children"] == "Open"
    commands_before = [c for c in rig.device.calls if c[0] == "set_state"]
    invoke(app, "refresh", clicks=20)  # Old click counts must never replay an Open command.
    assert [c for c in rig.device.calls if c[0] == "set_state"] == commands_before
    assert invoke(app, "close")["shutter-state"]["children"] == "Closed"
    assert invoke(app, "disconnect")["connection"]["children"] == "Disconnected"


def test_gui_reports_fault_and_allows_cleanup_and_reconnect(rig):
    app = create_app(rig.controller)
    invoke(app, "connect")
    rig.device.CommsStatus = "Timeout"
    result = invoke(app, "refresh")
    assert result["shutter-state"]["children"] == "Unknown"
    assert "Timeout" in result["message"]["children"]
    assert result["open"]["disabled"] is True
    assert result["close"]["disabled"] is False
    result = invoke(app, "disconnect")
    assert result["connect"]["disabled"] is False
    rig.device.CommsStatus = "OK"
    assert invoke(app, "connect")["connection"]["children"] == "Connected"


@pytest.mark.parametrize("feedback", [None, False, True])
def test_interlock_is_display_only_and_users_manage_it_externally(rig, monkeypatch, feedback):
    read_status = rig.controller._read_status
    monkeypatch.setattr(
        rig.controller,
        "_read_status",
        lambda **kwargs: replace(read_status(**kwargs), interlock_enabled=feedback),
    )
    app = create_app(rig.controller)
    result = invoke(app, "connect")
    assert result["connection"]["children"] == "Connected"
    display = {None: "unknown", False: "not enabled", True: "enabled"}[feedback]
    assert f"Interlock: {display}" in result["safeguards"]["children"]
    assert result["open"]["disabled"] is False
    assert result["arm-ttl"]["disabled"] is False
    assert "Users manage the physical interlock" in result["control-hint"]["children"]
    assert not any(
        c[0] in {"enable", "set_state", "set_mode", "set_triggers"} for c in rig.device.calls
    )
    assert invoke(app, "open")["shutter-state"]["children"] == "Open"
    invoke(app, "close")
    assert "arm command sent" in invoke(app, "arm-ttl")["message"]["children"]
    rig.controller.safe_shutdown()


def three_slot_app(rig):
    rig.serials[:] = list(rig.devices)
    hub = ShutterHub(controllers=[KCubeShutter(timeout=0.5) for _ in range(3)])
    return create_app(hub), hub


def test_gui_duplicate_selection_does_not_reconnect_an_owned_cube(rig):
    app, _ = three_slot_app(rig)
    serials = ["68000001", "68000001", "68000003"]
    invoke(app, "connect-1", serials=serials)
    result = invoke(app, "connect-2", serials=serials)
    assert "already owned" in result["message-2"]["children"]
    assert result["connection-1"]["children"] == "Connected"
    assert result["connection-2"]["children"] == "Disconnected"
    assert [call for call in rig.device.calls if call[0] == "connect"] == [("connect", "68000001")]


def test_shutdown_without_handles_never_claims_verified_closure(rig):
    app, _ = three_slot_app(rig)
    serials = list(rig.devices)
    result = invoke(app, "shutdown-all", serials=serials)
    assert "closure" not in result["hub-message"]["children"]
    assert "message-1" not in result
    invoke(app, "connect-1", serials=serials)
    invoke(app, "open-1", serials=serials)
    rig.device.fail.add("set_state")
    result = invoke(app, "shutdown-all", serials=serials)
    assert result["connection-1"]["children"] == "Fault"
    assert not rig.device.IsConnected
    result = invoke(app, "shutdown-all", serials=serials)
    assert "closure" not in result["hub-message"]["children"]
    assert "unverified" in result["message-1"]["children"]
    assert result["shutter-state-1"]["children"] == "Unknown"


def test_ttl_drafts_apply_readback_and_arming_are_independent_per_panel(rig):
    app, hub = three_slot_app(rig)
    serials = list(rig.devices)
    for index in range(1, 4):
        invoke(app, f"connect-{index}", serials=serials)
    ttl = {"trig1-mode-2": "disabled", "trig2-mode-2": "input", "trig2-polarity-2": "low"}
    result = invoke(app, "refresh", serials=serials, ttl=ttl)
    assert "TRIG2 output/high" in result["ttl-status-2"]["children"]
    assert "trig2-mode-2" not in result  # Refresh preserves unapplied draft edits.
    assert not any(c[0] == "set_triggers" for d in rig.devices.values() for c in d.calls)
    result = invoke(app, "apply-ttl-2", serials=serials, ttl=ttl)
    assert "TRIG2 input/low" in result["ttl-status-2"]["children"]
    assert hub.controllers[1].get_status().ttl_armed is False
    assert all(hub.controllers[i].get_trigger_config().trig2_mode == "output" for i in (0, 2))
    result = invoke(app, "read-ttl-2", serials=serials)
    assert result["trig1-mode-2"]["value"] == "disabled"
    assert result["trig2-mode-2"]["value"] == "input"
    assert result["trig2-polarity-2"]["value"] == "low"
    result = invoke(app, "arm-ttl-2", serials=serials)
    assert "Armed" in result["ttl-status-2"]["children"]
    assert result["shutter-state-2"]["children"] == "Open"  # LOW input, active-low.
    assert result["open-2"]["disabled"] is True
    assert result["apply-ttl-2"]["disabled"] is True
    assert result["disarm-ttl-2"]["disabled"] is False
    assert all(hub.controllers[i].get_status().shutter_state == "closed" for i in (0, 2))
    before = {s: len(d.calls) for s, d in rig.devices.items()}
    invoke(app, "refresh", serials=serials, clicks=40)
    assert not any(
        c[0] in {"set_triggers", "set_state", "set_mode", "enable"}
        for s, d in rig.devices.items()
        for c in d.calls[before[s] :]
    )
    invoke(app, "disarm-ttl-2", serials=serials)
    assert hub.controllers[1].get_status().ttl_armed is False
    assert rig.devices[serials[1]].state == "Closed"
    invoke(app, "shutdown-all", serials=serials)
    assert all(not d.IsConnected for d in rig.devices.values())


def test_open_disabled_reason_distinguishes_key_and_trigger_mode(rig):
    app = create_app(rig.controller)
    invoke(app, "connect")
    rig.device.Status.KeyEnabled = False
    keyed = invoke(app, "refresh")
    assert keyed["open"]["disabled"] and "key" in keyed["control-hint"]["children"]
    rig.device.Status.KeyEnabled = True
    rig.device.interlock = False
    interlock = invoke(app, "refresh")
    assert interlock["open"]["disabled"] is False
    assert "Users manage the physical interlock" in interlock["control-hint"]["children"]
    rig.device.mode = "Triggered"
    triggered = invoke(app, "refresh")
    assert triggered["open"]["disabled"]
    assert "Disarm / Close" in triggered["control-hint"]["children"]
    rig.controller.safe_shutdown()


@pytest.mark.parametrize("count", [3])
def test_manual_actions_reuse_feedback_without_reading_other_panels(rig, count):
    from thorlabs_shutter_control import controller as driver

    serials = [f"6800{i:04d}" for i in range(1, count + 1)]
    for serial in serials:
        if serial not in rig.devices:
            rig.devices[serial] = type(rig.device)(serial)
    rig.serials[:] = serials
    hub = ShutterHub(serials, slots=count)
    app = create_app(hub)
    suffix = "" if count == 1 else "-1"
    for index in range(count):
        key = "connect" if count == 1 else f"connect-{index + 1}"
        invoke(app, key, serials=serials)
    for action, expected_seconds in (("open", 0.5), ("close", 0.25)):
        for device in rig.devices.values():
            device.calls.clear()
        start = driver.time.monotonic()
        result = invoke(app, action + suffix, serials=serials)
        assert driver.time.monotonic() - start == pytest.approx(expected_seconds)
        assert result["shutter-state" + suffix]["children"] == (
            "Open" if action == "open" else "Closed"
        )
        assert not any(c[0] == "request_triggers" for c in rig.devices[serials[0]].calls)
        assert all(not rig.devices[s].calls for s in serials[1:])
    for device in rig.devices.values():
        device.calls.clear()
    start = driver.time.monotonic()
    invoke(app, "refresh", serials=serials)
    assert driver.time.monotonic() - start == pytest.approx(0.25 * count)
    assert all(
        [c[0] for c in rig.devices[s].calls] == ["status", "request_mode", "request_operation"]
        for s in serials
    )
    hub.safe_shutdown()


def test_cached_ttl_display_cannot_authorize_arm_with_changed_device_settings(rig):
    app = create_app(rig.controller)
    invoke(app, "connect")
    rig.device.trigger_config.Trigger1Mode = "Disabled"
    result = invoke(app, "refresh")
    assert "TRIG1 input/high" in result["ttl-status"]["children"]
    assert "last read" in result["ttl-status"]["children"]
    rig.device.calls.clear()
    result = invoke(app, "arm-ttl")
    assert "configure at least one trigger input" in result["message"]["children"]
    assert "TRIG1 disabled/high" in result["ttl-status"]["children"]
    assert not any(c[0] in {"enable", "set_mode", "set_state"} for c in rig.device.calls)
    rig.controller.safe_shutdown()


@pytest.mark.parametrize("field", ["operation", "state", "mode"])
def test_connect_with_unknown_feedback_keeps_connection_but_disables_open(rig, field):
    setattr(rig.device, field, "0")
    app = create_app(rig.controller)
    result = invoke(app, "connect")
    assert result["connection"]["children"] == "Connected"
    assert result["open"]["disabled"] is True
    assert result["arm-ttl"]["disabled"] is True
    assert "feedback is unknown" in result["control-hint"]["children"]
    assert result["close"]["disabled"] is False
    rig.device.calls.clear()
    result = invoke(app, "open")  # Recheck even when a stale browser submits a click.
    assert "Open refused" in result["message"]["children"]
    assert not any(c[0] in {"enable", "set_mode", "set_state"} for c in rig.device.calls)
    rig.controller.disconnect(close_shutter=False)


def test_arm_button_requires_closed_inactive_manual_feedback(rig):
    app = create_app(rig.controller)
    assert invoke(app, "connect")["arm-ttl"]["disabled"] is False
    result = invoke(app, "open")
    assert result["arm-ttl"]["disabled"] is True
    rig.device.calls.clear()
    result = invoke(app, "arm-ttl")
    assert "Arm refused" in result["message"]["children"]
    assert not any(c[0] in {"enable", "set_mode", "set_state"} for c in rig.device.calls)
    assert invoke(app, "close")["arm-ttl"]["disabled"] is False
    rig.controller.safe_shutdown()


def test_failed_connect_can_retry_without_output_commands(rig):
    app = create_app(rig.controller)
    rig.device.fail.add("connect")
    failed = invoke(app, "connect")
    assert failed["connection"]["children"] == "Fault"
    assert "Connect failed" in failed["message"]["children"]
    assert failed["connect"]["disabled"] is False
    rig.device.fail.clear()
    connected = invoke(app, "connect")
    assert connected["connection"]["children"] == "Connected"
    assert connected["message"]["children"] == "Connected."
    assert not any(
        c[0] in {"enable", "set_mode", "set_state", "set_triggers"} for c in rig.device.calls
    )
    rig.controller.disconnect(close_shutter=False)
