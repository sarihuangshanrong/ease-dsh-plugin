---
description: 从交互式或提供的原则输入创建或更新项目宪章，并确保所有依赖模板保持同步。**首次使用 ease-spec 时必须执行此文档。**
handoffs: 
  - label: 构建规范
    agent: ease.specify
    prompt: 基于更新后的宪章实施功能规范。我想构建...
skills: ease-spec
---

> ⚠️ **首次使用 ease-spec 必读**：对于第一次使用 ease-spec 技能的项目，**必须先执行本文档创建 `/memory/constitution.md`**，然后才能执行其他 spec 流程。

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你必须考虑用户输入（如非空）。

## 纲要

你正在更新位于 `/memory/constitution.md` 的项目宪章。

### 首次使用（不可协商）

如果项目中没有 `/memory/` 目录或 `constitution.md` 文件，你**必须**：

1. 创建 `/memory/` 目录
2. 使用 ease-spec 的 `memory/constitution.md` 模板
3. 结合项目的现有文档（README、docs/ 等）填充模板
4. 产出完整的 `/memory/constitution.md`

> **原则**：没有 constitution.md 的项目，不允许执行后续的 需求规范/技术计划/任务分解/执行实现 流程。

### 更新现有宪章

该文件是一个模板，包含方括号中的占位符令牌（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）。你的工作是：(a) 收集/推导具体取值，(b) 精确填充模板，(c) 将任何修订传播到所有依赖工件。

## 执行流程

### 1. 检查/创建目录结构

```bash
# 检查并创建必要的目录
mkdir -p memory
mkdir -p docs/domains
mkdir -p eases
```

### 2. 加载现有宪章模板

使用 ease-spec 技能的 `memory/constitution.md` 作为模板。

- 识别所有形式为 `[ALL_CAPS_IDENTIFIER]` 的占位符令牌。
- **重要**：用户可能需要比模板中使用的原则条目更少或更多。如果指定了数量，请遵从该数量——沿用通用模板，并相应更新文档。

### 3. 收集/推导占位符的取值

- 若用户输入（对话）提供了值，则使用该值。
- 否则从现有仓库上下文推断（README、docs、若嵌入则参考先前宪章版本）。
- 关于治理日期：`RATIFICATION_DATE` 为最初采纳日期（若未知则询问或标注 TODO），`LAST_AMENDED_DATE` 如有改动则为今天，否则保持先前值。
- `CONSTITUTION_VERSION` 必须依据语义化版本规则递增：
  - MAJOR：治理/原则的移除或重定义，导致向后不兼容。
  - MINOR：新增原则/章节或显著扩展指导。
  - PATCH：澄清、措辞、错别字修复、非语义性精炼。
- 若版本提升类型不明确，先提出理由再最终确定。

### 4. 起草更新后的宪章内容

- 用具体文本替换每一个占位符（除非项目明确选择暂不定义的模板位——任何保留必须明确说明理由）。不应留下方括号形式的令牌。
- 保留标题层级；一旦替换完成，可移除注释，除非仍具澄清价值。
- 确保每个"原则"章节包含：简洁的名称行、描述不可协商规则的段落或要点列表、在不明显时给出明确的理由。
- 确保"治理"章节列出修订流程、版本策略与合规审查期望。

### 5. 一致性传播检查清单

把先前清单转化为主动校验：

- 阅读 ease-spec 技能中的 `templates/plan-template.md`，确保任意 "Constitution Check" 或规则与更新原则一致。
- 阅读 ease-spec 技能中的 `templates/spec-template.md` 以核对范围/需求一致性——若宪章新增/移除强制章节或约束，请更新。
- 阅读 ease-spec 技能中的 `templates/tasks-template.md`，确保任务分类反映新增或移除的原则驱动任务类型（例如，可观测性、版本化、测试纪律）。
- 阅读 `commands/*.md` 中的每个命令文件（包括本文件），在需要通用指引时，校验不再保留过时引用。
- 阅读任何运行时指引文档（如 `README.md`、`docs/quickstart.md`，或如存在的特定代理指引文件）。对变更的原则更新引用。

### 6. 生成同步影响报告

在更新后将其作为 HTML 注释预置在宪章文件顶部：

- 版本变更：旧 → 新
- 变更的原则列表（若重命名：旧标题 → 新标题）
- 新增章节
- 移除章节
- 需要更新的模板（✅ 已更新 / ⚠ 待处理），附文件路径
- 后续 TODO（若有占位符被刻意延后）

