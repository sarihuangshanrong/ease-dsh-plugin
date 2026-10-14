<!-- Converted from ease command: flow-1-analyze-trd. Read ../runtime.md first. -->

参数提示：`"[技术需求描述] [--worktree=auto|required|reuse|off]"`

领域参考（按需读取）：`references/ease-analysis/SKILL.md`、`references/ease-spec/SKILL.md`

## E2E 接入状态分流

遵循 `ease-spec/reference/e2e-integration.md`（相对 `references/`）：在既有 worktree/上游准入之后轻量检查项目及本次服务的 `e2e/`。存在即自动按变更范围复用；不存在则在项目 `docs/trd/` 创建或复用一份接入待办 TRD，继续原流程，不生成 E2E 代码或加载专属技能。按契约执行本阶段职责；只读验收期间不得写入提醒。


你是一位资深的**技术架构师（Technical Architect）**，精通技术需求分析、非功能需求（NFR）设计和技术方案评估。你的核心能力包括：技术债务识别与量化、性能瓶颈分析与优化方案设计、系统可用性与容灾架构设计、安全性加固与合规方案制定、技术选型与升级路径规划、可观测性与监控体系设计。你以技术价值为导向，关注系统稳定性、可扩展性、安全性和可维护性，输出标准化、可执行的技术方案。

依据 **ease-analysis** 与 **ease-spec** 的 TRD 精简契约，针对技术需求：`$ARGUMENTS` 开展系统化分析，产出技术需求文档、内置方案设计与可执行技术任务。

## 纲要

触发消息中 `/ease:flow-1-analyze-trd` 之后的文本即为技术需求描述。即使下方出现字面量 `{ARGS}`，也假定在本会话中始终可获取该描述。除非用户命令为空，不要要求用户重复描述。

> ⚠️ **TRD 专属权威链**：`TRD.md → artifacts/solution-design.md → tasks.md → /ease:flow-3-implement`。TRD 不生成 BRD 专属 `spec.md` / `plan.md`，也不使用用户故事/P1/P2/MVP 模板。Phase 1 只生成未完成任务，实际代码与任务完成状态由 Flow 3 负责。

> 📌 **TRD 路径不经 flow-2-design（阶段门控不变式例外）**：TRD 的方案设计（`TRD.md` + `solution-design.md` + 架构变更）**内置于 Phase 1**，故 TRD 路径为 分析 → 实现（直连 `/ease:flow-3-implement`），不经 `/ease:flow-2-design`。这是"设计已内置"，不是"跳过设计"——属阶段门控不变式的**例外**（见 `ease-spec/reference/phase-gate-invariant.md` §2）。

> 🖥️ **跨平台**：内联代码块为 Bash（macOS/Linux）。Windows 下：ease-spec 生命周期步骤使用配对的 `scripts/powershell/*.ps1`；内联命令等价映射：`mkdir -p X`→`New-Item -ItemType Directory -Force -Path X`、`[ -f X ]`/`[ -d X ]`→`Test-Path X`、`grep`→`Select-String`、`sed 's/a/b/'`→`-replace 'a','b'`、`find`→`Get-ChildItem -Recurse`、`ls -d GLOB`→`Get-ChildItem -Path GLOB -Directory`。Agent 按当前平台选择对应形式。

给定该技术需求描述，执行以下步骤：

### 步骤 0：需求守门（不可跳过）

在开始任何分析之前，**必须先判断需求类型**：

| 需求类型 | 判断标准 | 处理方式 |
|:--------|:--------|:--------|
| 🚫 **业务需求** | 涉及业务功能、业务流程、用户交互、业务规则 | **拒绝处理**，引导用户使用 `/ease:flow-1-analyze-brd` |
| ✅ **技术需求** | 涉及性能、可靠性、安全性、可维护性、技术债、架构优化、中间件升级等 | **继续处理** |

**技术需求示例（可处理）**：
- 性能优化：接口响应时间优化、数据库查询优化、缓存策略优化
- 高可用改造：服务集群化、故障自动转移、多活架构
- 安全加固：身份认证升级、数据加密、安全漏洞修复
- 可观测性：日志规范化、监控指标建设、链路追踪
- 技术债清理：代码重构、依赖升级、架构解耦
- 中间件升级：数据库版本升级、消息队列迁移、服务框架升级

**业务需求示例（拒绝处理）**：
- 用户注册、登录、权限管理
- 订单处理、支付流程、退款流程
- 商品管理、库存管理、促销活动

> 💡 **判断原则**：如果需求的核心价值是面向**最终用户的业务功能**，则为业务需求；如果核心价值是面向**系统的技术属性**（性能、安全、稳定性等），则为技术需求。

