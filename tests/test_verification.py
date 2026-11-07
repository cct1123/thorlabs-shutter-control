"""Verification evidence contracts, not device or bench tests."""

import importlib.util
from pathlib import Path

import pytest


def verifier():
    path = Path(__file__).resolve().parents[1] / "scripts/verify.py"
    spec = importlib.util.spec_from_file_location("verification_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "counts",
    [dict(tests=0), dict(tests=1, skipped=1), dict(tests=1, failures=1), dict(tests=1, errors=1)],
)
def test_unexecuted_or_failed_tests_cannot_be_reported_as_pass(tmp_path, counts):
    attributes = " ".join(f'{key}="{value}"' for key, value in counts.items())
    path = tmp_path / "result.xml"
    path.write_text(f"<testsuites><testsuite {attributes}/></testsuites>")
    with pytest.raises(RuntimeError, match="not all executed"):
        verifier().read_test_totals(path)


def test_successful_test_counts_are_retained(tmp_path):
    path = tmp_path / "result.xml"
    path.write_text(
        '<testsuites><testsuite tests="2" failures="0" errors="0" skipped="0"/></testsuites>'
    )
    assert verifier().read_test_totals(path) == dict(tests=2, failures=0, errors=0, skipped=0)


def test_frozen_fixture_changes_invalidate_verification_hashes(tmp_path, monkeypatch):
    module = verifier()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    for name in ("pyproject.toml", "uv.lock", ".python-version", "README.md"):
        (tmp_path / name).write_text("input")
    (tmp_path / "records").mkdir()
    fixture = tmp_path / "records/webui-final-live.json"
    fixture.write_text("old input")
    before = module.hashes()
    (tmp_path / "records/current-results.json").write_text("generated output")
    assert module.hashes() == before
    fixture.write_text("changed input")
    assert module.hashes() != before
