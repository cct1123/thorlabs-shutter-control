"""Verify software tests and the exact wheel without instruments or lab networking.

Run: uv run --locked --offline --group dev --extra gui python scripts/verify.py
All dependencies must be cached. TCP tests use local loopback only.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
import uuid
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def hashes():
    patterns = (
        "src/**/*.py",
        "src/**/*.css",
        "tests/*.py",
        "scripts/*.py",
        "docs/examples/*",
        "config/*.toml",
    )
    files = {ROOT / name for name in ("pyproject.toml", "uv.lock", ".python-version", "README.md")}
    files.add(ROOT / "records/webui-final-live.json")  # Frozen input to the UI regressions.
    files.update(p for pattern in patterns for p in ROOT.glob(pattern) if p.is_file())
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
    }


def read_test_totals(path):
    """A successful pytest process alone cannot turn skipped/uncollected tests into PASS."""
    totals = dict(tests=0, failures=0, errors=0, skipped=0)
    for suite in ElementTree.parse(path).getroot().iter("testsuite"):
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    if totals["tests"] <= 0 or any(totals[key] for key in ("failures", "errors", "skipped")):
        raise RuntimeError(f"Required tests were not all executed and passed: {totals}")
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test-path",
        action="append",
        type=Path,
        help="Select a test file/directory under tests (repeatable); default is the full suite",
    )
    parser.add_argument(
        "--record-prefix",
        default="",
        help="Prefix record filenames to preserve earlier campaigns (letters/digits/dashes only)",
    )
    args = parser.parse_args()
    if args.record_prefix and not re.fullmatch(r"[a-z0-9-]{1,48}", args.record_prefix):
        parser.error("--record-prefix must contain1..48 lowercase letters/digits/dashes")
    selected = [path.resolve() for path in (args.test_path or [ROOT / "tests"])]
    for path in selected:
        if not path.is_relative_to(ROOT / "tests") or not path.exists():
            parser.error("--test-path must be an existing path under this repository's tests")
        if path.is_file() and path.suffix != ".py":
            parser.error("--test-path files must be Python tests")
    before = hashes()
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv must be installed")
    uv, source_python = [uv], [sys.executable]
    work = ROOT / "tmp" / ("verification-" + uuid.uuid4().hex)
    work.mkdir(parents=True)
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    results = []
    summaries = {}

    def run(label, prefix, flags, *arguments, cwd=ROOT, reject=False):
        """Split only our static flags; keep paths/code as separate argv values."""
        print(label, flush=True)
        command = [str(arg) for arg in (*prefix, *flags.split(), *arguments)]
        started = time.perf_counter()
        result = subprocess.run(
            command, cwd=cwd, env=environment, text=True, capture_output=True, timeout=120
        )
        results.append(
            dict(
                test=label,
                command=command,
                returncode=result.returncode,
                elapsed_s=time.perf_counter() - started,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        )
        if (result.returncode == 0) == reject:
            raise RuntimeError(
                f"{label}: unexpected exit {result.returncode}\n{result.stdout}\n{result.stderr}"
            )

    def tests(label, python):
        report = ROOT / f"records/{args.record_prefix}{label}-tests.xml"
        run(
            label + " tests",
            python,
            "-m pytest -q --tb=short -p no:cacheprovider",
            *selected,
            "--basetemp",
            work / label,
            "--junitxml",
            report,
            cwd=work,
        )
        summaries[label] = read_test_totals(report)

    run("lock current", uv, "lock --check --offline")
    for check in ("check", "format --check"):
        run(
            "ruff " + check,
            source_python,
            "-m ruff " + check + " --no-cache",
            "src",
            "tests",
            "scripts",
            "docs/examples",
        )
    tests("offline", source_python)
    run(
        "build locked backend",
        source_python,
        "-m hatchling build -t wheel -d",
        work / "build-wheel",
    )
    (wheel,) = (work / "build-wheel").glob("*.whl")
    with ZipFile(wheel) as archive:
        expected = {
            p.relative_to(ROOT / "src").as_posix(): p.read_bytes()
            for p in (ROOT / "src").rglob("*")
            if p.is_file() and p.suffix in (".py", ".css")
        }
        actual = {
            name: archive.read(name)
            for name in archive.namelist()
            if name.endswith((".py", ".css"))
        }
        if actual != expected:
            raise RuntimeError("Wheel runtime Python/CSS files differ from source")
    clean = work / "clean"
    run("clean venv", uv, "venv --offline --python 3.12", clean)
    python = clean / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    requirements = work / "requirements.txt"
    run(
        "locked clean dependencies",
        uv,
        "export --locked --offline --extra gui --group dev --no-emit-project "
        "--format requirements-txt --output-file",
        requirements,
    )
    run(
        "clean sync",
        uv,
        "pip sync --offline --require-hashes --python",
        python,
        requirements,
    )
    run(
        "install exact wheel",
        uv,
        "pip install --offline --no-deps --python",
        python,
        wheel,
    )
    isolated = [*uv, "run", "--offline", "--no-project", "--python", python, "python", "-I", "-B"]
    run(
        "clean no SDK/native dependencies",
        isolated,
        "-c",
        """
import importlib.util, json, sys
import thorlabs_shutter_control as package
assert 'site-packages' in package.__file__
for name in ('pythonnet', 'clr', 'ftd2xx', 'serial'):
    assert importlib.util.find_spec(name) is None, name
assert not {'ftd2xx', 'serial', 'clr', 'pythonnet'} & set(sys.modules)
print(json.dumps({'python': sys.version, 'package': package.__file__}))
""",
        cwd=work,
    )
    run("clean CLI help", isolated, "-m thorlabs_shutter_control --help", cwd=work)
    run("clean WebUI help", isolated, "-m thorlabs_shutter_control gui --help", cwd=work)
    tests("wheel", isolated)
    for label in ("missing", "outdated"):
        folder = work / label
        folder.mkdir()
        project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        if label == "outdated":
            version = tomllib.loads(project)["project"]["version"]
            project = project.replace(f'version = "{version}"', f'version = "{version}.post1"', 1)
            shutil.copyfile(ROOT / "uv.lock", folder / "uv.lock")
        (folder / "pyproject.toml").write_text(project, encoding="utf-8")
        run(label + " lock rejected", uv, "lock --check --offline", cwd=folder, reject=True)
    run(
        "passive config validation",
        source_python,
        "-m thorlabs_shutter_control --config",
        ROOT / "config/shutters.example.toml",
        "check-config",
    )
    if before != hashes():
        raise RuntimeError(
            "Source, tests, tutorials, configuration or dependencies changed during verification"
        )
    (ROOT / "dist").mkdir(exist_ok=True)
    shutil.copyfile(wheel, ROOT / "dist" / wheel.name)
    report = dict(
        scope="Software checks for the listed paths only; no instruments or lab network",
        python=sys.version,
        deadline_clock=vars(time.get_clock_info("perf_counter")),
        tested_paths=[path.relative_to(ROOT).as_posix() for path in selected],
        test_totals=summaries,
        source_sha256=before,
        wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
        wheel_source_parity="PASS",
        results=results,
    )
    (ROOT / f"records/{args.record_prefix}direct-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    # Preserve failed-run diagnostics, but remove this successful disposable environment.
    if work.resolve().parent != (ROOT / "tmp").resolve():
        raise RuntimeError("Refusing to remove verification data outside the project tmp directory")
    shutil.rmtree(work)
    print("All software checks passed; physical/Ethernet/driver acceptance remains open.")


if __name__ == "__main__":
    main()
