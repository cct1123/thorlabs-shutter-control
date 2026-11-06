"""Verify the full source suite and exact wheel without instruments or lab networking.

Run: uv run --locked --offline --group dev --extra gui python scripts/verify.py
All dependencies must be cached. TCP tests use local loopback only.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import tomllib
import uuid
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def hashes():
    patterns = ("src/**/*.py", "tests/*.py", "scripts/*.py", "docs/examples/*", "config/*.toml")
    files = {ROOT / name for name in ("pyproject.toml", "uv.lock", ".python-version")}
    files.update(p for pattern in patterns for p in ROOT.glob(pattern) if p.is_file())
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
    }


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
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
        run(
            label + " tests",
            python,
            "-m pytest -q --tb=short -p no:cacheprovider",
            ROOT / "tests",
            "--basetemp",
            work / label,
            "--junitxml",
            ROOT / f"records/{label}-tests.xml",
            cwd=work,
        )

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
            for p in (ROOT / "src").rglob("*.py")
        }
        actual = {name: archive.read(name) for name in archive.namelist() if name.endswith(".py")}
        if actual != expected:
            raise RuntimeError("Wheel Python files differ from source")
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
    isolated = [*uv, "run", "--offline", "--no-project", "--python", python, "python", "-I"]
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
        scope="offline/simulated and TCP loopback only; no instruments or lab network",
        python=sys.version,
        deadline_clock=vars(time.get_clock_info("perf_counter")),
        tested_paths=["tests"],
        source_sha256=before,
        wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
        wheel_source_parity="PASS",
        results=results,
    )
    (ROOT / "records/direct-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    # Preserve failed-run diagnostics, but remove this successful disposable environment.
    if work.resolve().parent != (ROOT / "tmp").resolve():
        raise RuntimeError("Refusing to remove verification data outside the project tmp directory")
    shutil.rmtree(work)
    print("All software checks passed; physical/Ethernet/driver acceptance remains open.")


if __name__ == "__main__":
    main()
