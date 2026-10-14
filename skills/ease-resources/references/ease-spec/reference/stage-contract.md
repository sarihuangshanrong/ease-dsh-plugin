# 阶段契约总表（Stage Contract）

> 本文档是三阶段开发流程的**契约权威依据**。当需要判断"某阶段的精确输入/输出路径""跨阶段连接键如何推导""某个阈值以哪份定义为准"时，**以此为准**。
>
> 关联：`SKILL.md`、`reference/phase-gate-invariant.md`（路径不变式）、`commands/flow-1-analyze-brd.md`、`commands/flow-1-analyze-trd.md`、`commands/flow-2-design.md`、`commands/flow-3-implement.md`、`commands/starter.md`（一键三阶段编排器，复用本表全部路径/连接键，不新增）、`scripts/bash/*.sh`。
>
> ⚠️ **维护原则**：任何一方（命令 / reference / 脚本）改动了路径、连接键或阈值，必须**同步更新本表**。本表存在的意义就是消除"文档说一套、脚本做一套"的契约漂移。

---

## 0. 绿地 Bootstrap 与三流程的关系

Bootstrap 是零实现系统的一次性预处理，不是 BRD/TRD 的第三条 Track，也不属于 Flow 1/2/3：

```text
Greenfield: constitution → /ease:bootstrap-system → 正常 BRD/TRD 三流程
Brownfield: constitution → analyze-code/arch-docs → 正常 BRD/TRD 三流程
```

它只建立 `docs/architecture/target/`、Walking Skeleton 和首次 observed 基线。现有 BRD/TRD 的 `DOMAIN_ID`、`CHANGE_ID`、`TRACK`、worktree 状态机、阶段目录、生产者/消费者门禁与阈值保持不变；Bootstrap 不得复用某个业务 `CHANGE_ID`，三流程也不得把 Bootstrap 门禁解释为 Flow 1/2/3 PASS。

Flow 2 的架构知识输入按 `ease-system-bootstrap/scripts/resolve-architecture-baseline.sh` 解析：

- `target` → 已批准的 `docs/architecture/target/`；
- `observed` → 原有 `docs/system/` 六件套；
- `hybrid` → observed 当前事实 + target 演进约束；
- `bootstrap_required` → 停止并显式请求 Bootstrap；
- `generate_observed_baseline` → 对已有代码执行 `/ease:arch-docs` 后重新准入。

---

## 1. 为什么需要这张表

三阶段流程的连接键散落在多处：`DOMAIN_ID/CHANGE_ID`、路径约定、UC/BR ID、增量变动标记（Δ）和覆盖率阈值。任何一处漂移都会让下游阶段**静默失效**。

本表把这些连接键收敛到**单一权威定义源**，与 `phase-gate-invariant.md` 把"路径规则"收敛到单一权威的做法一脉相承。

---

## 2. 核心连接键（Single Source of Truth）

### 2.1 `DOMAIN_ID` / `CHANGE_ID` 推导规则（不可协商）

三阶段使用两个互不替代的标识：

- `DOMAIN_ID` 是**长期领域身份**，格式为 `[三位编号]-[domain-name]`，只用于 `docs/domains/${DOMAIN_ID}/`。全新领域创建一次；增量需求复用匹配到的已有领域。
- `CHANGE_ID` 是**单次需求/变更身份**，格式为 `[三位编号]-[change-name]`，每次执行 Flow 都扫描 `.eases/` 生成新编号，所有过程产物写入 `.eases/${CHANGE_ID}/`。即使多个需求修改同一领域，也不得复用 `CHANGE_ID`。
- `TRACK=brd|trd` 决定是否使用 `.eases/trd/` 前缀，标识本身永远不包含 `trd/`。
- `FEATURE_NAME` 是 `CHANGE_ID` 的迁移期兼容别名；新文档和新逻辑不得再用它表示 `DOMAIN_ID`。

