"""HTTP callback coverage for shared-owner command controls; no hardware or browser substitute."""

import json
from dataclasses import asdict, replace

import pytest
from conftest import FakeTransport
from ui_helpers import post_callback

from thorlabs_shutter_control import ShutterHub
from thorlabs_shutter_control.gui import DETAIL_ACTIONS, create_app


def action(app, name, **values):
    key = next(key for key in app.callback_map if "notice.children" in key)
    changed = name + (".n_intervals" if name == "poll" else ".n_clicks")
    return post_callback(app, key, {"target": "beam", name: 1, **values}, changed)


def details(app, data, sample, changed="details.data", target="beam"):
    key = next(key for key in app.callback_map if "channel-reading.children" in key)
    return post_callback(app, key, {"details": data, "sample": sample, "target": target}, changed)


@pytest.mark.parametrize(
    "name,field,expected",
    [
        ("read-channel", "channel_enabled", False),
        ("read-bay", "bay", 2),
        ("read-led", "led_modes", 1),
        ("start-updates", "update_request", "Start requested"),
        ("stop-updates", "update_request", "Stop requested"),
        ("read-events", "events", []),
    ],
)
def test_extra_controls_use_owner_and_refresh_status(bench, name, field, expected):
    hub, devices, _, _ = bench
    hub.connect("beam")
    app = create_app(hub)
    response = action(app, name)
    sample = response["sample"]["data"]
    data = response["details"]["data"]
    assert data["values"][field] == expected
    assert data["target"] == "beam" and data["generation"] == sample["generation"]
    assert sample["electrical_state"] == "off"
    assert response["settings-notice"]["children"] == response["notice"]["children"]
    assert not devices[0].output_frames
    if name.endswith("updates"):
        assert "no device acknowledgement" in response["notice"]["children"]


def test_diagnostic_results_merge_without_false_channel_or_bay_mapping(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].bay = 255
    app = create_app(hub)
    first = action(app, "read-channel")
    second = action(app, "read-bay", details=first["details"]["data"])
    shown = details(app, second["details"]["data"], second["sample"]["data"])
    assert shown["channel-reading"]["children"] == "Channel enable: Disabled"
    assert shown["bay-reading"]["children"] == "Raw bay: 255 (0xFF)"
    assert hub.configs[0].route.kind == "d2xx"


@pytest.mark.parametrize("action_name", ["reset", "read-led"])
def test_polling_keeps_led_drafts_and_both_operator_messages(bench, action_name):
    hub, _, _, _ = bench
    hub.connect("beam")
    app = create_app(hub)
    sample = asdict(hub.get_status("beam"))
    data = {
        "target": "beam",
        "generation": sample["generation"],
        "action": action_name,
        "values": {"led_modes": 1},
    }
    rendered = details(app, data, sample, "sample.data")
    assert "led-modes" not in rendered
    refreshed = action(app, "poll", details=data)
    assert "notice" not in refreshed and "settings-notice" not in refreshed
    assert "details" not in refreshed


@pytest.mark.parametrize("change", ["target", "generation", "disconnected", "fault"])
def test_old_diagnostics_and_led_drafts_do_not_cross_sessions(bench, change):
    hub, _, _, _ = bench
    hub.connect("beam")
    app = create_app(hub)
    sample = asdict(hub.get_status("beam"))
    data = {
        "target": "beam",
        "generation": sample["generation"],
        "action": "read-led",
        "values": {"channel_enabled": True, "led_modes": 9, "events": ["old"]},
    }
    if change == "target":
        data["target"] = "other"
    elif change == "generation":
        sample["generation"] += 1
    elif change == "disconnected":
        sample["has_device"] = False
    else:
        sample["error"] = "fault"
    shown = details(app, data, sample, "sample.data")
    assert shown["led-modes"]["value"] == []
    assert shown["channel-reading"]["children"] == "Channel enable: Not read"
    assert shown["event-data"]["children"] == "No events collected"


