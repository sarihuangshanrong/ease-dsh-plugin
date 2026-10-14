# Ease Spec — 规范驱动开发（SDD）

## Overview

基于 SDD（Spec-Driven Development）方法论维护需求、设计、任务与实现的可追溯性。BRD 使用 **需求规范 → 技术计划 → 任务分解 → 执行实现**；TRD 使用专属精简链 **TRD.md → solution-design.md → tasks.md → 执行实现**，避免把业务用户故事模板重复套到技术需求上。

## When to Use

**Use when:**
- Executing /ease:flow-1-analyze-brd, /ease:flow-1-analyze-trd, /ease:flow-2-design, /ease:flow-3-implement
- Need a traceable BRD lifecycle or the lean TRD authority chain
- Need to maintain traceability between requirements, plans, and outputs

**Do NOT use:**
- For /ease-tools:architecture-review, /ease-tools:code-review, /ease-tools:generate-tests, /ease-tools:gitflow (these don't invoke ease-spec)

## Quick Reference

| Task | Input | Output | Reference |
|---|---|---|---|
| Create constitution | None | memory/constitution.md | reference/project-constitution.md |
| Create BRD spec | BRD/docs | .eases/[编号]/[cmd]/spec.md | reference/create-requirements-spec.md |
| Create BRD plan | spec.md | plan.md | reference/create-technical-plan.md |
| Generate BRD tasks | plan.md | tasks.md | reference/generate-tasks.md |
| Generate TRD tasks | TRD.md + solution-design.md | tasks.md | templates/trd-tasks-template.md |

## Non-negotiables

1. **Constitution FIRST**: Must create `memory/constitution.md` before first use
2. **唯一目录名**: Use `.eases/` (NOT `eases/` or `specs/`)
3. **相对路径**: Use `.eases/...`, `docs/domains/...` (NOT `/.eases/...`)
4. **编号规则**: Three-digit incrementing numbers (001, 002, 003...)
5. **Command scope**: Only 4 commands invoke ease-spec:
   - /ease:flow-1-analyze-brd (Phase 1 - Business)
   - /ease:flow-1-analyze-trd (Phase 1 - Technical)
   - /ease:flow-2-design (Phase 2)
   - /ease:flow-3-implement (Phase 3)

   > **Note**: `/ease:analyze-code` does NOT invoke ease-spec. It stores raw reports/workplans under `.eases/reverse-engineering/${RUN_ID}/` and promotes reviewed domain facts to `docs/domains/${DOMAIN_ID}/`; it does not generate spec.md/plan.md/tasks.md.

6. **阶段产物边界（Phase Output Boundaries）** — **不可协商，不可质疑**

   > ⚠️ **核心原则**：不同阶段的 ease-spec 意图和产物**必须严格区分**。除 `flow-3-implement` 外，其他阶段**禁止生成/实现实际代码**。

   | 阶段 | 命令 | 允许产物 | **禁止产物** |
   |------|------|----------|-------------|
   | **Phase 1 - BRD** | flow-1-analyze-brd | • 领域文档<br>• 用例与业务规则<br>• spec.md / 高层 plan.md / tasks.md | ❌ **任何代码**<br>❌ API 接口定义<br>❌ 数据库 Schema<br>❌ 技术架构图 |
   | **Phase 1 - TRD** | flow-1-analyze-trd | • TRD 与现状/问题分析<br>• 内置技术方案设计<br>• 按需的架构图、API 变更设计、DB Schema/迁移设计<br>• TRD 专属 tasks.md | ❌ 业务代码实现（由 Phase 3 完成）<br>❌ 重复生成 BRD `spec.md` / `plan.md` |
   | **Phase 2** | flow-2-design | • 架构设计文档 (arch-design.md)<br>• 详细设计文档 (detail-design.md)<br>• spec.md（含 Clarifications）<br>• plan.md<br>• tasks.md<br>• **框架代码骨架**（仅有结构 + TODO 注释） | ❌ **具体业务逻辑实现**<br>❌ 完整的方法实现<br>❌ 可运行的业务代码 |
   | **Phase 3** | flow-3-implement | • 实际代码实现<br>• 测试代码<br>• 实现总结<br>• 实现校验清单<br>• 就地回写前置阶段的权威 tasks.md | ❌ 新建 spec.md / plan.md / tasks.md<br>❌ 私自修改前置 spec/plan |

   **红旗警示**：如果出现以下情况，**立即停止，拒绝执行**：
   - BRD Phase 1 尝试生成任何代码、接口定义、数据库 Schema 或技术架构图
   - TRD Phase 1 尝试实现业务代码（架构/API/数据设计文档属于允许产物）
   - Phase 2 尝试实现完整的业务逻辑（框架代码应只有 `throw UnsupportedOperationException("TODO")` 或 TODO 注释）
   - 以"效率"为由在 Phase 1/2 提前实现代码
   - 用户要求跳过阶段边界直接写代码

   **阶段产物边界不可协商的原因**：
   1. **职责分离**：BRD 分析只关注“做什么”，BRD 设计与 TRD 内置设计关注“怎么做”，Phase 3 才关注“具体写”
   2. **可追溯性**：每个阶段的产物是下一阶段的输入，混淆边界会破坏追溯链
   3. **变更控制**：BRD 需求变更在 Phase 1、设计变更在 Phase 2；TRD 的技术分析与设计均在 Phase 1；代码变更统一在 Phase 3
   4. **质量保证**：每个阶段有独立的质量检查标准，跨阶段产出会导致质量失控

7. **路径不变式（Path Invariant）** — BRD 路径「缺设计不编码」

   > ⚠️ **核心规则**：BRD 路径（`flow-1-analyze-brd`）= 分析 → **设计** → 实现，**设计阶段独立且强制**，Phase 2 产物缺失时**拒绝直接编码**（含 ease-coding、对话内裸编码、`flow-3-implement`），阻断并重定向到 `/ease:flow-2-design`。TRD 路径（`flow-1-analyze-trd`）= 分析 → 实现，因方案设计**内置于 Phase 1** 而不经 `flow-2-design`，属例外。三阶段内不允许跳过强制阶段；如选择其他方法，必须退出当前 Flow 并记录 `FLOW_ABORTED`/`PROCESS_CHANGED`。详见 `reference/phase-gate-invariant.md` 与 `gates/README.md`。

8. **阶段契约总表（Stage Contract）** — 路径/连接键/阈值的单一权威

   > ⚠️ **核心规则**：各阶段的精确输入/输出路径、`DOMAIN_ID/CHANGE_ID` 推导规则、UC/BR ID、增量标记、领域对齐证据和质量阈值，**以 `reference/stage-contract.md` 为唯一权威定义源**。

9. **Change Worktree 契约** — 一个变更、一个分支、一个工作目录

   > ⚠️ **核心规则**：所有写入型 Flow 使用 `scripts/bash/ensure-change-worktree.sh`，将 `${CHANGE_ID}` 映射到 `feature/${CHANGE_ID}`。Flow 1 首次建立，Flow 2/3 与 Starter 只保证和复用；不得依赖 `claude -w`、`.claude/worktrees`、`../.bare/` 或可选 `ease-tools` 来决定是否创建。只有用户显式选择 `--worktree=off` 才能豁免。详见 `reference/worktree-contract.md`。

## Path Conventions

| Purpose | Format |
|---|---|
| Constitution | memory/constitution.md |
| Domain docs | docs/domains/[编号]-[module_name]/ |
| Spec directory | .eases/[编号]-[功能名]/[command]/ |
| Usecase directory | docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/ |

## Numbering Rules (Three-digit)

| Level | Format | Example |
|---|---|---|
| Domain | [编号]-[module_name] | 001-user-management |
| Subdomain | [编号]-[subdomain] | 001-authentication |
| Usecase | [编号]-[usecase-name].md | 001-login-with-password.md |
| Feature | [编号]-[功能名] | .eases/001-user-auth/ |

### Number generation
- 新增 domain：扫描 `docs/domains/`，取最大编号 + 1
- 新增 subdomain：扫描对应 domain 的 `usecases/` 目录
- 新增 usecase：扫描对应 subdomain 目录
- 新增 feature/.eases/：扫描 `.eases/` 目录

### Numbering Conflict Resolution

当编号冲突时：
1. 检查是否存在已删除/归档的功能目录（可复用编号）
2. 如果冲突目录活跃，使用最大编号 + 1
3. 记录冲突解决日志到 `.eases/numbering-log.md`
4. 多团队协作时，先拉取最新代码再生成编号

## Output Quality Gates

每个阶段产出必须通过质量检查。以下 spec/plan 门禁只适用于 BRD；TRD 使用后述专属门禁。

### spec.md Quality Gates
- [ ] **需求完整性**: 覆盖所有输入需求点（BRD/代码分析）
- [ ] **可追溯性**: 每个需求点有来源引用（BRD 章节/代码路径）
- [ ] **无歧义**: 术语使用一致，无模糊表述（如"可能"、"应该"已澄清）
- [ ] **范围明确**: 明确列出 in-scope 和 out-of-scope

### plan.md Quality Gates
- [ ] **技术方案可行性**: 所有技术选型有依据（POC/文档/最佳实践）
- [ ] **风险评估**: 列出 ≥3 个主要风险及缓解措施
- [ ] **依赖清晰**: 明确列出内部/外部依赖及版本要求

### tasks.md Quality Gates
- [ ] **任务可执行**: 每个任务有明确的完成标准
- [ ] **粒度适中**: 单个任务预估工时 ≤4 小时
- [ ] **依赖排序**: 任务按依赖关系正确排序

### TRD Quality Gates
- [ ] **需求权威**：TRD.md 包含风险级别、范围、量化目标和验收方式
- [ ] **设计权威**：solution-design.md 包含实现点、兼容性、风险与回滚
- [ ] **实施账本**：tasks.md 使用技术工作包分类、包含路径/命令/证据，且 Flow 1 中保持 `[ ]`
- [ ] **按风险裁剪**：Lite/Standard/Strict 同时控制文档拆分和 Flow 3 比例门禁，但不降低 Domain Impact、回滚判断及与实际风险对应的验证证据

## Directory Mapping

| Ease Command | Docs 输出 | Eases 输出 |
|---|---|---|
| /ease:flow-1-analyze-brd | docs/domains/${DOMAIN_ID}/domain-overview.md + usecases/ + domain-alignment.json + 按需 decisions/ | .eases/${CHANGE_ID}/context.json + flow-1-analyze/outputs/analysis-report.md + {spec,plan,tasks}.md |
| /ease:flow-1-analyze-trd | docs/trd/[编号]-[模块].md + `.eases/trd/[编号]-[模块]/flow-1-analyze-trd/` 下的 `TRD.md`、`artifacts/solution-design.md`、`validation/domain-impact.json` 与按风险生成的辅助工件 | `.eases/trd/[编号]-[模块]/flow-1-analyze-trd/tasks.md`；TRD 不生成 `spec.md` / `plan.md` |
| /ease:flow-2-design | ADR/system 的已确认长期更新（按需） | .eases/${CHANGE_ID}/flow-2-design/{spec,plan,tasks}.md + architecture/detail/test-cases/alignment + framework-code/ 或 code-annotations/ |
| /ease:flow-3-implement | 实际代码、测试代码、ADR/DDR 实现证据 | .eases/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md + checklists/；消费并回写权威 tasks.md |

> **Note**: `/ease:analyze-code` 不调用 ease-spec。原始报告与 workplan 位于 `.eases/reverse-engineering/${RUN_ID}/`；只有审核确认后的 `domain-overview.md`、usecases 和领域工件进入 `docs/domains/${DOMAIN_ID}/`。

`docs/` 是当前长期事实，`.eases/` 是按 `CHANGE_ID` 隔离的过程与验收证据。文件由 Agent 生成并不自动意味着它可以进入 `docs/`。

## Spec Lifecycle

生命周期按路径执行，不得把 BRD 模板套到 TRD。

### BRD 路径

1. 检查 `constitution.md` → 不存在则先创建
2. 生成编号（扫描现有目录）
3. 建立/复用并验证 `feature/${CHANGE_ID}` worktree
4. 需求规范阶段 → spec.md
5. 需求澄清阶段（仅 /ease:flow-2-design，可选）→ spec.md 的 Clarifications 章节
6. 技术计划阶段 → plan.md
7. 框架代码阶段（仅 /ease:flow-2-design）→ framework-code/
8. 任务分解阶段 → tasks.md
9. 执行实现阶段（仅 /ease:flow-3-implement）→ 实际代码（Phase 1 / Phase 2 不执行 implement，与"阶段产物边界"一致）
10. 质量检查 → checklists/

### TRD 精简路径

1. 检查 constitution 并生成 `CHANGE_ID`
2. 建立/复用并验证 `feature/${CHANGE_ID}` worktree，再生成 `context.json`
3. 执行 Domain Impact Guard；只有 `none` 留在 TRD
4. 按 `Lite / Standard / Strict` 风险级别生成 `TRD.md`、`artifacts/solution-design.md` 与按需辅助工件
4. 使用 `templates/trd-tasks-template.md` 从权威需求/设计直接生成未完成的 `tasks.md`
5. Flow 3 消费 `TRD.md → solution-design.md → tasks.md` 并回写任务进度

TRD 无需 `spec.md` / `plan.md`。`TRD.md` 是需求权威，`solution-design.md` 是设计权威，`tasks.md` 是实施账本；不得为满足通用生命周期而复制同义内容。

## Edge Cases

| 场景 | 处理策略 |
|------|----------|
| **constitution.md 版本过旧** | 询问用户是否更新，或标记为 "待更新" 继续执行 |
| **多团队协作编号冲突** | 先执行 `git pull`，再扫描目录生成编号；如仍冲突，使用最大编号 + 1 |
| **spec.md 超过 500 行** | 拆分为 `spec-core.md` + `spec-detail.md`，在 spec.md 中引用 |
| **目录权限不足** | 提示用户检查目录权限，提供 `chmod` / `chown` 命令示例 |
| **Git 工作区不干净** | 提示用户先提交或暂存现有变更，避免混淆 |

## Common Mistakes

| 错误 | 症状 | 修复 |
|---|---|---|
| Using absolute paths | Writing `/.eases/` instead of `.eases/` | Use relative paths, remove leading `/` |
| Mixed directory names | Using both `eases/` and `.eases/` | Standardize on `.eases/` |
| Skipping constitution | No constitution.md exists | Create memory/constitution.md first |
| Non-sequential numbering | Skipped or non-consecutive numbers | Scan existing directories and use max + 1 |
| Command scope error | Non-specified commands invoke ease-spec | Only 4 commands invoke ease-spec |

## Handoff Guidelines

### From ease-analysis
接收分析阶段的产出：
- [ ] 领域模型已定义
- [ ] 核心用例已识别
- [ ] 业务规则已提取

### To ease-architecture (for /ease:flow-2-design)
移交架构设计：
- [ ] spec.md 已通过质量检查
- [ ] 技术方案需要架构评审

### To ease-coding (for /ease:flow-3-implement)
移交代码实现：
- [ ] tasks.md 已生成并评审
- [ ] 所有依赖资源已准备就绪
- [ ] TRD 路径的 `TRD.md`、`solution-design.md`、`tasks.md` 权威链完整（无需 spec.md / plan.md）

## See Also

### Upstream (Input Sources)
- `ease-analysis/SKILL.md` - Provides domain models and usecases
- `commands/flow-1-analyze-brd.md` - Command for BRD analysis (Phase 1)
- `commands/flow-1-analyze-trd.md` - Command for TRD analysis (Phase 1)
- `commands/analyze-code.md` - Command for code reverse engineering
- `commands/flow-2-design.md` - Command for architecture design (Phase 2)
- `commands/flow-3-implement.md` - Command for code implementation (Phase 3)
- `reference/worktree-contract.md` - Single branch/worktree admission contract

### Downstream (Output Consumers)
- `ease-architecture/SKILL.md` - Receives spec.md for architecture design
- `ease-framework-code/SKILL.md` - Receives plan.md for framework generation
- `ease-coding/SKILL.md` - Receives tasks.md for implementation

### Alternatives
- `quick-develop/SKILL.md` - For small changes (<200 LOC) without full SDD
- `ease-poc/SKILL.md` - For technical feasibility validation before spec

### Reference documents
- `reference/project-constitution.md` - First-time setup guide
- `reference/create-requirements-spec.md` - Specify phase
- `reference/create-technical-plan.md` - Plan phase
- `reference/generate-tasks.md` - Tasks phase
- `reference/execute-implementation.md` - Implement phase
- `reference/requirements-clarification.md` - Clarify phase
- `reference/phase-gate-invariant.md` - 阶段门控不变式（BRD 路径缺设计不编码 / TRD 路径例外）
- `reference/stage-contract.md` - 阶段契约总表（路径、DOMAIN_ID/CHANGE_ID、UC/BR ID、Δ 标记和阈值的单一权威定义源）

### Templates & Scripts
- `templates/` - Document templates for each phase
- `scripts/bash/` and `scripts/powershell/` - Cross-platform init/validation scripts