| 路径 | 标识规则 |
|------|----------|
| **BRD - 全新领域** | 创建新的 `DOMAIN_ID`；同时创建独立的 `CHANGE_ID`，二者允许首次同名但语义不得混用 |
| **BRD - 增量领域** | 复用已有 `DOMAIN_ID`；始终新建 `CHANGE_ID`，防止分析报告、tasks 和实现总结覆盖历史变更 |
| **TRD** | 不要求 `DOMAIN_ID`；创建 `CHANGE_ID=${TRD_NUM}-${CHANGE_NAME}`，由 `TRACK=trd` 写入 `.eases/trd/${CHANGE_ID}/` |

Flow 1 必须生成 `.eases/${CHANGE_ID}/context.json`（TRD 位于 `.eases/trd/${CHANGE_ID}/context.json`），至少记录 `schema_version`、`change_id`、`domain_id`（TRD 可为空）、`track`、`requirement_source` 与新流程的 `git` 准入证据。Flow 2/3 优先接收显式 `CHANGE_ID`；仅在未提供时按 `context.json` 查找匹配 `DOMAIN_ID` 的未完成变更，匹配 0 个或多个都必须停止并要求用户指定，禁止猜测。为兼容历史续跑，validator 仍接受没有 `git` 的旧 context，但消费者必须补做 worktree 准入，不得把缺字段视为豁免。

`context.json` 必须符合 `ease-analysis/schemas/flow-context.schema.json` 并通过 `validate_flow_context.py`；BRD 的 `domain_id` 必填，TRD 的 `domain_id` 必须为 null。

> 🔑 **flow-2 / flow-3 推导一致性要求**：starter 必须同时传递 `DOMAIN_ID + CHANGE_ID + TRACK`。单阶段调用从显式参数或 `context.json` 恢复，绝不能从某个领域目录直接推断唯一的变更目录。

#### 落地机制：Change Worktree 准入

`CHANGE_ID` 同时绑定唯一分支 `feature/${CHANGE_ID}` 与唯一 Git worktree。Flow 1 在首次写入任何产物前、Flow 2/3 在首次写入本阶段产物前，都必须调用：

```bash
scripts/bash/ensure-change-worktree.sh \
  --change-id "${CHANGE_ID}" --policy "${WORKTREE_POLICY:-auto}"

# PowerShell
$WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
scripts/powershell/ensure-change-worktree.ps1 `
  -ChangeId "${CHANGE_ID}" -Policy $WorktreePolicy
