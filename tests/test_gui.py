from thorlabs_shutter_control.gui import create_app


def invoke(app, action, *, serial=None, clicks=1):
    key, callback = next(iter(app.callback_map.items()))
    outputs = [
        {"id": item.component_id, "property": item.component_property}
        for item in callback["output"]
    ]
    inputs = [
        {"id": name, "property": prop, "value": clicks}
        for name, prop in [
            ("discover", "n_clicks"),
            ("connect", "n_clicks"),
            ("disconnect", "n_clicks"),
            ("open", "n_clicks"),
            ("close", "n_clicks"),
            ("refresh", "n_intervals"),
        ]
    ]
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": key,
            "outputs": outputs,
            "inputs": inputs,
            "state": [{"id": "serial", "property": "value", "value": serial}],
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
