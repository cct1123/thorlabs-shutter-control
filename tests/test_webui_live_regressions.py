"""Offline UI regressions using saved real observations; no device emulation or I/O."""

import json
from dataclasses import asdict, fields
from pathlib import Path
from types import SimpleNamespace

import pytest
from ui_helpers import post_callback

from thorlabs_shutter_control import ShutterStatus, load_config
from thorlabs_shutter_control.controller import Identity
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
    # Translate the frozen historical capture only; runtime accepts the flat schema.
    readings = value.pop("feedback")
    value.update(readings)
    value["interlock_required"] = readings["interlock_enabled"]
    if value["identity"] is not None:
        value["identity"] = Identity(**value["identity"])
    return ShutterStatus(
        **{f.name: value[f.name] for f in fields(ShutterStatus) if f.name in value}
    )


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
    assert rendered["sample"]["data"]["electrical_state"] == expected_state
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


@pytest.mark.parametrize("state", ["off", "disconnected", "fault", "native"])
def test_connected_controls_delegate_qualification_to_owner(state):
    owner = SimpleNamespace(configs=load_config(ROOT / "config/shutter.ethernet.toml"))
    assert owner.configs[0].policy.qualified_modes == ("manual",)
    sample = asdict(saved_sample("disconnected" if state == "disconnected" else "off"))
    if state == "fault":
        sample["error"] = "Unconfirmed operation"
    if state == "native":
        sample["operating_mode"] = "auto"
    app = create_app(owner)
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    rendered = post_callback(app, key, {"target": "shutter", "sample": sample}, "sample.data")
    for mode in ("manual", "single", "auto", "triggered"):
        assert rendered[mode]["disabled"] is (state in ("disconnected", "fault"))
    assert rendered["on"]["disabled"] is (state in ("disconnected", "fault"))
    if state == "native":
        assert rendered["auto"]["className"] == "mode-button selected"
        assert rendered["off"]["disabled"] is False
        assert rendered["pulse"]["disabled"] is True