@pytest.mark.parametrize("changed", ["details.data", ["sample.data", "details.data"]])
def test_explicit_led_read_updates_draft_but_other_reads_preserve_it(bench, changed):
    hub, devices, _, _ = bench
    hub.connect("beam")
    devices[0].led_modes = 0x8009
    app = create_app(hub)
    response = action(app, "read-led")
    data, sample = response["details"]["data"], response["sample"]["data"]
    shown = details(app, data, sample, changed)
    assert shown["led-modes"]["value"] == [1, 8]
    assert "Extra flags" in shown["led-reading"]["children"]
    data["action"] = "read-channel"
    assert "led-modes" not in details(app, data, sample)


@pytest.mark.parametrize("name", ["apply-led", "require-interlock"])
def test_settings_policy_refusal_is_visible_inside_dialog_without_writes(bench, name):
    hub, devices, _, _ = bench
    hub.connect("beam")
    before = len(devices[0].history)
    app = create_app(hub)
    response = action(app, name, **{"led-modes": [1], "source-inhibited": ["protected"]})
    assert "allow_device_settings" in response["settings-notice"]["children"]
    assert response["settings-notice"]["children"] == response["notice"]["children"]
    assert len(devices[0].history) == before


def test_led_apply_and_interlock_repair_use_shared_settings_api(config, tmp_path):
    config = replace(config, policy=replace(config.policy, allow_device_settings=True))
    device = FakeTransport(config)
    with ShutterHub(
        [config], transport_factory=lambda c, d: device, lock_directory=tmp_path
    ) as hub:
        hub.connect("beam")
        app = create_app(hub)
        response = action(
            app, "apply-led", **{"led-modes": [1, 8], "source-inhibited": ["protected"]}
        )
        assert device.led_modes == 9 and response["details"]["data"]["values"]["led_modes"] == 9
        device.interlock = 2
        response = action(app, "require-interlock", **{"source-inhibited": ["protected"]})
        assert response["sample"]["data"]["interlock_required"] is True
        assert device.interlock == 1
        assert not device.output_frames


@pytest.mark.parametrize("flags", [[True], [4], ["1"]])
def test_invalid_led_checklist_fails_without_io(bench, flags):
    hub, devices, _, _ = bench
    hub.connect("beam")
    before = len(devices[0].history)
    response = action(create_app(hub), "apply-led", **{"led-modes": flags})
    assert "documented LED" in response["settings-notice"]["children"]
    assert len(devices[0].history) == before


def test_update_collection_displays_raw_bytes_and_disconnect_clears_results(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    app = create_app(hub)
    started = action(app, "start-updates")
    collected = action(app, "read-events", details=started["details"]["data"])
    values = collected["details"]["data"]["values"]
    assert values["events"] and values["events"][0]["id"] == "0x0481"
    assert bytes.fromhex(values["events"][0]["frame"])[6:] == devices[0].update_payload
    action(app, "stop-updates")
    released = action(app, "release")
    assert not released["sample"]["data"]["has_device"] and released["details"]["data"] is None
    assert devices[0].closed and not devices[0].bus_disconnected
    assert not devices[0].output_frames


def test_protected_hardware_disconnect_is_api_only(bench):
    hub, devices, _, _ = bench
    hub.connect("beam")
    app = create_app(hub)
    client = app.server.test_client()
    assert b"hardware-disconnect" not in client.get("/_dash-layout").data
    assert b"hardware-disconnect" not in client.get("/_dash-dependencies").data
    assert hub.connection_snapshot("beam").has_device
    assert not devices[0].bus_disconnected


def test_all_new_controls_exist_without_startup_device_access(bench):
    hub, devices, _, _ = bench
    app = create_app(hub)
    layout = app.server.test_client().get("/_dash-layout").get_json()
    ids = set()

    def visit(node):
        if isinstance(node, dict):
            props = node.get("props", {})
            if "id" in props:
                ids.add(props["id"])
            visit(props.get("children"))
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(layout)
    assert set(DETAIL_ACTIONS) <= ids
    assert not devices
    assert "Raw bay" in json.dumps(layout)