```

只有 `reused-current` 或用户显式选择 `off` 后的 `skipped` 可以继续写入。`created`、`attached*`、`existing-worktree` 表示已经找到目标，但调用者仍须把后续工具工作目录切到返回的绝对路径并二次校验。状态机、策略和错误处理以 `reference/worktree-contract.md` 为权威。

#### 落地机制：`EASE_FEATURE_DIR` / `--feature-dir`

各阶段调用 ease-spec 脚本前，**必须先导出 `EASE_FEATURE_DIR`（相对 `.eases/` 的阶段子目录）**，或给 `create-new-feature.sh` 传 `--feature-dir`：

| 阶段 | `EASE_FEATURE_DIR` 取值 |
|------|------------------------|
| flow-1 (BRD) | `${CHANGE_ID}/flow-1-analyze` |
| flow-1 (TRD) | `trd/${CHANGE_ID}/flow-1-analyze-trd`（仅定位 TRD 精简权威链，不触发通用 spec/plan 脚本） |
| flow-2 | `${CHANGE_ID}/flow-2-design` |
| flow-3 | 指向**权威任务目录**：BRD→`${CHANGE_ID}/flow-2-design`，TRD→`trd/${CHANGE_ID}/flow-1-analyze-trd` |

> BRD 设置后：脚本把 spec/plan/tasks 写入该子目录、**复用同一特性目录而非 `git checkout -b` 新建分支**，且 `check-prerequisites.sh` / `setup-plan.sh` 跳过分支名校验。TRD 不调用这些 BRD 生命周期脚本，只复用目录身份约定并直接生成专属 `tasks.md`。
>
> **旧目录兼容规则**：新任务只允许写入 `flow-2-design/`。下游命令在新目录不存在时可兼容读取历史 `design/`；若 `flow-2-design/` 与 `design/` 同时存在，必须阻断并要求人工确认权威目录，禁止静默合并或覆盖。

### 2.2 UC / BR ID 规范（权威：`ease-analysis/references/id-standards.md`）

| 元素 | 格式 | 示例 |
|------|------|------|
| 用例 ID | `UC-[%03d]` | `UC-001`、`UC-042` |
| 规则 ID | `BR-[%03d]-[rule-name]` | `BR-001-approval-limit` |

> 🔑 UC/BR ID 是贯穿三阶段的**核心连接键**：Δ 标记、TODO 注释、测试方法关联、commit message 全部引用它。**ID 不规范或不唯一 → 下游所有引用断链。** flow-1 Phase Gate 必须校验"ID 格式合规且全局唯一"。

### 2.3 增量变动标记（Δ）体系（权威：本表 + flow-1 步骤 5.5.1）

| 标记 | 含义 | 贯穿阶段 |
|------|------|---------|
| `[Δ-NEW]` | 本次需求新增 | flow-1（delta-analysis）→ flow-2（设计/注释标注）→ flow-3（实现+Javadoc 保留） |
| `[Δ-MOD]` | 本次需求修改已有元素 | 同上，且 flow-3 须做回归保护 |
| `[Δ-UNCHANGED]` | 涉及但未变（上下文引用） | 同上 |

> 🔑 唯一信号文件：`.eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md`。flow-2/flow-3 以该文件与 `context.json.domain_id` 判定 `REQUIREMENT_MODE=incremental-domain`。

### 2.4 领域对齐基线、决策与阶段证据

UC/BR 不仅是文本编号，也是需求、设计、代码和测试之间的稳定连接键。BRD 路径使用以下三类工件形成闭环：

| 工件 | 路径 | 权威职责 |
|------|------|----------|
| 领域基线 | `docs/domains/${DOMAIN_ID}/domain-alignment.json` | 活动/废弃 UC/BR、需求来源、Δ 与领域漂移状态 |
| 设计证据 | `.eases/${CHANGE_ID}/flow-2-design/alignment/domain-design-matrix.json` | UC/BR → 架构/详细/API/测试设计映射 |
| 实现证据 | `.eases/${CHANGE_ID}/flow-3-implement/checklists/domain-implementation-alignment.json` | UC/BR → 代码/测试映射 |
| 领域决策 | `docs/domains/${DOMAIN_ID}/decisions/{README.md,NNN-title.md}` | 重要业务语义变化的理由、选项和历史 |
| 语义裁决 | `.eases/${CHANGE_ID}/domain-semantic-review.json` | 对指定 Git 提交范围的领域漂移裁决 |

规则：

- Flow 1 全新与增量领域都必须生成/更新领域基线；`delta-analysis.md` 只作为单次变动说明。
- 本次 `NEW`/`MOD` UC/BR 的设计、代码和测试证据覆盖率均为 100%。
- Flow 2/3 发现业务语义变化必须回流 Flow 1，禁止下游阶段静默修改领域事实。
- Flow 3 存在未解决或 blocking 领域漂移时阻断完成。
- TRD 必须生成 `validation/domain-impact.json`：`none` 保持直连 Flow 3，`potential/confirmed` 转 BRD。
- 本地 git-commit 使用 drift `warn`；CI 使用严格只读 `block` 验收，高风险裁决要求人工确认。
- Schema、模板、验证命令以 `ease-analysis/references/domain-alignment-contract.md` 为权威。

### 2.5 质量阈值（单一定义源）

> 🔑 覆盖率与质量阈值**以本表为唯一定义源**，其余文件应引用而非各自硬编码。

| 指标 | 阈值 | 适用阶段 |
|------|------|---------|
| 行覆盖率 | ≥ 80% | flow-3（GREEN 后）/ ease-testing |
| 分支覆盖率 | ≥ 70% | 同上 |
| 方法覆盖率 | ≥ 85% | 同上 |
| 断言价值 | 每个测试最高有效断言等级 ≥ L2；允许辅助 L1，但不得存在仅 L0/L1 的测试 | flow-3（GREEN 后）/ ease-testing §7.3.5 |
| 确定性隔离 | D1–D9 / D-Gate 全部通过 | flow-3（GREEN 后）/ ease-testing §7.3.6 |
| 核心方法变异冒烟 | 每个核心业务方法至少 1 个变异被测试杀死 | flow-3（GREEN 后）/ ease-testing §7.5.1 |
| 设计要点可追溯率 | ≥ 80% | flow-2（设计要点引用用例） |
| 测试案例可追溯率 | ≥ 90% | flow-2（test-case-document） |
| 规则覆盖率 | ≥ 90% | flow-2（test-case-document） |
| 本次变更 UC/BR 设计覆盖率 | 100% | flow-2（domain-design-matrix） |
| 本次变更 UC/BR 代码/测试证据覆盖率 | 100% | flow-3（domain-implementation-alignment） |

### 2.6 TRD 比例质量门禁

本节只裁剪纯技术 TRD；BRD 继续使用 §2.5 全部门禁。

| TRD Profile | Flow 3 必需证据 | 可条件化项目 |
|---|---|---|
| **Lite** | 变更前失败/复现基线、相关回归测试、构建/静态检查、依赖或运行时兼容验证、回滚判断 | 未新增/修改核心方法时，覆盖率阈值、D-Gate、变异冒烟不强制，记录 `N/A + 理由`；涉及外部资源或核心方法时恢复对应门禁 |
| **Standard** | Lite 全部；变更代码的 TDD/回归与适用覆盖率；兼容/灰度验证 | D-Gate 在触及 DB/Redis/MQ/网络/时间时强制；变异冒烟只针对新增/修改的核心方法 |
| **Strict** | 完整 TDD、覆盖率阈值、断言价值、D-Gate、核心方法变异冒烟、兼容/迁移、灰度观测和回滚演练 | 无；确实不存在核心方法时，变异项可 `N/A`，但必须由设计说明证明 |

风险级别从 `TRD.md` 读取；旧 TRD 未记录时按 `Standard`，命中数据库迁移、安全合规、高可用、不可逆或跨系统风险时强制升级 `Strict`。

### 2.7 临时文件落盘契约（不可协商）

本节适用于 `plugins/ease/` 下所有 skill、command 及其直接调用的脚本。凡 Ease 主动创建、仅服务于执行过程且不属于最终交付物的文件或目录，包括分析草稿、中间转换文件、评审暂存件、下载/解压目录、缓存、备份和原子替换文件，均视为 **Ease 临时产物**。

| 执行类型 | 唯一允许的临时目录 |
|------|----------|
| BRD Flow（已知 `CHANGE_ID`） | `.eases/${CHANGE_ID}/.tmp/${PRODUCER}/` |
| TRD Flow（已知 `CHANGE_ID`） | `.eases/trd/${CHANGE_ID}/.tmp/${PRODUCER}/` |
| quick-develop 任务（已知任务目录） | `.eases/quick/[编号]-[task_name]/.tmp/${PRODUCER}/` |
| 非 Flow、初始化或尚未确定 `CHANGE_ID` | `.eases/.tmp/${RUN_ID}/${PRODUCER}/` |

其中 `PRODUCER` 使用稳定的 skill/command/script 名称，`RUN_ID` 必须在本次执行内唯一，避免并发覆盖。

强制规则：

- 禁止 Ease 临时产物写入 `/tmp`、系统临时目录、`.ease/`、项目根目录、`docs/` 或源码目录；不得以“稍后清理”为理由绕过 `.eases/`。
- 创建临时文件前必须先建立对应 `.eases/.../.tmp/` 目录；原子替换文件应与仓库位于同一文件系统，并使用唯一文件名和安全权限。
- skill/command 成功结束时必须通过 `trap`、`finally` 或等价机制清理其临时产物；失败时可保留在原 `.eases/.../.tmp/` 目录用于诊断，并在执行摘要中记录路径。临时产物不得成为下游阶段的唯一输入或事实来源。
- 需要长期保留、跨阶段消费或用于验收的内容不是临时文件，必须提升到本表定义的正式 `.eases/` 产物路径；经确认的领域事实、长期 TC 和架构质量资产允许进入 `docs/`。
- 测试代码通过 `@TempDir`、`tmp_path`、`t.TempDir()` 等测试框架创建并自动回收的隔离资源，不属于 Ease skill/command 的过程产物；Ease 不得自行把同类测试夹具写入仓库外目录。
- 第三方程序不可配置的内部缓存不纳入本契约；只要调用方能够指定临时目录，就必须显式指向上述 `.eases/.../.tmp/` 路径。

---

## 长期 TC 产物补充契约

TC 与 UC 一样是长期资产，定义以 `ease-test-case-design/references/durable-test-assets.md` 为准。Flow 2 的测试设计角色拥有 `docs/domains/${DOMAIN_ID}/testcases/` 和 `docs/qa/testcases/{cross-domain,architecture}/` 的维护权限；UC/BR 权限不变。新任务 `test-case-document.md` 是可选只读投影，唯一权威是 docs 中的 TC。

BRD 选择为 `flow-2-design/test-cases/test-selection.json`，TRD 为 `flow-1-analyze-trd/validation/test-selection.json`；两轨 Flow 3 都产出 `testing/{test-execution,execution-snapshot}.json`。案例内容不得散落为各任务独立副本。旧任务无 selection 时兼容旧案例文档；有 selection 则必须验证，失败不能降级。


## 3. 阶段输入 / 输出契约表

> ✅ **现状**：自引入 `EASE_FEATURE_DIR` / `--feature-dir` 机制后（见 §2.1），脚本实际产出已与命令文档声明的阶段子目录路径**对齐**。§4 原列出的 C-1~C-4 不一致项已修复。

### 3.1 Phase 1 - BRD（`/ease:flow-1-analyze-brd`）

| 项 | 路径 |
|----|------|
| **输入** | 用户需求描述 `$ARGUMENTS`；`memory/constitution.md`；已有 `docs/domains/`（增量检测） |
| **长期领域产出** | `docs/domains/${DOMAIN_ID}/` 下的 `domain-overview.md`、`artifacts/{data-model,stakeholders}.md`、`usecases/[编号]-[subdomain]/{usecase,rules}.md`、`domain-alignment.json`、按需的 `decisions/` |
| **过程报告** | `.eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md` |
| **spec 产出（文档声明）** | `.eases/${CHANGE_ID}/flow-1-analyze/{spec,plan,tasks}.md` |
| **增量产出** | `.eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md`（仅 incremental-domain） |
| **ease-spec 入口** | `reference/create-requirements-spec.md` → `reference/create-technical-plan.md` → `reference/generate-tasks.md` |
| **脚本** | `scripts/bash/ensure-change-worktree.sh`、`create-new-feature.sh`、`setup-plan.sh`、`check-prerequisites.sh` |

### 3.2 Phase 1 - TRD（`/ease:flow-1-analyze-trd`）

| 项 | 路径 |
|----|------|
| **输入** | 技术需求描述 `$ARGUMENTS`（需经需求守门）；`memory/constitution.md`；`docs/system/`（现状自查） |
| **简洁描述** | `docs/trd/[编号]-[trd_name].md` |
| **权威产出** | `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/`：`TRD.md`（需求权威）、`artifacts/solution-design.md`（设计权威）、`tasks.md`（实施账本）、`validation/domain-impact.json` |
| **按风险产出** | `Lite`：其余分析/风险/验证内容内联于两份权威文档；`Standard`：有独立消费价值时生成 `analysis/`、`impact-analysis.md`、`risk-assessment.md`、验收文档；`Strict`：数据库迁移、安全合规、高可用、不可逆或跨系统变更必须生成完整分析、兼容/迁移、风险回滚、验证工件与 checklists。三档均可按需生成架构图、API 与 Schema 设计。 |
| **精简约束** | TRD 不生成 `spec.md` / `plan.md`；不得把 BRD 用户故事、P1/P2/P3 或 MVP 模板套入技术需求。`tasks.md` 使用 `templates/trd-tasks-template.md` 按基线、实施、兼容、验证、发布、回滚组织。 |
| **历史兼容** | 旧 TRD 的 `spec.md` / `plan.md` 可原地只读保留，但不参与新门禁且不得覆盖 `TRD.md` / `solution-design.md`。旧 US/MVP tasks 或被提前全标 `[X]` 的 tasks 必须在 Flow 1 一次性迁移为技术工作包：保留旧 ID 映射，只有实现/测试证据充分时保留完成状态，其余恢复 `[ ]`，迁移记录写入 `migration/legacy-trd-lifecycle.md`。范围、验收、方案、任务任一冲突未解决时 Stop-the-Line。 |
| **路径不变式** | Domain Impact Guard=`none` 时 TRD 设计内置于 Phase 1，**直连 flow-3**；`potential/confirmed` 转 BRD，不得借 TRD 绕过领域分析 |

### 3.3 Phase 2 - 设计（`/ease:flow-2-design`，仅 BRD 路径）

| 项 | 路径 |
|----|------|
| **输入** | `docs/domains/${DOMAIN_ID}/usecases/`；架构基线（存量保持 `docs/system/` 六件套；绿地使用已批准 `docs/architecture/target/`；hybrid 同时读取）；`.eases/${CHANGE_ID}/flow-1-analyze/{spec,plan,tasks}.md`；`delta-analysis.md`（增量） |
| **设计产出** | `.eases/${CHANGE_ID}/flow-2-design/architecture/{arch-design,api-interface-report}.md`、`detail/detail-design.md`、`test-cases/test-selection.json`、`test-cases/test-case-document.md`（只读投影）、`alignment/domain-design-matrix.json` |
| **代码产出（全新）** | `.eases/${CHANGE_ID}/flow-2-design/framework-code/`（骨架 + `framework-code-manifest.md` + `test-framework-manifest.md` + `src/test/`） |
| **代码产出（增量）** | 现有代码内 TODO 注释 + `.eases/${CHANGE_ID}/flow-2-design/code-annotations/code-annotation-manifest.md` + `code-mapping.md` |
| **spec 产出（文档声明）** | `.eases/${CHANGE_ID}/flow-2-design/{spec,plan,tasks}.md` |
| **生命周期** | 全新：`specify → clarify → plan → framework-code → tasks`；增量：`specify → clarify → plan → code-mapping → code-annotation → tasks` |

### 3.4 Phase 3 - 实现（`/ease:flow-3-implement`）

| 项 | 路径 |
|----|------|
| **输入（BRD）** | flow-2 的 framework-code/ 或现有代码 TODO 注释；`arch-design.md`、`detail-design.md`、**权威任务列表 `flow-2-design/tasks.md`**、`delta-analysis.md`（增量） |
| **输入（TRD）** | `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/`（`TRD.md`、`artifacts/solution-design.md`、`validation/domain-impact.json`、**权威任务列表 `tasks.md`**）；无需 `spec.md` / `plan.md` |
| **实现产出** | 实际代码 + 测试代码；BRD 总结 `.eases/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`、TRD 总结 `.eases/trd/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`；BRD 清单 `.eases/${CHANGE_ID}/flow-3-implement/checklists/{implementation.md,domain-implementation-alignment.json}`、TRD 清单 `.eases/trd/${CHANGE_ID}/flow-3-implement/checklists/implementation.md` |
| **任务回写** | **就地**在权威 `tasks.md` 中把完成项标记为 `[X]`，**不生成** `flow-3-implement/{spec,plan,tasks}.md` |
| **生命周期** | 仅 `implement`：BRD 消费 Phase 2 的 spec/plan/tasks；TRD 消费 `TRD.md → solution-design.md → tasks.md`。两者均不重跑前置生命周期，实现以 TDD 红-绿-重构驱动。 |

---

## 4. 契约一致性历史（已修复）

> 以下为曾存在的命令文档声明与脚本实际行为之间的差异，**均已修复**。保留记录以便理解设计取舍与回归排查。

| 编号 | 原不一致点 | 修复方式 | 状态 |
|------|-----------|---------|------|
| **C-1** | 脚本产出 `.eases/<BRANCH_NAME>/spec.md`（根层），与文档声明的阶段子目录不符 | 脚本支持 `EASE_FEATURE_DIR`/`--feature-dir`，写入指定阶段子目录 | ✅ 已修复 |
| **C-2** | 每阶段 `git checkout -b` 新建分支+编号，导致 `FEATURE_NAME ≠ BRANCH_NAME`、阶段产物互不可见 | feature-dir 模式下**不新建分支、不算编号**，三阶段复用同一特性目录 | ✅ 已修复 |
| **C-3** | flow-3 门控按 BRD 产物（usecases/design）检查，TRD 直连路径被卡死 | flow-3 步骤 1.2.1 改为 BRD/TRD **双分支**门控 | ✅ 已修复 |
| **C-4** | flow-3 重跑 `specify→plan→tasks`，产生第三套产物破坏单一事实来源 | flow-3 改为仅 `implement`：消费权威 tasks 并就地回写 `[X]` | ✅ 已修复 |
| **C-5** | 命令已从 `design` 重命名为 `flow-2-design`，但阶段目录仍保留 `design/`，与其他 Flow 命名不一致 | 新产物统一写入 `flow-2-design/`；下游只在新目录缺失时兼容历史 `design/`，双目录并存即阻断 | ✅ 已修复 |
| **C-6** | TRD 先生成完整 TRD/solution-design，再套用 BRD 用户故事模板重复生成 spec/plan，任务也被错误组织为 US/MVP | 新 TRD 使用 `TRD.md → solution-design.md → trd-tasks-template.md` 精简链；Flow 3 不再要求 TRD spec/plan，历史文件只读兼容 | ✅ 已修复 |
| **C-7** | 分支创建责任散落在 Flow 2、旧 `create-new-feature` 路径和可选 `ease-tools` 中，导致不同入口有时建分支、有时不建 | `ensure-change-worktree.sh` 成为五个写入口的统一 Git 原生状态机；一个 `CHANGE_ID` 只创建/复用一个 `feature/${CHANGE_ID}` worktree | ✅ 已修复 |

> 📌 跨平台：PowerShell 脚本同步支持 `EASE_FEATURE_DIR`/`-FeatureDir`，并修正了历史遗留的 `eases/`（应为 `.eases/`）目录名 bug。

### 4.1 过程 Output 迁移兼容

- 新执行只写 `outputs/analysis-report.md` 与 `outputs/implementation-summary.md`，不得再向 `docs/` 创建 `analyze-brd-output.md`、`design-output.md`、`flow-3-implement-output.md` 或 `*-implementation.md`。
- 下游在新路径不存在时，可只读兼容旧 `docs` output；新旧同时存在时以 `.eases/${CHANGE_ID}/` 为权威并报告旧文件待迁移，禁止双写。
- `docs/` 中的领域概览、UC/BR、领域基线、DDR、ADR 和 system 文档属于长期事实，不受本迁移影响。
>
> ⚠️ **遗留待办（非本轮范围）**：PowerShell `create-new-feature.ps1` 在**非** feature-dir 模式下仍使用 `.ease/templates/spec-template.md`（bash 用 `.specify/templates/`）与 `$env:ease_FEATURE`（bash/common 用 `SPECIFY_FEATURE`）。这两处仅影响"自动新建分支"的旧路径，不影响三阶段 feature-dir 主流程，留待后续统一。

---

## 5. 引用方式

判断阶段路径、连接键或阈值时，引用本表为依据：

> 📋 阶段输入/输出路径、`DOMAIN_ID/CHANGE_ID` 推导、UC/BR ID、Δ 标记、领域对齐工件、覆盖率阈值，以 `ease-spec/reference/stage-contract.md` 为权威定义源。

阶段放行的所有权、只读二次验收、反证检查、双向集合对账、证据新鲜度和失败回流，以 `ease-spec/gates/README.md` 及对应路径契约为权威；生产者的 `gate-submission.md` 不等于 PASS。
