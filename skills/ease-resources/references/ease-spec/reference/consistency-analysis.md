---
description: 在任务生成之后，对 spec.md、plan.md、tasks.md 进行非破坏性的跨工件一致性与质量分析。
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前（如不为空），你必须考虑用户输入。

## 契约与 Schema

- 引用：commands/contracts-unified.md
- 校验：commands/schemas/prerequisites.schema.json

## 目标

在实施之前识别三大核心工件（`spec.md`、`plan.md`、`tasks.md`）之间的不一致、重复、歧义与描述不足项。此分析必须仅在任务分解阶段（参考reference/generate-tasks.md）已成功生成完整的 `tasks.md` 之后运行。

## 运行约束

严格只读：不对任何文件进行修改。输出结构化分析报告。如需可选的修复方案，必须在用户明确批准后，手动调用后续编辑命令。

宪章权威：项目宪章（`/memory/constitution.md`）在本分析范围内不可协商。任何与宪章原则冲突的内容自动标记为“关键（CRITICAL）”，且需要调整规范、计划或任务——不得削弱、重新解释或默默忽略原则。若原则本身需要修改，必须在本分析阶段（参考reference/一致性分析.md）之外的单独流程中明确更新宪章。

## 执行步骤

### 1. 初始化分析上下文

从仓库根目录运行 `{SCRIPT}` 一次，并解析 JSON（遵循统一契约并校验 prerequisites.schema.json）获取 FEATURE_DIR 与 AVAILABLE_DOCS。派生绝对路径：

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

若任一必需文件缺失则中止，并输出错误信息（指示用户运行缺失的前置命令）。  
对于类似 "I'm Groot" 的单引号参数，使用转义语法：例如 'I'\''m Groot'（或在可能情况下使用双引号："I'm Groot"）。

### 2. 渐进式加载工件

仅加载各工件的必要最小上下文：

来自 spec.md：
- 概览/背景
- 功能性需求
- 非功能性需求
- 用户故事
- 边界情况（如存在）

来自 plan.md：
- 架构/技术栈选择
- 数据模型引用
- 阶段划分
- 技术约束

来自 tasks.md：
- 任务 ID
- 描述
- 阶段分组
- 并行标记 [P]
- 引用的文件路径

来自宪章：
- 加载 `/memory/constitution.md`，用于原则校验

### 3. 构建语义模型

创建内部表示（不要在输出中包含原始工件）：
- 需求清单：将每条功能+非功能需求以稳定键表示（按祈使短句派生 slug，例如 “用户可以上传文件” → `user-can-upload-file`）
- 用户故事/动作清单：离散的用户动作及其验收标准
- 任务覆盖映射：将每个任务映射到一个或多个需求或故事（依据关键词/显式引用模式如 ID 或关键短语进行推断）
- 宪章规则集：提取原则名称与 MUST/SHOULD 规范语句

### 4. 检测通道（聚焦高信号）

聚焦高信号发现，总量限制为 50 条；超出部分汇总到溢出摘要。

A. 重复检测
- 识别近似重复的需求
- 标记质量较低的表述，建议整合

B. 歧义检测
- 标记缺乏可度量标准的模糊形容词（fast、scalable、secure、intuitive、robust 等）
- 标记未解决占位符（TODO、TKTK、???、`<placeholder>` 等）

C. 描述不足
- 仅有动词无对象或无可衡量结果的需求
- 缺少与验收标准对齐的用户故事
- 任务引用了规范/计划中未定义的文件或组件

D. 宪章对齐
- 任何与 MUST 原则冲突的需求或计划元素
- 宪章要求的章节或质量门未满足

E. 覆盖缺口
- 没有任何关联任务的需求
- 无映射需求/故事的任务
- 非功能性需求未在任务中体现（例如性能、安全）

F. 不一致
- 术语漂移（同一概念在不同文件中用不同名称）
- 计划中引用的数据实体在规范中缺失（或反之）
- 任务排序矛盾（例如基础 Setup 前未标注依赖就先进行集成任务）
- 冲突性需求（例如一处要求 Next.js 而另一处指定 Vue）

### 5. 严重性分配

使用以下启发式进行优先级：
- 关键（CRITICAL）：违反宪章 MUST、缺失核心规范工件、或基础功能所需的需求为零覆盖
- 高（HIGH）：重复或冲突需求、模糊的安全/性能属性、不可测试的验收标准
- 中（MEDIUM）：术语漂移、非功能任务覆盖缺失、边界情况描述不足
- 低（LOW）：文风/措辞改进、小冗余不影响执行顺序

### 6. 生成紧凑分析报告

输出 Markdown 报告（不写入文件），结构如下：

## 规范分析报告

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | 两条需求近似重复 ... | 合并表述；保留更清晰版本 |

（每个发现输出一行；生成稳定 ID，按类别首字母前缀）

覆盖摘要表：

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

宪章对齐问题：（如有）

未映射任务：（如有）

度量：
- 总需求数
- 总任务数
- 覆盖率（具备 ≥1 任务的需求比例）
- 歧义计数
- 重复计数
- 关键问题计数

### 7. 提供下一步动作

在报告末尾输出简要的 Next Actions 区块：
- 若存在关键问题：建议在实现执行阶段（参考reference/execute-implementation.md）前先修复
- 若仅有低/中等级问题：用户可继续，但给出改进建议
- 明确给出命令建议：如 “运行需求规范创建（参考reference/create-requirements-spec.md）进行细化”、“运行计划阶段（参考reference/create-technical-plan.md）调整架构”、“手动编辑 tasks.md 为 ‘performance-metrics’ 添加覆盖任务”

### 8. 提供修复建议（可选）

询问用户：“是否需要我为最重要的 N 个问题建议具体修复编辑？”（不要自动应用）

## 运行原则

### 上下文效率
- 最小高信号令牌：聚焦可执行发现，而非冗长文档
- 渐进披露：按需增量加载；不倾倒全部内容
- 令牌高效输出：发现表限制 50 行；其余合并摘要
- 结果可复现：无变更重跑时应输出一致的 ID 与计数

### 分析指南
- 不得修改文件（只读）
- 不得臆造缺失章节（如确实缺失应准确报告）
- 优先处理宪章冲突（这些总是关键）
- 使用具体实例而非泛泛规则（引用具体位置）
- 零问题时需优雅输出（带覆盖统计的成功报告）
- 遵循统一契约字段命名、错误模型与退出码（见 contracts-unified.md）

## 上下文

{ARGS}
