# Ease Analysis

## 异步任务检测

> **优先检测**：在执行本技能前，首先检测用户输入是否包含 `[@ease]` 和 `async` 关键词。

**检测条件**：当用户输入**同时满足**以下条件时，触发 `async-task` 技能：
- 包含 `[@ease]` 标记（或 `[@Ease]`、`[@EASE]`）
- 包含 `async` 关键词（或 `--async` 标记）

**触发示例**：
- `[@ease] async 分析整个项目代码`
- `/ease:analyze-code [@ease]--async 提取领域模型`
- `[@ease] 异步执行：分析代码结构`

**检测逻辑**：
```bash
# 检测用户输入中是否同时包含 @ease 和 async 关键词
USER_INPUT="$1"  # 用户完整输入
if [[ "$USER_INPUT" =~ @ease|@Ease|@EASE ]] && [[ "$USER_INPUT" =~ async|\[async\]|异步 ]]; then
    # 触发 async-task 技能，将任务提交到云端
    # 任务类型：技术任务 (issue_type=5, 标题前缀=[task])
    # 任务内容：完整的用户输入（包括命令）
fi
```

**触发后的行为**：
1. 将完整的用户输入（如 `/ease:analyze-code [@ease]--async 分析代码`）作为任务描述
2. 使用 `async-task` 技能提交到云端后台
3. 向用户反馈"任务已提交到云端后台"

## Overview

面向"需求文档 / 存量代码"的 DDD 分析入口：输出领域模型、用例与业务规则，并要求可追溯（术语统一、边界清晰、规则可测试）。

## Role Contract

- **BRD 模式 — 需求与领域分析师（BA/Domain Analyst）**：从业务意图提炼领域边界、用例与规则；不得进行技术选型或代码实现。
- **存量代码模式 — 逆向工程专家（Reverse Engineering Specialist）**：只把代码可直接证明的行为记为现状事实；由命名、结构或调用关系推导出的业务含义必须标记为“待业务确认”。
- **证据冲突**：BRD 表达目标状态，代码表达当前状态；两者冲突时并列记录差异，不得自行选择一方覆盖另一方。
- **混合输入**：先声明当前模式；需要同时分析时分别产出“目标业务语义”和“代码现状”，再建立差异映射。
- **边界与移交**：本技能不修改生产代码；需要架构决策时移交 `ease-architecture`，需要实现或修复时移交 `ease-coding`。

## When to Use

**Use when:**
- 术语不一致（同一概念在不同文档/代码中有不同称呼）
- 领域边界模糊（无法明确划分模块/服务职责）
- 业务规则散落（规则在代码、口头、遗留文档中混杂，无集中来源）
- 需求与实现难以对齐（BRD 中的用例无法映射到具体代码逻辑）

**Input types:**
- BRD/需求文档 → 正向分析
- 现有代码 → 逆向工程

**Do NOT use when:**
- 只写 API 文档/架构文档 → `ease-tools` 插件的 `ease-arch-documentation` / `ease-architecture`
- 只实现功能代码/补测试 → `ease-coding` / `ease-testing`

## Quick Reference

| 输入类型 | 关键流程 | 参考 | 输出目录 |
|---|---|---|---|
| BRD/需求文档 | analyze-domains → analyze-usecases | `flows/analyze-domains.md`, `analyze-usecases.md` | `docs/domains/<编号>-<模块>/` |
| 现有代码 | extract-domains → extract-usecases | `flows/extract-domains.md`, `extract-usecases.md` | 同上（反向工程产出） |

## Decision Flowchart

```dot
digraph ease_analysis_decision {
    "Is input available?" [shape=diamond];
    "BRD/Requirements docs" [shape=box, label="Analyze domains\n→ usecases → rules"];
    "Existing codebase" [shape=box, label="Extract domains\n→ usecases → rules"];
    "ease-analysis" [shape=ellipse, style=filled, fillcolor=lightblue];

    "Is input available?" → "BRD/Requirements docs" [label="BRD/docs exist"];
    "Is input available?" → "Existing codebase" [label="Code only"];
    "BRD/Requirements docs" → ease-analysis;
    "Existing codebase" → ease-analysis;
}
```

## Non-negotiables

### Execution requirements
- **TodoWrite 追踪**: 所有关键任务必须追踪到 `completed`
- **可落地产出**: 用例主流程 ≥ 3 步；规则描述清晰且可测试
- **建模优先顺序**: 领域模型/术语，再写用例与规则（避免"先写结论后找依据"）

