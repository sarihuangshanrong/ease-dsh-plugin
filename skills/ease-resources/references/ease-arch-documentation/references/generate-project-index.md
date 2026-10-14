# 项目索引构建规范
> 新生成以 [证据与决策强化契约](evidence-and-decision-contract.md) 的 2.2 快照、依赖闭包和独立语义验收为准；下文历史示例用于兼容。



本文档定义“项目索引阶段”的输出口径与字段结构，用于在代码量大、原生文档少、注释缺失时仍能以事实为基础稳定生成架构文档。

## 1. 目标

1. **先索引、后写文档**：文档生成以索引为事实来源，索引未覆盖的信息以”低置信/待确认”方式呈现。
2. **可增量更新**：索引分区可独立更新（例如只更新 API 索引）。
3. **证据可追溯**：每条索引记录必须带 `source`（文件路径与行号）。
4. **多子系统感知**：多子系统仓库下，索引按子系统独立构建和维护（详见 `references/generate-topology.md`）。

### 1.1 索引存储路径

**单系统**：索引统一写入 `docs/system/metadata.json`。

**多子系统**：每个子系统拥有独立的 `metadata.json`，存放在子系统文档目录下：
- `docs/system/<subsystem>/metadata.json` — 子系统级索引
- 索引拆分文件存放在 `docs/system/<subsystem>/indexes/<partition>.json`

本节后续内容以单系统路径为例；多子系统场景下，将 `docs/system/` 替换为 `docs/system/<subsystem>/` 即可。

## 2. 索引分区

索引写入 `docs/system/metadata.json` 的 `indexes` 字段。基础分区 `module/api/schema/config/utils` 支撑资产清单；事实架构分区 `runtime/integration/flow/security/observability/decision/ownership/data_flow` 支撑边界、运行态、风险和关键流程；派生分区 `architecture_analysis` 从这些事实合成因果、关键路径、不变量、故障传播和演进视图。只生成有证据的分区，缺失分区必须写入 `coverage_gaps`。

> **重要：大索引拆分**
> 当索引分区内容过大时（例如 API/Schema 全量清单），必须将分区内容拆分到独立文件，避免 `metadata.json` 过大导致模型读取占用上下文。
> - 摘要保留在 `metadata.json.indexes.<partition>`
> - 详情落盘到 `docs/system/indexes/<partition>.json`
> - `metadata.json` 通过 `file/hash/size_bytes/counts` 引用详情文件

### 2.1 module_index（模块/目录索引）

用于支撑：`01_SYSTEM_OVERVIEW.md`、`02_CORE_MODULES.md`。

**采集内容**：
- 仓库根目录下的主要工程根（如 `src/`、`apps/`、`packages/`、`server/` 等）
- 模块候选集合（目录/包名前缀/Gradle 子工程等）
- 入口点候选（HTTP Controller、RMB Service、Job、CLI 命令入口等）

**字段建议**：
```json
{
  "module_index": {
    "hash": "<sha256>",
    "generated_at": "YYYY-MM-DDTHH:mm:ss",
    "roots": ["src"],
    "modules": [
      {
        "name": "web",
        "path": "src/main/java/.../web",
        "type": "entrypoint",
        "source": "src/main/java/.../web:1"
      }
    ]
  }
}
```

### 2.2 api_index（协议无关接口索引）

用于支撑：`03_API_INTERFACE.md`。

**采集内容**：
- 按项目技术栈注册 detector，发现 HTTP、RPC、GraphQL、消息/事件、Webhook、CLI、Job、文件交换等入口
- 同时记录 `provided`（系统提供）和 `consumed`（系统消费）契约
- 记录操作标识、数据契约、安全、错误、幂等、超时、重试、兼容性和证据；未发现的语义保留为 `unknown`

