"""Check a manually completed bench record; never load an SDK or contact hardware.

Run from the checkout: python docs/hardware_tests/stage_0.py
Exit 0 means the initial-stage record fields are complete, not launch approval.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

DEFAULT_RECORD = Path(__file__).resolve().parents[2] / "records" / "hardware-bench.json"
FIELDS = {
    "hub": (
        "model",
        "supply_model",
        "supply_rating",
        "power_and_docking_reference",
        "usb_host_path",
    ),
    "host": (
        "os",
        "python_version",
        "python_bitness",
        "kinesis_directory",
        "kinesis_version",
        "kinesis_bitness",
        "net_runtime",
        "usb_driver",
    ),
    "bench": (
        "operator",
        "observer_and_method",
        "independent_protection",
        "physical_shutdown_procedure",
        "recovery_operator",
    ),
}
PAIR_FIELDS = (
    "label",
    "serial",
    "firmware",
    "shutter_model",
    "bay_label",
    "shutter_cable_label",
    "initial_blade_position",
    "initial_mode_and_output",
    "key_and_interlock",
    "external_trigger_arrangement",
)


def known_text(value):
    return isinstance(value, str) and value.strip().casefold() not in {
        "",
        "unknown",
        "tbd",
        "todo",
        "null",
        "none",
        "n/a",
        "?",
    }


def record_gaps(record):
    """Return structural/consistency gaps; no physical fact is verified here."""
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    gaps = []
    try:
        observed = datetime.fromisoformat(record.get("observed_at") or "")
        if observed.utcoffset() is None:
            raise ValueError
    except (TypeError, ValueError):
        gaps.append("observed_at: supply an ISO timestamp with timezone for the bench observation")
    for section, fields in FIELDS.items():
        values = record.get(section)
        if not isinstance(values, dict):
            gaps.append(f"{section}: must be an object")
            continue
        for field in fields:
            if not known_text(values.get(field)):
                gaps.append(f"{section}.{field}: missing/unknown text")
    host = record.get("host")
    if isinstance(host, dict):
        if not known_text(host.get("os")) or "windows" not in host["os"].casefold():
            gaps.append("host.os: the current backend requires Windows")
        for field in ("python_bitness", "kinesis_bitness"):
            if host.get(field) != "x64":
                gaps.append(f"host.{field}: this bench plan uses x64")
    bench = record.get("bench")
    if not isinstance(bench, dict) or bench.get("one_owner_confirmed") is not True:
        gaps.append("bench.one_owner_confirmed: must be true")
    pairs = record.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        gaps.append("pairs: record the actual installed pairs; do not guess the count")
        return gaps
    identities = {field: set() for field in ("serial", "label", "bay_label", "shutter_cable_label")}
    for index, pair in enumerate(pairs):
        prefix = f"pairs[{index}]"
        if not isinstance(pair, dict):
            gaps.append(f"{prefix}: must be an object")
            continue
        for field in PAIR_FIELDS:
            value = pair.get(field)
            if not known_text(value):
                gaps.append(f"{prefix}.{field}: missing/unknown text")
            elif field in identities:
                if value.strip() in identities[field]:
                    gaps.append(f"{prefix}.{field}: duplicate identity/mapping")
                identities[field].add(value.strip())
        if not isinstance(pair.get("serial"), str) or not re.fullmatch(
            r"68[0-9]{6}", pair["serial"]
        ):
            gaps.append(
                f"{prefix}.serial: requires an actual eight-digit KSC101 serial starting 68"
            )
        if pair.get("shutter_model") not in ("SH05R", "SH05R/M"):
            gaps.append(f"{prefix}.shutter_model: review a model other than SH05R or SH05R/M")
    return gaps


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD, help="Local bench JSON file")
    args = parser.parse_args(argv)
    print("Offline record review only. Hardware tests are explicitly selected in later tools.")
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Cannot read bench record: {exc}")
        return 2
    gaps = record_gaps(record)
    if gaps:
        print("Stage 0 record INCOMPLETE:")
        for gap in gaps:
            print(f"- {gap}")
        return 1
    print("Stage 0 record fields COMPLETE; human review and physical verification still required.")
    print(
        "Later-stage operating/TTL limits are not assessed. No discovery or launch is authorized."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
