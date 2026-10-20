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


def test_layout_and_first_refresh_are_passive(rig):
    app = create_app(rig.controller)
    client = app.server.test_client()
    assert client.get("/").status_code == 200
    assert client.get("/assets/style.css").status_code == 200
    layout = client.get("/_dash-layout").get_data(as_text=True)
    assert "controller reported" in layout
    result = invoke(app, "refresh")
    assert result["connection"]["children"] == "Disconnected"
    assert result["open"]["disabled"] is True
    assert rig.device.calls == []
    assert rig.manager_calls == []


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


def test_no_device_error_is_visible(rig):
    rig.serials.clear()
    result = invoke(create_app(rig.controller), "connect")
    assert "found 0" in result["message"]["children"]
    assert result["connect"]["disabled"] is False


def three_slot_app(rig):
    rig.serials[:] = list(rig.devices)
    hub = ShutterHub(controllers=[KCubeShutter(timeout=0.5) for _ in range(3)])
    return create_app(hub), hub


def test_default_gui_has_three_passive_panels(rig):
    app = create_app()
    layout = app.server.test_client().get("/_dash-layout").get_data(as_text=True)
    assert all(f"Shutter {index}" in layout for index in range(1, 4))
    result = invoke(app, "refresh", serials=[None] * 3)
    assert all(result[f"connection-{index}"]["children"] == "Disconnected" for index in range(1, 4))
    assert all(device.calls == [] for device in rig.devices.values())
    assert rig.manager_calls == []


def test_discovery_populates_three_slots_without_auto_assigning_duplicate_serial(rig):
    app = create_app()
    result = invoke(app, "discover", serials=[None] * 3)
    for index in range(1, 4):
        assert result[f"serial-{index}"]["options"] == ["68000001"]
        assert result[f"serial-{index}"]["value"] is None
    assert rig.manager_calls == ["discover"]
    result = invoke(app, "connect-1", serials=[None] * 3)
    assert "serial" in result["message-1"]["children"].lower()
    assert not rig.device.IsConnected


def test_three_panel_lifecycle_is_independent(rig):
    app, hub = three_slot_app(rig)
    serials = list(rig.devices)
    found = invoke(app, "discover", serials=serials)
    assert all(found[f"serial-{index}"]["options"] == serials for index in range(1, 4))
    for index in range(1, 4):
        result = invoke(app, f"connect-{index}", serials=serials)
        assert result[f"connection-{index}"]["children"] == "Connected"
        assert result[f"serial-{index}"]["disabled"] is True
        assert serials[index - 1] in result[f"identity-{index}"]["children"]
    assert all(
        not any(c[0] in {"set_state", "set_mode", "enable"} for c in d.calls)
        for d in rig.devices.values()
    )
    result = invoke(app, "open-2", serials=serials)
    assert [result[f"shutter-state-{index}"]["children"] for index in range(1, 4)] == [
        "Closed",
        "Open",
        "Closed",
    ]
    commands = {s: len([c for c in d.calls if c[0] == "set_state"]) for s, d in rig.devices.items()}
    invoke(app, "refresh", serials=serials, clicks=20)
    assert commands == {
        s: len([c for c in d.calls if c[0] == "set_state"]) for s, d in rig.devices.items()
    }
    invoke(app, "disconnect-1", serials=serials)
    assert [c.get_status().connection for c in hub.controllers] == [
        "disconnected",
        "connected",
        "connected",
    ]
    result = invoke(app, "shutdown-all", serials=serials)
    assert all(result[f"connection-{index}"]["children"] == "Disconnected" for index in range(1, 4))
    assert all(d.state == "Closed" and not d.IsConnected for d in rig.devices.values())


def test_gui_duplicate_selection_does_not_reconnect_an_owned_cube(rig):
    app, _ = three_slot_app(rig)
    serials = ["68000001", "68000001", "68000003"]
    invoke(app, "connect-1", serials=serials)
    result = invoke(app, "connect-2", serials=serials)
    assert "already owned" in result["message-2"]["children"]
    assert result["connection-1"]["children"] == "Connected"
    assert result["connection-2"]["children"] == "Disconnected"
    assert [call for call in rig.device.calls if call[0] == "connect"] == [("connect", "68000001")]


def test_one_fault_keeps_other_panels_usable_and_shutdown_reports_each_failure(rig):
    app, _ = three_slot_app(rig)
    serials = list(rig.devices)
    for index in range(1, 4):
        invoke(app, f"connect-{index}", serials=serials)
        invoke(app, f"open-{index}", serials=serials)
    rig.device.CommsStatus = "Timeout"
    result = invoke(app, "refresh", serials=serials)
    assert result["connection-1"]["children"] == "Fault"
    assert result["shutter-state-1"]["children"] == "Unknown"
    assert result["open-1"]["disabled"] is True
    assert result["close-1"]["disabled"] is False
    assert result["open-2"]["disabled"] is False
    invoke(app, "close-2", serials=serials)
    assert rig.devices["68000002"].state == "Closed"
    rig.devices["68000002"].fail.add("disconnect")
    result = invoke(app, "shutdown-all", serials=serials)
    assert "Shutter 1 (68000001)" in result["hub-message"]["children"]
    assert "Shutter 2 (68000002)" in result["hub-message"]["children"]
    assert result["connection-2"]["children"] == "Fault"
    assert result["close-2"]["disabled"] is False
    assert all(d.calls[-2:] == [("stop_poll",), ("disconnect",)] for d in rig.devices.values())
    assert rig.devices["68000003"].state == "Closed"
    assert not rig.devices["68000003"].IsConnected
    rig.devices["68000002"].fail.clear()
    invoke(app, "shutdown-all", serials=serials)
    assert not rig.devices["68000002"].IsConnected


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


def test_discovery_cannot_erase_identity_of_retained_lost_device(rig):
    app, _ = three_slot_app(rig)
    serials = list(rig.devices)
    invoke(app, "connect-2", serials=serials)
    rig.devices["68000002"].USBConnected = "Disconnected"
    rig.serials.remove("68000002")
    result = invoke(app, "discover", serials=serials)
    assert result["serial-2"]["value"] == "68000002"
    assert "68000002" in result["serial-2"]["options"]
    assert result["serial-2"]["disabled"] is True
    assert result["connection-2"]["children"] == "Fault"


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


def test_gui_arm_uses_device_settings_instead_of_unapplied_drafts(rig):
    app = create_app(rig.controller)
    invoke(app, "connect")
    result = invoke(app, "arm-ttl", ttl={"trig1-polarity": "low"})
    assert result["shutter-state"]["children"] == "Closed"  # Device remains active-high.
    assert "TRIG1 input/high" in result["ttl-status"]["children"]
    assert "trig1-polarity" not in result
    rig.device.fail.add("get_triggers")
    result = invoke(app, "refresh")
    assert result["ttl-status"]["children"] == "Unknown"
    assert result["arm-ttl"]["disabled"] is True
    assert result["disarm-ttl"]["disabled"] is False
    result = invoke(app, "shutdown-all")
    assert "completed" in result["hub-message"]["children"]
    assert rig.device.mode == "Manual" and not rig.device.IsConnected


def test_ttl_invalid_browser_values_are_errors_without_output_writes(rig):
    app = create_app(rig.controller)
    invoke(app, "connect")
    result = invoke(app, "apply-ttl", ttl={"trig1-mode": "bogus"})
    assert "Trigger mode must" in result["message"]["children"]
    assert not any(c[0] == "set_triggers" for c in rig.device.calls)
