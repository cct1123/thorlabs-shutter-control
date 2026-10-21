"""Prepared motion helpers exercised with software devices only."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

FOLDER = Path(__file__).resolve().parents[1] / "docs" / "hardware_tests"
WRITES = {"set_state", "set_mode", "enable", "set_triggers"}


@pytest.fixture
def motion(monkeypatch, rig):
    monkeypatch.syspath_prepend(str(FOLDER))
    stage_0 = importlib.import_module("stage_0")
    stage_3 = importlib.import_module("stage_3")
    stage_4 = importlib.import_module("stage_4")
    record = {name: dict.fromkeys(fields, "TEST ONLY") for name, fields in stage_0.FIELDS.items()}
    record["observed_at"] = "2026-10-20T10:00:00-05:00"
    record["hub"]["model"] = "KEH3"
    record["host"].update(os="Windows", python_bitness="x64", kinesis_bitness="x64")
    record["bench"]["one_owner_confirmed"] = True
    record["pairs"] = [dict.fromkeys(stage_0.PAIR_FIELDS, "TEST ONLY")]
    record["pairs"][0].update(serial="68000001", shutter_model="SH05R")
    assert not stage_0.record_gaps(record)
    sleeps = []
    monkeypatch.setattr(stage_3, "time", SimpleNamespace(sleep=sleeps.append))
    return SimpleNamespace(record=record, third=stage_3, fourth=stage_4, sleeps=sleeps)


def review(stage):
    return dict(
        stage=stage,
        serial="68000001",
        physical_test_status="PASS",
        reviewed=True,
        evidence="FICTIONAL physical acceptance fixture, never bench evidence",
    )


def run(motion, rig, stage, prior=None, hold=0.75):
    args = (
        motion.record,
        "68000001",
        rig.controller,
        review(stage - 1) if prior is None else prior,
    )
    if stage == 3:
        return motion.third.first_close(*args)
    return motion.fourth.open_close_pair(*args, open_seconds=hold)


@pytest.mark.parametrize("stage", [3, 4])
def test_success_captures_feedback_but_never_physical_pass(motion, rig, stage):
    result = run(motion, rig, stage)
    assert result["status"] == "READBACK_CAPTURED"
    assert result["physical_test_status"] == "UNTESTED"
    assert result["communication_release"] == "COMPLETED"
    assert result["cleanup_close_authorized"] is True
    assert rig.device.state == "Closed" and not rig.device.IsConnected
    assert [call for call in rig.device.calls if call == ("set_state", "Active")] == (
        [("set_state", "Active")] if stage == 4 else []
    )
    assert motion.sleeps == ([0.75] if stage == 4 else [])
    assert rig.device.calls[-2:] == [("stop_poll",), ("disconnect",)]


@pytest.mark.parametrize("confirmed", [False, True])
def test_unknown_interlock_motion_uses_explicit_session_confirmation(motion, rig, confirmed):
    rig.device.interlock = False
    rig.controller.serial_number = "68000001"
    if confirmed:
        rig.controller.confirm_interlock("68000001")
    result = run(motion, rig, 4)
    assert result["status"] == ("READBACK_CAPTURED" if confirmed else "ERROR")
    assert any(c == ("set_state", "Active") for c in rig.device.calls) is confirmed
    assert rig.device.state == "Closed" and not rig.device.IsConnected


@pytest.mark.parametrize("stage", [3, 4])
@pytest.mark.parametrize(
    "field,value",
    [
        ("stage", 0),
        ("serial", "68000002"),
        ("physical_test_status", "UNTESTED"),
        ("reviewed", False),
        ("evidence", ""),
        ("evidence", None),
    ],
)
def test_review_gate_precedes_all_controller_calls(motion, rig, stage, field, value):
    prior = review(stage - 1)
    prior[field] = value
    assert run(motion, rig, stage, prior)["status"] == "BLOCKED"
    assert not rig.device.calls and not rig.manager_calls


@pytest.mark.parametrize("hold", [None, True, 0, -1, float("nan"), float("inf"), "1"])
def test_bad_hold_blocks_before_connection(motion, rig, hold):
    assert run(motion, rig, 4, hold=hold)["status"] == "BLOCKED"
    assert not rig.device.calls


@pytest.mark.parametrize("stage", [3, 4])
def test_incomplete_bench_blocks(motion, rig, stage):
    motion.record["bench"]["one_owner_confirmed"] = None
    assert run(motion, rig, stage)["status"] == "BLOCKED"
    assert not rig.device.calls


@pytest.mark.parametrize("stage", [3, 4])
def test_existing_owner_is_not_released_or_retargeted(motion, rig, stage):
    rig.controller.connect()
    rig.device.calls.clear()
    assert run(motion, rig, stage)["status"] == "BLOCKED"
    assert not any(
        c[0] in WRITES | {"connect", "disconnect", "stop_poll"} for c in rig.device.calls
    )
    rig.controller.disconnect(close_shutter=False)


@pytest.mark.parametrize("stage", [3, 4])
@pytest.mark.parametrize("fault", ["identity", "unknown", "connect"])
def test_unverified_target_gets_passive_cleanup_only(motion, rig, monkeypatch, stage, fault):
    if fault == "identity":
        monkeypatch.setattr(
            rig.controller, "identify_device", lambda: {"serial_number": "68000002"}
        )
    elif fault == "unknown":
        rig.device.operation = "0"
    else:
        rig.device.fail.add("connect")
    result = run(motion, rig, stage)
    assert result["status"] == "ERROR" and not result["cleanup_close_authorized"]
    assert not any(c[0] in WRITES for c in rig.device.calls)
    assert not rig.device.IsConnected and not motion.sleeps


@pytest.mark.parametrize("stage", [3, 4])
def test_primary_and_release_errors_both_preserved(motion, rig, stage):
    rig.device.fail.update({"set_state", "disconnect"})
    result = run(motion, rig, stage)
    assert result["status"] == "ERROR"
    assert len(result["errors"]) == 2
    assert "initial Close" in result["errors"][0]
    assert "cleanup" in result["errors"][1]
    assert result["communication_release"] == "UNCONFIRMED"
    assert rig.controller.get_status().has_device
    assert not any(c[0] == "enable" for c in rig.device.calls)
    rig.device.fail.clear()
    rig.controller.disconnect(close_shutter=False)


def test_interrupt_during_open_hold_closes_and_releases_then_propagates(motion, rig, monkeypatch):
    def interrupt(_):
        raise KeyboardInterrupt("TEST ONLY")

    monkeypatch.setattr(motion.third, "time", SimpleNamespace(sleep=interrupt))
    with pytest.raises(KeyboardInterrupt) as caught:
        run(motion, rig, 4)
    assert "added Open hold" in str(caught.value.__notes__)
    assert rig.device.state == "Closed" and not rig.device.IsConnected
    assert rig.device.calls.count(("set_state", "Active")) == 1


def test_open_fault_stops_without_hold_and_attempts_close(motion, rig):
    rig.device.fail.add("enable")
    result = run(motion, rig, 4)
    assert result["status"] == "ERROR" and "Open" in result["errors"][0]
    assert not motion.sleeps
    assert rig.device.state == "Closed" and not rig.device.IsConnected


def test_stage_3_reads_fresh_status_before_first_close(motion, rig, monkeypatch):
    get_status, close = rig.controller.get_status, rig.controller.close_shutter
    read_before_motion = []

    def status():
        result = get_status()
        if result.connection == "connected":
            read_before_motion.append(result)
        return result

    def checked_close():
        assert read_before_motion, "Fresh status must precede motion"
        return close()

    monkeypatch.setattr(rig.controller, "get_status", status)
    monkeypatch.setattr(rig.controller, "close_shutter", checked_close)
    assert run(motion, rig, 3)["status"] == "READBACK_CAPTURED"


def test_stage_3_failed_pre_motion_read_never_closes(motion, rig, monkeypatch):
    get_status = rig.controller.get_status

    def failed_status():
        if rig.device.IsConnected:
            rig.device.fail.add("status")
        return get_status()

    monkeypatch.setattr(rig.controller, "get_status", failed_status)
    result = run(motion, rig, 3)
    assert result["status"] == "ERROR"
    assert "pre-motion status" in result["errors"][0]
    assert not result["cleanup_close_authorized"]
    assert not any(c[0] in WRITES for c in rig.device.calls)
    assert result["communication_release"] == "COMPLETED"
