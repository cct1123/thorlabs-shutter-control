"""Offline UI regressions using saved real observations; no device emulation or I/O."""

import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterStatus, load_config
from thorlabs_shutter_control.controller import ShutterFeedback
from thorlabs_shutter_control.device import Identity
from thorlabs_shutter_control.gui import create_app

ROOT = Path(__file__).resolve().parents[1]


def saved_sample(state):
    record = json.loads((ROOT / "records/webui-final-live.json").read_text())
    raw = (
        record["released_status"]
        if state == "disconnected"
        else record["connect"]
        if state == "off"
        else record["sequence"][0]["visibleResult"]
    )
    value = json.loads(raw)
    if value["identity"] is not None:
        value["identity"] = Identity(**value["identity"])
    value["feedback"] = ShutterFeedback(**value["feedback"])
    return ShutterStatus(**value)


def post_callback(app, key, values, changed):
    callback = app.callback_map[key]
    outputs = [
        {"id": output.component_id, "property": output.component_property}
        for output in callback["output"]
    ]
    response = app.server.test_client().post(
        "/_dash-update-component",
        json={
            "output": key,
            "outputs": outputs,
            "changedPropIds": [changed],
            "inputs": [dict(item, value=values.get(item["id"])) for item in callback["inputs"]],
            "state": [dict(item, value=values.get(item["id"])) for item in callback["state"]],
        },
    )
    assert response.status_code == 200
    return response.get_json()["response"]


@pytest.mark.parametrize(
    "action,state", [("poll", "off"), ("read", "off"), ("read", "disconnected")]
)
def test_background_poll_preserves_operator_notice_but_explicit_read_reports(action, state):
    sample = saved_sample(state)
    owner = SimpleNamespace(
        configs=load_config(ROOT / "config/shutter.ethernet.toml"),
        get_status=lambda target: sample,
    )
    app = create_app(owner)
    key = next(key for key in app.callback_map if "notice.children" in key)
    rendered = post_callback(
        app,
        key,
        {"target": "shutter", action: 1},
        action + (".n_intervals" if action == "poll" else ".n_clicks"),
    )
    expected_state = "unknown" if state == "disconnected" else "off"
    assert rendered["sample"]["data"]["feedback"]["electrical_state"] == expected_state
    if action == "poll":
        assert "notice" not in rendered
    elif state == "off":
        assert rendered["notice"]["children"] == "Readback updated."
    else:
        assert rendered["notice"]["children"] == "Disconnected; no device feedback was requested."


@pytest.mark.parametrize("state", ["off", "on"])
def test_timed_pulse_is_available_only_for_displayed_manual_off(state):
    owner = SimpleNamespace(configs=load_config(ROOT / "config/shutter.ethernet.toml"))
    app = create_app(owner)
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    rendered = post_callback(
        app, key, {"target": "shutter", "sample": asdict(saved_sample(state))}, "sample.data"
    )
    assert rendered["pulse"]["disabled"] is (state == "on")
    assert rendered["off"]["disabled"] is False
