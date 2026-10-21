"""Stage-0 record checks use local fictional data only, with no vendor SDK."""

import builtins
import copy
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "hardware_tests" / "stage_0.py"


@pytest.fixture
def checker(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".")[0] in {"clr", "pythonnet", "Thorlabs", "thorlabs_shutter_control"}:
            pytest.fail(f"Stage 0 attempted a hardware/controller import: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    return runpy.run_path(str(SCRIPT))


@pytest.fixture
def complete_record(checker):
    record = {
        section: dict.fromkeys(fields, "FICTIONAL TEST RECORD")
        for section, fields in checker["FIELDS"].items()
    }
    record["observed_at"] = "2026-10-20T10:00:00-05:00"
    record["hub"]["model"] = "KEH3"
    record["host"].update(os="Windows TEST", python_bitness="x64", kinesis_bitness="x64")
    record["bench"]["one_owner_confirmed"] = True
    record["pairs"] = [dict.fromkeys(checker["PAIR_FIELDS"], "FICTIONAL TEST RECORD")]
    record["pairs"][0].update(serial="68000001", shutter_model="SH05R")
    return record


def test_supplied_record_is_incomplete_and_preserves_unknown_count(checker):
    record = json.loads((ROOT / "records" / "hardware-bench.json").read_text(encoding="utf-8"))
    assert record["pairs"] == [] and record["hub"]["model"] == "KEH3"
    gaps = checker["record_gaps"](record)
    assert any(gap.startswith("pairs:") for gap in gaps)
    assert any(gap.startswith("hub.supply_model:") for gap in gaps)


def test_one_pair_record_does_not_require_future_motion_or_ttl_limits(checker, complete_record):
    assert checker["record_gaps"](complete_record) == []


@pytest.mark.parametrize("field", ("serial", "label", "bay_label", "shutter_cable_label"))
def test_duplicate_identity_or_mapping_is_reported(checker, complete_record, field):
    second = copy.deepcopy(complete_record["pairs"][0])
    second.update(
        serial="68000002", label="PAIR 2", bay_label="BAY 2", shutter_cable_label="CABLE 2"
    )
    complete_record["pairs"].append(second)
    assert checker["record_gaps"](complete_record) == []
    second[field] = complete_record["pairs"][0][field]
    assert f"pairs[1].{field}: duplicate identity/mapping" in checker["record_gaps"](
        complete_record
    )


@pytest.mark.parametrize("value", [None, "", "UNKNOWN", " TBD ", [], False])
def test_unknown_or_nontext_field_blocks_record(checker, complete_record, value):
    complete_record["bench"]["physical_shutdown_procedure"] = value
    assert "bench.physical_shutdown_procedure: missing/unknown text" in checker["record_gaps"](
        complete_record
    )


@pytest.mark.parametrize("value", [None, "2026-10-20T10:00:00", "not a date", {}])
def test_missing_or_timezone_free_observation_is_reported(checker, complete_record, value):
    complete_record["observed_at"] = value
    assert any(gap.startswith("observed_at:") for gap in checker["record_gaps"](complete_record))


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("hub", "model", "KCH301"),
        ("host", "os", "Linux"),
        ("host", "python_bitness", "x86"),
        ("host", "kinesis_bitness", "x86"),
        ("bench", "one_owner_confirmed", "true"),
    ],
)
def test_changed_configuration_or_unconfirmed_ownership_is_reported(
    checker, complete_record, section, field, value
):
    complete_record[section][field] = value
    assert any(
        gap.startswith(f"{section}.{field}:") for gap in checker["record_gaps"](complete_record)
    )


@pytest.mark.parametrize("value", [None, [], {"hub": []}, {"pairs": [None]}])
def test_malformed_structures_report_gaps_without_crashing(checker, value):
    assert checker["record_gaps"](value)


@pytest.mark.parametrize("serial", [68000001, "6800000", "99000001", "6800000x"])
def test_serial_shape_is_checked(checker, complete_record, serial):
    complete_record["pairs"][0]["serial"] = serial
    assert any(
        gap.startswith("pairs[0].serial:") for gap in checker["record_gaps"](complete_record)
    )


def test_three_distinct_pairs_are_supported(checker, complete_record):
    pair = complete_record["pairs"][0]
    complete_record["pairs"] = [
        dict(
            pair,
            serial=f"6800000{i}",
            label=f"PAIR {i}",
            bay_label=f"BAY {i}",
            shutter_cable_label=f"CABLE {i}",
        )
        for i in range(1, 4)
    ]
    assert checker["record_gaps"](complete_record) == []
    complete_record["pairs"].append(dict(pair, serial="68000004"))
    assert any(gap.startswith("pairs:") for gap in checker["record_gaps"](complete_record))


def test_cli_complete_record_never_claims_permission_or_writes_file(
    checker, complete_record, monkeypatch, capsys
):
    path = ROOT / "records" / "fictional-test-only.json"
    original = json.dumps(complete_record)
    reads = []

    def read(record_path, *, encoding):
        assert record_path == path and encoding == "utf-8"
        reads.append(record_path)
        return original

    def forbid_write(*args, **kwargs):
        pytest.fail("Stage 0 attempted to write a file")

    monkeypatch.setattr(Path, "read_text", read)
    monkeypatch.setattr(Path, "write_text", forbid_write)
    monkeypatch.setattr(Path, "write_bytes", forbid_write)
    assert checker["main"](["--record", str(path)]) == 0
    output = capsys.readouterr().out
    assert "Offline record review only" in output
    assert "human review and physical verification still required" in output
    assert "No discovery or launch is authorized" in output
    assert reads == [path]
    assert complete_record["pairs"][0]["serial"] == "68000001"


def test_cli_incomplete_record_exits_one(checker, monkeypatch, capsys):
    path = ROOT / "records" / "fictional-test-only.json"
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: "{}")
    assert checker["main"](["--record", str(path)]) == 1
    assert "INCOMPLETE" in capsys.readouterr().out


@pytest.mark.parametrize("content", [FileNotFoundError("missing test record"), "{", UnicodeError()])
def test_cli_missing_malformed_or_invalid_encoding_exits_two(checker, monkeypatch, content):
    path = ROOT / "records" / "fictional-test-only.json"

    def read(*args, **kwargs):
        if isinstance(content, Exception):
            raise content
        return content

    monkeypatch.setattr(Path, "read_text", read)
    assert checker["main"](["--record", str(path)]) == 2


def test_help_is_passive(checker, capsys):
    with pytest.raises(SystemExit) as caught:
        checker["main"](["--help"])
    assert caught.value.code == 0
    assert "--record" in capsys.readouterr().out