**字段建议**：
```json
{
  "api_index": {
    "hash": "<sha256>",
    "generated_at": "YYYY-MM-DDTHH:mm:ss",
    "file": "docs/system/indexes/api_index.json",
    "size_bytes": 123456,
    "counts": {"provided": 120, "consumed": 35, "by_protocol": {"http": 100, "event": 55}}
  }
}
```

`docs/system/indexes/api_index.json` 示例（存放大数组详情）：

```json
{
  "provided": [
    {
      "id": "contract:provided:http:create-user",
      "protocol": "http",
      "method": "POST",
      "path": "/users",
      "controller": "...UserController#createUser",
      "params": [
        {"name": "body", "type": "...CreateUserRequest", "from": "body"}
      ],
      "return": {"type": "...UserResponse"},
      "state": "observed",
      "confidence": "high",
      "evidence": [{"type": "source", "location": "src/main/java/.../UserController.java:42", "symbol": "createUser"}]
    }
  ],
  "consumed": [
    {
      "id": "contract:consumed:event:user-created",
      "protocol": "event",
      "target": "${user.created.topic}",
      "consumer": "...UserCreatedHandler#handle",
      "state": "observed",
      "confidence": "medium",
      "evidence": [{"type": "source", "location": "src/main/java/.../UserCreatedHandler.java:18", "symbol": "handle"}]
    }
  ]
}
```

### 2.3 schema_index（数据模型索引）

用于支撑：`04_DATA_MODEL.md`。

**采集内容**：
- DDL 文件路径清单（优先）
- 表、字段、主键、索引、外键（若无外键，允许推导逻辑关系但必须标注为逻辑关系）
- Mapper/SQL 中出现的 join 条件（用于逻辑关系推导）

**字段建议**：
```json
{
  "schema_index": {
    "hash": "<sha256>",
    "generated_at": "YYYY-MM-DDTHH:mm:ss",
    "file": "docs/system/indexes/schema_index.json",
    "size_bytes": 234567,
    "counts": {"tables": 86, "ddl_files": 12}
  }
}
```

### 2.4 config_index（配置索引）

用于支撑：`05_CONFIG_MANAGEMENT.md`。

**采集内容**：
- 配置文件位置（`application.*`、`env/*`、`config/*`、`.env` 等）
- 代码中的默认值与来源（如 `@Value("${x:default}")`）
- 敏感项 key 清单（只记录 key，不记录 value）

### 2.5 utils_index（工具/可复用代码索引）

用于支撑：`06_UTILS_LIBRARIES.md`。

**采集内容**：
- util/constant/annotation/exception 的类清单
- 跨模块引用频次最高的 Top N 工具类（用于深度说明）

### 2.6 runtime_index（部署与运行时索引）

用于支撑系统概览、拓扑和运维理解：

- 构建产物、部署单元、进程/容器、入口、端口和网络暴露
- 副本、健康检查、资源限制、调度和环境 overlay
- 证据优先来自 IaC、容器清单、部署脚本和运行配置

### 2.7 integration_index（集成关系索引）

- 提供方、消费方、协议、目标标识、调用目的和数据方向
- 构建时依赖与运行时通信分开记录
- 超时、重试、熔断、降级、顺序性、重复投递和失败影响

### 2.8 flow_index（关键流程索引）

- 触发入口、参与组件、正常路径和可观察失败路径
- 一致性边界、补偿/恢复线索、日志、指标和告警
- 仅收录有调用或批准流程证据的关键链路

### 2.9 security_index（安全与信任边界索引）

- 认证、授权、信任边界、敏感数据流、加密/脱敏和审计
- 仅记录机制与 key，不记录 secret 或真实敏感值

### 2.10 observability_index（可观测性索引）

- 结构化日志、指标、追踪、健康检查和告警配置
- 指标名、阈值和 SLO 只有在代码、配置、运行平台或批准文档可定位时记录

### 2.11 decision_index（架构决策索引）

