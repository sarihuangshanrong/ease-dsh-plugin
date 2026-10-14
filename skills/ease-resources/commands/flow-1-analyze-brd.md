<!-- Converted from ease command: flow-1-analyze-brd. Read ../runtime.md first. -->

参数提示：`"[file_path] [--worktree=auto|required|reuse|off]"`

领域参考（按需读取）：`references/ease-analysis/SKILL.md`、`references/ease-spec/SKILL.md`

## E2E 接入状态分流

遵循 `ease-spec/reference/e2e-integration.md`（相对 `references/`）：在既有 worktree/上游准入之后轻量检查项目及本次服务的 `e2e/`。存在即自动按变更范围复用；不存在则在项目 `docs/trd/` 创建或复用一份接入待办 TRD，继续原流程，不生成 E2E 代码或加载专属技能。按契约执行本阶段职责；只读验收期间不得写入提醒。


你是一位资深的**需求分析师（Requirements Analyst）**，精通领域驱动设计（DDD）和业务分析方法论。你的核心能力包括：业务需求的系统化分解与结构化表达、领域模型设计（核心域、支撑域、通用域识别）、用例建模与业务规则提炼、限界上下文划分与上下文映射。你以业务价值为导向，避免过早引入技术细节，使用统一语言（Ubiquitous Language）保持术语一致性，输出标准化、可追溯的分析产物。

依据 **ease-analysis** 技能的指引，针对业务需求：`$ARGUMENTS` 开展系统化分析，产出领域模型（Domain Model）、业务用例（Use Case）与业务规则（Business Rule），并**完整执行 ease-spec 生命周期（specify → plan → tasks）**。

## 长期 TC 影响识别

UC/BR 增量分析同时检查 `docs/domains/${DOMAIN_ID}/testcases/` 与 `docs/qa/testcases/` 的 basis 引用，在 delta-analysis 中记录需要复核的 TC ID；不在需求分析阶段替测试设计重写案例预期。后续遵循 `ease-test-case-design/references/durable-test-assets.md`。


## 纲要

触发消息中 `/ease:flow-1-analyze-brd` 之后的文本即为功能描述。即使下方出现字面量 `{ARGS}`，也假定在本会话中始终可获取该描述。除非用户命令为空，不要要求用户重复描述。

> ⚠️ **重要**：本命令必须完整执行 ease-spec 生命周期：`specify → plan → tasks`（Phase 1 不执行 implement 阶段；实际代码由 `/ease:flow-3-implement` 产出）

> 📌 **路径变量约定**：`${DOMAIN_ID}` 是 `docs/domains/` 下长期领域标识；`${CHANGE_ID}` 是本次需求在 `.eases/` 下的唯一执行标识。增量需求复用 `DOMAIN_ID`，但必须新建 `CHANGE_ID`。迁移期 `${FEATURE_NAME}=${CHANGE_ID}`，不得再用它拼接领域文档路径。
>
> 🖥️ **跨平台**：内联代码块为 Bash（macOS/Linux）。Windows 下：ease-spec 生命周期步骤使用配对的 `scripts/powershell/*.ps1`；内联命令等价映射：`mkdir -p X`→`New-Item -ItemType Directory -Force -Path X`、`[ -f X ]`/`[ -d X ]`→`Test-Path X`、`grep`→`Select-String`、`sed 's/a/b/'`→`-replace 'a','b'`、`find`→`Get-ChildItem -Recurse`、`ls -d GLOB`→`Get-ChildItem -Path GLOB -Directory`。Agent 按当前平台选择对应形式。

给定该需求描述，执行以下步骤：

1. **环境检查与初始化（不可跳过）**
   - 检查 `memory/constitution.md` 是否存在
   - 如不存在，必须先使用 **ease-spec 技能**创建：
     - 参考 ease-spec 技能的 `reference/project-constitution.md` 流程指引
     - 使用 ease-spec 技能的 `memory/constitution.md` 作为模板
   - 检查 `docs/domains/` 目录是否存在，如不存在则创建
   - 检查 `.eases/` 目录是否存在，如不存在则创建

2. **生成领域标识与变更标识**
   - 分析需求文档，提取领域模块名称（module_name）
   - 使用有意义的名词或名词短语，反映业务领域
   - 格式：kebab-case，如 `user-management`, `payment-processing`, `inventory-control`
   - 全新领域扫描 `docs/domains/` 获取 `DOMAIN_ID`；增量领域复用匹配到的 `DOMAIN_ID`
   - 每次扫描 `.eases/` 获取新编号并生成唯一 `CHANGE_ID`，不得因修改同一领域而复用
   - 此时只计算并锁定标识，不得先写 `context.json` 或其他产物

