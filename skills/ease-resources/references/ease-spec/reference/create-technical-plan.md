---
description: 使用计划模板执行实施规划工作流以生成设计工件。
handoffs: 
  - label: 创建清单
    agent: ease.checklist
    prompt: 为以下领域创建一份清单...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
skills: ease-spec
---
## 用户输入

```text
$ARGUMENTS
```

在继续之前，若用户输入不为空，必须优先考虑该输入。

## 契约与 Schema

- 引用：commands/contracts-unified.md
- 校验：commands/schemas/paths-only.schema.json

## 阶段边界模式（必须先判定）

> 📌 新版 `/ease:flow-1-analyze-trd` 使用 `TRD.md → solution-design.md → trd-tasks-template.md` 精简链，不再调用本 BRD plan 工作流。下方 `phase-1-trd` 仅用于续跑已经存在 `plan.md` 的历史 TRD，不得为新 TRD 创建 plan.md。

根据 `EASE_FEATURE_DIR` 判定调用阶段：

- 以 `/flow-1-analyze` 结尾：`PLAN_MODE=phase-1-brd`
- 以 `/flow-1-analyze-trd` 结尾：`PLAN_MODE=phase-1-trd`
- 以 `/design` 结尾：`PLAN_MODE=phase-2`

> ⛔ **BRD Phase 1 保持分析边界。** `PLAN_MODE=phase-1-brd` 禁止生成 API、DB Schema、架构图；`plan.md` 只记录高层技术约束、风险、依赖、验证策略和下一阶段输入。详细技术设计由 Flow 2 完成。
>
> ✅ **TRD Phase 1 内置技术设计。** `PLAN_MODE=phase-1-trd` 允许根据技术需求生成 API 变更设计、DB Schema/迁移设计、架构图及相关技术文档，产物写入 `.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/artifacts/`。这是 TRD 路径直连 Phase 3 的设计依据。
>
> `PLAN_MODE=phase-2` 执行 BRD 的独立详细设计。任何模式不明确时按更严格的 `phase-1-brd` 边界处理并报告。

## 纲要

配合ease-spec技能完成任务，其中scripts/bash/create-new-feature.sh和模版等脚本位于ease-spec技能包中。

1. 设置：在仓库根目录运行 `{SCRIPT}` 并解析 JSON（遵循统一契约并校验 paths-only.schema.json），获取 FEATURE_SPEC、IMPL_PLAN、EASES_DIR、CURRENT_BRANCH、HAS_GIT。对于包含单引号的参数（如 "I'm Groot"），使用转义语法：例如 `'I'\''m Groot'`（或尽量使用双引号："I'm Groot"）。
2. 加载上下文：读取 FEATURE_SPEC 与 `/memory/constitution.md`。加载 IMPL_PLAN 模板（若模板缺失将生成最小 plan.md 并输出 WARNING）。
3. 执行计划工作流：遵循 IMPL_PLAN 模板结构，并按 `PLAN_MODE` 裁剪：

   - 填写技术背景（对未知项标记为 "NEEDS CLARIFICATION"）
   - 基于宪章填充“宪章检查”章节
   - 评估关卡（若存在未获正当理由的违规，ERROR）
   - `phase-1-brd`：只更新 plan.md；禁止生成 API、DB Schema、架构图及其衍生工件
   - `phase-1-trd`：执行技术方案详细设计，允许生成 API、DB Schema、架构图及相关文档，写入 TRD artifacts/
   - `phase-2`：执行第 1 阶段详细设计，生成允许的 data-model.md、contracts/、quickstart.md
   - 第 1 阶段：运行代理脚本以更新代理上下文
   - 设计后重新评估“宪章检查”
4. 停止并报告：命令在第 2 阶段规划结束后终止。报告分支、IMPL_PLAN 路径与生成的工件。

## 阶段

### 第 0 阶段：纲要与研究

1. 从上述技术背景中提取未知项：

   - 每个 "NEEDS CLARIFICATION" → 研究任务
   - 每个依赖项 → 最佳实践任务
   - 每个集成项 → 模式任务
2. 生成并派发研究代理任务：

   ```text
   对技术背景中的每个未知项：
     Task: "Research {unknown} for {feature context}"
   对每个技术选择：
     Task: "Find best practices for {tech} in {domain}"
   ```
3. 在 `research.md` 中整理结论，使用以下格式：

   - Decision: [选择的方案]
   - Rationale: [选择原因]
   - Alternatives considered: [评估过的替代方案]

**输出**：research.md（所有 "NEEDS CLARIFICATION" 已解决）

### 第 1 阶段：设计与契约

**先决条件：** `research.md` 完成，且 `PLAN_MODE=phase-1-trd|phase-2`。`PLAN_MODE=phase-1-brd` 必须跳过本节。

1. 从功能规范中提取实体 → 写入 `data-model.md`：

   - 实体名称、字段、关系
   - 来自需求的校验规则
   - 如适用，状态流转
2. 从功能性需求生成 API 契约：

   - 对每个用户动作 → 一个端点
   - 使用标准 REST/GraphQL 模式
   - 将 OpenAPI/GraphQL 模式输出到 `/contracts/`
3. 更新代理上下文：

   - 运行 `{AGENT_SCRIPT}`
   - 这些脚本会检测当前使用的 AI 代理
   - 更新相应的代理特定上下文文件
   - 仅添加本次计划中新出现的技术
   - 在标记之间保留手动添加内容
   - 模板缺失：输出 WARNING 并跳过新建；不中断流程；已存在的代理文件仍将更新

**输出路由**：

- `phase-1-trd`：`artifacts/solution-design.md`，并按需生成 `architecture-diagram.md`、`api-change-design.md`、`data-schema-design.md`
- `phase-2`：data-model.md、/contracts/*、quickstart.md、代理特定文件

## 关键规则

- 使用绝对路径
- 关卡失败或澄清未解决即 ERROR
- 遵循统一契约字段命名、错误模型与退出码（见 contracts-unified.md）