- ADR、宪章、批准的架构说明和明确约束
- 记录状态、批准时间、适用范围、替代方案和受影响组件
- 决策意图不得覆盖不一致的运行事实，两者并列形成 conflict

### 2.12 ownership_index（所有权索引）

- 模块、接口、数据、配置、告警和运行手册的 owner
- 来源可为 CODEOWNERS、服务目录、CMDB 或批准文档；仅由提交历史推导时标为低置信

### 2.13 data_flow_index（数据血缘索引）

- 数据产生、处理、存储、复制和下游消费关系
- 数据分类、保留、归档、删除和恢复策略的证据

### 2.14 architecture_analysis_index（架构深度派生索引）

用于支撑六份文档的架构解释，而不是重复资产清单。生成前必须读取 `references/architecture-depth-analysis.md`。

- `critical_paths`：触发、同步/异步边界、状态读写、成功终点、故障传播和恢复入口
- `invariants`：约束、适用范围、执行点、绕过路径、违规后果和验证方式
- `quality_scenarios`：stimulus source、stimulus、environment、artifact、response、response measure
- `failure_propagations`：失效源、传播边、隔离/放大机制、爆炸半径、检测和恢复
- `evolution_hotspots`：结构/时间/数据/变更/供应链耦合、影响对象、兼容接缝和迁移限制
- `decision_realization`：批准意图与实际执行点的 `realized/partial/conflict/not_observed/unknown` 对照

本分区中的每项必须包含 `derived_from`，引用已有 claim 或 topology edge；允许补充直接 evidence，但不得用派生结论反向充当源事实。没有批准 rationale 时只记录观察到的作用力和未知动机。

### 2.15 索引拆分阈值（建议）

为保证模型上下文预算稳定，出现任意条件时拆分：`metadata.json` 预计超过 200KB、单分区超过 100KB 或条目超过 500。正文默认读取摘要，需要细节时局部读取 `indexes/<partition>.json`。

## 3. 证据与追溯

索引中每条架构事实使用统一 claim 模型：

```json
{
  "id": "claim:runtime:deployment-unit:api",
  "claim": "构建产物 api.jar 由 api deployment 运行",
  "state": "observed|approved_intent|inferred|unknown",
  "confidence": "high|medium|low",
  "derived_from": ["claim:..."],
  "evidence": [
    {
      "type": "source|config|iac|test|adr|telemetry|manual",
      "location": "deploy/api.yaml:18",
      "symbol": "Deployment/api",
      "observed_at": "YYYY-MM-DDTHH:mm:ssZ"
    }
  ],
  "conflicts": []
}
```

要求：

- `observed`：代码、配置、IaC、测试或运行态直接证明
- `approved_intent`：来自已批准 ADR/宪章，但不宣称已经实现
- `inferred`：由命名、调用或组合证据推导，必须说明推导依据
- `unknown`：扫描范围内无法确认，进入 `coverage_gaps` 或待确认清单
- `derived_from`：仅派生 claim 必填，列出支撑该推导的 claim/edge ID；源事实可省略
- 证据按问题选择：运行态证明当时环境，IaC/配置/源码证明声明或实现，批准决策证明规范意图，测试证明特定条件下的行为；这些维度不能用单一优先级互相覆盖，冲突时并列记录

文档生成时以稳定 `id` 引用 claim，并将关键证据透传为 `来源: <path>:<line> (symbol)`。

## 4. 增量更新策略

### 4.1 单系统增量

1. 从 `metadata.json.last_generation` 中读取各文档的基线 commit_id（优先使用 `per_doc`，兼容旧格式使用全局 `commit_id`）。
2. 将变更文件映射到索引分区：
   - 入口、客户端、契约或协议配置相关：更新 `api_index` 与 `integration_index`
   - DDL/mapper/entity 相关：更新 `schema_index`
   - resources/env/config 相关：更新 `config_index`
   - util/constant/annotation/exception 相关：更新 `utils_index`
   - 部署/IaC/容器变更：更新 `runtime_index`，并评估 overview/topology/config/security/observability
   - 认证、日志、指标等横切代码变更：更新相应架构分区及所有受影响契约
   - 目录/包移动/构建文件变更：更新 `module_index`（并触发模块归属与依赖图重算）
