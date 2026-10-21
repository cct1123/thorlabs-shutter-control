"""Stage-1 offline preflight and discovery-result checks.

Live SDK discovery is explicitly selected with --discover; it never connects.
Default/--preflight reads local metadata and the bench record only.
"""

import argparse
import importlib.metadata
import json
import platform
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

from stage_0 import DEFAULT_RECORD, record_gaps


def check_discovery(record, enumerate_serials):
    """Exercise an explicitly supplied enumerator against a complete bench record.

    Tests supply KCubeShutter.discover backed by the existing software SDK double.
    This checks enumeration only, not connection, shutter mapping or physical motion.
    """
    result = {
        "stage": 1,
        "test": "TEST-003 (enumeration subcase only)",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "scope": "enumeration only; no connection or physical mapping validation",
        "status": "BLOCKED",
    }
    gaps = record_gaps(record)
    if gaps:
        return dict(result, record_gaps=gaps)
    expected = sorted(pair["serial"] for pair in record["pairs"])
    result["expected_serials"] = expected
    try:
        observed = list(enumerate_serials())
        if any(not isinstance(s, str) or not re.fullmatch(r"68[0-9]{6}", s) for s in observed):
            return dict(result, status="ERROR", error="Discovery returned an invalid KSC101 serial")
        if len(observed) != len(set(observed)):
            return dict(result, status="ERROR", error="Discovery returned duplicate serials")
        observed = sorted(observed)
    except Exception as exc:
        return dict(result, status="ERROR", error=f"Discovery failed: {type(exc).__name__}: {exc}")
    missing = sorted(set(expected) - set(observed))
    unexpected = sorted(set(observed) - set(expected))
    return dict(
        result,
        status="MATCH" if not missing and not unexpected else "MISMATCH",
        observed_serials=observed,
        missing_serials=missing,
        unexpected_serials=unexpected,
    )


def preflight(record):
    """Inspect local Python/distribution metadata only; never import the vendor SDK."""
    gaps = record_gaps(record)
    packages = {}
    for name in ("thorlabs-shutter-control", "dash", "pythonnet", "pytest"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
            gaps.append(f"Missing Python distribution: {name}; run uv sync --locked")
    host = {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "python_bitness": f"x{struct.calcsize('P') * 8}",
        "python_executable": sys.executable,
    }
    if host["os"] != "Windows" or host["python_bitness"] != "x64":
        gaps.append("Live backend preparation requires Windows x64; no device access attempted")
    reported = record.get("host") if isinstance(record, dict) else None
    if isinstance(reported, dict):
        for field in ("python_version", "python_bitness"):
            if reported.get(field) is not None and reported[field] != host[field]:
                gaps.append(f"host.{field}: recorded value differs from this interpreter")
    return {
        "stage": 1,
        "scope": "offline preflight only; SDK/driver/physical operation unverified",
        "hardware_access": "NOT_REQUESTED",
        "status": "INCOMPLETE" if gaps else "RECORD_AND_ENVIRONMENT_CHECKS_COMPLETE",
        "host": host,
        "python_distributions": packages,
        "gaps": gaps,
        "physical_test_status": "UNTESTED",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD, help="Local bench JSON file")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="Offline checks only (default)")
    mode.add_argument(
        "--discover", action="store_true", help="Enumerate USB identities without connecting"
    )
    args = parser.parse_args(argv)
    if args.discover:
        from thorlabs_shutter_control import KCubeShutter

        try:
            result = {
                "stage": 1,
                "status": "ENUMERATED",
                "hardware_access": "ENUMERATION_ONLY",
                "observed_serials": KCubeShutter().discover(),
                "physical_test_status": "UNTESTED",
            }
        except Exception as exc:
            result = {"stage": 1, "status": "ERROR", "error": str(exc)}
        print(json.dumps(result, indent=2))
        return 2 if result["status"] == "ERROR" else 0
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "stage": 1,
                    "status": "ERROR",
                    "hardware_access": "NOT_REQUESTED",
                    "error": f"Cannot read bench record: {exc}",
                },
                indent=2,
            )
        )
        return 2
    result = preflight(record)
    print(json.dumps(result, indent=2))
    return 1 if result["gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
