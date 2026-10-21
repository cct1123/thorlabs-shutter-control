"""Shutdown/GUI preparation tests with software devices only."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def stage5(monkeypatch):
    folder = Path(__file__).resolve().parents[1] / "docs" / "hardware_tests"
    monkeypatch.syspath_prepend(str(folder))
    module = importlib.import_module("stage_5")
    clock = [0.0]
    monkeypatch.setattr(
        module,
        "time",
        SimpleNamespace(
            sleep=lambda value: clock.__setitem__(0, clock[0] + value), monotonic=lambda: clock[0]
        ),
    )
    return module


@pytest.mark.parametrize("hold", [None, 2])
def test_shutdown_actually_receives_closed_or_open_device(stage5, rig, monkeypatch, hold):
    states = []
    shutdown = rig.controller.safe_shutdown

    def observed_shutdown():
        states.append(rig.device.state)
        shutdown()

    monkeypatch.setattr(rig.controller, "safe_shutdown", observed_shutdown)
    result = stage5.shutdown_case(rig.controller, "68000001", open_seconds=hold)
    assert result["status"] == "READBACK_PASS"
    assert states == (["Closed"] if hold is None else ["Open"])
    assert result["physical_status"] == "UNTESTED" and not rig.device.IsConnected


def test_unverified_identity_only_releases(stage5, rig, monkeypatch):
    monkeypatch.setattr(rig.controller, "identify_device", lambda: {"serial_number": "68000002"})
    result = stage5.shutdown_case(rig.controller, "68000001")
    assert result["status"] == "ERROR" and result["cleanup_method"] == "passive_release"
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_unknown_interlock_stops_open_without_skipping_shutdown(stage5, rig):
    rig.device.interlock = False
    result = stage5.shutdown_case(rig.controller, "68000001", open_seconds=2)
    assert result["status"] == "ERROR" and "not confirmed enabled" in result["errors"][0]
    assert not any(c == ("set_state", "Active") for c in rig.device.calls)
    assert result["cleanup_method"] == "safe_shutdown" and result["release"] == "COMPLETED"


def test_primary_and_shutdown_error_preserved(stage5, rig):
    rig.device.fail.update({"enable", "disconnect"})
    result = stage5.shutdown_case(rig.controller, "68000001", open_seconds=2)
    assert len(result["errors"]) == 2 and result["release"] == "UNCONFIRMED"
    assert rig.controller.get_status().has_device
    rig.device.fail.clear()
    rig.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize("value", [0, -1, True, float("nan"), float("inf"), "2"])
def test_invalid_hold_never_connects(stage5, rig, value):
    assert (
        stage5.shutdown_case(rig.controller, "68000001", open_seconds=value)["status"] == "BLOCKED"
    )
    assert not rig.device.calls


def test_interrupted_open_hold_still_shutdowns(stage5, rig, monkeypatch):
    def interrupt(_):
        raise KeyboardInterrupt("TEST ONLY")

    monkeypatch.setattr(stage5, "time", SimpleNamespace(sleep=interrupt, monotonic=lambda: 0.0))
    with pytest.raises(KeyboardInterrupt):
        stage5.shutdown_case(rig.controller, "68000001", open_seconds=2)
    assert rig.device.state == "Closed" and not rig.device.IsConnected


def test_stage6_closed_gui_path_preserves_disabled_open(stage5, rig):
    from test_gui import invoke

    from thorlabs_shutter_control import ShutterHub
    from thorlabs_shutter_control.gui import create_app

    module = importlib.import_module("stage_6")
    rig.device.interlock = False
    hub = ShutterHub(["68000001"])
    app = create_app(hub)
    result = module.closed_gui_lifecycle(
        lambda action: invoke(app, action, serials=["68000001", None, None]), "68000001"
    )
    assert result["closed_lifecycle"] == "READBACK_PASS" and result["open_subcases"] == "BLOCKED"
    assert rig.device.IsConnected and rig.device.state == "Closed"
    assert not any(c[0] == "enable" or c == ("set_state", "Active") for c in rig.device.calls)
    hub.safe_shutdown()


def test_stage6_payload_uses_actual_dependency_and_selects_only_slot1(stage5):
    from thorlabs_shutter_control.gui import create_app

    module = importlib.import_module("stage_6")
    dependency = create_app().server.test_client().get("/_dash-dependencies").get_json()[0]
    counters = {}
    payload = module.callback_payload(dependency, "connect-1", "68000001", counters)
    states = {state["id"]: state["value"] for state in payload["state"]}
    assert states["serial-1"] == "68000001" and states["serial-2"] is None
    assert payload["changedPropIds"] == ["connect-1.n_clicks"]
    assert any(item["id"] == "connect-1" and item["value"] == 1 for item in payload["inputs"])


def test_stage6_enabled_open_close_and_refresh_do_not_replay_open(stage5, rig, monkeypatch):
    from test_gui import invoke

    from thorlabs_shutter_control import ShutterHub
    from thorlabs_shutter_control.gui import create_app

    module = importlib.import_module("stage_6")
    monkeypatch.setattr(module, "time", stage5.time)
    hub = ShutterHub(["68000001"])
    hub.controllers[0].confirm_interlock("68000001")
    rig.device.interlock = False
    app = create_app(hub)

    def call(action):
        return invoke(app, action, serials=["68000001", None, None])

    module.closed_gui_lifecycle(call, "68000001")
    result = module.open_close_gui(call, open_seconds=2)
    assert result["status"] == "READBACK_PASS" and result["added_open_hold_s"] == 2
    assert sum(c == ("set_state", "Active") for c in rig.device.calls) == 1
    hub.safe_shutdown()


def test_stage6_never_invokes_disabled_open(stage5, rig, monkeypatch):
    from test_gui import invoke

    from thorlabs_shutter_control import ShutterHub
    from thorlabs_shutter_control.gui import create_app

    module = importlib.import_module("stage_6")
    monkeypatch.setattr(module, "time", stage5.time)
    hub = ShutterHub(["68000001"])
    rig.device.interlock = False
    app = create_app(hub)

    def call(action):
        return invoke(app, action, serials=["68000001", None, None])

    module.closed_gui_lifecycle(call, "68000001")
    with pytest.raises(ValueError, match="not ready"):
        module.open_close_gui(call, open_seconds=2)
    assert not any(c == ("set_state", "Active") for c in rig.device.calls)
    assert not rig.device.IsConnected