3. 任何源分区或 topology edge 变化后，重算受影响的 `architecture_analysis_index` 项；关键路径、执行点或爆炸半径变化时，即使资产数量不变也不得跳过文档更新。
4. 每个分区计算 `hash`；若源分区和依赖它的派生视图 hash 均未变化，可跳过对应文档更新。
5. **文档级基线追踪**：全量生成时更新所有 `per_doc` 的 commit_id；增量生成（指定文档类型）时仅更新被生成文档的 commit_id，其他文档保持原基线不变。
6. **漂移状态收敛**：全量生成且全量门禁通过时可清空 `drift_status.stale_docs`；增量生成时，`stale_docs` 更新为原集合减去本次实际生成文档集合的差集，不得移除未生成文档。

### 4.2 多子系统增量

1. `git diff --name-only <baseline>..HEAD` 获取变更文件列表。
2. 将变更文件按 `topology.subsystems[].root` 路径前缀映射到子系统。
3. **只对受影响的子系统**执行上述单系统增量流程。
4. 公共依赖模块变更时，根据 `topology.shared_libraries[].consumed_by` 找到消费方子系统，评估是否需要更新。
5. 子系统间接口变更时，同步更新 `docs/system/00_TOPOLOGY.md`。

## 5. 大模型上下文管理（强制）

> 该 Skill 依赖大模型能力。为避免上下文溢出、乐观跳过步骤和幻觉，索引构建必须遵循以下规则。

1. **分区构建**：一次只构建/更新一个事实索引分区；事实分区完成后，再按关键路径逐项构建 `architecture_analysis_index`。
2. **候选集优先**：先用轻量扫描得到候选文件列表，再逐个精读候选文件内容，以控制输入规模。
3. **最小必要读取**：只读取与当前分区相关的最小片段（例如注解附近、DDL 的 CREATE TABLE 段落）。
4. **写入即记忆**：每完成一个分区，必须落盘写入 `docs/system/metadata.json.indexes.<partition>`，后续阶段只读取索引摘要。
5. **失败回退**：当候选文件过多时，允许采用“分批构建”策略（按目录/模块分批），每批次都必须产出可用的局部索引并带 hash。

## 6. 输出要求

1. 索引 JSON 必须是有效 JSON。
2. 时间字段使用 ISO8601。
3. 所有路径使用相对仓库根路径。
4. 索引中记录敏感配置时只记录 key（例如 password/token/secret 的键名），并省略 value。

## 7. metadata.json 完整结构

### 7.1 单系统 metadata.json