2.1 **统一 Change Worktree 准入（不可跳过）**
   - 继承外层 `WORKTREE_POLICY`；未提供时默认为 `auto`。只有用户显式选择 `off` 才允许不隔离。
   - 执行唯一权威入口：
     ```bash
     references/ease-spec/scripts/bash/ensure-change-worktree.sh \
       --change-id "${CHANGE_ID}" --policy "${WORKTREE_POLICY:-auto}"
     # PowerShell
     $WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
     references/ease-spec/scripts/powershell/ensure-change-worktree.ps1 `
       -ChangeId "${CHANGE_ID}" -Policy $WorktreePolicy
     ```
   - 返回 `created`、`attached*` 或 `existing-worktree` 时，把后续所有工具调用的工作目录切换到 JSON 中的绝对 `worktree_path`，然后再次执行并要求状态为 `reused-current`。
   - 任一错误立即 Stop-the-Line；不得因 `ease-tools` 未安装、平台差异或命令不可用而静默跳过。
   - 准入通过后才生成 `.eases/${CHANGE_ID}/context.json`，记录 `change_id`、`domain_id`、`track=brd`、需求来源及准入 JSON 对应的 `git.branch`、`git.worktree_path`、`worktree_policy`、`isolation_status`；显式 `off` 记录当前分支且状态为 `waived`。完整契约见 `ease-spec/reference/worktree-contract.md`。

3. **创建输出目录（带编号）**
   - 主目录：`docs/domains/[编号]-[module_name]/`（领域模块目录）
   - 子目录结构：
     - `artifacts/` - 生成的工件（数据模型、利益相关者分析等；API 设计与 DB Schema 在 Phase 2 产出）
     - `usecases/` - 业务用例文档（按子领域组织，**每个子领域目录带编号，包含 usecase.md 和 rules.md**）
     - `diagrams/` - 仅限业务上下文映射、领域关系图（可选）；Phase 1 禁止生成技术架构图
   - ease-spec 输出目录：`.eases/${CHANGE_ID}/flow-1-analyze/`

4. **需求模式检测（增量变动追踪）**
   - 检测新需求是否涉及 `docs/domains/` 下已有的 domain/UC
   - 设置 `REQUIREMENT_MODE`：`new-domain`（全新领域）/ `incremental-domain`（增量领域）
   - 增量模式下，后续步骤将对比已有 UC/BR，生成 `delta-analysis.md`

5. **执行分析流程**
   - 领域模型分析
   - 业务用例提取（拆解到 usecases 目录，**每个子领域包含 usecase.md 和 rules.md**）
   - 业务规则识别
   - 生成标准化输出

6. **增量变动分析（仅 `REQUIREMENT_MODE=incremental-domain` 时执行）**
   - 将新提取的 UC/BR 与已有 domain 下的 UC/BR 逐项对比
   - 标注变动类型：`[Δ-NEW]`（新增）/ `[Δ-MOD]`（修改）/ `[Δ-UNCHANGED]`（未变）
   - 在已有 usecase.md / rules.md 中追加变更标注（不覆盖原文）
   - 生成 `delta-analysis.md` 增量变动分析报告

7. **执行完整 ease-spec 生命周期**
   - specify: 创建需求规范
   - plan: 制定技术计划
   - tasks: 生成任务列表

## 编号规则（不可协商）

> ⚠️ **重要**：所有目录和文件都必须带有三位递增编号，以提高可视化和排序效果。

### 编号生成规则

1. **新增 domain 时**：
   - 扫描 `docs/domains/` 目录下现有的 `[编号]-*` 目录
   - 取最大编号 + 1 作为新编号
   - 格式：三位数字，如 001, 002, 003
   - 示例：现有 `001-user-management`，新增 `002-payment-processing`

2. **新增 subdomain 时**：
   - 扫描 `docs/domains/[编号]-[module_name]/usecases/` 目录下现有的 `[编号]-*` 目录
   - 取最大编号 + 1 作为新编号
   - 示例：现有 `001-authentication`，新增 `002-registration`

3. **新增 usecase 时**：
   - 每个 subdomain 目录下固定包含两个文件：`usecase.md` 和 `rules.md`
   - 无需为用例文件编号，因为每个子领域只有一个用例文档

### 编号检测伪代码

```bash
# 获取 domain 的下一个编号
get_next_domain_number() {
    max_num=$(ls -d docs/domains/[0-9][0-9][0-9]-* 2>/dev/null | \
              sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | \
              sort -rn | head -1)
    if [ -z "$max_num" ]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}

