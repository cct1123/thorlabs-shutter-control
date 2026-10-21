"""Stage-1 offline/discovery CLI with a fake SDK; real SDK imports forbidden."""

import builtins
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs" / "hardware_tests"


@pytest.fixture
def tool(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in {"clr", "pythonnet", "Thorlabs"}:
            pytest.fail(f"Stage 1 attempted a real SDK import: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.syspath_prepend(str(FOLDER))
    return runpy.run_path(str(FOLDER / "stage_1.py"))


@pytest.fixture
def record(tool):
    stage_0 = runpy.run_path(str(FOLDER / "stage_0.py"))
    value = {
        name: dict.fromkeys(fields, "FICTIONAL TEST RECORD")
        for name, fields in stage_0["FIELDS"].items()
    }
    value["observed_at"] = "2026-10-20T10:00:00-05:00"
    value["hub"]["model"] = "KEH3"
    value["host"].update(
        os="Windows", python_version="3.12.7", python_bitness="x64", kinesis_bitness="x64"
    )
    value["bench"]["one_owner_confirmed"] = True
    value["pairs"] = [dict.fromkeys(stage_0["PAIR_FIELDS"], "FICTIONAL TEST RECORD")]
    value["pairs"][0].update(serial="68000001", shutter_model="SH05R")
    assert tool["record_gaps"](value) == []
    return value


@pytest.fixture
def environment(tool, monkeypatch):
    monkeypatch.setattr(tool["platform"], "system", lambda: "Windows")
    monkeypatch.setattr(tool["platform"], "python_version", lambda: "3.12.7")
    monkeypatch.setattr(tool["struct"], "calcsize", lambda _: 8)
    monkeypatch.setattr(tool["importlib"].metadata, "version", lambda _: "TEST VERSION")


def test_import_and_help_never_enumerate(tool, rig, capsys):
    with pytest.raises(SystemExit) as caught:
        tool["main"](["--help"])
    assert caught.value.code == 0 and "--discover" in capsys.readouterr().out
    assert not rig.manager_calls


def test_discover_cli_enumerates_without_record_or_connection(tool, rig, monkeypatch, capsys):
    def forbidden_read(*args, **kwargs):
        pytest.fail("Enumeration does not need an offline physical-record check")

    monkeypatch.setattr(Path, "read_text", forbidden_read)
    assert tool["main"](["--discover"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ENUMERATED" and result["observed_serials"] == ["68000001"]
    assert rig.manager_calls == ["discover"]
    assert all(not device.calls for device in rig.devices.values())


def test_unknown_approval_flag_is_rejected(tool, rig):
    with pytest.raises(SystemExit) as caught:
        tool["main"](["--discover", "--approve-hardware"])
    assert caught.value.code == 2 and not rig.manager_calls


@pytest.mark.parametrize("args", [[], ["--preflight"]])
def test_offline_cli_complete_record_never_enumerates_or_writes(
    tool, record, environment, rig, monkeypatch, capsys, args
):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: json.dumps(record))

    def forbidden_write(*args, **kwargs):
        pytest.fail("Offline preflight attempted to write a file")

    monkeypatch.setattr(Path, "write_text", forbidden_write)
    monkeypatch.setattr(Path, "write_bytes", forbidden_write)
    assert tool["main"](args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "RECORD_AND_ENVIRONMENT_CHECKS_COMPLETE"
    assert (
        result["hardware_access"] == "NOT_REQUESTED"
        and result["physical_test_status"] == "UNTESTED"
    )
    assert not rig.manager_calls and all(not d.calls for d in rig.devices.values())


def test_offline_cli_incomplete_record(tool, environment, monkeypatch, capsys):
    monkeypatch.setattr(Path, "read_text", lambda *a, **k: "{}")
    assert tool["main"]([]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "INCOMPLETE"


@pytest.mark.parametrize("content", ["{", FileNotFoundError("test missing"), UnicodeError()])
def test_unreadable_record_exits_two(tool, monkeypatch, content, capsys):
    def read(*args, **kwargs):
        if isinstance(content, Exception):
            raise content
        return content

    monkeypatch.setattr(Path, "read_text", read)
    assert tool["main"]([]) == 2
    assert json.loads(capsys.readouterr().out)["hardware_access"] == "NOT_REQUESTED"


def test_missing_dependency_and_host_mismatch_block_preflight(
    tool, record, environment, monkeypatch
):
    def missing(name):
        raise tool["importlib"].metadata.PackageNotFoundError(name)

    monkeypatch.setattr(tool["importlib"].metadata, "version", missing)
    monkeypatch.setattr(tool["platform"], "system", lambda: "Linux")
    record["host"]["python_version"] = "3.11.0"
    result = tool["preflight"](record)
    assert result["status"] == "INCOMPLETE"
    assert len(result["gaps"]) == 6  # Four missing packages, host OS, recorded interpreter.


def test_incomplete_record_prevents_enumerator_call(tool):
    def forbidden():
        pytest.fail("Incomplete record must block enumeration")

    assert tool["check_discovery"]({}, forbidden)["status"] == "BLOCKED"


@pytest.mark.parametrize("count", [1, 3])
def test_expected_fake_devices_match_without_any_connection(tool, record, rig, count):
    rig.serials[:] = list(rig.devices)[:count]
    record["pairs"] = [
        dict(
            record["pairs"][0],
            serial=serial,
            label=f"PAIR {i}",
            bay_label=f"BAY {i}",
            shutter_cable_label=f"CABLE {i}",
        )
        for i, serial in enumerate(rig.serials)
    ]
    result = tool["check_discovery"](record, rig.controller.discover)
    assert result["status"] == "MATCH" and result["observed_serials"] == sorted(rig.serials)
    assert "enumeration subcase only" in result["test"]
    assert rig.manager_calls == ["discover"]
    assert all(not d.calls for d in rig.devices.values())


@pytest.mark.parametrize(
    ("observed", "missing", "unexpected"),
    [
        ([], ["68000001"], []),
        (["68000002"], ["68000001"], ["68000002"]),
        (["68000001", "68000002"], [], ["68000002"]),
    ],
)
def test_missing_and_unexpected_identities_are_not_match(
    tool, record, observed, missing, unexpected
):
    result = tool["check_discovery"](record, lambda: observed)
    assert result["status"] == "MISMATCH"
    assert result["missing_serials"] == missing and result["unexpected_serials"] == unexpected


@pytest.mark.parametrize("observed", [["68000001", "68000001"], [68000001], ["bad"], None])
def test_invalid_or_duplicate_serials_are_error(tool, record, observed):
    assert tool["check_discovery"](record, lambda: observed)["status"] == "ERROR"


def test_enumerator_failure_is_preserved_without_retry(tool, record):
    calls = []

    def fail():
        calls.append("enumerate")
        raise RuntimeError("test USB enumeration failed")

    result = tool["check_discovery"](record, fail)
    assert result["status"] == "ERROR" and "test USB enumeration failed" in result["error"]
    assert calls == ["enumerate"]


def test_interrupt_is_not_swallowed_or_retried(tool, record):
    def interrupt():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        tool["check_discovery"](record, interrupt)