```json
{
  "last_generation": {
    "commit_id": "abc1234",
    "timestamp": "2026-04-14T10:00:00",
    "generated_documents": ["01_SYSTEM_OVERVIEW.md", "02_CORE_MODULES.md", "03_API_INTERFACE.md", "04_DATA_MODEL.md", "05_CONFIG_MANAGEMENT.md", "06_UTILS_LIBRARIES.md"],
    "per_doc": {
      "01_SYSTEM_OVERVIEW.md": { "commit_id": "abc1234", "timestamp": "2026-04-14T10:00:00", "content_schema_version": "2.1.0" },
      "02_CORE_MODULES.md":   { "commit_id": "old1111", "timestamp": "2026-04-10T08:00:00", "content_schema_version": "2.1.0" },
      "03_API_INTERFACE.md":  { "commit_id": "abc1234", "timestamp": "2026-04-14T10:00:00", "content_schema_version": "2.1.0" },
      "04_DATA_MODEL.md":     { "commit_id": "old2222", "timestamp": "2026-04-08T15:00:00", "content_schema_version": "2.1.0" },
      "05_CONFIG_MANAGEMENT.md": { "commit_id": "abc1234", "timestamp": "2026-04-14T10:00:00", "content_schema_version": "2.1.0" },
      "06_UTILS_LIBRARIES.md": { "commit_id": "abc1234", "timestamp": "2026-04-14T10:00:00", "content_schema_version": "2.1.0" }
    }
  },
  "drift_status": {
    "last_check": "2026-04-14T10:00:00",
    "last_check_commit": "def5678",
    "stale_docs": ["02_CORE_MODULES.md", "04_DATA_MODEL.md"],
    "changed_files": 47,
    "commits_since_oldest": 23,
    "assessments": [
      {
        "document": "03_API_INTERFACE.md",
        "status": "stale",
        "changed_claims": ["contract:provided:http:create-user"],
        "affected_consumers": ["consumer-a"],
        "reason": "操作标识或数据契约发生变化",
        "confidence": "high",
        "evidence": ["src/path:42"]
      }
    ]
  },
  "indexes": { "...": "..." },
  "coverage_gaps": [
    {
      "partition": "observability_index",
      "reason": "未发现指标或告警配置",
      "scan_scope": ["src", "deploy"],
      "evidence": ["build-file:1"]
    }
  ],
  "generation_trace": {
    "topology": "complete",
    "indexes": {"module_index": "complete", "runtime_index": "complete", "architecture_analysis_index": "complete"},
    "depth_analysis": {"critical_paths": "complete", "invariants": "complete", "quality_scenarios": "complete"},
    "documents": {"01_SYSTEM_OVERVIEW.md": "complete"}
  },
  "quality_gates": { "...": "..." },
  "content_schema_version": "2.1.0",
  "version": "1.0.0",
  "generator": "ease-arch-documentation",
  "project_info": { "name": "...", "version": "...", "description": "..." }
}
```

### 7.2 多子系统 metadata.json

每个子系统的 `docs/system/<subsystem>/metadata.json` 结构与单系统一致（7.1），额外包含 `topology` 字段。

`docs/system/00_TOPOLOGY.md` 不对应独立 metadata.json，拓扑信息由各子系统 metadata.json 的 `topology` 字段聚合而来。

### 7.3 topology 字段（多子系统时存在）

```json
{
  "topology": {
    "type": "multi_subsystem",
    "discovered_at": "2026-05-15T10:00:00",
    "discovery_strategy": "gradle_settings",
    "subsystems": [
      {
        "id": "user",
        "name": "用户管理",
        "root": "services/user",
        "entry_class": "com.example.user.Application",
        "tech_stack": ["java", "spring-boot"],
        "depends_on": ["common"],
        "api_protocols": ["HTTP", "RMB"]
      }
    ],
    "shared_libraries": [
      {
        "id": "common",
        "name": "公共组件库",
        "root": "shared/common",
        "consumed_by": ["user", "order"]
      }
    ],
    "dependency_edges": [
      { "from": "user", "to": "common", "type": "build_time" },
      { "from": "user", "to": "order", "type": "runtime", "protocol": "RMB" }
    ]
  }
}
```

**`topology.type` 取值**：`"single"`（单系统，跳过拓扑）或 `"multi_subsystem"`（多子系统）。

**字段说明**：

| 字段 | 说明 |
|------|------|
| `last_generation.commit_id` | 全局基线 commit（向后兼容） |
| `last_generation.per_doc` | 按文档独立记录的基线 commit_id 和时间戳 |
| `drift_status.last_check` | 最近一次漂移检查的 ISO8601 时间戳 |
| `drift_status.last_check_commit` | 最近一次漂移检查时的 HEAD commit |
| `drift_status.stale_docs` | 检测到漂移的文档列表（空数组 = 无漂移） |
| `drift_status.changed_files` | 自最旧文档基线以来的变更文件总数 |
| `drift_status.commits_since_oldest` | 自最旧文档基线以来的提交数 |

