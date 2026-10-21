"""Stage-2 lifecycle tests with software devices; real SDK imports forbidden."""

import builtins
import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest

FOLDER = Path(__file__).resolve().parents[1] / "docs" / "hardware_tests"


@pytest.fixture
def tool(monkeypatch):
    original = builtins.__import__

    def guard(name, *args, **kwargs):
        if name.split(".")[0] in {"clr", "pythonnet", "Thorlabs"}:
            pytest.fail(f"Stage 2 attempted a real SDK import: {name}")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guard)
    monkeypatch.syspath_prepend(str(FOLDER))
    return runpy.run_path(str(FOLDER / "stage_2.py"))


@pytest.fixture
def record(tool):
    stage_0 = runpy.run_path(str(FOLDER / "stage_0.py"))
    result = {
        name: dict.fromkeys(fields, "TEST ONLY") for name, fields in stage_0["FIELDS"].items()
    }
    result["observed_at"] = "2026-10-20T10:00:00-05:00"
    result["hub"]["model"] = "KEH3"
    result["host"].update(os="Windows", python_bitness="x64", kinesis_bitness="x64")
    result["bench"]["one_owner_confirmed"] = True
    result["pairs"] = [dict.fromkeys(stage_0["PAIR_FIELDS"], "TEST ONLY")]
    result["pairs"][0].update(serial="68000001", shutter_model="SH05R")
    assert not tool["record_gaps"](result)
    return result


@pytest.fixture
def discovery(record, rig):
    check = runpy.run_path(str(FOLDER / "stage_1.py"))["check_discovery"]
    return check(record, rig.controller.discover)


def cycle(tool, record, rig, discovery):
    return tool["passive_cycle"](record, "68000001", rig.controller, discovery)


def assert_passive(rig):
    for device in rig.devices.values():
        assert not any(
            c[0] in {"set_state", "set_mode", "enable", "set_triggers"} for c in device.calls
        )


def test_three_separately_invoked_cycles_release_same_owner(tool, record, rig, discovery):
    for _ in range(3):
        result = cycle(tool, record, rig, discovery)
        assert result["status"] == "READBACK_CAPTURED"
        assert result["physical_test_status"] == "UNTESTED"
        assert result["communication_release"] == "COMPLETED"
        assert result["identity"]["serial_number"] == "68000001"
        assert not rig.controller.get_status().has_device
    assert len([c for c in rig.device.calls if c[0] == "connect"]) == 3
    assert_passive(rig)


def test_open_triggered_device_is_not_closed_or_reconfigured(tool, record, rig, discovery):
    rig.device.mode, rig.device.operation, rig.device.state = "Triggered", "Active", "Open"
    rig.device.inputs[0] = True
    result = cycle(tool, record, rig, discovery)
    assert result["status"] == "READBACK_CAPTURED"
    assert rig.device.state == "Open" and rig.device.mode == "Triggered"
    assert not rig.device.IsConnected
    assert_passive(rig)


def test_passive_capture_preserves_unverified_interlock(tool, record, rig, discovery):
    rig.device.interlock = False
    result = cycle(tool, record, rig, discovery)
    assert result["status"] == "READBACK_CAPTURED"
    assert result["reported_status"]["interlock_enabled"] is None
    assert_passive(rig)


@pytest.mark.parametrize(
    "bad", [None, {}, {"status": "MISMATCH"}, {"status": "MATCH", "observed_serials": []}]
)
def test_missing_or_mismatching_discovery_blocks_all_controller_calls(tool, record, rig, bad):
    assert cycle(tool, record, rig, bad)["status"] == "BLOCKED"
    assert not rig.manager_calls and not rig.device.calls


def test_unknown_record_or_serial_prevents_connection(tool, record, rig, discovery):
    assert tool["passive_cycle"]({}, "68000001", rig.controller, discovery)["status"] == "BLOCKED"
    assert (
        tool["passive_cycle"](record, "68000002", rig.controller, discovery)["status"] == "BLOCKED"
    )
    assert not rig.device.calls


def test_existing_owner_is_not_disconnected(tool, record, rig, discovery):
    rig.controller.connect("68000001")
    result = cycle(tool, record, rig, discovery)
    assert result["status"] == "BLOCKED" and rig.device.IsConnected
    assert not any(c[0] == "disconnect" for c in rig.device.calls)
    rig.controller.disconnect(close_shutter=False)
    assert_passive(rig)


@pytest.mark.parametrize("failure", ["connect", "identity", "status", "stop_poll", "disconnect"])
def test_failures_stop_cycle_and_preserve_passive_cleanup(
    tool, record, rig, discovery, monkeypatch, failure
):
    if failure == "identity":

        def fail_identity():
            raise RuntimeError("injected identity failure")

        monkeypatch.setattr(rig.controller, "identify_device", fail_identity)
    elif failure == "status":
        original = rig.controller.get_status
        reads = []

        def faulty_status():
            reads.append(1)
            status = original()
            return (
                replace(status, connection="fault", error="injected status failure")
                if len(reads) == 2
                else status
            )

        monkeypatch.setattr(rig.controller, "get_status", faulty_status)
    else:
        rig.device.fail.add(failure)
    result = cycle(tool, record, rig, discovery)
    assert result["status"] == "ERROR" and result["retain_controller_for_diagnosis"]
    assert result["errors"]
    assert any(c[0] == "disconnect" for c in rig.device.calls)
    assert rig.device.IsConnected == (failure == "disconnect")
    assert_passive(rig)


