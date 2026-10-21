"""Representative diagnostic workflows, with fictional records and software devices."""

import builtins
import copy
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from thorlabs_shutter_control import ShutterError
from thorlabs_shutter_control import controller as driver


@pytest.fixture
def diagnostics(monkeypatch, rig):
    def forbidden_interlock_gate(_):
        pytest.fail("Interlock metadata must not gate project operations")

    monkeypatch.setattr(driver.ShutterStatus, "interlock_ready", property(forbidden_interlock_gate))
    original_import = builtins.__import__

    def import_without_sdk(name, *args, **kwargs):
        if name.split(".")[0] in {"clr", "pythonnet", "Thorlabs"}:
            pytest.fail("Diagnostics attempted to import the real SDK")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_sdk)
    folder = Path(__file__).resolve().parents[1] / "docs" / "hardware_tests"
    monkeypatch.syspath_prepend(str(folder))
    modules = [importlib.import_module(f"stage_{n}") for n in range(7)]
    ttl = importlib.import_module("ttl_unconnected")
    for module in (modules[3], modules[5], ttl):
        monkeypatch.setattr(module, "time", driver.time)
    stage0 = modules[0]
    record = {
        name: dict.fromkeys(fields, "FICTIONAL TEST") for name, fields in stage0.FIELDS.items()
    }
    record["observed_at"] = "2026-10-20T10:00:00-05:00"
    record["hub"]["model"] = "KEH3"
    record["host"].update(os="Windows", python_bitness="x64", kinesis_bitness="x64")
    record["bench"]["one_owner_confirmed"] = True
    record["pairs"] = [dict.fromkeys(stage0.PAIR_FIELDS, "FICTIONAL TEST")]
    record["pairs"][0].update(serial="68000001", shutter_model="SH05R")
    assert not stage0.record_gaps(record)
    assert not rig.manager_calls and not rig.device.calls  # All helper imports are passive.
    return SimpleNamespace(stages=modules, ttl=ttl, record=record)


def review(stage):
    return dict(
        stage=stage,
        serial="68000001",
        physical_test_status="PASS",
        reviewed=True,
        evidence="Fictional acceptance fixture, never physical evidence",
    )


def test_record_gates_and_passive_discovery_cycle(diagnostics, rig):
    stage0, stage1, stage2 = diagnostics.stages[:3]
    assert stage0.record_gaps({})
    duplicate = copy.deepcopy(diagnostics.record)
    duplicate["pairs"].append(copy.deepcopy(duplicate["pairs"][0]))
    assert any("duplicate" in gap for gap in stage0.record_gaps(duplicate))
    discovery = stage1.check_discovery(diagnostics.record, rig.controller.discover)
    assert discovery["status"] == "MATCH"
    result = stage2.passive_cycle(diagnostics.record, "68000001", rig.controller, discovery)
    assert result["status"] == "READBACK_CAPTURED"
    assert result["physical_test_status"] == "UNTESTED"
    assert result["communication_release"] == "COMPLETED"
    assert not rig.device.IsConnected
    assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_missing_review_blocks_motion_before_device_access(diagnostics, rig):
    result = diagnostics.stages[3].first_close(diagnostics.record, "68000001", rig.controller, {})
    assert result["status"] == "BLOCKED"
    assert not rig.device.calls and not rig.manager_calls


@pytest.mark.parametrize("stage", [3, 4])
def test_motion_helper_records_feedback_and_releases(diagnostics, rig, stage):
    args = (diagnostics.record, "68000001", rig.controller, review(stage - 1))
    result = (
        diagnostics.stages[3].first_close(*args)
        if stage == 3
        else diagnostics.stages[4].open_close_pair(*args, open_seconds=0.5)
    )
    assert result["status"] == "READBACK_CAPTURED"
    assert result["physical_test_status"] == "UNTESTED"
    assert rig.device.state == "Closed" and not rig.device.IsConnected


@pytest.mark.parametrize("failure", ["identity", "open", "interrupt"])
def test_motion_failure_and_interrupt_keep_identity_gated_cleanup(
    diagnostics, rig, monkeypatch, failure
):
    if failure == "identity":
        monkeypatch.setattr(
            rig.device, "GetDeviceInfo", lambda: SimpleNamespace(SerialNumberText="68000002")
        )
    elif failure == "open":
        rig.device.fail.add("enable")
    else:

        def interrupt(_):
            raise KeyboardInterrupt("hold interrupted")

        monkeypatch.setattr(diagnostics.stages[3], "time", SimpleNamespace(sleep=interrupt))
    args = (diagnostics.record, "68000001", rig.controller, review(3))
    if failure == "interrupt":
        with pytest.raises(KeyboardInterrupt):
            diagnostics.stages[4].open_close_pair(*args, open_seconds=0.5)
    else:
        result = diagnostics.stages[4].open_close_pair(*args, open_seconds=0.5)
        assert result["status"] == "ERROR"
    assert rig.device.state == "Closed" and not rig.device.IsConnected
    if failure == "identity":
        assert not any(c[0] in {"enable", "set_state", "set_mode"} for c in rig.device.calls)


def test_shutdown_helper_observes_open_then_closes_and_releases(diagnostics, rig, monkeypatch):
    shutdown = rig.controller.safe_shutdown
    observed = []

    def cleanup():
        observed.append(rig.device.state)
        shutdown()

    monkeypatch.setattr(rig.controller, "safe_shutdown", cleanup)
    result = diagnostics.stages[5].shutdown_case(rig.controller, "68000001", open_seconds=0.5)
    assert observed == ["Open"] and result["status"] == "READBACK_PASS"
    assert result["physical_status"] == "UNTESTED"
    assert rig.device.state == "Closed" and not rig.device.IsConnected


@pytest.mark.parametrize("mismatch", [False, True])
def test_no_cable_helper_restores_settings_after_success_or_failure(diagnostics, rig, mismatch):
    rig.controller.connect()
    original = rig.controller.get_trigger_config()
    rig.device.inputs[0] = mismatch
    if mismatch:
        with pytest.raises(ShutterError, match="expectation failed"):
            diagnostics.ttl.run_matrix(rig.controller, armed_seconds=0.001, emit=lambda *_: None)
    else:
        diagnostics.ttl.run_matrix(rig.controller, armed_seconds=0.001, emit=lambda *_: None)
    assert rig.controller.get_trigger_config() == original
    assert rig.controller.get_operating_status().is_closed_manual
    rig.controller.disconnect(close_shutter=False)
