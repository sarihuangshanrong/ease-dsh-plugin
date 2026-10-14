# 质量门禁与一致性校验规范
> 新生成以 [证据与决策强化契约](evidence-and-decision-contract.md) 的 2.2 快照、依赖闭包和独立语义验收为准；下文历史示例用于兼容。



本文档定义架构文档生成后的强制校验规则，用于保证在“大项目/少注释/少原生文档”场景下仍能稳定交付“完整、一致、可验证”的文档。

## 1. 门禁目标

1. **完整性**：6 份文档齐全，章节有实质内容；“不适用”也必须说明扫描范围和证据。
2. **一致性**：跨文档的模块名、接口归属、数据实体引用一致。
3. **可追溯**：关键结论可定位到代码/配置/DDL 的证据来源。
4. **不确定性可见**：无法证明的内容必须以“低置信/待确认”表达。
5. **架构解释力**：关键机制必须能追踪到驱动力、执行点、运行效果、故障传播和演进约束，而不是停留在组件清单。

## 1.1 面向大模型的额外目标

1. **防止上下文溢出**：生成过程必须可分块执行，且中间结果可落盘复用。
2. **防止乐观跳步**：阶段完成后进入下游阶段，并在元数据中记录阶段轨迹。
3. **防止幻觉**：所有关键结论必须能被反向定位到证据。

## 2. 强制检查（Fail 级）

### 2.1 文件存在性

质量门禁必须显式选择范围：

- `full`：用于首次全量生成或完整重建，要求完整 6 份文档。
- `partial`：用于定向/增量生成，仅校验本次实际生成的文档及其依赖索引；其他文档缺失或仍有漂移不导致本次门禁失败。

**单系统 full 模式**：必须存在以下文件（路径与文件名固定）：
- `docs/system/01_SYSTEM_OVERVIEW.md`
- `docs/system/02_CORE_MODULES.md`
- `docs/system/03_API_INTERFACE.md`
- `docs/system/04_DATA_MODEL.md`
- `docs/system/05_CONFIG_MANAGEMENT.md`
- `docs/system/06_UTILS_LIBRARIES.md`
- `docs/system/metadata.json`

**多子系统 full 模式**：每个本次全量生成的子系统目录下必须存在完整的 6 份文档 + `metadata.json`：
- `docs/system/<subsystem>/01_SYSTEM_OVERVIEW.md` ~ `06_UTILS_LIBRARIES.md`
- `docs/system/<subsystem>/metadata.json`
- `docs/system/00_TOPOLOGY.md`（依赖架构汇总）

**partial 模式**：
- 必须显式传入本次实际生成的文档集合。
- 只要求目标文档、`metadata.json` 及目标文档引用的外置索引存在。
- 章节、证据、Mermaid、索引对齐和反向验证都只作用于目标文档。
- 不得因为非目标文档缺失或 `stale_docs` 中仍有其他条目而失败。

### 2.2 章节结构

每份目标文档必须包含固定二级标题集合（可根据项目调整，但必须在生成器中固化并校验）。

最低要求与 `scripts/validate_arch_docs.py::DOCUMENT_HEADINGS` 保持单一契约：

- `01_SYSTEM_OVERVIEW.md`：范围基线、职责边界、技术栈、系统上下文、架构图、驱动力与机制、部署运行时、故障域与恢复、质量属性场景、项目结构、风险
- `02_CORE_MODULES.md`：范围基线、业务能力与边界、模块职责、代码结构、边界契约、不变量与执行点、关键流程、耦合与演进热点、数据所有权与变更影响、风险
- `03_API_INTERFACE.md`：范围基线、协议总览、提供方契约、消费方契约、数据/错误语义、端到端调用与故障传播、安全可靠性兼容性、风险
- `04_DATA_MODEL.md`：范围基线、存储与所有权、核心模型、血缘、数据不变量与关键写路径、一致性、分类保护、生命周期、备份恢复迁移、风险
- `05_CONFIG_MANAGEMENT.md`：范围基线、来源优先级、环境差异、核心目录、Secret、配置控制面与失效半径、变更校验回滚、风险
- `06_UTILS_LIBRARIES.md`：范围基线、共享能力、内部组件、外部依赖治理、横切机制、依赖中心性与演进约束、升级废弃替代、风险

