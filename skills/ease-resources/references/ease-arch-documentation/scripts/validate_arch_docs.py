#!/usr/bin/env python3
"""Deterministic quality gates for generated architecture documentation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


DOCUMENT_HEADINGS = {
    "01_SYSTEM_OVERVIEW.md": (
        "文档范围与基线",
        "系统职责与边界",
        "技术栈说明",
        "系统上下文",
        "整体架构图",
        "架构驱动力与机制",
        "部署与运行时",
        "故障域与恢复路径",
        "质量属性场景",
        "项目结构说明",
        "风险与待确认",
    ),
    "02_CORE_MODULES.md": (
        "文档范围与基线",
        "业务能力与模块边界",
        "模块职责说明",
        "代码结构图",
        "模块依赖与边界契约",
        "架构不变量与执行点",
        "关键业务流程",
        "耦合与演进热点",
        "数据所有权与变更影响",
        "风险与待确认",
    ),
    "03_API_INTERFACE.md": (
        "文档范围与基线",
        "协议与契约总览",
        "提供的接口",
        "消费的接口",
        "数据契约与错误语义",
        "端到端调用语义与故障传播",
        "安全、可靠性与兼容性",
        "风险与待确认",
    ),
    "04_DATA_MODEL.md": (
        "文档范围与基线",
        "数据存储与所有权总览",
        "核心数据模型",
        "数据流与血缘",
        "数据不变量与关键写路径",
        "一致性与事务",
        "数据分类分级与保护",
        "生命周期、保留与归档",
        "备份、恢复与迁移",
        "风险与待确认",
    ),
    "05_CONFIG_MANAGEMENT.md": (
        "文档范围与基线",
        "配置来源与优先级",
        "环境差异",
        "核心配置目录",
        "Secret 与访问控制",
        "配置控制面与失效半径",
        "变更、校验与回滚",
        "风险与待确认",
    ),
    "06_UTILS_LIBRARIES.md": (
        "文档范围与基线",
        "共享能力总览",
        "内部可复用组件",
        "外部依赖治理",
        "横切机制",
        "依赖中心性与演进约束",
        "升级、废弃与替代策略",
        "风险与待确认",
    ),
}
PREVIOUS_DOCUMENT_HEADINGS = {
    "01_SYSTEM_OVERVIEW.md": (
        "文档范围与基线", "系统职责与边界", "技术栈说明", "系统上下文", "整体架构图",
        "部署与运行时", "质量属性现状", "项目结构说明", "风险与待确认",
    ),
    "02_CORE_MODULES.md": (
        "文档范围与基线", "业务能力与模块边界", "模块职责说明", "代码结构图",
        "模块依赖与边界契约", "关键业务流程", "数据所有权与变更影响", "风险与待确认",
    ),
    "03_API_INTERFACE.md": (
        "文档范围与基线", "协议与契约总览", "提供的接口", "消费的接口",
        "数据契约与错误语义", "安全、可靠性与兼容性", "风险与待确认",
    ),
    "04_DATA_MODEL.md": (
        "文档范围与基线", "数据存储与所有权总览", "核心数据模型", "数据流与血缘",
        "一致性与事务", "数据分类分级与保护", "生命周期、保留与归档", "备份、恢复与迁移", "风险与待确认",
    ),
    "05_CONFIG_MANAGEMENT.md": (
        "文档范围与基线", "配置来源与优先级", "环境差异", "核心配置目录",
        "Secret 与访问控制", "变更、校验与回滚", "风险与待确认",
    ),
    "06_UTILS_LIBRARIES.md": (
        "文档范围与基线", "共享能力总览", "内部可复用组件", "外部依赖治理",
        "横切机制", "升级、废弃与替代策略", "风险与待确认",
    ),
}
LEGACY_DOCUMENT_HEADINGS = {
    "01_SYSTEM_OVERVIEW.md": ("技术栈说明", "整体架构图", "系统特性", "部署环境", "项目结构说明"),
    "02_CORE_MODULES.md": ("模块职责说明", "代码结构图", "模块间关系"),
    "03_API_INTERFACE.md": ("接口分类说明", "RMB 接口详情列表", "HTTP 接口详情列表"),
    "04_DATA_MODEL.md": ("ER 图设计", "核心表结构说明", "数据关系分析", "约束和安全"),
    "05_CONFIG_MANAGEMENT.md": ("环境配置分析", "配置文件说明", "配置加载机制", "安全管理"),
    "06_UTILS_LIBRARIES.md": ("公共方法库分析", "第三方依赖梳理", "自定义注解", "常量定义", "异常处理"),
}

EVIDENCE_PATTERN = re.compile(r"来源:\s+\S+:\d+(?:\s+\([^)]+\))?")
NUMBER_PREFIX_PATTERN = re.compile(r"^\d+(?:\.\d+)*[.)、]?\s*")
MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
MERMAID_START = re.compile(
    r"^(?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|"
    r"erDiagram|journey|gantt|pie|mindmap|timeline|quadrantChart|"
    r"requirementDiagram|gitGraph|C4\w*)\b"
)
HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
PLACEHOLDER_ONLY_PATTERN = re.compile(r"^\s*\[[^\]]+\]\s*$", re.DOTALL)
DEPTH_COLLECTIONS = (
    "critical_paths",
    "invariants",
    "quality_scenarios",
    "failure_propagations",
    "evolution_hotspots",
    "decision_realization",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("full", "partial"))
    parser.add_argument("--documents", nargs="*", default=[])
    parser.add_argument("--report", type=Path)
    parser.add_argument("--strict", action="store_true", help="Require schema 2.2 evidence and semantic admission")
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--semantic-review", type=Path)
    return parser.parse_args()


def normalize_heading(value: str) -> str:
    return NUMBER_PREFIX_PATTERN.sub("", value).strip()


def add_failure(failures: list[dict[str, str]], check_id: str, message: str) -> None:
    failures.append({"id": check_id, "message": message})


def extract_section(text: str, target: str) -> str | None:
    """Return a heading body up to the next heading of equal or higher level."""
    matches = list(re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.MULTILINE))
    for index, match in enumerate(matches):
        if normalize_heading(match.group(2)) != target:
            continue
        level = len(match.group(1))
        end = len(text)
        for next_match in matches[index + 1 :]:
            if len(next_match.group(1)) <= level:
                end = next_match.start()
                break
        return text[match.end() : end].strip()
    return None


def has_substantive_content(body: str) -> bool:
    cleaned = HTML_COMMENT_PATTERN.sub("", body).strip()
    if not cleaned or PLACEHOLDER_ONLY_PATTERN.fullmatch(cleaned):
        return False
    without_evidence = EVIDENCE_PATTERN.sub("", cleaned).strip()
    # Header + delimiter without body rows is an empty table, not content.
    lines = without_evidence.splitlines()
    kept = []
    i = 0
    while i < len(lines):
        if i + 1 < len(lines) and "|" in lines[i] and re.fullmatch(r"[\s|:\-]+", lines[i + 1]):
            i += 2
            continue
        if lines[i].strip() and not lines[i].lstrip().startswith("#"):
            kept.append(lines[i])
        i += 1
    return bool("\n".join(kept).strip())


def validate_document(path: Path, failures: list[dict[str, str]], warnings: list[dict[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        add_failure(failures, "EMPTY_DOCUMENT", f"{path.name} is empty")
        return

    current_sections = DOCUMENT_HEADINGS[path.name]
    previous_sections = PREVIOUS_DOCUMENT_HEADINGS[path.name]
    legacy_sections = LEGACY_DOCUMENT_HEADINGS[path.name]
    if all(extract_section(text, heading) is not None for heading in current_sections):
        required_sections = current_sections
    elif all(extract_section(text, heading) is not None for heading in previous_sections):
        required_sections = previous_sections
        warnings.append(
            {
                "id": "PREVIOUS_CONTENT_SCHEMA",
                "message": f"{path.name} uses architecture content schema 2.0; regenerate to add depth views",
            }
        )
    elif all(extract_section(text, heading) is not None for heading in legacy_sections):
        required_sections = legacy_sections
        warnings.append(
            {
                "id": "LEGACY_CONTENT_SCHEMA",
                "message": f"{path.name} uses the legacy architecture content schema; regenerate to migrate",
            }
        )
    else:
        required_sections = current_sections

    for required in required_sections:
        section = extract_section(text, required)
        if section is None:
            add_failure(failures, "MISSING_HEADING", f"{path.name} missing heading: {required}")
            continue
        if not has_substantive_content(section):
            add_failure(failures, "EMPTY_SECTION", f"{path.name} has no substantive content: {required}")
        if ("不适用" in section or "暂无可记录" in section) and not EVIDENCE_PATTERN.search(section):
            add_failure(
                failures,
                "NOT_APPLICABLE_WITHOUT_EVIDENCE",
                f"{path.name} marks {required} not applicable without scan evidence",
            )

    if not EVIDENCE_PATTERN.search(text):
        add_failure(failures, "EVIDENCE_MISSING", f"{path.name} has no valid source evidence")

    opening_fences = len(re.findall(r"^```", text, re.MULTILINE))
    if opening_fences % 2:
        add_failure(failures, "UNBALANCED_CODE_FENCE", f"{path.name} has an unbalanced code fence")

    for index, block in enumerate(MERMAID_PATTERN.findall(text), start=1):
        first_line = next((line.strip() for line in block.splitlines() if line.strip()), "")
        if not MERMAID_START.match(first_line):
            add_failure(
                failures,
                "MERMAID_STRUCTURE_INVALID",
                f"{path.name} Mermaid block {index} has an unsupported declaration",
            )

    if "```mermaid" in text.lower() and not MERMAID_PATTERN.search(text):
        add_failure(failures, "MERMAID_FENCE_INVALID", f"{path.name} contains an incomplete Mermaid block")

    if not MERMAID_PATTERN.search(text):
        warnings.append({"id": "NO_MERMAID", "message": f"{path.name} contains no Mermaid diagram"})


def resolve_index_file(docs_dir: Path, file_value: str) -> Path | None:
    candidate = Path(file_value)
    if candidate.is_absolute():
        return None

    docs_root = next((path for path in (docs_dir, *docs_dir.parents) if path.name == "docs"), None)
    project_root = docs_root.parent if docs_root else docs_dir
    roots = (docs_dir, project_root)
    for root in roots:
        resolved = (root / candidate).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if resolved.exists():
            return resolved
    return None


def validate_external_indexes(
    docs_dir: Path,
    metadata: dict[str, Any],
    failures: list[dict[str, str]],
    partitions: set[str] | None = None,
) -> None:
    indexes = metadata.get("indexes", {})
    if not isinstance(indexes, dict):
        add_failure(failures, "INDEXES_INVALID", "metadata.indexes must be an object")
        return

    for partition, summary in indexes.items():
        if partitions is not None and partition not in partitions:
            continue
        if not isinstance(summary, dict):
            continue
        if "file" not in summary:
            if partition == "architecture_analysis_index":
                validate_architecture_analysis_index(summary, failures)
            continue
        index_path = resolve_index_file(docs_dir, str(summary["file"]))
        if index_path is None:
            add_failure(failures, "INDEX_FILE_MISSING", f"{partition} index file is missing or unsafe")
            continue
        try:
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            add_failure(failures, "INDEX_JSON_INVALID", f"{partition} index is invalid JSON: {exc}")
            continue

        if partition == "architecture_analysis_index":
            validate_architecture_analysis_index(index_data, failures)

        expected_hash = summary.get("hash")
        if expected_hash:
            actual_hash = hashlib.sha256(index_path.read_bytes()).hexdigest()
            normalized_expected = str(expected_hash).removeprefix("sha256:")
            if actual_hash != normalized_expected:
                add_failure(failures, "INDEX_HASH_MISMATCH", f"{partition} index hash does not match")

        expected_counts = summary.get("counts")
        if expected_counts is not None:
            if not isinstance(expected_counts, dict) or not isinstance(index_data, dict):
                add_failure(failures, "INDEX_COUNTS_INVALID", f"{partition} counts must describe an object index")
                continue
            validate_index_counts(partition, expected_counts, index_data, failures)


def validate_architecture_analysis_index(
    index_data: Any,
    failures: list[dict[str, str]],
) -> None:
    """Validate traceability and minimum semantics of derived architecture views."""
    if not isinstance(index_data, dict):
        add_failure(failures, "DEPTH_INDEX_INVALID", "architecture analysis index must be an object")
        return

    for collection_name in DEPTH_COLLECTIONS:
        collection = index_data.get(collection_name)
        if not isinstance(collection, list):
            add_failure(
                failures,
                "DEPTH_COLLECTION_MISSING",
                f"architecture analysis index missing array: {collection_name}",
            )
            continue
        for position, item in enumerate(collection):
            label = f"{collection_name}[{position}]"
            if not isinstance(item, dict):
                add_failure(failures, "DEPTH_ITEM_INVALID", f"{label} must be an object")
                continue
            if not item.get("id"):
                add_failure(failures, "DEPTH_ID_MISSING", f"{label} has no stable id")
            derived_from = item.get("derived_from")
            if not isinstance(derived_from, list) or not derived_from:
                add_failure(failures, "DEPTH_DERIVATION_MISSING", f"{label} has no derived_from claims")

            if collection_name == "critical_paths":
                if not item.get("trigger") or not item.get("steps"):
                    add_failure(failures, "CRITICAL_PATH_INCOMPLETE", f"{label} has no trigger or steps")
                if not item.get("failure_propagation") and not item.get("failure_gap"):
                    add_failure(failures, "CRITICAL_PATH_FAILURE_MISSING", f"{label} has no failure branch or gap")
                if not item.get("recovery") and not item.get("recovery_gap"):
                    add_failure(failures, "CRITICAL_PATH_RECOVERY_MISSING", f"{label} has no recovery or gap")
            elif collection_name == "invariants":
                if not item.get("constraint") or (
                    not item.get("enforcement_point") and not item.get("enforcement_gap")
                ):
                    add_failure(failures, "INVARIANT_ENFORCEMENT_MISSING", f"{label} lacks constraint/enforcement")
            elif collection_name == "quality_scenarios":
                required = ("stimulus_source", "stimulus", "environment", "artifact", "response", "response_measure")
                missing = [field for field in required if field not in item]
                if missing:
                    add_failure(
                        failures,
                        "QUALITY_SCENARIO_INCOMPLETE",
                        f"{label} missing fields: {', '.join(missing)}",
                    )
            elif collection_name == "failure_propagations":
                if not item.get("failure_source") or not item.get("propagation_edges") or not item.get("impact"):
                    add_failure(failures, "FAILURE_PROPAGATION_INCOMPLETE", f"{label} lacks source/edges/impact")
            elif collection_name == "decision_realization":
                if item.get("realization_status", item.get("status")) not in ("realized", "partial", "conflict", "not_observed", "unknown") or not item.get("adr_id") or not item.get("constraint_id"):
                    add_failure(failures, "DECISION_REALIZATION_INVALID", f"{label} lacks ADR, constraint or valid realization status")
            elif collection_name == "evolution_hotspots":
                if not item.get("coupling_type") or not item.get("affected_objects"):
                    add_failure(failures, "EVOLUTION_HOTSPOT_INCOMPLETE", f"{label} lacks coupling/impact")


def validate_depth_coverage(metadata: dict[str, Any], failures: list[dict[str, str]]) -> None:
    """Require a depth index or an explicit evidence-backed gap for schema 2.1 full sets."""
    if str(metadata.get("content_schema_version", "")) != "2.1.0":
        return
    indexes = metadata.get("indexes", {})
    if isinstance(indexes, dict) and "architecture_analysis_index" in indexes:
        return
    gaps = metadata.get("coverage_gaps", [])
    if isinstance(gaps, list) and any(
        isinstance(gap, dict)
        and gap.get("partition") == "architecture_analysis_index"
        and gap.get("scan_scope")
        and gap.get("evidence")
        for gap in gaps
    ):
        return
    add_failure(
        failures,
        "DEPTH_COVERAGE_MISSING",
        "content schema 2.1 full generation requires architecture_analysis_index or an evidenced coverage gap",
    )


def validate_index_counts(
    partition: str,
    expected: dict[str, Any],
    index_data: dict[str, Any],
    failures: list[dict[str, str]],
) -> None:
    """Validate summary counts against top-level arrays and protocol groups."""
    actual: dict[str, Any] = {
        key: len(value) for key, value in index_data.items() if isinstance(value, list)
    }
    protocol_counts: dict[str, int] = {}
    for collection_name in ("provided", "consumed"):
        collection = index_data.get(collection_name, [])
        if not isinstance(collection, list):
            continue
        for item in collection:
            if isinstance(item, dict) and item.get("protocol"):
                protocol = str(item["protocol"])
                protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
    if protocol_counts:
        actual["by_protocol"] = protocol_counts

    def compare(prefix: str, expected_node: dict[str, Any], actual_node: dict[str, Any]) -> None:
        for key, expected_value in expected_node.items():
            field = f"{prefix}.{key}" if prefix else key
            actual_value = actual_node.get(key)
            if isinstance(expected_value, dict):
                if not isinstance(actual_value, dict):
                    add_failure(failures, "INDEX_COUNT_MISMATCH", f"{partition} missing count group: {field}")
                else:
                    compare(field, expected_value, actual_value)
            elif actual_value != expected_value:
                add_failure(
                    failures,
                    "INDEX_COUNT_MISMATCH",
                    f"{partition} count {field}: expected {expected_value}, found {actual_value}",
                )

    compare("", expected, actual)


def main() -> int:
    args = parse_args()
    docs_dir = args.docs_dir.resolve()
    failures: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if args.mode == "full":
        if args.documents:
            add_failure(failures, "FULL_DOCUMENT_ARGUMENT", "full mode does not accept --documents")
        targets = list(DOCUMENT_HEADINGS)
    else:
        targets = list(dict.fromkeys(args.documents))
        if not targets:
            add_failure(failures, "PARTIAL_TARGETS_MISSING", "partial mode requires --documents")

    unknown = sorted(set(targets) - set(DOCUMENT_HEADINGS))
    if unknown:
        add_failure(failures, "UNKNOWN_DOCUMENT", f"unsupported documents: {', '.join(unknown)}")

    metadata_path = docs_dir / "metadata.json"
    metadata: dict[str, Any] = {}
    if not metadata_path.is_file():
        add_failure(failures, "METADATA_MISSING", f"missing {metadata_path}")
    else:
        try:
            loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("root value must be an object")
            metadata = loaded
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            add_failure(failures, "METADATA_INVALID", f"invalid metadata.json: {exc}")

    for name in targets:
        if name not in DOCUMENT_HEADINGS:
            continue
        path = docs_dir / name
        if not path.is_file():
            add_failure(failures, "DOCUMENT_MISSING", f"missing {path}")
            continue
        validate_document(path, failures, warnings)

    strict = args.strict or metadata.get("content_schema_version") == "2.2.0"
    semantic = {"result": "pending", "reason": "Legacy structural validation does not certify semantics"}
    if not metadata:
        add_failure(failures, "METADATA_EMPTY", "metadata requires a baseline and indexes")
    if metadata:
        partitions = None
        if args.mode == "partial":
            dependencies = metadata.get("document_dependencies", {})
            if all(name in dependencies for name in targets):
                partitions = set()
                for name in targets:
                    partitions.update(dependencies[name].get("partitions", []))
                queue = list(partitions)
                while queue:
                    key = queue.pop()
                    for dependency in metadata.get("indexes", {}).get(key, {}).get("depends_on", []):
                        if dependency not in partitions:
                            partitions.add(dependency)
                            queue.append(dependency)
        validate_external_indexes(docs_dir, metadata, failures, partitions)
        if args.mode == "full":
            validate_depth_coverage(metadata, failures)

    structural_result = "fail" if failures else "pass"
    evidence_result = "pending"
    if strict and not failures:
        try:
            from validate_evidence import validate
            root = args.repo_root or next(p.parent for p in (docs_dir, *docs_dir.parents) if p.name == "docs")
            semantic = validate(root.resolve(), docs_dir, metadata, targets, args.mode, args.semantic_review)
            evidence_result = "pass"
        except (ValueError, KeyError, TypeError, OSError, StopIteration) as exc:
            add_failure(failures, "EVIDENCE_CONTRACT_INVALID", str(exc))
            evidence_result = "fail"
    report = {
        "structural_result": structural_result,
        "evidence_result": evidence_result,
        "semantic_result": semantic,
        "overall_result": "fail" if failures else semantic["result"],
        "mode": args.mode,
        "documents": targets,
        "result": "fail" if failures else (semantic["result"] if strict else "pass"),
        "failed_checks": failures,
        "warnings": warnings,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 1 if failures else (2 if strict and semantic["result"] != "pass" else 0)


if __name__ == "__main__":
    raise SystemExit(main())
