"""A readable electrical sample must not hide a persistent owner fault."""

from dataclasses import asdict

import pytest
from ui_helpers import post_callback

from thorlabs_shutter_control.gui import create_app


@pytest.mark.parametrize("action", ["connect", "read", "poll", "release"])
def test_persistent_fault_remains_in_both_notices_without_actuation(bench, action):
    hub, devices, _, path = bench
    journal = path / "uncertain-68000001"
    journal.write_text("Previous owner cleanup unconfirmed (software fixture)", encoding="utf-8")
    hub.connect("beam")
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    prop = "n_intervals" if action == "poll" else "n_clicks"
    response = post_callback(app, key, {"target": "beam", action: 1}, f"{action}.{prop}")
    assert response["sample"]["data"]["error"].startswith("Persistent uncertainty:")
    assert "notice" in response  # Faults must also surface during background polling.
    message = response["notice"]["children"]
    assert "fault" in message.lower() and "Stop / OFF" in message
    assert "Previous owner cleanup unconfirmed" in message
    assert response["settings-notice"]["children"] == message
    assert journal.exists() and not devices[0].output_frames


@pytest.mark.parametrize("action", ["off", "settings-stop"])
def test_confirmed_stop_clears_fault_and_enables_controls(bench, action):
    hub, devices, _, path = bench
    journal = path / "uncertain-68000001"
    journal.write_text("Previous cleanup unconfirmed (software fixture)", encoding="utf-8")
    hub.connect("beam")
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    response = post_callback(app, key, {"target": "beam", action: 1}, f"{action}.n_clicks")
    sample = response["sample"]["data"]
    message = response["notice"]["children"]
    assert "Stop / OFF sent; fresh electrical OFF readback received." in message
    assert "Controller fault remains:" not in message
    assert response["settings-notice"]["children"] == message
    assert sample["error"] is None and sample["electrical_state"] == "off"
    assert sample["electrical_observed_at"] and not journal.exists()
    assert sample["optical_closed_at"] is None and sample["optical_evidence"] is None
    assert [frame.param2 for frame in devices[0].output_frames] == [2]
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    shown = post_callback(app, key, {"target": "beam", "sample": sample}, "sample.data")
    assert shown["output-lamp-value"]["children"] == "Off"
    assert shown["error-lamp-value"]["children"] == "None reported"
    assert not shown["on"]["disabled"] and not shown["pulse"]["disabled"]
    assert not shown["off"]["disabled"]


@pytest.mark.parametrize(
    "state,connected,dated,expected",
    [
        ("off", True, True, "Off"),
        ("on", True, True, "On"),
        ("off", True, False, "Unknown"),
        ("off", False, True, "Unknown"),
        ("unknown", True, True, "Unknown"),
    ],
)
def test_fault_display_keeps_only_connected_dated_electrical_feedback(
    bench, state, connected, dated, expected
):
    hub, _, _, path = bench
    (path / "uncertain-68000001").write_text("Retained fault (software fixture)", encoding="utf-8")
    hub.connect("beam")
    sample = asdict(hub.get_status("beam"))
    assert sample["error"]
    sample["electrical_state"], sample["has_device"] = state, connected
    if not dated:
        sample["electrical_observed_at"] = None
    app = create_app(hub)
    key = next(key for key in app.callback_map if "serial-label.children" in key)
    shown = post_callback(app, key, {"target": "beam", "sample": sample}, "sample.data")
    assert shown["output-lamp-value"]["children"] == expected
    assert shown["error-lamp-value"]["children"] == "Reported"
    assert shown["on"]["disabled"] and shown["pulse"]["disabled"]


@pytest.mark.parametrize(
    "context", ["same", "target", "generation", "fault", "undated", "disconnected", "old-fault"]
)
def test_refusal_preserves_only_same_session_dated_feedback(bench, context):
    hub, devices, _, _ = bench
    hub.connect("beam")
    previous = asdict(hub.get_status("beam"))
    if context == "target":
        previous["name"] = "other"
    elif context == "generation":
        previous["generation"] -= 1
    elif context == "undated":
        previous["electrical_observed_at"] = None
    elif context == "fault":
        hub._channel("beam").error = "Retained fault"
    elif context == "disconnected":
        hub.disconnect("beam")
    elif context == "old-fault":
        previous["error"] = "Old fault"
    # A denied settings request performs no I/O, so retain an old dated reading
    # only for the unchanged healthy connection, never infer a fresh reading.
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    before = len(devices[0].history)
    response = post_callback(
        app,
        key,
        {"target": "beam", "sample": previous, "apply-led": 1, "led-modes": [1]},
        "apply-led.n_clicks",
    )
    sample = response["sample"]["data"]
    assert len(devices[0].history) == before
    if context == "same":
        assert sample["electrical_state"] == "off"
        assert sample["electrical_observed_at"] == previous["electrical_observed_at"]
        assert "Last dated feedback retained" in response["notice"]["children"]
    else:
        assert sample["electrical_state"] == "unknown"
        assert sample["electrical_observed_at"] is None
    if context == "fault":
        assert sample["error"] == "Retained fault"


def test_premature_on_retains_original_off_timestamp_without_actuation(bench, monkeypatch):
    from dataclasses import replace

    hub, devices, _, _ = bench
    channel = hub._channel("beam")
    channel.config = replace(channel.config, policy=replace(channel.config.policy, min_off_s=2))
    tick = [100.0]
    monkeypatch.setattr("thorlabs_shutter_control.controller.clock", lambda: tick[0])
    hub.connect("beam")
    previous = asdict(hub.get_status("beam"))
    tick[0] = 101.06
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    response = post_callback(
        app, key, {"target": "beam", "sample": previous, "on": 1}, "on.n_clicks"
    )
    assert "wait 0.94 s" in response["notice"]["children"]
    assert response["sample"]["data"]["electrical_state"] == "off"
    assert (
        response["sample"]["data"]["electrical_observed_at"] == previous["electrical_observed_at"]
    )
    assert response["sample"]["data"]["error"] is None
    assert not devices[0].output_frames


@pytest.mark.parametrize("failure", ["interlock", "write"])
def test_explicit_stop_reset_preserves_fault_when_verification_fails(bench, failure):
    hub, devices, _, path = bench
    journal = path / "uncertain-68000001"
    journal.write_text("Previous interrupted cleanup", encoding="utf8")
    hub.connect("beam")
    if failure == "interlock":
        devices[0].interlock = 2
    else:
        devices[0].partial = True
    app = create_app(hub)
    key = next(key for key in app.callback_map if "notice.children" in key)
    response = post_callback(app, key, {"target": "beam", "off": 1}, "off.n_clicks")
    assert response["sample"]["data"]["error"]
    assert "Refused or unconfirmed" in response["notice"]["children"]
    assert journal.exists()
    assert all(frame.param2 == 2 for frame in devices[0].output_frames)


def test_source_checkbox_is_absent_from_layout_and_callbacks(bench):
    hub, devices, _, _ = bench
    app = create_app(hub)
    client = app.server.test_client()
    assert b"source-inhibited" not in client.get("/_dash-layout").data
    assert b"source-inhibited" not in client.get("/_dash-dependencies").data
    assert b"Source independently blocked" not in client.get("/_dash-layout").data
    assert not devices