每个必需章节必须包含去除 HTML 注释和证据行后的实质内容。单独的占位符、空表或标题不算完成。

v2.0 与更早的六文档章节仍可通过兼容校验，但必须产生 `PREVIOUS_CONTENT_SCHEMA` 或 `LEGACY_CONTENT_SCHEMA` Warning。增量更新只迁移本次目标文档，并在 `last_generation.per_doc.<document>.content_schema_version` 记录 `2.1.0`；不得强迫无关文档在 partial 模式同时迁移。

### 2.3 Mermaid 可渲染

所有 Mermaid 代码块必须能通过 Mermaid 语法校验（渲染失败则判定 Fail，或回退为文本图并记录 Warning）。

### 2.4 接口索引对齐

以 `metadata.json.indexes.api_index` 为准：

- 外置索引的 `provided`、`consumed` 和 `by_protocol` 数量必须与摘要 `counts` 完全一致
- 正文不强制复制全量条目；正文声明的摘要数量必须与索引一致
- 随机抽样 5%（至少 5 条，不足 5 条则全量）校验操作标识、数据契约和关键运行语义

### 2.5 Schema 索引对齐

以 `metadata.json.indexes.schema_index` 为准：

- 外置索引的对象数量必须与摘要 `counts` 一致
- 正文只需覆盖核心数据对象，但必须链接全量索引并说明选择依据
- 每个正文核心对象至少包含所有权、用途、主键/标识、关键约束和证据

### 2.6 证据覆盖率

对以下“关键结论”要求 100% claim/证据覆盖（缺 1 条即 Fail）：
- 技术栈版本（语言版本、主要框架版本）
- 每个核心模块的目录/包位置
- 每个提供/消费契约的协议和操作标识
- 每张核心表的 DDL 来源
- 每个部署单元及外部依赖关系
- 每项高可用、安全、备份恢复或具体 NFR 结论

索引必须记录 `state`、`confidence` 和结构化 `evidence[]`；正文证据格式：`来源: <path>:<line> (symbol)`。`approved_intent` 和 `inferred` 不得以已实现事实的语气呈现。

### 2.7 随机反向验证（Anti-hallucination）

为对抗“模型凭经验补全”，必须执行随机抽样回查：
- 每份文档至少抽样 3 条“关键条目”（契约、部署单元、依赖边、数据对象、配置 key 等）
- 对每条条目，必须能在 `source` 指向的代码/DDL/配置中找到对应事实
- 若任意 1 条回查失败：本次质量门禁 Fail，必须回退修正索引并重新生成

### 2.8 阶段完成性（Anti-skip）

在 `metadata.json` 中记录各阶段完成情况（建议 `generation_trace`），并校验：
- 对应 `indexes` 分区就绪后再标记对应文档为生成完成
- `full` 模式在 `quality_gates.last_run.result=pass` 之前确保 6 份文档已生成/更新并落盘
- `partial` 模式在标记通过前只要求本次目标文档全部生成/更新并落盘

### 2.9 索引分区文件一致性（Large-metadata safe）

当 `metadata.json.indexes.<partition>.file` 存在时：
- `file` 指向的文件必须存在
- `hash` 必须与分区详情文件的内容 hash 一致
- `counts` 必须与分区详情文件的统计一致（允许误差 0）

否则质量门禁 Fail。

### 2.10 架构深度完整性（Semantic gate）

全量生成必须读取 `architecture_analysis_index`，或在对应 `coverage_gaps` 中给出扫描范围和缺失理由。Agent 在机械门禁后执行以下语义检查：

- 每个有运行入口的 deployable 至少一条关键路径；纯库项目至少一条调用/扩展路径，或有证据的不适用说明。
- 每条关键路径有成功终点、可观察失败分支、传播范围以及恢复机制/证据缺口。
- 每个核心状态写入或信任边界至少对应一个不变量和执行点；只存在设计声明时必须标“未强制执行”。
- 每项具体质量结论包含场景和 response measure；`unknown` 可以通过，但把框架/配置直接等同于质量目标达成则 Fail。
- 每条派生结论包含 `derived_from`；“设计理由”必须来自批准决策证据，无证据的历史动机表述为事实则 Fail。
- 每个演进热点说明耦合类型、影响对象、兼容接缝和证据；仅凭主观复杂度下结论则 Fail。