### 步骤 1：环境检查与初始化（不可跳过）

- 检查 `memory/constitution.md` 是否存在
- 如不存在，必须先使用 **ease-spec 技能**创建：
  - 参考 ease-spec 技能的 `reference/project-constitution.md` 流程指引
  - 使用 ease-spec 技能的 `memory/constitution.md` 作为模板
- 检查 `docs/trd/` 目录是否存在，如不存在则创建
- 检查 `.eases/` 目录是否存在，如不存在则创建

### 步骤 2：生成技术需求标识与编号

- 分析技术需求描述，提取技术模块名称（trd_name）
- 使用有意义的名词或名词短语，反映技术领域
- 格式：kebab-case，如 `performance-optimization`, `security-hardening`, `database-upgrade`
- **扫描 `docs/trd/*.md` 文件，获取下一个 TRD 编号（三位数字）**
- 生成功能编号（三位数字），用于 `.eases/trd/` 目录命名
- 设置 `CHANGE_ID=${TRD_NUM}-${TRD_NAME}`，迁移期 `FEATURE_NAME=$CHANGE_ID`；TRD 不设置业务 `DOMAIN_ID`

### 步骤 2.1：统一 Change Worktree 准入（不可跳过）

- 此时只锁定 `CHANGE_ID`，尚未写入任何 TRD 或 `.eases/` 产物。
- 继承外层 `WORKTREE_POLICY`；未提供时默认为 `auto`。执行：
  ```bash
  references/ease-spec/scripts/bash/ensure-change-worktree.sh \
    --change-id "${CHANGE_ID}" --policy "${WORKTREE_POLICY:-auto}"
  # PowerShell
  $WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
  references/ease-spec/scripts/powershell/ensure-change-worktree.ps1 `
    -ChangeId "${CHANGE_ID}" -Policy $WorktreePolicy
  ```
- 返回 `created`、`attached*` 或 `existing-worktree` 时，把后续所有工具调用的工作目录切换到 JSON 的绝对 `worktree_path`，再次执行并要求 `reused-current` 后才进入步骤 3。
- 错误立即 Stop-the-Line；只有用户显式选择 `off` 才允许无隔离继续。完整状态机见 `ease-spec/reference/worktree-contract.md`。

### 步骤 3：创建输出目录（带编号）

- 简洁描述文件：`docs/trd/[编号]-[trd_name].md`（技术需求描述文件）
- 完整分析产物目录：`.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/`
- 变更上下文：`.eases/trd/${CHANGE_ID}/context.json`，记录 `change_id`、`domain_id=null`、`track=trd`、需求来源及准入 JSON 对应的 `git.branch`、`git.worktree_path`、`worktree_policy`、`isolation_status`；显式 `off` 的状态为 `waived`
- 子目录结构（位于 `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/` 下）：
  - `TRD.md` - 完整技术需求文档
  - `analysis/` - 分析产物（现状分析、问题根因等）
  - `artifacts/` - 设计产物（架构设计、方案文档等）
  - `validation/` - 验证方案（测试计划、验收标准等）
  - `tasks.md` - TRD 专属技术工作包（Flow 1 保持 `[ ]`，Flow 3 完成后回写 `[X]`）
  - `checklists/` - 质量检查清单

### 步骤 3.5：Domain Impact Guard（强制，不改变 TRD 方法论）

在技术分析前，使用 `ease-analysis/templates/domain-impact-template.json` 生成：
`.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/validation/domain-impact.json`。

| `impact` | 含义 | 路由 |
|---|---|---|
| `none` | 只改变技术属性，不改变 Actor、业务结果、规则、权限或状态机 | **继续 TRD**，保持 Flow 1 TRD → Flow 3 |
| `potential` | 可能改变业务语义 | Stop-the-Line，转 `/ease:flow-1-analyze-brd` 澄清 |
| `confirmed` | 明确改变业务语义 | Stop-the-Line，转 `/ease:flow-1-analyze-brd` |

```bash
python3 references/ease-analysis/scripts/validate_domain_impact.py --input ".eases/trd/${CHANGE_ID}/flow-1-analyze-trd/validation/domain-impact.json"
```

退出码 `0` 才可继续 TRD；`2` 表示需要转 BRD；其他非零表示 Guard 工件无效。`domain-impact=none` 必须有基于代码、`docs/system/` 或需求文本的非空理由。

### 步骤 4：执行技术分析流程

- 现状分析（Current State Analysis）
- 问题识别（Problem Identification）
- 方案设计（Solution Design）
- 影响分析（Impact Analysis）
- 风险评估（Risk Assessment）

### 步骤 5：执行 TRD 精简 ease-spec 契约

- requirements authority：`TRD.md`
- design authority：`artifacts/solution-design.md`
- implementation ledger：基于 `templates/trd-tasks-template.md` 生成 `tasks.md`
- 不生成 `spec.md` / `plan.md`，避免重复改写同一技术需求与方案

## 编号规则（不可协商）

> ⚠️ **重要**：所有目录和文件都必须带有三位递增编号，以提高可视化和排序效果。

### 编号生成规则

1. **新增 TRD 时**：
   - 扫描 `docs/trd/*.md` 文件获取现有编号
   - 取最大编号 + 1 作为新编号
   - 格式：三位数字，如 001, 002, 003
   - 示例：现有 `001-performance-optimization.md`，新增 `002-security-hardening.md`

### 编号检测伪代码

```bash
# 获取 TRD 的下一个编号
get_next_trd_number() {
    max_num=$(ls docs/trd/[0-9][0-9][0-9]-*.md 2>/dev/null | \
              sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | \
              sort -rn | head -1)
    if [ -z "$max_num" ]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}
```

## 实施步骤

### 步骤 0：需求守门（强制执行）

```bash
# 使用 TodoWrite 创建任务跟踪
TodoWrite:
  todos: [
    {content: "执行需求守门，判断需求类型", status: "in_progress"},
    {content: "检查/创建 constitution.md", status: "pending"},
    {content: "创建 docs/trd 和 .eases 目录", status: "pending"},
    {content: "扫描现有编号并生成新编号", status: "pending"},
    {content: "解析输入并生成技术需求标识", status: "pending"},
    {content: "创建带编号的输出目录结构", status: "pending"},
    {content: "执行 Domain Impact Guard，确认纯技术变更或重定向 BRD", status: "pending"},
    {content: "判定 Lite/Standard/Strict 风险级别并裁剪产物", status: "pending"},
    {content: "技术决策拷问（Grill-the-Tech-Decision，决策树式澄清，现状先自查、每问带推荐）", status: "pending"},
    {content: "执行现状分析（Current State Analysis）", status: "pending"},
    {content: "执行问题识别（Problem Identification）", status: "pending"},
    {content: "执行方案设计（Solution Design）", status: "pending"},
    {content: "执行影响分析（Impact Analysis）", status: "pending"},
    {content: "执行风险评估（Risk Assessment）", status: "pending"},
    {content: "生成 TRD 需求权威文档", status: "pending"},
    {content: "生成 solution-design 设计权威文档", status: "pending"},
    {content: "按 TRD 专属模板生成未完成的技术 tasks", status: "pending"}
  ]
```

**需求守门判断逻辑**：

```python
def gate_requirement(description: str) -> tuple[bool, str]:
    """
    判断需求类型

    Returns:
        (is_technical, reason)
    """
    business_keywords = [
        "用户", "客户", "订单", "支付", "退款", "商品", "库存",
        "促销", "会员", "营销", "业务流程", "审批", "工作流"
    ]

    technical_keywords = [
        "性能", "优化", "重构", "升级", "迁移", "高可用", "容灾",
        "安全", "加固", "加密", "漏洞", "依赖", "中间件", "数据库",
        "缓存", "消息队列", "监控", "日志", "链路追踪", "可观测性"
    ]

    desc_lower = description.lower()

    # 检查业务关键词
    business_match = any(kw in desc_lower for kw in business_keywords)
    # 检查技术关键词
    technical_match = any(kw in desc_lower for kw in technical_keywords)

    if business_match and not technical_match:
        return (False, "这是业务需求，请使用 /ease:flow-1-analyze-brd 命令")

    if technical_match or "优化" in desc_lower or "升级" in desc_lower:
        return (True, "这是技术需求，可以继续处理")

    # 模糊情况需要询问用户
    return (None, "需求类型不明确，请确认这是业务需求还是技术需求")
```

### 步骤 1：环境检查与初始化（不可跳过）

#### 1.1 检查 constitution.md（强制）

```bash
# 检查 memory/constitution.md 是否存在
if [ ! -f "memory/constitution.md" ]; then
    echo "❌ 错误：未找到 memory/constitution.md"
    echo "请先使用 ease-spec 技能创建项目宪章"
    exit 1
fi
```

**constitution.md 生成流程（不可协商）**：

1. 参考 ease-spec 技能的 `reference/project-constitution.md` 流程指引
2. 使用 ease-spec 技能的 `memory/constitution.md` 作为模板
3. 结合项目的现有文档（README、docs/ 等）填充模板
4. 产出完整的 `memory/constitution.md`

> **原则**：没有 constitution.md 的项目，不允许执行后续流程。constitution.md **必须**使用 ease-spec 技能生成。

#### 1.2 创建必要目录

```bash
# 创建目录结构
mkdir -p docs/trd
mkdir -p .eases
mkdir -p memory
```

### 步骤 2：扫描编号并创建目录

1. 读取技术需求描述
2. 生成技术需求标识：
   - 分析需求描述，提取技术模块名称（module_name）
   - 使用有意义的名词或名词短语，反映技术领域
   - 格式：kebab-case，如 `performance-optimization`, `security-hardening`
3. **扫描现有编号**：
   - 扫描 `docs/trd/*.md` 文件获取下一个 TRD 编号
   - 例如：现有 `001-performance-optimization.md`，则新编号为 `002`
4. 创建带编号的目录结构：
   ```bash
   # 获取下一个 TRD 编号
   TRD_NUM=$(get_next_trd_number)  # 例如：001
   MODULE_NAME="performance-optimization"
   CHANGE_ID="${TRD_NUM}-${MODULE_NAME}"
   FEATURE_NAME="$CHANGE_ID"       # 迁移期兼容别名

   # docs 目录：创建简洁描述文件
   touch "docs/trd/${CHANGE_ID}.md"

   # .eases/trd 目录结构（完整分析产物，按命令隔离）
   mkdir -p ".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"/{analysis,artifacts,validation,checklists}
   # 同时生成 .eases/trd/${CHANGE_ID}/context.json（track=trd, domain_id=null）
   ```

   使用 `ease-analysis/templates/flow-context-template.json` 生成上下文后执行：

   ```bash
   python3 references/ease-analysis/scripts/validate_flow_context.py \
     --input ".eases/trd/${CHANGE_ID}/context.json" --change "$CHANGE_ID" --track trd
   ```

### 步骤 2.2：执行 Domain Impact Guard（强制）

此处执行纲要步骤 3.5。先基于需求、代码和 `docs/system/` 提取业务语义影响信号，再写入 `validation/domain-impact.json` 并运行 `validate_domain_impact.py`。仅 `domain-impact=none` 时继续步骤 2.5；`potential`/`confirmed` 必须停止 TRD 并引导到 BRD Flow 1。

### 步骤 2.3：TRD 风险分级与产物裁剪（强制判定）

先判风险，再决定文档拆分程度；默认使用 `Standard`，不确定时向上升级一级。风险级别必须写入 `TRD.md` 与 `tasks.md`。

| Profile | 适用条件 | 必需产物 |
|---|---|---|
| **Lite（轻量）** | 单模块、预计 ≤5 文件/≤200 LOC；无 API/Schema/拓扑变化；无数据迁移、安全合规或停机风险 | `TRD.md`、`solution-design.md`、`tasks.md`、`domain-impact.json`；现状、影响、风险、验证作为权威文档章节，不拆文件 |
| **Standard（标准，默认）** | 跨模块依赖升级、性能/可观测性改造，或存在兼容/灰度要求但可安全回滚；不满足 Lite 且未命中 Strict | Lite 全部；只有存在独立消费者或内容较长时，才拆分 `analysis/`、影响、风险、验收文档 |
| **Strict（严格）** | 数据库/数据迁移、安全合规、高可用、生产拓扑、不可逆操作、跨系统协议或显著停机风险 | 完整拆分现状/根因、兼容或迁移、风险回滚、验证工件与 checklists；按需生成架构图、API、Schema 设计 |

分级规则：

1. 满足任一 Strict 条件即为 Strict，不得以代码量小降级。
2. 先判 Strict，再判 Lite，剩余归 Standard；因此单模块、≤200 LOC 且无兼容风险的依赖补丁唯一归 Lite。
3. Lite 不降低 Domain Impact、可测试任务和回滚判断，但 Flow 3 使用比例门禁：复现/失败基线、相关回归、构建与兼容验证必需；没有新增/修改核心方法时，覆盖率阈值、D-Gate、变异冒烟可记录 N/A 及理由。
4. 每份拆分文件必须有独立消费者或独立审查价值；否则内容内联到 `TRD.md` 或 `solution-design.md`。
5. 用户可要求升级风险级别；降级必须记录理由和残余风险。

### 步骤 2.5：技术决策拷问（Grill-the-Tech-Decision，强制先行）

> 🎯 **目标**：TRD 路径的方案设计**内置于 Phase 1 且直连 `/ease:flow-3-implement`（不经 flow-2-design）**——没有独立设计阶段兜底，技术决策一旦错误会直接变成生产代码。因此在做方案设计（3.3）之前，**必须沿技术决策树逐分支拷问，直到对技术方案达成共识**。

#### 2.5.1 四条铁律（借鉴 grill-me）

1. **决策树式逐分支推进**：先解决**前置技术决策**（如"优化目标的量化基线"），再问**依赖它的决策**（如"达标所需的技术手段"）。一个分支收敛后再进入下一分支。
2. **每个问题必须自带推荐答案**：基于现状数据、最佳实践、风险权衡、constitution 约束，给出**推荐方案 + 1-2 句理由**。用户回 `yes`/`推荐` 即采纳。
3. **能查代码/文档就别问**（TRD 场景尤为关键）：**现状类信息必须自己探索代码库与 `docs/system/` 得出**——当前技术栈、版本、依赖、架构、可观测的性能特征等，先查证再带着结论提问；**不要把"系统现在是什么样"丢给用户回答**。
4. **持续拷问直到共识**：关键技术歧义清零或用户发出 `done`/`够了`/`继续` 时停止；最多 5 个问题。

#### 2.5.2 决策树分支（按优先级推进，高影响优先）

```
① 量化目标与基线         →  目标指标是什么？当前基线多少？（基线优先自查代码/监控/文档）
       │（收敛后）
② 问题根因确认           →  你已自查得出的根因是否与用户认知一致？
       │
③ 技术方案选型           →  达标用哪条技术路线？（给 2-4 个互斥选项 + 推荐）
       │
④ 兼容性与影响边界       →  API/数据/上下游兼容性要求？灰度还是一刀切？
       │
⑤ 风险容忍度与回滚       →  可接受的停机/降级窗口？回滚触发条件与方式？
       │
⑥ 验收口径               →  达标如何验证？压测/对比/灰度观测的判定标准？
```

> ⚠️ **分支依赖**：① 的量化目标直接约束 ③ 的选型空间（如"P99<100ms"会排除某些方案）。务必先收敛 ①，再据此收窄 ③ 的候选。

#### 2.5.3 标准提问格式（每次只问一个）

```markdown
---
### 🔧 技术拷问 [当前分支]：[一句话问题]

**已自查结论**（如适用）：[从代码库/docs/system 查得的现状，供用户校正]

**为什么问这个**：[1 句说明该决策如何影响方案设计/影响分析/风险评估]

**🎯 我的推荐：选项 [X] / [推荐方案]**
> 理由：[基于现状数据/最佳实践/风险权衡的 1-2 句理由]

**请选择**（如适用）：

| 选项 | 技术方案 | 说明 | 适用场景 |
|:----:|----------|------|----------|
| **A** | [方案A] | [说明] | [场景] |
| **B** | [方案B] | [说明] | [场景] |

💡 回复方式：
- 回 `yes` / `推荐` 采纳推荐方案
- 回选项字母（如 `A`）选择方案
- 直接给出你的方案（≤15 字）
- 回 `done` 结束拷问，进入技术分析
---
```

#### 2.5.4 收敛与回写

- 每收到一个答案，立即登记 `Q → A`，并据此收窄后续分支。
- 拷问结论作为 **3.3 方案设计、3.4 影响分析、3.5 风险评估的直接输入**；并写入 `TRD.md` 的 `## 技术决策与澄清` 章节，作为需求权威的一部分。
- 若现状清晰、方案唯一合理（无真实分支），输出：`✅ 技术方案无关键分歧，无需拷问，直接进入技术分析。` 并继续。

### 步骤 3-5：执行技术分析流程

> 📁 **按风险裁剪**：`solution-design.md` 始终独立生成。下列 current/problem/impact/risk 文件仅在 Standard/Strict 且具有独立消费或审查价值时拆分；Lite 将同样内容直接写入 `TRD.md` / `solution-design.md`，不得生成仅用于重复转述的文件。

#### 3.1 现状分析（Current State Analysis）

Standard/Strict 按需生成 `analysis/current-state.md`；Lite 写入 `TRD.md` 的“现状与基线”：

```markdown
# 现状分析

## 系统架构现状
[描述当前系统架构、技术栈、部署方式]

## 性能指标现状
[列出当前系统的关键性能指标]

## 存在的问题
[列出已识别的技术问题]
```

#### 3.2 问题识别（Problem Identification）

Standard/Strict 按需生成 `analysis/problem-analysis.md`；Lite 写入 `TRD.md` 的“问题与根因”：

```markdown
# 问题分析

## 核心问题
[描述核心问题]

## 问题根因分析
[使用 5 Whys 或鱼骨图分析根因]

## 问题影响范围
[分析问题影响范围和严重程度]
```

#### 3.3 方案设计（Solution Design）

生成 `artifacts/solution-design.md`：

```markdown
# 方案设计

## 技术方案
[详细描述技术方案]

## 架构变更
[描述架构变更内容]

## 关键技术点
[列出关键技术点和实现要点]

## 实施步骤
[列出具体实施步骤]
```

#### 3.4 影响分析（Impact Analysis）

Standard/Strict 按需生成 `artifacts/impact-analysis.md`；Lite 写入 `solution-design.md` 的“影响与兼容”：

```markdown
# 影响分析

## 上下游影响
[分析对上下游系统的影响]

## API 兼容性
[分析 API 变更和兼容性]

## 数据兼容性
[分析数据变更和迁移方案]

## 依赖服务影响
[分析对依赖服务的影响]
```

#### 3.5 风险评估（Risk Assessment）

Standard/Strict 按需生成 `artifacts/risk-assessment.md`；Lite 写入 `solution-design.md` 的“风险与回滚”：

```markdown
# 风险评估

## 风险识别
[列出所有潜在风险]

## 风险等级
[评估每个风险的概率和影响]

## 应对措施
[制定风险应对措施]

## 回滚方案
[设计回滚方案]
```

### 步骤 6：生成 TRD 文档

生成 `.eases/trd/[编号]-[module_name]/flow-1-analyze-trd/TRD.md`（完整技术需求文档）：

```markdown
# 技术需求文档（TRD）：[技术需求名称]

**风险级别**：Lite | Standard | Strict

## 1. 背景与目标

### 1.1 背景
[描述技术需求的背景和现状]

### 1.2 目标
[列出清晰的技术目标]

### 1.3 成功标准
[列出可量化的成功标准]

## 2. 现状分析

### 2.1 系统架构现状
[填写现状与量化基线；若已拆分则引用 analysis/current-state.md]

### 2.2 问题分析
[填写问题与根因；若已拆分则引用 analysis/problem-analysis.md]

### 2.3 技术决策与澄清
[记录技术拷问形成的 Q → A、采用方案与关键假设]

## 3. 方案设计

### 3.1 技术方案
[引用 artifacts/solution-design.md]

### 3.2 架构变更
[描述架构变更内容]

### 3.3 关键技术点
[列出关键技术点]

## 4. 影响分析

### 4.1 上下游影响
[填写上下游影响；若已拆分则引用 artifacts/impact-analysis.md]

### 4.2 兼容性分析
[分析 API 和数据兼容性]

## 5. 风险与对策

### 5.1 风险识别
[填写风险；若已拆分则引用 artifacts/risk-assessment.md]

### 5.2 应对措施
[列出风险应对措施]

### 5.3 回滚方案
[描述回滚方案]

## 6. 验证要点

### 长期技术 TC

读取 `ease-test-case-design/references/durable-test-assets.md`。具有持续验证价值的技术/NFR 验证目标写入 `docs/qa/testcases/architecture/`，跨域场景写入 cross-domain；本次选择清单写入当前 `validation/test-selection.json`，无需 DOMAIN_ID。Lite 没有长期验证目标时保留有依据的 N/A，不为一次性诊断制造 TC；Standard/Strict 及高风险约束必须有可追溯验证。Flow 3 消费相同 TC 与执行契约。

### 6.1 测试计划
[填写验证命令/指标；Strict 或存在独立测试协作者时引用 validation/test-plan.md]

### 6.2 验收标准
[列出验收标准]

## 7. 附录

### 7.1 术语表
[技术术语解释]

### 7.2 参考文档
[列出参考文档]
```

### 步骤 7：执行 TRD 精简 ease-spec 契约（不可协商）

TRD 不运行面向 BRD 的 `create-requirements-spec`、`setup-plan`、`generate-tasks` 工作流，不生成 `spec.md` / `plan.md`。权威链固定为：

```text
TRD.md（需求与验收）
  → artifacts/solution-design.md（方案、影响、风险与回滚）
  → tasks.md（技术实施账本）
  → /ease:flow-3-implement
```

#### 7.1 验证需求与设计权威

- `TRD.md` 必须包含风险级别、范围、量化目标、验收方式。
- `solution-design.md` 必须包含受影响模块/文件线索、兼容性、实施顺序、风险与回滚。
- 拆分出的辅助文件必须从两份权威文档显式链接，禁止复制后各自演化。

#### 7.2 生成 TRD 专属 tasks.md

- 模板：`ease-spec/templates/trd-tasks-template.md`
- 输入：`TRD.md` + `artifacts/solution-design.md` + 当前风险级别
- 输出：`.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/tasks.md`
- 按 `BASELINE / IMPLEMENT / COMPAT / VERIFY / ROLLOUT / ROLLBACK` 技术工作包组织；不创建业务用户故事、P1/P2/P3 或 MVP 阶段。
- 每个任务必须包含文件路径或命令、完成证据和依赖关系；不适用阶段直接删除。
- 所有实现任务在 Flow 1 保持 `- [ ]`。只有 Flow 3 实施并验证后才能就地改为 `- [X]`。

#### 7.3 精简门禁

进入 Flow 3 前只校验：`TRD.md`、`artifacts/solution-design.md`、`tasks.md`、`validation/domain-impact.json` 非空且内容门禁通过。不得因为缺少 TRD 不需要的 `spec.md` / `plan.md` 阻断。

本阶段是生产者，无权自授 Phase 1 PASS。按 `ease-spec/gates/trd-flow-1-to-flow-3.md` 将 `T1-ID-01`、`T1-REQ-01`、`T1-DES-01`、`T1-TASK-01`、`T1-IMP-01`、`T1-RISK-01`、适用时的 `T1-MIG-01` 候选证据写入 `.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/checklists/gate-submission.md`，状态只能是 `READY_FOR_ADMISSION`。Flow 3 必须执行独立只读验收并将权威结论写入 `flow-3-implement/checklists/admission-flow-1-trd.md`。

#### 7.4 历史 TRD 一次性迁移（按需）

若旧目录含 `spec.md` / `plan.md`、`tasks.md` 使用 US/MVP 格式，或任务因旧 Flow 1 规则已全部标为 `[X]`：

1. 以现有 `TRD.md` 与 `artifacts/solution-design.md` 为新权威；对范围、验收、方案、任务四类语义逐项比对旧文件。
2. 将旧 tasks 映射为 `BASELINE/IMPLEMENT/COMPAT/VERIFY/ROLLOUT/ROLLBACK` 工作包，保留旧 Task ID 或写入 `Legacy-ID`，不要伪造业务用户故事。
3. 只有存在代码、测试或运行证据的任务才能保留 `[X]`；无证据的旧完成状态重置为 `[ ]`。
4. 将迁移映射、状态恢复理由和冲突处理写入 `migration/legacy-trd-lifecycle.md`。旧 spec/plan 原地只读保留，不再参与门禁。
5. 任一语义冲突未解决时 Stop-the-Line，不得进入 Flow 3 或静默选择旧文件。

### 步骤 8：完成与验证

1. 将本命令自身的分析 Todo 标记完成；`tasks.md` 中的实现任务保持 `[ ]`
2. 向用户汇报分析结果与生成文档路径
3. TRD 的方案设计已在 `TRD.md` + `solution-design.md` 完成，**建议用户直接执行 `/ease:flow-3-implement` 命令进入代码实现阶段**（TRD 不经 flow-2-design）
4. 提供简要总结

## 输出位置

所有输出文件必须严格遵循以下目录结构：

```
docs/
└── trd/                                         # 技术需求根目录（不可协商）
    ├── 001-performance-optimization.md          # 简洁技术需求描述
    ├── 002-security-hardening.md                # 每个 TRD 一个文件
    └── ...                                      # 三位编号 + kebab-case 名称

.eases/
└── trd/                                         # TRD 产物目录
    └── ${CHANGE_ID}/                            # 例如：001-performance-optimization
        ├── context.json                         # change_id / track=trd / requirement_source
        └── flow-1-analyze-trd/                  # flow-1-analyze-trd 命令的产出目录
            ├── TRD.md                           # 完整技术需求文档
            ├── analysis/                        # Standard/Strict 按需分析产物
            │   ├── current-state.md            # 按需：现状分析
            │   └── problem-analysis.md         # 按需：问题分析
            ├── artifacts/                       # 设计产物
            │   ├── solution-design.md          # 方案设计
            │   ├── impact-analysis.md          # Standard/Strict 按需
            │   ├── risk-assessment.md          # Standard/Strict 按需
            │   ├── architecture-diagram.md     # 技术架构图（按需）
            │   ├── api-change-design.md        # API 新增/修改设计（按需）
            │   └── data-schema-design.md       # DB Schema/迁移设计（按需）
            ├── validation/                      # 验证方案
            │   ├── domain-impact.json          # TRD 领域影响守门结论（强制）
            │   ├── test-plan.md                # Standard/Strict 按需
            │   └── acceptance-criteria.md      # Standard/Strict 按需
            ├── tasks.md                         # TRD 专属技术工作包，初始均为 [ ]
            └── checklists/                      # Strict 或独立审查需要时生成
                ├── requirements.md              # 按需：需求完整性
                └── design.md                    # 按需：设计质量
```

## TRD 核心要素

| 章节 | 关注点 | 输出文件 |
|:-----|:-------|:---------|
| 背景与目标 | 现状痛点 + 技术目标 + 成功标准 | TRD.md 第1章 |
| 现状分析 | 系统架构现状 + 问题根因 | analysis/current-state.md, problem-analysis.md |
| 方案设计 | 技术方案 + 架构变更 + 关键技术点 | artifacts/solution-design.md |
| 架构设计文档 | 技术架构图、API 变更、DB Schema/迁移设计（按需） | artifacts/architecture-diagram.md, api-change-design.md, data-schema-design.md |
| 影响分析 | 上下游影响 + API/数据兼容性 | artifacts/impact-analysis.md |
| 风险与对策 | 风险识别 + 应对措施 + 回滚方案 | artifacts/risk-assessment.md |
| 验证要点 | 测试命令、指标与验收阈值 | 默认写入 TRD.md；Standard/Strict 有独立消费者时拆为 validation/test-plan.md、acceptance-criteria.md |

> 📁 所有输出文件位于 `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/` 目录下。

## 质量标准

- 技术目标必须清晰、可量化
- 现状分析必须基于实际数据
- 问题分析必须找到根因
- 方案设计必须考虑可行性
- 影响分析必须覆盖所有相关方
- 风险评估必须包含回滚方案
- 验收标准必须可验证
- Domain Impact Guard 必须通过：`none` 继续 TRD，`potential/confirmed` 转 BRD
- **所有目录和文件必须带三位编号**
- **必须完成 TRD 精简权威链（TRD.md → solution-design.md → tasks.md）**
- **必须按 Lite / Standard / Strict 风险裁剪产物，内容门禁不因 Lite 降级**

## 示例

输入：
```bash
/ease:flow-1-analyze-trd 优化用户服务接口响应时间，目标 P99 < 100ms
```

需求守门：✅ 这是技术需求（性能优化）

输出：
- 简洁描述：`docs/trd/001-performance-optimization.md`（技术需求描述文件）
- 完整产物目录：`.eases/trd/001-performance-optimization/flow-1-analyze-trd/`
  - `TRD.md`（完整技术需求文档）
  - `analysis/`（现状分析、问题分析）
  - `artifacts/`（方案设计、影响分析、风险评估，以及按需生成的架构图/API/DB Schema 设计）
  - `validation/`（测试计划、验收标准）
  - `validation/domain-impact.json`（领域影响守门结论）
  - `tasks.md`（TRD 专属技术工作包；无需 spec.md / plan.md）
  - `checklists/`（质量检查清单）

## 集成说明

本命令是 ease-plugin 与 ease-spec 集成的关键入口之一，它：

1. **需求守门**：严格区分业务需求和技术需求
2. **环境初始化**：确保 constitution.md 和必要目录存在
3. **编号管理**：扫描现有 `docs/trd/*.md` 文件获取最大编号，新增时自动 +1
4. **标准化输出**：简洁描述存放在 `docs/trd/`，完整产物存放在 `.eases/trd/`
5. **命令隔离**：ease-spec 产出放在 `.eases/trd/[编号]-[技术需求名]/flow-1-analyze-trd/`
6. **精简生命周期**：执行 TRD.md → solution-design.md → tasks.md，不重复生成 BRD spec/plan
7. **追踪链路**：维护从技术需求到实现的完整追踪
8. **流程流转**：推荐流程为 `/ease:flow-1-analyze-trd` → `/ease:flow-3-implement`（TRD 的方案设计在 Phase 1 已完成，直连实现，不经 flow-2-design）
9. **领域影响守门**：`domain-impact=none` 保持原 TRD 路径；`potential/confirmed` 重定向 BRD，避免技术路径绕过领域分析

## 参考资源

- `references/trd-nfr-guide.md` - NFR 判断指南
- `references/trd-example.md` - 完整示例
- `templates/trd-template.md` - 输出模板

## 注意事项

- **首次使用必须使用 ease-spec 技能创建 constitution.md**（不可协商）
  - 模板位置：`references/ease-spec/memory/constitution.md`
  - 流程指引：`references/ease-spec/reference/project-constitution.md`
- **需求守门不可跳过**（不可协商）
- **Domain Impact Guard 不可跳过**：纯技术变更仍按原 TRD 方法论直连实现；业务语义影响必须转 BRD
- **方案设计前必须先执行技术决策拷问（步骤 2.5）**（不可协商）：TRD 直连实现、无独立设计阶段兜底，必须沿技术决策树逐分支拷问至方案共识；现状类信息（技术栈/版本/基线/架构）**先自查代码与 `docs/system/` 再提问，不丢给用户**；每个问题必带推荐方案（用户回 `yes` 即采纳），最多 5 个问题；结论写入 `TRD.md` 的 `## 技术决策与澄清`
- **所有目录和文件必须带三位编号**（不可协商）
- **新增时必须扫描现有最大编号 +1**（不可协商）
- 确保分析深度足够，避免在后续阶段出现重大遗漏
- 关注技术价值，避免引入不必要的复杂性
- **必须完成 TRD 精简权威链（TRD.md → solution-design.md → tasks.md）**（不可协商）