### 7. 最终输出前的校验

- 不应残留未解释的方括号占位符。
- 版本行与报告一致。
- 日期使用 ISO 格式 YYYY-MM-DD。
- 原则应具备宣告性、可测试，避免含糊语言（例如 "should" → 以 MUST/SHOULD 并附理据替换）。

### 8. 写入宪章

将完成的宪章写回 `/memory/constitution.md`（覆盖写入）。

### 9. 输出最终摘要

向用户输出最终摘要，包括：

- 新版本及版本提升的理由。
- 任何被标记为需人工跟进的文件。
- 建议的提交信息（例如：`docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。
- **下一步操作提示**：提示用户可以继续执行 ease-spec 的其他流程。

## 宪章模板示例

```markdown
# [PROJECT_NAME] Constitution

## Core Principles

### I. Library-First
Every feature starts as a standalone library; Libraries must be self-contained, 
independently testable, documented; Clear purpose required - no organizational-only libraries.

### II. CLI Interface
Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, 
errors → stderr; Support JSON + human-readable formats.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement; 
Red-Green-Refactor cycle strictly enforced.

### IV. Integration Testing
Focus areas requiring integration tests: New library contract tests, Contract changes, 
Inter-service communication, Shared schemas.

### V. Observability
Text I/O ensures debuggability; Structured logging required.

### VI. Versioning & Breaking Changes
MAJOR.MINOR.BUILD format; Breaking changes require migration plan.

### VII. Simplicity
Start simple, YAGNI principles; Avoid over-engineering.

## Directory Structure

```
/memory/constitution.md                    # 本文件

/docs/domains/                             # 领域模块文档（不可协商）
└── [编号]-[module_name]/                  # 领域模块（三位编号）
    │                                      # 例如：001-user-management
    └── usecases/                          # 用例文档
        └── [编号]-[subdomain]/            # 子领域（三位编号）
            └── uc-[编号]-[usecase].md        # 用例（三位编号）

.eases/                                   # ease-spec 规范文档（按功能和命令隔离）
└── [编号]-[功能名]/                       # 例如：001-user-auth
    └── [command]/                         # 例如：flow-1-analyze-brd/
```

## Numbering Rules (NON-NEGOTIABLE)

- All directories and files MUST have 3-digit incremental number prefix
- When adding new domain/subdomain/usecase, scan existing max number + 1
- Format: 001, 002, 003...

## Governance

Constitution supersedes all other practices; Amendments require documentation, 
approval, migration plan. All PRs/reviews must verify compliance; 
Complexity must be justified.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
```

## 格式与风格要求

- 严格按照模板使用 Markdown 标题（不要提升或降级层级）。
- 为可读性对长的理据行进行换行（理想 <100 字符），但不要为此造成生硬的断行。
- 各章节之间保持单个空行。
- 避免末尾空格。

## 特殊情况处理

如果用户提供的是部分更新（例如仅修订一个原则），仍需执行校验与版本决策步骤。

如果关键信息缺失（例如确实未知的采纳日期），插入 `TODO(<FIELD_NAME>): 说明`，并在"同步影响报告"的"延后项"中包含它。

不要创建新模板；始终在现有 `/memory/constitution.md` 文件上操作。

## 与其他命令的关系

> ⚠️ **重要**：以下五个命令在执行前会检查 constitution.md 是否存在：
> - `/ease:flow-1-analyze-brd` (Phase 1 - Business)
> - `/ease:flow-1-analyze-trd` (Phase 1 - Technical)
> - `/ease:analyze-code`
> - `/ease:flow-2-design` (Phase 2)
> - `/ease:flow-3-implement` (Phase 3)

如果 constitution.md 不存在，这些命令会中止并提示用户先执行本文档创建宪章。

## 下一步操作

宪章创建/更新完成后，可以继续执行：

1. **创建需求规范**：参考 `reference/create-requirements-spec.md`
2. **一键执行**：参考 `reference/一键执行.md` 自动执行完整流程
3. **直接使用命令**：
   - `/ease:flow-1-analyze-brd` - 分析业务需求（三阶段-阶段1）
   - `/ease:flow-1-analyze-trd` - 分析技术需求（三阶段-阶段1）
   - `/ease:analyze-code` - 分析源代码
   - `/ease:flow-2-design` - 统一设计（三阶段-阶段2）
   - `/ease:flow-3-implement` - 代码实现（三阶段-阶段3）
