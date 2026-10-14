#!/usr/bin/env python3
"""Validate the TRD Domain Impact Guard decision and route business impact."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FEATURE_PATTERN = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
IMPACTS = {"none", "potential", "confirmed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[dict[str, str]] = []
    try:
        data: Any = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        data = {}
        failures.append({"id": "DOMAIN_IMPACT_INVALID_JSON", "message": str(exc)})

    required = {"schema_version", "feature_name", "impact", "signals", "rationale"}
    allowed = required
    if not isinstance(data, dict):
        failures.append({"id": "DOMAIN_IMPACT_INVALID", "message": "root must be an object"})
        data = {}
    else:
        for key in sorted(required - set(data)):
            failures.append({"id": "DOMAIN_IMPACT_FIELD_MISSING", "message": f"missing field: {key}"})
        for key in sorted(set(data) - allowed):
            failures.append({"id": "DOMAIN_IMPACT_FIELD_UNKNOWN", "message": f"unknown field: {key}"})

    if data.get("schema_version") != "1.0":
        failures.append({"id": "DOMAIN_IMPACT_SCHEMA_VERSION", "message": "schema_version must be 1.0"})
    if not FEATURE_PATTERN.fullmatch(str(data.get("feature_name", ""))):
        failures.append({"id": "DOMAIN_IMPACT_FEATURE", "message": "feature_name must be NNN-kebab-case"})
    impact = data.get("impact")
    if impact not in IMPACTS:
        failures.append({"id": "DOMAIN_IMPACT_VALUE", "message": "impact must be none, potential or confirmed"})
    signals = data.get("signals")
    if not isinstance(signals, list) or not all(isinstance(item, str) and item.strip() for item in signals):
        failures.append({"id": "DOMAIN_IMPACT_SIGNALS", "message": "signals must be an array of non-empty strings"})
    rationale = data.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        failures.append({"id": "DOMAIN_IMPACT_RATIONALE", "message": "rationale must be non-empty"})

    redirect = not failures and impact in {"potential", "confirmed"}
    report = {
        "status": "invalid" if failures else "redirect-brd" if redirect else "passed",
        "impact": impact,
        "route": "/ease:flow-1-analyze-brd" if redirect else "continue-trd",
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        return 1
    return 2 if redirect else 0


if __name__ == "__main__":
    raise SystemExit(main())
