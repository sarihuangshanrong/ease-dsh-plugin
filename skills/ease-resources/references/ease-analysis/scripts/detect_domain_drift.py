#!/usr/bin/env python3
"""Detect domain-impacting Git changes and enforce semantic-review policy."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

VERDICTS = {"no-semantic-change", "aligned-domain-change", "semantic-drift"}
DOMAIN_MARKER = re.compile(r"\b(?:UC-\d{3}|BR-\d{3}-[a-z0-9]+(?:-[a-z0-9]+){0,2})\b", re.IGNORECASE)
SCANNED_CODE_SUFFIXES = {
    ".java", ".kt", ".go", ".py", ".ts", ".tsx", ".js", ".jsx",
    ".cs", ".rs", ".rb", ".php", ".swift",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", help="deprecated compatibility alias for both --change and --domain")
    parser.add_argument("--change", help="per-change execution id under .eases")
    parser.add_argument("--domain", help="durable domain id under docs/domains")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--policy", choices=("warn", "block"), default="block")
    parser.add_argument("--semantic-review", type=Path)
    args = parser.parse_args()
    if not (args.change or args.feature):
        parser.error("one of --change or --feature is required")
    if not (args.domain or args.feature):
        parser.error("one of --domain or --feature is required")
    return args


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def normalize_path(value: str) -> str:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe repository-relative path: {value}")
    return str(path)


def changed_files(repo_root: Path, base: str, head: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-only", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return {normalize_path(line.strip()) for line in result.stdout.splitlines() if line.strip()}


def resolve_revision(repo_root: Path, revision: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", f"{revision}^{{commit}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def domain_markers_at_revision(repo_root: Path, head: str, path: str) -> set[str]:
    """Read a changed source file from the inspected commit, never from the worktree."""
    if path.startswith(("docs/", ".eases/")) or PurePosixPath(path).suffix.lower() not in SCANNED_CODE_SUFFIXES:
        return set()
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{head}:{path}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:  # Deleted files have no blob at HEAD.
        return set()
    contents = result.stdout.decode("utf-8", errors="ignore")
    return {match.group(0).upper() for match in DOMAIN_MARKER.finditer(contents)}


def validate_review(
    review: dict[str, Any],
    feature: str,
    base: str,
    head: str,
    impacted: set[str],
    domain_docs_changed: bool,
) -> tuple[str, list[dict[str, str]]]:
    failures: list[dict[str, str]] = []
    required = {
        "schema_version", "feature_name", "base_commit", "head_commit",
        "verdict", "risk_level", "impacted_elements", "evidence", "reviewer",
        "human_approval",
    }
    for key in sorted(required - set(review)):
        failures.append({"id": "SEMANTIC_REVIEW_FIELD_MISSING", "message": f"missing field: {key}"})
    for key in sorted(set(review) - required):
        failures.append({"id": "SEMANTIC_REVIEW_FIELD_UNKNOWN", "message": f"unknown field: {key}"})
    if review.get("schema_version") != "1.0":
        failures.append({"id": "SEMANTIC_REVIEW_SCHEMA", "message": "schema_version must be 1.0"})
    if review.get("feature_name") != feature:
        failures.append({"id": "SEMANTIC_REVIEW_FEATURE", "message": "feature_name does not match"})
    if review.get("base_commit") != base or review.get("head_commit") != head:
        failures.append({"id": "SEMANTIC_REVIEW_RANGE", "message": "review commit range does not match the inspected diff"})
    verdict = str(review.get("verdict", ""))
    if verdict not in VERDICTS:
        failures.append({"id": "SEMANTIC_REVIEW_VERDICT", "message": "invalid verdict"})
    reviewed = review.get("impacted_elements")
    valid_reviewed = (
        isinstance(reviewed, list)
        and bool(reviewed)
        and all(isinstance(item, str) and item.strip() for item in reviewed)
        and len(reviewed) == len(set(reviewed))
    )
    if not valid_reviewed or set(reviewed) != impacted:
        failures.append({"id": "SEMANTIC_REVIEW_COVERAGE", "message": "impacted_elements must exactly match detected elements"})
    for field in ("evidence", "reviewer"):
        if not isinstance(review.get(field), str) or not str(review[field]).strip():
            failures.append({"id": "SEMANTIC_REVIEW_EVIDENCE", "message": f"{field} must be non-empty"})
    risk_level = review.get("risk_level")
    if risk_level not in {"low", "medium", "high"}:
        failures.append({"id": "SEMANTIC_REVIEW_RISK", "message": "risk_level must be low, medium or high"})
    human_approval = review.get("human_approval")
    if not isinstance(human_approval, str):
        failures.append({"id": "SEMANTIC_REVIEW_HUMAN_APPROVAL", "message": "human_approval must be a string"})
    elif risk_level == "high" and verdict in {"no-semantic-change", "aligned-domain-change"} and not human_approval.strip():
        failures.append({"id": "HIGH_RISK_HUMAN_APPROVAL_REQUIRED", "message": "high-risk semantic clearance requires human approval"})
    if verdict == "aligned-domain-change" and not domain_docs_changed:
        failures.append({"id": "ALIGNED_CHANGE_WITHOUT_DOMAIN_DOCS", "message": "aligned-domain-change requires domain documents in the diff"})
    return verdict, failures


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    change_id = args.change or args.feature
    domain_id = args.domain or args.feature
    failures: list[dict[str, str]] = []
    implementation_path = (
        repo_root / ".eases" / change_id / "flow-3-implement" /
        "checklists" / "domain-implementation-alignment.json"
    )
    try:
        implementation = load_json(implementation_path)
        base_commit = resolve_revision(repo_root, args.base)
        head_commit = resolve_revision(repo_root, args.head)
        changed = changed_files(repo_root, base_commit, head_commit)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "failed", "failures": [{"id": "DRIFT_INPUT_INVALID", "message": str(exc)}]}, indent=2))
        return 1

    watched_by_element: dict[str, set[str]] = {}
    entries = implementation.get("entries", [])
    if not isinstance(entries, list):
        failures.append({"id": "IMPLEMENTATION_ENTRIES_INVALID", "message": "implementation.entries must be an array"})
        entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        element_id = str(entry.get("element_id", ""))
        refs: set[str] = set()
        for field in ("code_refs", "test_refs"):
            values = entry.get(field, [])
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str) and value.strip():
                        try:
                            refs.add(normalize_path(value))
                        except ValueError as exc:
                            failures.append({"id": "WATCH_PATH_INVALID", "message": str(exc)})
        watched_by_element[element_id] = refs

    impacted = {
        element_id for element_id, watched in watched_by_element.items()
        if changed.intersection(watched)
    }
    for path in sorted(changed):
        for marker in sorted(domain_markers_at_revision(repo_root, head_commit, path)):
            if marker not in watched_by_element:
                failures.append({
                    "id": "UNKNOWN_DOMAIN_MARKER",
                    "message": f"{path} references unknown domain element {marker}",
                })
                continue
            impacted.add(marker)
            if path not in watched_by_element[marker]:
                failures.append({
                    "id": "UNMAPPED_DOMAIN_FILE",
                    "message": f"{path} references {marker} but is absent from its implementation evidence",
                })
    domain_prefix = f"docs/domains/{domain_id}/"
    domain_docs_changed = any(path.startswith(domain_prefix) for path in changed)

    verdict = "not-required"
    status = "blocked" if failures else "clean"
    if impacted and not failures:
        if args.semantic_review is None:
            status = "review-required"
        else:
            try:
                review = load_json(args.semantic_review)
                verdict, review_failures = validate_review(
                    review, change_id, base_commit, head_commit, impacted, domain_docs_changed
                )
                failures.extend(review_failures)
                if review_failures:
                    status = "blocked"
                elif verdict == "semantic-drift":
                    status = "blocked"
                    failures.append({"id": "SEMANTIC_DRIFT_CONFIRMED", "message": "semantic drift requires Flow 1 realignment"})
                else:
                    status = "accepted"
            except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
                status = "blocked"
                failures.append({"id": "SEMANTIC_REVIEW_INVALID", "message": str(exc)})

    report = {
        "status": status,
        "policy": args.policy,
        "feature_name": change_id,
        "change_id": change_id,
        "domain_id": domain_id,
        "base_commit": base_commit,
        "head_commit": head_commit,
        "changed_files": sorted(changed),
        "impacted_elements": sorted(impacted),
        "domain_docs_changed": domain_docs_changed,
        "semantic_verdict": verdict,
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        return 0 if args.policy == "warn" else 1
    if status == "review-required":
        return 0 if args.policy == "warn" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