def test_identity_mismatch_is_released(tool, record, rig, discovery, monkeypatch):
    monkeypatch.setattr(rig.controller, "identify_device", lambda: {"serial_number": "68000002"})
    result = cycle(tool, record, rig, discovery)
    assert result["status"] == "ERROR" and "Identity readback" in result["errors"][0]
    assert not rig.device.IsConnected
    assert_passive(rig)


@pytest.mark.parametrize(
    "change",
    [
        {"operating_mode": "unknown"},
        {"key_enabled": None},
        {"trigger_config": None},
        {"shutter_state": "open", "operating_state": "active"},
    ],
)
def test_unknown_or_changed_feedback_blocks_repetition(
    tool, record, rig, discovery, monkeypatch, change
):
    original = rig.controller.get_status
    reads = []

    def changed_status():
        reads.append(1)
        status = original()
        return replace(status, **change) if len(reads) == 2 else status

    monkeypatch.setattr(rig.controller, "get_status", changed_status)
    assert cycle(tool, record, rig, discovery)["status"] == "ERROR"
    assert not rig.device.IsConnected
    assert_passive(rig)


@pytest.mark.parametrize("release_error", [False, True])
def test_interrupt_releases_and_preserves_cleanup_error(
    tool, record, rig, discovery, monkeypatch, release_error
):
    def interrupt():
        raise KeyboardInterrupt("test interrupt")

    monkeypatch.setattr(rig.controller, "identify_device", interrupt)
    if release_error:
        rig.device.fail.add("stop_poll")
    with pytest.raises(KeyboardInterrupt) as caught:
        cycle(tool, record, rig, discovery)
    report = json.loads(caught.value.__notes__[-1])
    assert report["status"] == "ERROR"
    assert any("passive release" in item for item in report["errors"]) == release_error
    assert not rig.device.IsConnected
    assert_passive(rig)


def test_connect_cli_passively_connects_and_releases(tool, record, rig, monkeypatch, capsys):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: json.dumps(record))
    assert tool["main"](["--connect", "--serial", "68000001"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "READBACK_CAPTURED"
    assert rig.manager_calls == ["discover", "discover"] and not rig.device.IsConnected
    assert_passive(rig)


def test_release_interrupt_still_releases_before_propagation(
    tool, record, rig, discovery, monkeypatch
):
    def interrupt_release():
        raise KeyboardInterrupt("test release interrupt")

    monkeypatch.setattr(rig.device, "StopPolling", interrupt_release)
    with pytest.raises(KeyboardInterrupt) as caught:
        cycle(tool, record, rig, discovery)
    report = json.loads(caught.value.__notes__[-1])
    assert report["communication_release"] == "UNCONFIRMED"
    assert not rig.device.IsConnected and any(c[0] == "disconnect" for c in rig.device.calls)
    assert_passive(rig)


def test_operation_and_release_errors_both_survive(tool, record, rig, discovery, monkeypatch):
    def fail_identity():
        raise RuntimeError("test primary identity error")

    monkeypatch.setattr(rig.controller, "identify_device", fail_identity)
    rig.device.fail.add("disconnect")
    result = cycle(tool, record, rig, discovery)
    assert len(result["errors"]) == 2
    assert "test primary identity error" in result["errors"][0]
    assert "passive release" in result["errors"][1] and rig.device.IsConnected
    # No reconnect/automatic cleanup retry is made on the retained owner.
    calls = list(rig.device.calls)
    assert cycle(tool, record, rig, discovery)["status"] == "BLOCKED"
    assert rig.device.calls == calls
    assert_passive(rig)


def test_other_serial_controller_is_not_retargeted(tool, record, rig, discovery):
    rig.controller.serial_number = "68000002"
    assert cycle(tool, record, rig, discovery)["status"] == "BLOCKED"
    assert not rig.device.calls


def test_help_has_no_side_effects(tool, rig, capsys):
    with pytest.raises(SystemExit) as caught:
        tool["main"](["--help"])
    assert caught.value.code == 0 and "--connect" in capsys.readouterr().out
    assert not rig.manager_calls


@pytest.mark.parametrize("serial", [None, "68000001", "68000002"])
def test_offline_cli_checks_explicit_serial_without_connecting(
    tool, record, rig, monkeypatch, capsys, serial
):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: json.dumps(record))
    monkeypatch.setitem(
        tool["main"].__globals__,
        "preflight",
        lambda r: {"gaps": [], "physical_test_status": "UNTESTED"},
    )
    args = ["--preflight"] + (["--serial", serial] if serial else [])
    assert tool["main"](args) == (0 if serial == "68000001" else 1)
    assert json.loads(capsys.readouterr().out)["connection_access"] == "NOT_REQUESTED"
    assert not rig.manager_calls and not rig.device.calls


@pytest.mark.parametrize("content", ["{", FileNotFoundError("test missing")])
def test_unreadable_record_cannot_connect(tool, rig, monkeypatch, capsys, content):
    def read(*args, **kwargs):
        if isinstance(content, Exception):
            raise content
        return content

    monkeypatch.setattr(Path, "read_text", read)
    assert tool["main"]([]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "ERROR"
    assert not rig.manager_calls
