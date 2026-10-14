#!/usr/bin/env python3
"""Deterministic validation for Ease domain-alignment stage artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

UC_PATTERN = re.compile(r"^UC-[0-9]{3}$")
BR_PATTERN = re.compile(r"^BR-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+){0,2}$")
FEATURE_PATTERN = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
PHASES = ("flow-1", "flow-2", "flow-3")
CHANGED_DELTAS = {"NEW", "MOD"}
DDR_HEADINGS = {
    "Context",
    "Business Options",
    "Decision",
    "Business Rationale",
    "Compatibility and Migration",
    "Risks",
    "Acceptance Evidence",
    "Supersedes",
    "Related ADR",
    "Implementation Evidence",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--implementation", type=Path)
    return parser.parse_args()


def load_object(path: Path, label: str, failures: list[dict[str, str]]) -> dict[str, Any]:
    if not path.is_file():
        failures.append({"id": f"{label.upper()}_MISSING", "message": f"missing {path}"})
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append({"id": f"{label.upper()}_INVALID", "message": f"invalid JSON in {path}: {exc}"})
        return {}
    if not isinstance(value, dict):
        failures.append({"id": f"{label.upper()}_INVALID", "message": f"{path} root must be an object"})
        return {}
    return value


def require_keys(
    value: dict[str, Any],
    keys: set[str],
    label: str,
    failures: list[dict[str, str]],
) -> None:
    for key in sorted(keys - set(value)):
        failures.append({"id": "REQUIRED_FIELD_MISSING", "message": f"{label} missing field: {key}"})


def reject_unknown_keys(
    value: dict[str, Any],
    allowed: set[str],
    label: str,
    failures: list[dict[str, str]],
) -> None:
    for key in sorted(set(value) - allowed):
        failures.append({"id": "UNKNOWN_FIELD", "message": f"{label} contains unknown field: {key}"})


def nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def validate_decision_refs(
    manifest_path: Path,
    element_id: str,
    element: dict[str, Any],
    failures: list[dict[str, str]],
) -> None:
    required = element.get("decision_required", False)
    refs = element.get("decision_refs", [])
    if not isinstance(required, bool):
        failures.append({"id": "DECISION_REQUIRED_INVALID", "message": f"{element_id}.decision_required must be boolean"})
        return
    if not isinstance(refs, list) or not all(isinstance(ref, str) and ref.strip() for ref in refs):
        failures.append({"id": "DECISION_REFS_INVALID", "message": f"{element_id}.decision_refs must be an array of paths"})
        return
    if required and not refs:
        failures.append({"id": "DECISION_REFS_MISSING", "message": f"{element_id} requires a DDR"})
        return

    domain_dir = manifest_path.parent.resolve()
    index_path = domain_dir / "decisions" / "README.md"
    index_text = ""
    if refs:
        if not index_path.is_file():
            failures.append({"id": "DECISION_INDEX_MISSING", "message": f"missing {index_path}"})
        else:
            index_text = index_path.read_text(encoding="utf-8")

    for ref in refs:
        candidate = (domain_dir / ref).resolve()
        try:
            candidate.relative_to(domain_dir)
        except ValueError:
            failures.append({"id": "DECISION_REF_UNSAFE", "message": f"unsafe DDR path: {ref}"})
            continue
        if not candidate.is_file():
            failures.append({"id": "DECISION_FILE_MISSING", "message": f"missing DDR: {ref}"})
            continue
        text = candidate.read_text(encoding="utf-8")
        if element_id not in text:
            failures.append({"id": "DECISION_ELEMENT_UNLINKED", "message": f"{ref} does not reference {element_id}"})
        headings = {
            line.removeprefix("## ").strip()
            for line in text.splitlines()
            if line.startswith("## ")
        }
        for heading in sorted(DDR_HEADINGS - headings):
            failures.append({"id": "DECISION_HEADING_MISSING", "message": f"{ref} missing heading: {heading}"})
        title = next((line for line in text.splitlines() if line.startswith("# DDR-")), "")
        decision_id = title.split(":", 1)[0].removeprefix("# ").strip() if title else ""
        if not decision_id or decision_id not in index_text:
            failures.append({"id": "DECISION_NOT_INDEXED", "message": f"{ref} is not indexed in decisions/README.md"})


def validate_manifest(
    manifest_path: Path,
    manifest: dict[str, Any],
    failures: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    manifest_fields = {"schema_version", "feature_name", "baseline", "elements", "drift_status"}
    require_keys(manifest, manifest_fields, "manifest", failures)
    reject_unknown_keys(manifest, manifest_fields, "manifest", failures)
    if manifest.get("schema_version") != "1.0":
        failures.append({"id": "SCHEMA_VERSION_INVALID", "message": "manifest.schema_version must be 1.0"})
    if not FEATURE_PATTERN.fullmatch(str(manifest.get("feature_name", ""))):
        failures.append({"id": "FEATURE_NAME_INVALID", "message": "manifest.feature_name must be NNN-kebab-case"})

    baseline = manifest.get("baseline")
    if not isinstance(baseline, dict):
        failures.append({"id": "BASELINE_INVALID", "message": "manifest.baseline must be an object"})
    else:
        baseline_fields = {"status", "commit_id"}
        require_keys(baseline, baseline_fields, "baseline", failures)
        reject_unknown_keys(baseline, baseline_fields, "baseline", failures)
        if baseline.get("status") not in {"legacy-unverified", "analyzed", "designed", "verified"}:
            failures.append({"id": "BASELINE_STATUS_INVALID", "message": "baseline.status is invalid"})
        if not isinstance(baseline.get("commit_id"), str):
            failures.append({"id": "BASELINE_COMMIT_INVALID", "message": "baseline.commit_id must be a string"})

    elements = manifest.get("elements")
    if not isinstance(elements, list):
        failures.append({"id": "ELEMENTS_INVALID", "message": "manifest.elements must be an array"})
        return {}

    by_id: dict[str, dict[str, Any]] = {}
    for index, element in enumerate(elements):
        label = f"elements[{index}]"
        if not isinstance(element, dict):
            failures.append({"id": "ELEMENT_INVALID", "message": f"{label} must be an object"})
            continue
        element_required = {"id", "kind", "status", "delta", "source_refs"}
        element_allowed = element_required | {"decision_required", "decision_refs"}
        require_keys(element, element_required, label, failures)
        reject_unknown_keys(element, element_allowed, label, failures)
        element_id = str(element.get("id", ""))
        kind = element.get("kind")
        expected_pattern = UC_PATTERN if kind == "usecase" else BR_PATTERN if kind == "business-rule" else None
        if expected_pattern is None or not expected_pattern.fullmatch(element_id):
            failures.append({"id": "ELEMENT_ID_INVALID", "message": f"{label} has invalid kind/id combination: {kind}/{element_id}"})
        if element_id in by_id:
            failures.append({"id": "ELEMENT_ID_DUPLICATE", "message": f"duplicate domain element ID: {element_id}"})
        elif element_id:
            by_id[element_id] = element
        if element.get("status") not in {"active", "deprecated", "superseded"}:
            failures.append({"id": "ELEMENT_STATUS_INVALID", "message": f"{label}.status is invalid"})
        if element.get("delta") not in {"NEW", "MOD", "UNCHANGED", "NONE"}:
            failures.append({"id": "ELEMENT_DELTA_INVALID", "message": f"{label}.delta is invalid"})
        if element.get("status") == "active" and not nonempty_strings(element.get("source_refs")):
            failures.append({"id": "SOURCE_REFS_MISSING", "message": f"active element {element_id} has no source_refs"})
        validate_decision_refs(manifest_path, element_id, element, failures)

    drift = manifest.get("drift_status")
    if not isinstance(drift, dict):
        failures.append({"id": "DRIFT_STATUS_INVALID", "message": "manifest.drift_status must be an object"})
    else:
        drift_fields = {"status", "unresolved"}
        require_keys(drift, drift_fields, "drift_status", failures)
        reject_unknown_keys(drift, drift_fields, "drift_status", failures)
        if drift.get("status") not in {"clean", "warning", "blocking"}:
            failures.append({"id": "DRIFT_STATUS_INVALID", "message": "drift_status.status is invalid"})
        if not isinstance(drift.get("unresolved"), list):
            failures.append({"id": "DRIFT_UNRESOLVED_INVALID", "message": "drift_status.unresolved must be an array"})
    return by_id


def validate_evidence(
    artifact: dict[str, Any],
    label: str,
    expected_ids: set[str],
    known_ids: set[str],
    required_refs: tuple[str, ...],
    failures: list[dict[str, str]],
) -> None:
    if artifact.get("schema_version") != "1.0":
        failures.append({"id": "SCHEMA_VERSION_INVALID", "message": f"{label}.schema_version must be 1.0"})
    entries = artifact.get("entries")
    if not isinstance(entries, list):
        failures.append({"id": "EVIDENCE_ENTRIES_INVALID", "message": f"{label}.entries must be an array"})
        return

    covered: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            failures.append({"id": "EVIDENCE_ENTRY_INVALID", "message": f"{label}.entries[{index}] must be an object"})
            continue
        element_id = str(entry.get("element_id", ""))
        if element_id not in known_ids:
            failures.append({"id": "ORPHAN_ELEMENT_REFERENCE", "message": f"{label} references unknown element: {element_id}"})
        if element_id in covered:
            failures.append({"id": "EVIDENCE_ENTRY_DUPLICATE", "message": f"{label} repeats element: {element_id}"})
        covered.add(element_id)
        for field in required_refs:
            if not nonempty_strings(entry.get(field)):
                failures.append({"id": "EVIDENCE_REFS_MISSING", "message": f"{label} element {element_id} has no {field}"})

    for element_id in sorted(expected_ids - covered):
        failures.append({"id": "CHANGED_ELEMENT_UNCOVERED", "message": f"{label} does not cover changed element: {element_id}"})


def main() -> int:
    args = parse_args()
    failures: list[dict[str, str]] = []
    manifest = load_object(args.manifest, "manifest", failures)
    elements = validate_manifest(args.manifest, manifest, failures) if manifest else {}
    changed_ids = {
        element_id
        for element_id, element in elements.items()
        if element.get("status") == "active" and element.get("delta") in CHANGED_DELTAS
    }

    if args.phase in {"flow-2", "flow-3"}:
        if args.matrix is None:
            failures.append({"id": "MATRIX_ARGUMENT_MISSING", "message": f"{args.phase} requires --matrix"})
        else:
            matrix = load_object(args.matrix, "matrix", failures)
            if matrix:
                validate_evidence(matrix, "matrix", changed_ids, set(elements), ("design_refs",), failures)

    if args.phase == "flow-3":
        if args.implementation is None:
            failures.append({"id": "IMPLEMENTATION_ARGUMENT_MISSING", "message": "flow-3 requires --implementation"})
        else:
            implementation = load_object(args.implementation, "implementation", failures)
            if implementation:
                validate_evidence(
                    implementation,
                    "implementation",
                    changed_ids,
                    set(elements),
                    ("code_refs", "test_refs"),
                    failures,
                )
        drift = manifest.get("drift_status", {}) if manifest else {}
        if isinstance(drift, dict) and (drift.get("status") == "blocking" or drift.get("unresolved")):
            failures.append({"id": "DOMAIN_DRIFT_UNRESOLVED", "message": "Flow 3 has unresolved or blocking domain drift"})

    report = {
        "status": "failed" if failures else "passed",
        "phase": args.phase,
        "changed_elements": len(changed_ids),
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
