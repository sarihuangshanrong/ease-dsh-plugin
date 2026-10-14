---
description: 基于现有设计工件为该特性生成可执行、按依赖排序的 tasks.md。
handoffs: 
  - label: 一致性分析
    agent: ease.analyze
    prompt: 运行项目一致性分析
    send: true
  - label: 实施项目
    agent: ease.implement
    prompt: 按阶段开始实施
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---
## 用户输入

> 适用范围：本流程与 `tasks-template.md` 仅用于 BRD。TRD 必须使用 `templates/trd-tasks-template.md`，从 `TRD.md + solution-design.md` 直接生成技术工作包，不得虚构用户故事、P1/P2/P3 或 MVP。

```text
$ARGUMENTS
```

在继续之前，若用户输入不为空，必须优先考虑该输入。

## 纲要

1. 设置：在仓库根目录运行 `{SCRIPT}` 并解析 FEATURE_DIR 与 AVAILABLE_DOCS 列表。所有路径必须为绝对路径。对于包含单引号的参数（如 "I'm Groot"），使用转义语法：例如 `'I'\''m Groot'`（或尽量使用双引号："I'm Groot"）。
2. 加载设计文档：从 FEATURE_DIR 读取：

   - 必需：plan.md（技术栈、库、结构）、spec.md（带优先级的用户故事）
   - 可选：data-model.md（实体）、contracts/（API 端点）、research.md（决策）、quickstart.md（测试场景）
   - 注意：并非所有项目都具备上述全部文档。请基于可用文档生成任务。
3. 执行任务生成工作流：

   - 加载 plan.md，提取技术栈、库、项目结构
   - 加载 spec.md，提取用户故事及其优先级（P1、P2、P3 等）
   - 如果存在 data-model.md：提取实体并映射到用户故事
   - 如果存在 contracts/：将端点映射到用户故事
   - 如果存在 research.md：提取决策用于搭建阶段任务
   - 按用户故事组织生成任务（参见下方“任务生成规则”）
   - 生成显示用户故事完成顺序的依赖图
   - 为每个用户故事创建并行执行示例
   - 校验任务完整性（每个故事具备所需任务，且可独立测试）
4. 生成 tasks.md：使用 `templates/tasks-template.md` 的结构，并填充：

   - 来自 plan.md 的正确特性名称
   - 第 1 阶段：搭建任务（项目初始化）
   - 第 2 阶段：基础任务（阻塞所有用户故事的前置条件）
   - 第 3+ 阶段：按 spec.md 优先级顺序，每个用户故事一个阶段
   - 每个阶段包含：故事目标、独立测试标准、（若请求）测试任务、实施任务
   - 最终阶段：打磨与跨领域关注点
   - 所有任务必须遵循严格的清单格式（见下方“任务生成规则”）
   - 每个任务提供明确文件路径
   - 依赖章节显示故事完成顺序
   - 为每个故事提供并行执行示例
   - 实施策略章节（先 MVP、增量交付）
5. 报告：输出生成的 tasks.md 路径与摘要：

   - 任务总数
   - 每个用户故事的任务数量
   - 识别的并行机会
   - 每个故事的独立测试标准
   - 建议的 MVP 范围（通常仅用户故事 1）
   - 格式校验：确认所有任务均遵守清单格式（复选框、ID、标签、文件路径）

任务生成上下文：{ARGS}

生成的 tasks.md 应可立即执行——每个任务必须具体到无需额外上下文时，LLM 即可完成。

## 任务生成规则

关键：任务必须按用户故事组织，以支持独立实施与测试。

测试为可选：仅在功能规范明确请求或用户要求 TDD 时生成测试任务。

### 清单格式（必填）

每个任务必须严格遵循以下格式：

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

格式组成：

1. 复选框：始终以 `- [ ]` 开始（Markdown 复选框）
2. 任务 ID：按执行顺序的连续编号（T001、T002、T003……）
3. [P] 标记：仅在任务可并行（不同文件，且不依赖未完成任务）时添加
4. [Story] 标签：仅用户故事阶段的任务“必须”添加
   - 格式：[US1]、[US2]、[US3] 等（映射自 spec.md 的用户故事）
   - 搭建阶段：不添加故事标签
   - 基础阶段：不添加故事标签
   - 用户故事阶段：必须添加故事标签
   - 打磨阶段：不添加故事标签
5. 描述：清晰的动作说明，附精确文件路径

示例：

- ✅ 正确：`- [ ] T001 Create project structure per implementation plan`
- ✅ 正确：`- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确：`- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确：`- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误：`- [ ] Create User model`（缺少 ID 与故事标签）
- ❌ 错误：`T001 [US1] Create model`（缺少复选框）
- ❌ 错误：`- [ ] [US1] Create User model`（缺少任务 ID）
- ❌ 错误：`- [ ] T001 [US1] Create model`（缺少文件路径）

### 任务组织

1. 来自用户故事（spec.md）——主要组织依据：

   - 每个用户故事（P1、P2、P3……）拥有其独立阶段
   - 将相关组件映射到该故事：
     - 该故事所需的模型
     - 该故事所需的服务
     - 该故事所需的端点/UI
     - 若请求测试：在该故事阶段中加入相应测试
   - 标注故事依赖（大多数故事应可独立）
2. 来自契约（contracts）：

   - 将每个契约/端点映射到其服务的用户故事
   - 若请求测试：每个契约在实现前于该故事阶段添加 [P] 契约测试任务
3. 来自数据模型：

   - 将每个实体映射到需要它的用户故事
   - 若实体服务多个故事：放入最早的故事阶段或搭建阶段
   - 关系 → 在相应故事阶段的服务层任务中体现
4. 来自搭建/基础设施：

   - 共享基础设施 → 搭建阶段（第 1 阶段）
   - 阻塞性前置任务 → 基础阶段（第 2 阶段）
   - 与特定故事相关的搭建 → 放入该故事阶段

### 阶段结构

- 第 1 阶段：搭建（项目初始化）
- 第 2 阶段：基础（阻塞性前置——在用户故事前必须完成）
- 第 3+ 阶段：按优先级顺序的用户故事（P1、P2、P3……）
  - 在每个故事阶段内：测试（如请求）→ 模型 → 服务 → 端点 → 集成
  - 每个阶段应是可独立测试的完整增量
- 最终阶段：打磨与跨领域关注点
