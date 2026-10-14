#!/usr/bin/env python3
"""Validate the cross-phase DOMAIN_ID / CHANGE_ID mapping."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CHANGE_PATTERN = re.compile(r"^[0-9]{3,14}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DOMAIN_PATTERN = re.compile(r"^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
FIELDS = {"schema_version", "change_id", "domain_id", "track", "requirement_source", "git"}
REQUIRED_FIELDS = {"schema_version", "change_id", "domain_id", "track", "requirement_source"}
GIT_FIELDS = {"branch", "worktree_path", "worktree_policy", "isolation_status"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--change")
    parser.add_argument("--domain")
    parser.add_argument("--track", choices=("brd", "trd"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[dict[str, str]] = []
    try:
        data: Any = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        data = {}
        failures.append({"id": "FLOW_CONTEXT_INVALID_JSON", "message": str(exc)})

    if not isinstance(data, dict):
        failures.append({"id": "FLOW_CONTEXT_INVALID", "message": "root must be an object"})
        data = {}
    else:
        for key in sorted(REQUIRED_FIELDS - set(data)):
            failures.append({"id": "FLOW_CONTEXT_FIELD_MISSING", "message": f"missing field: {key}"})
        for key in sorted(set(data) - FIELDS):
            failures.append({"id": "FLOW_CONTEXT_FIELD_UNKNOWN", "message": f"unknown field: {key}"})

    if data.get("schema_version") != "1.0":
        failures.append({"id": "FLOW_CONTEXT_SCHEMA_VERSION", "message": "schema_version must be 1.0"})
    if not CHANGE_PATTERN.fullmatch(str(data.get("change_id", ""))):
        failures.append({"id": "FLOW_CONTEXT_CHANGE_ID", "message": "invalid change_id"})

    track = data.get("track")
    domain_id = data.get("domain_id")
    if track not in {"brd", "trd"}:
        failures.append({"id": "FLOW_CONTEXT_TRACK", "message": "track must be brd or trd"})
    elif track == "brd" and (not isinstance(domain_id, str) or not DOMAIN_PATTERN.fullmatch(domain_id)):
        failures.append({"id": "FLOW_CONTEXT_DOMAIN_ID", "message": "BRD requires a valid domain_id"})
    elif track == "trd" and domain_id is not None:
        failures.append({"id": "FLOW_CONTEXT_DOMAIN_ID", "message": "TRD domain_id must be null"})

    source = data.get("requirement_source")
    if not isinstance(source, str) or not source.strip():
        failures.append({"id": "FLOW_CONTEXT_REQUIREMENT_SOURCE", "message": "requirement_source must be non-empty"})

    git_context = data.get("git")
    if git_context is not None:
        if not isinstance(git_context, dict):
            failures.append({"id": "FLOW_CONTEXT_GIT", "message": "git must be an object"})
        else:
            for key in sorted(GIT_FIELDS - set(git_context)):
                failures.append({"id": "FLOW_CONTEXT_GIT_FIELD_MISSING", "message": f"missing git field: {key}"})
            for key in sorted(set(git_context) - GIT_FIELDS):
                failures.append({"id": "FLOW_CONTEXT_GIT_FIELD_UNKNOWN", "message": f"unknown git field: {key}"})

            policy = git_context.get("worktree_policy")
            isolation_status = git_context.get("isolation_status")
            branch = git_context.get("branch")
            worktree_path = git_context.get("worktree_path")
            if policy not in {"auto", "required", "reuse", "off"}:
                failures.append({"id": "FLOW_CONTEXT_WORKTREE_POLICY", "message": "invalid worktree_policy"})
            if not isinstance(branch, str) or not branch.strip():
                failures.append({"id": "FLOW_CONTEXT_GIT_BRANCH", "message": "git.branch must be non-empty"})
            if not isinstance(worktree_path, str) or not worktree_path.strip():
                failures.append({"id": "FLOW_CONTEXT_WORKTREE_PATH", "message": "git.worktree_path must be non-empty"})
            if policy == "off":
                if isolation_status != "waived":
                    failures.append({"id": "FLOW_CONTEXT_ISOLATION_STATUS", "message": "off policy requires isolation_status=waived"})
            else:
                expected_branch = f"feature/{data.get('change_id', '')}"
                if isolation_status != "active":
                    failures.append({"id": "FLOW_CONTEXT_ISOLATION_STATUS", "message": "enabled worktree policy requires isolation_status=active"})
                if branch != expected_branch:
                    failures.append({"id": "FLOW_CONTEXT_GIT_BRANCH", "message": f"git.branch must be {expected_branch}"})

    if args.change is not None and data.get("change_id") != args.change:
        failures.append({"id": "FLOW_CONTEXT_EXPECTED_CHANGE", "message": "change_id does not match the requested change"})
    if args.domain is not None and data.get("domain_id") != args.domain:
        failures.append({"id": "FLOW_CONTEXT_EXPECTED_DOMAIN", "message": "domain_id does not match the requested domain"})
    if args.track is not None and data.get("track") != args.track:
        failures.append({"id": "FLOW_CONTEXT_EXPECTED_TRACK", "message": "track does not match the requested track"})

    print(json.dumps({"status": "failed" if failures else "passed", "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
