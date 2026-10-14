#!/usr/bin/env python3
"""Read-only acceptance entry point for Ease domain alignment."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--feature", help="deprecated compatibility alias for both --change and --domain")
    parser.add_argument("--change", help="per-change execution id under .eases")
    parser.add_argument("--domain", help="durable domain id under docs/domains")
    parser.add_argument("--level", choices=("flow-1", "flow-2", "flow-3", "ci"), required=True)
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--semantic-review", type=Path)
    args = parser.parse_args()
    if not (args.change or args.feature):
        parser.error("one of --change or --feature is required")
    if not (args.domain or args.feature):
        parser.error("one of --domain or --feature is required")
    return args


def run_check(command: list[str], cwd: Path) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    try:
        report = json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        report = {"status": "invalid-output", "stdout": result.stdout, "stderr": result.stderr}
    return {"command": command, "exit_code": result.returncode, "report": report}


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    change_id = args.change or args.feature
    domain_id = args.domain or args.feature
    script_dir = Path(__file__).resolve().parent
    validator = script_dir / "validate_domain_alignment.py"
    drift_detector = script_dir / "detect_domain_drift.py"
    context_validator = script_dir / "validate_flow_context.py"
    context = repo_root / ".eases" / change_id / "context.json"
    manifest = repo_root / "docs" / "domains" / domain_id / "domain-alignment.json"
    matrix = repo_root / ".eases" / change_id / "flow-2-design" / "alignment" / "domain-design-matrix.json"
    implementation = (
        repo_root / ".eases" / change_id / "flow-3-implement" /
        "checklists" / "domain-implementation-alignment.json"
    )

    phase = "flow-3" if args.level == "ci" else args.level
    validation_command = [
        sys.executable, str(validator), "--manifest", str(manifest), "--phase", phase,
    ]
    if phase in {"flow-2", "flow-3"}:
        validation_command.extend(["--matrix", str(matrix)])
    if phase == "flow-3":
        validation_command.extend(["--implementation", str(implementation)])

    checks = []
    if args.change or args.domain:
        checks.append(run_check([
            sys.executable, str(context_validator), "--input", str(context),
            "--change", change_id, "--domain", domain_id, "--track", "brd",
        ], repo_root))
    checks.append(run_check(validation_command, repo_root))
    if args.level == "ci":
        if not args.base:
            print(json.dumps({"status": "failed", "message": "ci level requires --base"}, indent=2))
            return 1
        drift_command = [
            sys.executable, str(drift_detector), "--repo-root", str(repo_root),
            "--change", change_id, "--domain", domain_id,
            "--base", args.base, "--head", args.head,
            "--policy", "block",
        ]
        if args.semantic_review:
            drift_command.extend(["--semantic-review", str(args.semantic_review)])
        checks.append(run_check(drift_command, repo_root))

    failed = any(int(check["exit_code"]) != 0 for check in checks)
    print(json.dumps({
        "status": "failed" if failed else "passed",
        "level": args.level,
        "change_id": change_id,
        "domain_id": domain_id,
        "checks": checks,
    }, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