partial 模式只校验受本次源分区变化影响的关键路径、不变量和热点，不要求重算无关视图。

## 3. 一致性检查（Fail 或 Warning）

### 3.1 模块名一致

`02_CORE_MODULES.md` 定义的模块名集合是“权威集合”。
- `03_API_INTERFACE.md` 的“归属模块”必须属于该集合，否则 Fail。
- `06_UTILS_LIBRARIES.md` 的“归属模块/所在目录”必须能映射到 module_index，否则 Warning。

### 3.2 数据实体引用一致

`04_DATA_MODEL.md` 中出现的表/实体名是“权威集合”。
- `02/03` 引用实体时必须能在 `04` 中找到；找不到则标注“未收录”并 Warning。

### 3.3 术语一致

同一概念（如 RMB、服务注册、配置中心）必须使用统一中文名与缩写。建议维护 `glossary`（可放入 `metadata.json` 扩展字段）。

### 3.4 因果链一致（Fail）

- overview 中的机制/执行点必须能在核心模块、接口、数据、配置或共享能力文档中找到对应 claim。
- 关键路径中的边必须存在于 topology、integration/api/data flow 索引；额外推导边必须标 `inferred`。
- 故障传播、配置失效半径和共享能力爆炸半径引用同一依赖边时，受影响对象集合不得互相矛盾。
- 已批准决策的落实状态为 `conflict/not_observed` 时，不得在其他文档写成已实现事实。

## 4. 不确定性表达检查（Fail 级）

当文档出现以下词汇但没有 `inferred`、`low`、"低置信"或"待确认"标识时，判定 Fail（示例关键词）：
- "应该/可能/大概/推测/估计/通常/一般来说"

正确写法：
- `结论(低置信)` + `现有证据` + `待确认问题(<=3)`

“不适用”“暂无可记录”不是证据豁免：所在章节必须说明扫描范围并提供至少一条来源，否则 Fail。

## 4.1 多子系统额外检查

当 `topology.type = "multi_subsystem"` 时，额外执行以下检查：

### 4.1.1 子系统间接口一致性（Warning）

`00_TOPOLOGY.md` 中声明的子系统间通信，必须在双方文档中可追踪：
- 调用方的 `03_API_INTERFACE.md` 中应标注消费方契约
- 提供方的 `03_API_INTERFACE.md` 中应有对应的接口定义

### 4.1.2 公共依赖引用一致（Warning）

各子系统文档中引用的公共依赖模块，必须能在 `00_TOPOLOGY.md` 的公共依赖列表中找到。

### 4.1.3 目录名与子系统 ID 一致（Fail）

`docs/system/` 下的子目录名必须与 `topology.subsystems[].id` 一致。

## 5. 产出物：门禁报告

门禁执行后必须输出报告（可写入 `metadata.json.quality_gates.last_run`，也可额外生成 `docs/system/quality-report.md`）：

```json
{
  "quality_gates": {
    "last_run": {
      "timestamp": "YYYY-MM-DDTHH:mm:ss",
      "result": "pass|fail",
      "failed_checks": [
        {"id": "API_INDEX_MISMATCH", "message": "..."}
      ],
      "warnings": [
        {"id": "ENTITY_REFERENCE_MISSING", "message": "..."}
      ]
    }
  }
}
```

## 5.1 可执行机械门禁

使用技能内置脚本执行结构化校验：

```bash
# 全量生成
python3 scripts/validate_arch_docs.py \
  --docs-dir docs/system \
  --mode full

# 定向/增量生成
python3 scripts/validate_arch_docs.py \
  --docs-dir docs/system \
  --mode partial \
  --documents 03_API_INTERFACE.md 04_DATA_MODEL.md
```

脚本负责文件存在性、目标章节及非空内容、证据格式、不适用证据、Mermaid 基本结构、metadata JSON、外置索引 hash/counts 校验，并输出 JSON 报告。架构深度完整性、正文摘要数量、跨文档语义一致性及随机源码反查仍由 Agent 在机械门禁通过后执行。

## 6. 建议的实现顺序

1. 先做 2.1/2.2（结构性问题最常见）。
2. 再做 2.4/2.5（确保核心事实不漂移）。
3. 最后做 2.6/3.x/4（确保可信与一致）。