### Output structure
- 必须与 `commands/flow-1-analyze-brd.md` 一致
- 子领域目录固定两个文件：`usecase.md` + `rules.md`
- `docs/domains/${DOMAIN_ID}/` 只保存长期领域事实；单次分析报告写入 `.eases/${CHANGE_ID}/flow-1-analyze/outputs/`
- `context.json` 必须维持 `DOMAIN_ID ↔ CHANGE_ID ↔ TRACK` 映射并通过确定性校验

### ID standards (MUST follow)
- 用例 ID：`UC-[%03d]`（如 UC-001、UC-042）
- 规则 ID：`BR-[%03d]-[rule-name]`（如 BR-001-approval-limit）
- 权威规范：`references/id-standards.md`

### Output Quality Gates

产出物必须通过以下质量检查：

- [ ] **术语表完整性**: 包含 ≥3 个核心领域术语定义
- [ ] **用例可执行性**: 每个用例主流程 ≥3 步骤，有明确的触发条件和预期结果
- [ ] **规则可测试性**: 每条业务规则有明确的判定条件（可通过单元测试验证）
- [ ] **ID 规范性**: 所有 UC/BR ID 符合 `UC-[%03d]` / `BR-[%03d]-[name]` 格式
- [ ] **可追溯性**: 每个用例和规则能追溯到原始需求或代码来源
- [ ] **领域基线**: 全新/增量 BRD 均生成 `domain-alignment.json`，活动 UC/BR 的来源完整且 ID 唯一
- [ ] **确定性校验**: `scripts/validate_domain_alignment.py --phase flow-1` 执行通过
- [ ] **领域决策**: 重大业务语义变化已创建并索引 DDR；普通措辞/纯技术变化未滥建 DDR
- [ ] **TRD 守门**: `validate_domain_impact.py` 已证明 `none` 或将需求重定向到 BRD
- [ ] **身份映射**: `validate_flow_context.py` 已验证本次 change/domain/track 连接键

### Handoff to ease-architecture

当满足以下条件时，移交到架构设计阶段：
- [ ] 用例文档已通过质量检查
- [ ] 核心业务规则已定义（覆盖 ≥80% 核心场景）
- [ ] 术语表已确定且与业务方达成共识
- [ ] 领域边界已明确划分

## Edge Cases

| 场景 | 处理策略 |
|------|----------|
| 多语言混合项目 | 按语言分区分析，识别跨语言边界和数据交换格式 |
| 超大代码库 (>10万行) | 先分析核心模块入口，增量迭代；使用 `find . -type f -name "*.java" \| wc -l` 估算规模 |
| BRD 格式不标准 | 提取关键信息（角色/动作/数据/规则），标记缺失部分为 "待澄清" |
| 术语冲突严重 | 建立术语映射表，标注推荐用法和废弃用法 |

## Common Mistakes

| 错误 | 症状 | 修复 |
|---|---|---|
| 先写用例后找领域模型 | 用例和规则缺乏领域语境支撑 | 遵循建模优先顺序：先 domains，后 usecases |
| ID 格式不统一 | UC/BR 引用混乱，无法追溯 | 严格遵守 `references/id-standards.md` 规范 |
| 产出不可测试 | 规则描述模糊，无法验证 | 规则描述必须包含明确的判定条件 |
| 跳过 TodoWrite 追踪 | 任务状态不受控，容易遗漏 | 关键任务必须创建 TodoWrite 并标记 completed |

## See Also

### Upstream (Input Sources)
- `commands/flow-1-analyze-brd.md` - Command interface for BRD analysis (Phase 1)
- `commands/flow-1-analyze-trd.md` - Command interface for TRD analysis (Phase 1)
- `commands/analyze-code.md` - Command interface for code reverse engineering

### Downstream (Output Consumers)
- `ease-architecture/SKILL.md` - Receives usecases for architecture design
- `ease-framework-code/SKILL.md` - May receive domain models for framework generation
- `ease-spec/SKILL.md` - Uses analysis output for spec creation

### Alternatives
- `references/ease-arch-documentation/SKILL.md` - For system-level documentation (not domain analysis)
- `ease-architecture/SKILL.md` - For architecture design (higher level than analysis)

### References
- `references/id-standards.md` - 用例/规则 ID 规范
- `references/domain-alignment-contract.md` - 领域基线、设计/实现证据与阶段门禁
- `references/domain-alignment-ci.md` - Git 漂移、语义裁决和严格只读 CI 验收
- `references/task-management-standards.md` - 任务管理细则
- `references/flow-execution-standards.md` - Flow 执行标准
- `flows/` - 流程入口文档
- `templates/` - 文档模板