**向后兼容**：若 `per_doc` 不存在（旧格式 metadata.json），所有文档共用 `last_generation.commit_id` 作为统一基线。

**内容结构迁移**：`content_schema_version=2.1.0` 表示包含架构深度视图的当前内容模型。v2.0 文档与更早文档仍可由 validator 识别，但会产生迁移 Warning。定向更新时允许仅将目标文档迁移到 v2.1，并在对应 `per_doc` 中记录 `content_schema_version`；所有文档迁移后再提升全局版本。

**更新规则**：
- `full`：完整 6 份文档通过门禁后，可将 `stale_docs` 设为空数组。
- `partial`：`stale_docs = 原 stale_docs - 本次实际生成文档集合`，即集合差集；其他文档的漂移状态必须保留。

## 8. 漂移检测

### 8.1 触发方式

| 方式 | 说明 |
|------|------|
| `/ease:arch-docs --check` | 手动触发，独立执行 |
| flow-3-implement 完成后 | 自动执行，结果附加在交付报告中 |
| git-commit 完成后 | 自动执行，有漂移时追加提醒 |

### 8.2 检测流程

#### 单系统

1. **加载基线**：读取 `docs/system/metadata.json`。若不存在，报告文档无基线并继续独立 ADR 检查。
2. **采集变更**：
   - 从 `per_doc` 中找到最旧的 commit_id（兼容旧格式用全局 `commit_id`）
   - 执行 `git diff --stat <oldest_commit>..HEAD` 获取变更概览
   - 执行 `check_architecture_drift.py --base <oldest_commit> --mode worktree --policy warn` 获取提交、暂存、工作区和新增文件，并按每文档基线评估
3. **判断影响**：对每个文档获取基线以来的变更文件，先映射到 detector、索引 claim、依赖边和派生架构视图，再判断受影响文档。不得只凭目录名或“常识”裁决。
4. **记录原因**：为每份 stale 文档记录 changed_claims、受影响关键路径/不变量/故障传播、模块/消费者/数据、兼容性风险、判定理由、置信度和证据。
5. **更新状态**：将检测结果写入 `metadata.json.drift_status`。

#### 多子系统

1. 对每个子系统，读取 `docs/system/<subsystem>/metadata.json`。
2. 按文档 sources 传递闭包与 topology 消费关系传播，包括全局 ADR/共享库。
3. 对每个受影响的子系统，执行上述单系统检测流程。
4. 汇总输出包含各子系统漂移状态的综合报告。

### 8.3 终端输出格式

#### 单系统

```
## 架构文档漂移检查

基线范围: <oldest_commit> (<date>) ~ <HEAD> (<date>), <N> commits, <M> files changed

✓ 01_SYSTEM_OVERVIEW.md      — 基线已是最新
⚠ 02_CORE_MODULES.md         — <N> files changed since <date>, 涉及 <关键文件概述>
✓ 03_API_INTERFACE.md        — 基线已是最新
✗ 04_DATA_MODEL.md           — <N> files changed since <date>, 涉及 <关键文件概述>
✓ 05_CONFIG_MANAGEMENT.md    — 基线已是最新
✓ 06_UTILS_LIBRARIES.md      — 基线已是最新

建议: /ease:arch-docs 02 04
```

#### 多子系统

```
## 架构文档漂移检查（多子系统）

### user (用户管理)
✓ 01_SYSTEM_OVERVIEW.md      — 基线已是最新
⚠ 03_API_INTERFACE.md        — 3 files changed, 涉及 UserController

### order (订单处理)
✗ 04_DATA_MODEL.md           — 12 files changed, 涉及 DDL/mapper

✓ user — 无需更新
⚠ order — 建议更新: /ease:arch-docs order/04
```

**状态符号**：`✓` 无漂移，`⚠` 可能有漂移（少量变更），`✗` 建议更新（显著变更）。