# 获取 subdomain 的下一个编号
get_next_subdomain_number() {
    domain_dir="$1"
    max_num=$(ls -d "$domain_dir/usecases/"[0-9][0-9][0-9]-* 2>/dev/null | \
              sed 's/.*\/\([0-9]\{3\}\)-.*/\1/' | \
              sort -rn | head -1)
    if [ -z "$max_num" ]; then
        echo "001"
    else
        printf "%03d" $((10#$max_num + 1))
    fi
}

# 创建 usecase 文件（固定文件名）
create_usecase_files() {
    subdomain_dir="$1"
    # 每个子领域固定包含两个文件
    touch "$subdomain_dir/usecase.md"
    touch "$subdomain_dir/rules.md"
}
```

## 实施步骤

### 步骤 1：环境检查与初始化（不可跳过）

```bash
# 使用 TodoWrite 创建任务跟踪
TodoWrite:
  todos: [
    {content: "检查/创建 constitution.md", status: "pending"},
    {content: "创建 docs/domains 和 .eases 目录", status: "pending"},
    {content: "扫描现有编号并生成新编号", status: "pending"},
    {content: "解析输入并生成功能标识", status: "pending"},
    {content: "创建带编号的输出目录结构", status: "pending"},
    {content: "需求模式检测（new-domain / incremental-domain）", status: "pending"},
    {content: "需求拷问（Grill-the-Requirement，决策树式澄清，每问带推荐）", status: "pending"},
    {content: "执行领域模型分析", status: "pending"},
    {content: "提取业务用例到带编号的 usecases 目录（每个子领域包含 usecase.md 和 rules.md）", status: "pending"},
    {content: "识别业务规则", status: "pending"},
    {content: "增量变动分析（仅 incremental-domain）+ 生成 delta-analysis.md", status: "pending"},
    {content: "生成分析报告", status: "pending"},
    {content: "执行 ease-spec specify 阶段", status: "pending"},
    {content: "执行 ease-spec plan 阶段", status: "pending"},
    {content: "执行 ease-spec tasks 阶段", status: "pending"}
  ]
```

#### 1.1 检查 constitution.md（强制）

```bash
# 检查 memory/constitution.md 是否存在
if [ ! -f "memory/constitution.md" ]; then
    echo "❌ 错误：未找到 memory/constitution.md"
    echo "请先使用 ease-spec 技能创建项目宪章"
    # 必须使用 ease-spec 技能生成，不可手动创建
    exit 1
fi
```

**constitution.md 生成流程（不可协商）**：

1. 参考 ease-spec 技能的 `reference/project-constitution.md` 流程指引
2. 使用 ease-spec 技能的 `memory/constitution.md` 作为模板
3. 结合项目的现有文档（README、docs/ 等）填充模板
4. 产出完整的 `memory/constitution.md`

> **原则**：没有 constitution.md 的项目，不允许执行后续流程。constitution.md **必须**使用 ease-spec 技能生成，模板位于 `references/ease-spec/memory/constitution.md`。

#### 1.2 创建必要目录

```bash
# 创建目录结构
mkdir -p docs/domains
mkdir -p .eases
mkdir -p memory
```

#### 1.2.1 创建团队协作专用目录（幂等，强制）

> 🎯 **目标**：首次生成 `docs/` 结构时，同步为**测试人员**（`docs/qa/`）和**运维人员**（`docs/ops/`）创建专用目录及 README 说明文件，使团队成员的知识沉淀从项目初始即有明确归属。

> ⚠️ **幂等原则**：这两个目录是**项目级共享目录**（整个项目仅一份，不随 domain 编号递增）。若目录或 README 已存在，**必须跳过、不覆盖**，以保护用户已有内容。

```bash
# docs/qa/ — 测试人员专用目录（存放测试人员关心的案例信息）
if [ ! -f "docs/qa/README.md" ]; then
    mkdir -p docs/qa
    cat > docs/qa/README.md <<'EOF'
# QA / 测试人员专用目录

> 本目录用于存放**测试人员关心的案例信息**，是测试团队的知识沉淀区。

## 目录用途

存放与测试相关的案例、场景、数据和经验，帮助测试人员快速理解被测系统、复用历史测试资产、避免重复踩坑。

## 适合存放的内容

- **测试案例集**：业务功能测试、接口测试的具体案例（Given-When-Then）
- **回归测试清单**：核心链路、高风险场景的回归用例
- **边界与异常场景**：容易遗漏的边界值、异常分支、并发场景记录
- **测试数据**：构造测试所需的典型数据、Mock 数据说明
- **缺陷复盘**：典型 bug 的复现步骤、根因、对应的测试用例补充
- **环境与依赖说明**：测试环境配置、外部依赖 Mock 策略

## 命名建议

- 按领域/模块组织：`[模块名]/[案例主题].md`，如 `user-auth/login-cases.md`
- 缺陷复盘：`defects/[编号]-[简述].md`

## 与其他目录的关系

- 上游输入：`.eases/[特性名]/flow-2-design/test-cases/test-case-document.md`（设计阶段产出的需求驱动测试案例）
- 上游输入：`.eases/[特性名]/flow-2-design/architecture/api-interface-report.md`（接口测试上下文）
- 关联：`docs/domains/[编号]-[模块]/usecases/`（用例与业务规则来源，便于追溯 UC-XXX / BR-XXX）

> 提示：设计阶段（/ease:flow-2-design）产出的测试案例文档是临时工件，沉淀到本目录后可作为长期可复用的测试资产。
EOF
    echo "✓ 已创建 docs/qa/（测试人员专用目录）"
else
    echo "↩ docs/qa/ 已存在，跳过"
fi

# docs/ops/ — 运维人员专用目录（存放生产事故与处理排查方式）
if [ ! -f "docs/ops/README.md" ]; then
    mkdir -p docs/ops
    cat > docs/ops/README.md <<'EOF'
# Ops / 运维人员专用目录

> 本目录用于存放**生产环境出现过的事故、处理与排查方式**，是运维团队的应急知识库与经验沉淀区。

## 目录用途

记录生产环境真实发生的故障、处理过程和排查手段，沉淀可复用的应急预案与运维经验，缩短未来同类问题的定位与恢复时间（MTTR）。

## 适合存放的内容

- **事故复盘（Postmortem）**：生产事故的时间线、影响范围、根因、处理过程、改进项
- **排查手册（Runbook）**：常见故障的排查步骤、定位命令、关键日志位置
- **应急预案**：高风险场景的预案、回滚步骤、降级方案
- **监控与告警说明**：关键监控指标、告警含义、阈值与处置建议
- **部署与发布记录**：发布操作要点、灰度/回滚流程、配置变更影响
- **运维经验**：踩坑记录、易混淆配置、性能调优经验

## 命名建议

- 事故复盘：`incidents/YYYY-MM-DD-[简述].md`，如 `incidents/2026-06-15-db-connection-pool-exhausted.md`
- 排查手册：`runbooks/[场景].md`，如 `runbooks/high-latency-troubleshooting.md`
- 应急预案：`playbooks/[场景].md`

## 事故复盘建议结构

每篇事故复盘建议包含以下要素，便于横向检索与复用：

- **现象**：用户/监控观察到的异常表现
- **影响范围**：受影响的服务、用户、时长
- **时间线**：从发现到恢复的关键节点
- **根因**：技术根因 + 触发条件
- **排查过程**：用了哪些命令/日志/工具定位
- **处理方式**：临时止血 + 根本解决
- **改进项**：预防同类问题的行动项（监控/告警/代码/流程）

## 与其他目录的关系

- 关联：`docs/system/01_SYSTEM_OVERVIEW.md`（系统架构、技术栈，理解故障影响面）
- 关联：`docs/system/05_CONFIG_MANAGEMENT.md`（配置项含义，排查配置类故障）
- 关联：`docs/adr/`（架构决策中的回滚策略，对应应急预案）
EOF
    echo "✓ 已创建 docs/ops/（运维人员专用目录）"
else
    echo "↩ docs/ops/ 已存在，跳过"
fi
```

### 步骤 2：扫描编号并创建目录

1. 读取业务需求文档
2. 生成功能标识：
   - 分析需求文档，提取领域模块名称（module_name）
   - 使用有意义的名词或名词短语，反映业务领域
   - 格式：kebab-case，如 `user-management`, `payment-processing`
3. **扫描现有编号**：
   - 扫描 `docs/domains/` 确定长期 `DOMAIN_ID`（增量需求复用已有值）
   - 独立扫描 `.eases/` 获取本次 `CHANGE_ID` 的下一个编号
4. 创建带编号的目录结构：
   ```bash
   # 获取下一个 domain 编号
   DOMAIN_NUM=$(get_next_domain_number)  # 仅全新领域，例如：001
   DOMAIN_NAME="user-management"
   DOMAIN_ID="${DOMAIN_NUM}-${DOMAIN_NAME}"
   CHANGE_NUM=$(get_next_change_number)  # 每次需求递增，例如：042
   CHANGE_NAME="user-registration"
   CHANGE_ID="${CHANGE_NUM}-${CHANGE_NAME}"
   FEATURE_NAME="$CHANGE_ID"            # 迁移期兼容别名

   # docs 目录结构（领域模块，带编号）
   mkdir -p "docs/domains/${DOMAIN_ID}"/{artifacts,usecases,diagrams}

   # .eases 目录结构（按单次变更和命令隔离）
   mkdir -p ".eases/${CHANGE_ID}/flow-1-analyze"/{outputs,checklists}
   ```

   随后创建 `.eases/${CHANGE_ID}/context.json`。如果是增量领域，将 `DOMAIN_ID` 替换为 `MATCHED_DOMAIN_PATH` 的目录名，但 `CHANGE_ID` 保持新生成值。

   使用 `ease-analysis/templates/flow-context-template.json` 生成后立即校验：

   ```bash
   python3 references/ease-analysis/scripts/validate_flow_context.py \
     --input ".eases/${CHANGE_ID}/context.json" --change "$CHANGE_ID" --domain "$DOMAIN_ID" --track brd
   ```

### 步骤 2.5：需求模式检测（增量变动追踪，强制）

> 🎯 **目标**：检测本次需求是"全新领域"还是"对已有 domain/UC 的增量改动"。这一步决定了后续步骤 6（增量变动分析）是否执行，以及 Phase 2/3 的设计、实现是否带变动标注。

**检测流程**：

```bash
# 步骤 2.5.1：解析需求中的核心领域概念（名词短语）
# 从 $ARGUMENTS 中提取关键领域名词，如 "用户"、"登录"、"订单"、"支付"

# 步骤 2.5.2：扫描已有 domain 目录
if [ -d "docs/domains" ]; then
    for domain_dir in docs/domains/[0-9][0-9][0-9]-*; do
        [ -d "$domain_dir" ] || continue
        # 对比需求关键词与已有 domain 的 module_name
        # 读取该 domain 的 domain-overview.md、domain-alignment.json 与 UC/BR（如存在）
        # 匹配阈值：领域核心名词命中 ≥ 1 个 → 标记为潜在增量
    done
fi

# 步骤 2.5.3：设置需求模式变量
REQUIREMENT_MODE="new-domain"          # 默认：全新领域
MATCHED_DOMAIN_PATH=""                 # 匹配的已有 domain 路径
MATCHED_DOMAIN_NUM=""                  # 匹配的已有 domain 编号

# 如检测到匹配：
#   REQUIREMENT_MODE="incremental-domain"
#   MATCHED_DOMAIN_PATH="docs/domains/001-user-management"
#   MATCHED_DOMAIN_NUM="001"
```

**匹配判定规则**（语义匹配，非严格字符串匹配）：

| 判定维度 | 匹配条件 | 示例 |
|----------|---------|------|
| 领域名词命中 | 需求核心名词与已有 domain module_name 语义一致 | 需求含"用户登录" + 已有 `001-user-management` |
| UC 目标命中 | 需求涉及的操作目标已在已有 UC 文档中出现 | 需求含"登录校验" + 已有 `UC-001 用户登录` |
| 反向排除 | 新需求是独立业务领域，与已有 domain 无概念重叠 | 需求"支付处理" + 仅已有 `001-user-management` |

> ⚠️ **重要**：当 `REQUIREMENT_MODE=incremental-domain` 时，本次需求**不新建 domain 目录编号**，而是复用 `MATCHED_DOMAIN_PATH`；仅在已有 domain 下新增/修改 subdomain。详见步骤 4（业务用例提取）和步骤 6（增量变动分析）。

**输出变量**（供后续步骤使用）：
- `REQUIREMENT_MODE`: `"new-domain"` | `"incremental-domain"`
- `MATCHED_DOMAIN_PATH`: 空字符串 或 `"docs/domains/NNN-module_name"`
- `MATCHED_DOMAIN_NUM`: 空字符串 或 `"NNN"`

> **向用户确认**（推荐）：当检测结果介于"匹配/不匹配"边界时（如领域名词部分命中），向用户确认是按全新领域处理还是并入已有 domain，避免误判。

### 步骤 2.8：需求拷问（Grill-the-Requirement，强制先行）

> 🎯 **目标**：在动手做领域建模之前，像资深需求分析师一样**沿着需求决策树逐分支拷问用户，直到对业务意图达成共识**。这是 BRD 路径最关键的"需求发现"窗口——此处多问一个高价值问题，可避免 Phase 2/3 的 10x 返工。
>
> 📌 **本环节是 `ease-spec/reference/requirements-clarification.md` 澄清协议的"前移版"**：那套协议在 specify 之后扫描 spec 缺口；本环节在建模之前先把用户脑中的隐性需求挖出来。两者规则一致（≤5 问、逐个问、必带推荐、能查就别问），但聚焦点是**业务意图**而非 spec 文本。

#### 2.8.1 四条铁律（借鉴 grill-me）

1. **决策树式逐分支推进**：不要平铺式抛一堆问题。先解决**前置决策**（如"核心用户是谁"），再问**依赖它的决策**（如"该用户的权限边界"）。一个分支收敛后再进入下一分支。
2. **每个问题必须自带推荐答案**：基于业务常识、同类系统的常见模式、constitution 约束，给出**你推荐的答案 + 1 句理由**。用户回 `yes`/`推荐` 即采纳，把"问答"压缩成"确认"。
3. **能从已有信息推断就别问**：可由 `$ARGUMENTS`、`memory/constitution.md`、已有 `docs/domains/`、`README` 等推断的，**先推断并标注假设**，不要消耗用户耐心去问。
4. **持续拷问直到共识**：当**关键业务歧义已清零**或用户发出 `done`/`够了`/`继续` 时停止；最多 5 个问题（同一问题的消歧重试不计数）。

#### 2.8.2 决策树分支（按优先级推进，高影响优先）

> 按以下顺序遍历，**每个分支至多一个高价值问题**；某分支已能从已有信息确定时，直接标注假设跳过。

```
① 核心用户目标与成功标准  →  这个需求最终要让谁、完成什么、如何算成功？
       │（收敛后）
② 用户角色与权限边界      →  涉及哪些角色？各自能做什么、不能做什么？
       │
③ 关键业务规则与约束      →  有哪些必须遵守的业务规则？（条件→动作）
       │
④ 边界与异常场景          →  失败/为空/并发/越权时，期望的行为是什么？
       │
⑤ 范围边界（In/Out）      →  哪些明确不做？与已有 domain 的边界在哪？
       │
⑥ 可量化的完成定义        →  把"快""稳""好用"翻译成可验证的指标
```

> ⚠️ **分支依赖**：上层分支的答案会影响下层分支的提问。例如 ① 确定"核心用户是运营人员"后，② 的角色提问就应聚焦运营侧；不要在 ① 未定时空问 ②。

#### 2.8.3 标准提问格式（每次只问一个）

```markdown
---
### 🔍 需求拷问 [当前分支]：[一句话问题]

**为什么问这个**：[1 句说明该决策如何影响领域模型/用例/规则]

**🎯 我的推荐：[推荐答案]**
> 理由：[基于业务常识/同类系统模式/constitution 的 1-2 句理由]

**可选方向**（如适用）：

| 选项 | 方向 | 适用场景 |
|:----:|------|----------|
| **A** | [方向A] | [场景] |
| **B** | [方向B] | [场景] |

💡 回复方式：
- 回 `yes` / `推荐` 采纳推荐答案
- 回选项字母（如 `A`）选择方向
- 直接给出你的答案（≤15 字）
- 回 `done` 结束拷问，进入领域建模
---
```

#### 2.8.4 收敛与回写

- 每收到一个答案，**立即在工作内存登记**：`Q: <问题> → A: <最终答案>`，并据此调整后续分支的提问焦点。
- 拷问结束后，将所有结论**作为领域建模（步骤 3）和用例提取（步骤 4）的直接输入**；并在步骤 6.1 specify 阶段把这些答案写入 spec 的 `## Clarifications` 章节（沿用 requirements-clarification 的回写规范，避免重复提问）。
- 若开局即无关键歧义（需求已足够清晰），输出一行：`✅ 需求已清晰，无需拷问，直接进入领域建模。` 并继续。

> 📌 **与 Stop-the-Line 的关系**：拷问中若发现**需求内部矛盾**（两条规则互斥、角色权限冲突），不要试图自行调和——立即转入本命令的 Stop-the-Line 规则，向用户挑明矛盾并等待裁决。

### 步骤 3：领域模型分析

按照 ease-analysis 技能执行：

1. **Language & Global Understanding**
   - 提取业务术语
   - 识别核心域、支撑域、通用域

2. **Strategic Design**
   - 定义限界上下文
   - 创建上下文映射

3. **Tactical Design**
   - 识别聚合根与实体
   - 建模值对象
   - 定义领域事件

### 步骤 4：业务用例提取（带编号拆解到 usecases 目录）

> ⚠️ **重要**：usecases 必须从 ease-analysis 技能的 `flows/extract-usecases.md` 流程产出，**所有子领域目录必须带三位编号**。

1. 执行 ease-analysis 的用例提取流程
2. **扫描 usecases/ 获取下一个 subdomain 编号**
3. 按子领域（subdomain）创建带编号的目录
4. **为每个子领域创建两个固定文件**：
   - `usecase.md` - 业务用例文档（包含用例描述、参与者、流程步骤等）
   - `rules.md` - 用例规则文档（包含业务规则、约束条件、成功标准等）
5. 将用例内容写入 `usecase.md`
6. 将业务规则、约束、成功标准等写入 `rules.md`

#### usecases 目录结构示例

```
docs/domains/001-user-management/usecases/
├── 001-authentication/                    # 子领域1：认证（编号 001）
│   ├── usecase.md                          # 用例文档：认证相关用例（登录、登出、刷新令牌等）
│   └── rules.md                            # 用例规则：认证业务规则、约束、成功标准
├── 002-registration/                      # 子领域2：注册（编号 002）
│   ├── usecase.md                          # 用例文档：注册相关用例（邮箱注册、验证、完善资料等）
│   └── rules.md                            # 用例规则：注册业务规则、约束、成功标准
└── 003-password-management/               # 子领域3：密码管理（编号 003）
    ├── usecase.md                          # 用例文档：密码管理相关用例（重置密码、修改密码等）
    └── rules.md                            # 用例规则：密码管理业务规则、约束、成功标准
```

### 步骤 5：生成标准化输出

生成以下文档：

#### 5.1 分析过程报告 (`outputs/analysis-report.md`)

输出格式见模板：`references/ease-analysis/templates/analyze-brd-output-template.md`（生成前 Read 该文件获取完整骨架）

**输出路径**：`.eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md`。这是单次 Flow 过程文件，不写入 `docs/`。确认后的领域摘要另行提炼或更新为 `docs/domains/${DOMAIN_ID}/domain-overview.md`。

#### 5.2 工件文件 (artifacts/)

- `data-model.md` - 领域概念模型描述（实体、值对象及业务关系；**不是数据库 Schema**，禁止表/字段类型、DDL、索引等存储设计）
- `stakeholders.md` - 利益相关者分析

> **注**：API 设计规范与数据库 Schema 不在 Phase 1 产出（属 Phase 1 边界禁止产物），由 `/ease:flow-2-design` 的 arch-design.md / detail-design.md / api-interface-report.md 承接。

**格式要求：** 所有工件文件必须使用Markdown格式，禁止使用JSON、YAML、SQL等其他文件格式。

### 步骤 5.5：增量变动分析（仅 `REQUIREMENT_MODE=incremental-domain` 时执行）

> 🎯 **目标**：将本次新提取的 UC/BR 与 `MATCHED_DOMAIN_PATH` 下已有的 UC/BR 逐项对比，标注变动类型（`[Δ-NEW]` / `[Δ-MOD]` / `[Δ-UNCHANGED]`），生成 `delta-analysis.md` 供 Phase 2/3 消费。
>
> ⚠️ **全新领域模式跳过**：当 `REQUIREMENT_MODE=new-domain` 时，跳过本步骤，直接进入步骤 6。

#### 5.5.1 变动标记体系（贯穿三阶段）

| 标记 | 含义 | 适用层级 |
|------|------|---------|
| `[Δ-NEW]` | 本次需求新增的元素 | domain / UC / BR / 接口 / 方法 / 步骤 |
| `[Δ-MOD]` | 本次需求修改的已有元素 | 同上 |
| `[Δ-UNCHANGED]` | 本次需求涉及但未变动的已有元素（上下文引用） | 同上 |

#### 5.5.2 对比分析流程

```bash
# 1. UC 级别对比
#    遍历新提取的每个 UC，在 MATCHED_DOMAIN_PATH/usecases/ 下查找语义匹配（用例名称 + 目标）
#    - 无匹配           → 标记 [Δ-NEW]
#    - 有匹配但步骤/规则有变化 → 标记 [Δ-MOD]，记录变动点摘要
#    - 完全一致          → 标记 [Δ-UNCHANGED]

# 2. BR 级别对比
#    遍历新提取的每条 BR，在 MATCHED_DOMAIN_PATH 下已有 rules.md 中查找规则匹配
#    - 无匹配    → 标记 [Δ-NEW]
#    - 规则变更  → 标记 [Δ-MOD]，记录变更前后
#    - 未变      → 标记 [Δ-UNCHANGED]

# 3. Subdomain 级别对比
#    检查新需求的 subdomain 是否已有对应目录
#    - 已有目录 → 在现有 usecase.md/rules.md 中追加变更标注（不覆盖原文）
#    - 无目录   → 创建新编号目录，全部内容标记为 [Δ-NEW]
```

#### 5.5.3 在已有 usecase.md / rules.md 中追加变更标注

> ⚠️ **核心原则**：增量模式下**绝不覆盖已有内容**，仅追加变更标注。保护已有文档的历史完整性。

**usecase.md 变更标注格式**（HTML 注释，不影响渲染但可被工具检索）：

```markdown
<!-- [Δ-MOD] 需求#NNN: [变更说明] | 变动来源: UC-XXX [Δ-MOD], BR-XXX [Δ-NEW] | 日期: [DATE] -->

### [Δ-MOD] 主成功场景变更（需求#NNN）
**变更前**：[原有步骤描述]
**变更后**：[新步骤描述]
**变更原因**：[基于本次需求 UC-XXX / BR-XXX]
```

**rules.md 变更记录**（在已有的 "Rule Change History" 章节追加条目）：

```markdown
| 版本 | 日期 | 规则 ID | 变动类型 | 变动说明 | 变动来源 |
|------|------|---------|---------|---------|---------|
| v1.1 | [DATE] | BR-001-xxx | [Δ-MOD] | 新增密码过期校验条件 | 需求#NNN / UC-102 |
| v1.1 | [DATE] | BR-101-password-expiry | [Δ-NEW] | 新增密码过期策略规则 | 需求#NNN / UC-101 |
```

#### 5.5.4 生成 delta-analysis.md

**输出路径**：`.eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md`

输出格式见模板：`references/ease-analysis/templates/delta-analysis-template.md`（生成前 Read 该文件获取完整骨架）

> **原则**：`delta-analysis.md` 是 Phase 2/3 的核心输入。Phase 2 据此在设计文档中标注变动，Phase 3 据此确定实现优先级和回归测试范围。

### 步骤 5.6：建立领域对齐基线（全新/增量均强制）

> `delta-analysis.md` 只描述单次增量，不能替代长期领域基线。按照 `ease-analysis/references/domain-alignment-contract.md`，为当前领域创建或更新 `docs/domains/${DOMAIN_ID}/domain-alignment.json`。

1. 读取 `usecases/**/usecase.md`、`rules.md` 与需求来源，按模板 `ease-analysis/templates/domain-alignment-template.json` 登记全部活动 UC/BR。
2. 全新领域的本次元素标记为 `NEW`；增量领域与 `delta-analysis.md` 的 `NEW`/`MOD`/`UNCHANGED` 一一对应。
3. 既有元素被删除、拆分或替换时保留 ID，标记为 `deprecated` 或 `superseded`，禁止静默删除。
4. `baseline.status` 在本阶段设为 `analyzed`；工作区尚无可引用提交时，`commit_id` 使用 `WORKTREE`。
5. 判断是否需要 DDR（Domain Decision Record）：领域边界、Actor/Goal/主流程、聚合不变量/生命周期、核心业务规则或统一语言正式含义发生变化时，设置 `decision_required=true` 并创建 `docs/domains/${DOMAIN_ID}/decisions/NNN-title.md`；普通措辞、示例和纯技术实现变化不创建 DDR。
6. DDR 使用 `ease-analysis/templates/domain-decision-record-template.md`，并更新 `decisions/README.md` 索引。DDR 记录“为什么改变业务事实”，不得替代当前 UC/BR 正文。
7. 执行确定性门禁：

```bash
python3 references/ease-analysis/scripts/validate_domain_alignment.py --manifest "docs/domains/${DOMAIN_ID}/domain-alignment.json" --phase flow-1
```

校验失败时必须停止，不得进入步骤 6 或 Flow 2。

### 步骤 6：执行完整 ease-spec 生命周期（不可协商）

> ⚠️ **强制要求**：必须完整执行以下三个阶段（specify → plan → tasks），不可跳过。Phase 1 不执行 implement 阶段（实际代码由 flow-3-implement 产出）。

> 📌 **阶段子目录约定（不可协商）**：执行本阶段所有 ease-spec 脚本前，**必须先导出** `EASE_FEATURE_DIR="${CHANGE_ID}/flow-1-analyze"`。脚本会据此把 spec/plan/tasks 写入本次变更目录（见 `ease-spec/reference/stage-contract.md` §2.1）。
>
> ```bash
> export EASE_FEATURE_DIR="${CHANGE_ID}/flow-1-analyze"
> # PowerShell: $env:EASE_FEATURE_DIR = "$CHANGE_ID/flow-1-analyze"
> ```

#### 6.1 specify 阶段 - 创建需求规范

- 入口文档：`reference/create-requirements-spec.md`
- 输入：
  - `.eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md`
  - `docs/domains/${DOMAIN_ID}/usecases/` 目录下的用例文档
- 输出：`.eases/${CHANGE_ID}/flow-1-analyze/spec.md`
- 执行：
  ```bash
  # Bash（EASE_FEATURE_DIR 已导出，脚本写入对应阶段子目录，不新建分支）
  references/ease-spec/scripts/bash/create-new-feature.sh --json --feature-dir "${CHANGE_ID}/flow-1-analyze" "{ARGS}"
  # PowerShell
  references/ease-spec/scripts/powershell/create-new-feature.ps1 -Json -FeatureDir "$CHANGE_ID/flow-1-analyze" "{ARGS}"
  ```

#### 6.2 plan 阶段 - 制定技术计划

- 入口文档：`reference/create-technical-plan.md`
- 输入：`.eases/${CHANGE_ID}/flow-1-analyze/spec.md`
- 输出：`.eases/${CHANGE_ID}/flow-1-analyze/plan.md`
- 执行：
  ```bash
  # Bash
  references/ease-spec/scripts/bash/setup-plan.sh --json
  # PowerShell
  references/ease-spec/scripts/powershell/setup-plan.ps1 -Json
  ```

#### 6.3 tasks 阶段 - 生成任务列表

- 入口文档：`reference/generate-tasks.md`
- 输入：`.eases/${CHANGE_ID}/flow-1-analyze/plan.md`
- 输出：`.eases/${CHANGE_ID}/flow-1-analyze/tasks.md`
- 执行：
  ```bash
  # 前置检查
  # Bash
  references/ease-spec/scripts/bash/check-prerequisites.sh --json
  # PowerShell
  references/ease-spec/scripts/powershell/check-prerequisites.ps1 -Json
  ```

### 步骤 7：完成与验证

1. 将任务清单全部标记为已完成
2. 向用户汇报分析结果与生成文档路径
3. **下一步交接（唯一推荐）**——向用户输出以下结构化交接，**不要把"直接编码"列为选项**：

   ```
   ✅ Flow 1 生产遍完成，已提交 READY_FOR_ADMISSION。下一步（唯一推荐）：
      /ease:flow-2-design docs/domains/${DOMAIN_ID}/usecases/ --change-id=${CHANGE_ID}
      （DOMAIN_ID 指长期领域；CHANGE_ID 指本次变更执行）

   ⚠️ 用例分析 ≠ 可编码。BRD 路径必须先经设计阶段产出组件边界与接口契约
      （见 ease-spec/reference/phase-gate-invariant.md §3）。
      · 三阶段内不得跳过设计；如改用其他方法，须退出当前 Flow 并记录
        FLOW_ABORTED/PROCESS_CHANGED，不能使用当前产物直连 Flow 3
   ```
4. 提供简要总结

## 输出位置

所有输出文件必须严格遵循以下目录结构：

```
docs/
├── qa/                                          # 测试人员专用目录（首次生成时幂等创建）
│   └── README.md                                # 说明：存放测试人员关心的案例信息
├── ops/                                         # 运维人员专用目录（首次生成时幂等创建）
│   └── README.md                                # 说明：存放生产事故与处理排查方式
└── domains/                                     # 领域模块根目录（不可协商）
    └── [编号]-[module_name]/                    # 领域模块目录（三位编号）
        │                                        # 例如：001-user-management
        ├── domain-overview.md                   # 经确认的当前领域概览（长期事实）
        ├── domain-alignment.json                # UC/BR 领域对齐持久化基线（机器校验）
        ├── decisions/                           # 领域决策历史（按需）
        │   ├── README.md                        # DDR 索引
        │   └── 001-[decision-title].md          # Domain Decision Record
        ├── artifacts/                           # 生成的工件
        │   ├── data-model.md                    # 数据模型描述
        │   └── stakeholders.md                  # 利益相关者分析
        └── usecases/                            # 用例文档（必须从ease-analysis拆解）
            ├── [编号]-[subdomain1]/             # 子领域1（三位编号）
            │   │                                # 例如：001-authentication
            │   ├── usecase.md                   # 用例文档（固定文件名）
            │   └── rules.md                     # 用例规则文档（固定文件名）
            └── [编号]-[subdomain2]/             # 子领域2
                │                                # 例如：002-registration
                ├── usecase.md                   # 用例文档（固定文件名）
                └── rules.md                     # 用例规则文档（固定文件名）

.eases/
└── ${CHANGE_ID}/                                # 单次变更，例如：042-user-registration
    ├── context.json                             # change_id → domain_id / track / requirement
    └── flow-1-analyze/                         # flow-1-analyze 命令的产出目录
        ├── outputs/
        │   └── analysis-report.md               # 本次分析过程报告
        ├── spec.md                              # 需求规范
        ├── plan.md                              # 技术计划
        ├── tasks.md                             # 任务列表
        ├── delta-analysis.md                    # 增量变动分析报告（仅 incremental-domain 时生成）
        └── checklists/                          # 质量检查清单
            ├── requirements.md                  # 需求完整性
            ├── design.md                        # 设计质量
            └── implementation.md                # 实现验证
```

**重要：** `docs/` 只保存当前、长期维护的领域事实；单次分析报告不得写入 `docs/`。面向人的领域文档必须使用 Markdown 格式；`domain-alignment.json` 是机器校验基线例外。

## 全局行为准则 (Global Operating Behaviors)

### Stop-the-Line 规则

当分析过程中遇到任何意外情况，**立即停止推进**：

```
1. STOP  — 停止生成更多分析内容
2. PRESERVE — 保留触发问题的输入/输出/错误信息
3. DIAGNOSE — 判断是输入需求矛盾、constitution.md 冲突、还是分析方向错误
4. CLARIFY — 向用户明确提出困惑并等待确认
5. RESUME — 仅在问题解决后继续
```

**Stop-the-Line 触发条件**（任一满足即触发）：
- 业务需求中存在内部矛盾（两条规则互斥）
- 用例之间存在不可调和的状态转换冲突
- constitution.md 的 MUST 原则与业务需求冲突
- 领域边界模糊导致无法合理划分限界上下文
- 利益相关者之间存在无法自行裁决的优先级冲突

**铁律**：不要在存在未解决的矛盾或冲突时继续生成分析产物。错误的前提产生的分析全部是沉没成本。

## 质量标准

- 领域模型必须覆盖所有核心业务概念
- 用例必须包含明确的参与者、目标和步骤
- 业务规则必须是可验证的
- 成功标准必须是可量化的
- 输出格式必须符合模板规范
- **所有目录和文件必须带三位编号**
- **必须完整执行 ease-spec 生命周期（specify → plan → tasks）**

## 示例

输入：
```bash
/ease:flow-1-analyze-brd 实现用户注册、登录、密码重置功能
```

输出：
- 目录：`docs/domains/001-user-management/`（领域模块：用户管理，编号 001）
- 当前领域概览：`domain-overview.md`（从本次分析确认的事实中更新）
- 工件目录：`artifacts/`（包含data-model.md、stakeholders.md等）
- 用例目录：`usecases/`（按子领域组织的具体用例文档，带编号）
  - `001-authentication/`（子领域：认证）
    - `usecase.md`（认证相关用例：登录、登出、刷新令牌等）
    - `rules.md`（认证业务规则、约束、成功标准）
  - `002-registration/`（子领域：注册）
    - `usecase.md`（注册相关用例：邮箱注册、验证、完善资料等）
    - `rules.md`（注册业务规则、约束、成功标准）
  - `003-password-management/`（子领域：密码管理）
    - `usecase.md`（密码管理相关用例：重置密码、修改密码等）
    - `rules.md`（密码管理业务规则、约束、成功标准）
- 本次过程产出：`.eases/042-user-registration/flow-1-analyze/`
  - `outputs/analysis-report.md`（本次分析报告）
  - `spec.md`（需求规范）
  - `plan.md`（技术计划）
  - `tasks.md`（任务列表）
  - `checklists/`（质量检查清单）

## 集成说明

本命令是 ease-plugin 与 ease-spec 集成的关键入口，它：

1. **环境初始化**：确保 constitution.md 和必要目录存在
2. **编号管理**：扫描现有目录获取最大编号，新增时自动 +1
3. **分层输出**：长期领域事实写入 `docs/domains/${DOMAIN_ID}/`，本次分析过程写入 `.eases/${CHANGE_ID}/`
4. **用例拆解**：从 ease-analysis 拆解用例到带编号的 `usecases/` 目录（每个子领域包含 usecase.md 和 rules.md）
5. **命令隔离**：ease-spec 产出放在 `.eases/${CHANGE_ID}/flow-1-analyze/`
6. **完整生命周期**：自动执行 specify → plan → tasks
7. **追踪链路**：维护从需求到实现的完整追踪
8. **流程流转（BRD 路径标准流程，不可跳过 design）**：`/ease:flow-1-analyze-brd` → `/ease:flow-2-design` → `/ease:flow-3-implement`。Flow 1 生产遍提交后**唯一推荐下一步**是 `/ease:flow-2-design`，由 Flow 2 消费者验收决定 Phase 1 准入；Phase 2 产物缺失时**拒绝直接编码**（见 `ease-spec/reference/phase-gate-invariant.md`）。TRD 路径（`/ease:flow-1-analyze-trd`）为例外，因设计内置于 Phase 1 而直连 `/ease:flow-3-implement`，不经 flow-2-design

## Phase 1 完成门控 (Phase Gate)

> ⚠️ **强制要求**：提交 Phase 1 候选证据前必须逐项完成以下内容；任一条件不满足即不得标记 `READY_FOR_ADMISSION`。是否准入由 Flow 2 消费者验收决定。
>
> **生产者权限边界**：本阶段无权授予自己 Phase 1 PASS。按 `ease-spec/gates/README.md` 与 `gates/brd-flow-1-to-flow-2.md` 完成生产遍后，将全部候选证据写入 `.eases/${CHANGE_ID}/flow-1-analyze/checklists/gate-submission.md`，状态只能是 `READY_FOR_ADMISSION`。真正的 Phase 1 准入由 Flow 2 在首次写设计前以独立只读验收决定，并记录到 `flow-2-design/checklists/admission-flow-1.md`。
>
> `gate-submission.md` 必须逐项引用 `F1-ENV-01`、`F1-DOM-01`、`F1-REQ-01`、`F1-TRC-01`、`F1-BASE-01`、适用时的 `F1-DELTA-01` 与 `F1-SEM-01`；不得用“全部检查完成”替代逐项证据。

```markdown
## Phase 1 验证门控

### 环境与宪章
- [ ] `memory/constitution.md` 存在且包含 MUST/SHOULD 原则
- [ ] `docs/domains/` 目录结构完整

### 领域分析完整性
- [ ] 核心域、支撑域、通用域均已识别并文档化
- [ ] 限界上下文（Bounded Context）已划分，上下文映射已创建
- [ ] 聚合根、实体、值对象已识别
- [ ] 统一语言（Ubiquitous Language）术语表已产出

### 用例与规则覆盖
- [ ] 所有业务用例已拆解到 `usecases/` 目录（每个子领域包含 usecase.md 和 rules.md）
- [ ] 每个用例有明确的参与者（Actor）、目标（Goal）和主成功路径（Happy Path）
- [ ] 每条业务规则是可验证的（条件-行动格式，禁止模糊描述）
- [ ] 成功标准是可量化的（禁止"系统响应快"等主观描述，必须如"API 响应时间 P95 < 200ms"）

### 可追溯性
- [ ] `.eases/${CHANGE_ID}/context.json` 已通过身份映射校验
- [ ] `.eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md` 索引了所有子领域和用例文档路径
- [ ] ease-spec 生命周期（specify → plan → tasks）已完整执行
- [ ] `.eases/${CHANGE_ID}/flow-1-analyze/` 下 spec.md / plan.md / tasks.md 均存在且非空

### 领域对齐基线（全新/增量均强制）
- [ ] `docs/domains/${DOMAIN_ID}/domain-alignment.json` 已生成并通过 Schema/确定性校验
- [ ] 活动 UC/BR 均有需求来源，ID 格式合规且全局唯一
- [ ] 本次 `NEW`/`MOD` UC/BR 100% 进入领域基线
- [ ] 删除、拆分或替换的元素保留原 ID，并标记 `deprecated`/`superseded`
- [ ] `decision_required=true` 的元素均有关联 DDR，DDR 章节完整且已加入 `decisions/README.md`

### 增量变动追踪（仅 `REQUIREMENT_MODE=incremental-domain`）
- [ ] `REQUIREMENT_MODE` 已明确判定为 `incremental-domain`，`MATCHED_DOMAIN_PATH` 已记录
- [ ] `delta-analysis.md` 已生成且包含 UC/BR/Subdomain 变动明细
- [ ] 每个 `[Δ-MOD]` 的 UC 已标注具体变动点（变更前/变更后/原因）
- [ ] 每个 `[Δ-MOD]` 的 BR 已在对应 `rules.md` 的 Rule Change History 中追加记录
- [ ] 已有 `usecase.md` / `rules.md` 采用追加标注方式，**未覆盖原文**
- [ ] 变动标注使用标准格式：`<!-- [Δ-XXX] 需求#NNN: 说明 -->` / `[Δ-XXX]` 前缀

### 阻断条件
如果任一门控未通过，必须：
1. 列出未通过的门控项
2. 说明缺失的具体内容
3. 回到对应步骤补充
4. 重新验证所有门控

**未通过全部 Phase 1 门控前，严禁进入 `/ease:flow-2-design`。**
```

## 反理性化表 (Common Rationalizations)

在分析过程中，Agent 容易陷入以下"自我合理化"陷阱。识别并拒绝这些借口：

| 合理化借口 | 现实 |
|---|---|
| "需求已经很清楚了，不需要这么深入分析" | 跳过的边界条件会在 Phase 2/3 暴露，返工成本 10x。DDD 分析的每个环节都有其价值：领域模型防止边界模糊，用例分析防止遗漏场景，规则提炼防止业务逻辑矛盾。 |
| "这只是个小需求，跳过领域模型直接设计吧" | 小需求之间的领域概念如果不统一，会形成"术语债务"。后续需求会因概念模糊而增加沟通成本。 |
| "业务方没有明确说，我先假设一下" | 假设是需求分析最大的敌人。未验证的假设会在 Phase 3 变为返工。标注为显式假设并寻求确认，比私自填充模糊地带安全得多。 |
| "时间不够，先做核心域，支撑域和通用域后面再补" | 领域分类不仅是文档，更影响架构决策（如：通用域可采购/复用，支撑域可外包）。错误的领域分类导致技术选型偏差。 |
| "用例文档太长，写简略一点也没关系" | 用例的参与者和步骤在 Phase 2 中会直接映射为接口契约和关键流程伪代码。模糊的用例 → 模糊的接口 → 错误的实现。 |
| "这个术语大家都知道，不需要写进术语表" | "大家都知道"是技术债务的温床。新人、Agent 不知道。统一语言（Ubiquitous Language）要求所有术语显式定义。 |

## 注意事项

- **首次使用必须使用 ease-spec 技能创建 constitution.md**（不可协商）
  - 模板位置：`references/ease-spec/memory/constitution.md`
  - 流程指引：`references/ease-spec/reference/project-constitution.md`
- **所有目录和文件必须带三位编号**（不可协商）
- **新增时必须扫描现有最大编号 +1**（不可协商）
- 确保分析深度足够，避免在后续阶段出现重大遗漏
- 使用统一语言，保持术语一致性
- 关注业务价值，避免过早引入技术细节
- **usecases 必须从 ease-analysis 拆解**（不可协商）
- **建模前必须先执行需求拷问（步骤 2.8）**（不可协商）：沿决策树逐分支拷问用户至业务意图共识，每个问题必带推荐答案（用户回 `yes` 即采纳），能从已有信息推断的标注假设不问，最多 5 个问题；结论作为领域建模/用例提取的直接输入，并在 specify 阶段回写 spec 的 `## Clarifications`
- **必须完整执行 ease-spec 生命周期（specify → plan → tasks）**（不可协商）
- **增量需求必须检测需求模式并生成 delta-analysis.md**（不可协商）：
  - 通过步骤 2.5 检测 `REQUIREMENT_MODE`（new-domain / incremental-domain）
  - 当 `incremental-domain` 时，必须在步骤 5.5 生成 `delta-analysis.md`
  - 在已有 `usecase.md` / `rules.md` 中追加变更标注，**绝不覆盖原文**
  - 变动标记（`[Δ-NEW]` / `[Δ-MOD]` / `[Δ-UNCHANGED]`）将贯穿 Phase 2 设计和 Phase 3 实现
- **BRD 路径缺设计不编码**（不可协商）：Phase 1 完成后，Phase 2 产物（`arch-design.md` / `detail-design.md` / 框架代码或代码注释）缺失时，对任何编码请求（含 ease-coding、对话内裸编码、`/ease:flow-3-implement`）必须阻断并重定向 `/ease:flow-2-design`。如用户不采用三阶段方法，只能退出并记录 `FLOW_ABORTED`/`PROCESS_CHANGED` 后切换流程，不能在当前 Flow 内豁免
