"""Software checks for the no-cable hardware diagnostic, never bench proof."""

import importlib.util
from dataclasses import replace
from pathlib import Path

import pytest

from thorlabs_shutter_control import ShutterError

spec = importlib.util.spec_from_file_location(
    "ttl_unconnected", Path(__file__).parents[1] / "docs/hardware_tests/ttl_unconnected.py"
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def test_no_cable_matrix_restores_original_closed(rig):
    rig.controller.connect()
    original = rig.controller.get_trigger_config()
    events = []
    helper.run_matrix(
        rig.controller, armed_seconds=0.001, emit=lambda action, data: events.append((action, data))
    )
    assert len([e for e in events if e[0] == "input_pass"]) == 4
    assert rig.controller.get_trigger_config() == original
    helper.require_closed(rig.controller.get_status())


def test_failed_expectation_disarms_and_restores_without_retry(rig):
    rig.controller.connect()
    original = rig.controller.get_trigger_config()
    rig.device.inputs[0] = True  # Competing electrical state, contrary to no-cable expectation.
    events = []
    with pytest.raises(ShutterError, match="expectation failed"):
        helper.run_matrix(
            rig.controller,
            armed_seconds=0.001,
            emit=lambda action, data: events.append((action, data)),
        )
    assert len([e for e in events if e[0] == "input_start"]) == 1
    assert rig.controller.get_trigger_config() == original
    helper.require_closed(rig.controller.get_status())


def test_arm_position_can_settle_before_final_expectation(rig, monkeypatch):
    rig.controller.connect()
    original_arm = rig.controller.arm_triggers

    def early_feedback():
        # The device model has changed position, but the first reply is stale.
        return replace(original_arm(), shutter_state="closed")

    monkeypatch.setattr(rig.controller, "arm_triggers", early_feedback)
    events = []
    helper.run_matrix(
        rig.controller, armed_seconds=0.001, emit=lambda action, data: events.append((action, data))
    )
    assert len([e for e in events if e[0] == "input_pass"]) == 4
    helper.require_closed(rig.controller.get_status())


@pytest.mark.parametrize("window", [0, -1, float("nan"), float("inf"), 2.01, True, "1", None])
def test_invalid_window_never_touches_device(rig, window):
    with pytest.raises(ValueError):
        helper.run_matrix(rig.controller, armed_seconds=window, emit=lambda *_: None)
    assert not rig.device.calls


@pytest.mark.parametrize("ports", [(True,), (1.0,), (), (1, 1), (3,), None])
def test_invalid_ports_never_touch_device(rig, ports):
    with pytest.raises(ValueError):
        helper.run_matrix(rig.controller, armed_seconds=1, emit=lambda *_: None, ports=ports)
    assert not rig.device.calls and not rig.manager_calls
