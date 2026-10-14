<!-- Converted from ease command: starter. Read ../runtime.md first. -->

参数提示：`<requirement_doc_or_text> [--async] [--resume] [--path=brd|trd] [--from-phase=1|2|3] [--worktree=auto|required|reuse|off]`

领域参考（按需读取）：`references/ease-spec/SKILL.md`、`references/ease-system-bootstrap/SKILL.md`、`references/ease-analysis/SKILL.md`、`references/ease-architecture/SKILL.md`、`references/ease-architecture-design/SKILL.md`、`references/ease-framework-code/SKILL.md`、`references/ease-coding/SKILL.md`、`references/ease-code-implement/SKILL.md`、`references/ease-testing/SKILL.md`、`references/ease-test-case-design/SKILL.md`、`references/test-driven-development/SKILL.md`

## 纲要0: 异步检测逻辑

> ⚠️ **重要**：如果用户输入包含 `--async` 标记，则把**整个三阶段流程**提交到云端异步执行，否则在本会话内顺序执行。

### 触发条件

用户输入参数 `$ARGUMENTS` 中包含 `--async` 字符串

### 处理流程

1. 解析原始命令参数，去除 `--async` 标记
2. 净化参数后，提示用户任务将被提交到云端异步执行
3. 调用 `ease:async-task` 技能
4. 返回任务提交结果

### 具体实现

```bash
# 检测用户输入是否包含 --async 标记
if echo "$ARGUMENTS" | grep -q "\-\-async"; then
    echo "检测到 --async 标记，整个三阶段流程将提交到云端异步执行..."

    # 净化参数，去除 --async 标记
    CLEAN_ARGS=$(echo "$ARGUMENTS" | sed 's/--async//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # 构建异步任务描述：把整个 starter 交给 async-task
    TASK_DESC="/ease:starter $CLEAN_ARGS"

    # 调用 async-task skill 提交到云端
    /ease:async-task $TASK_DESC

    # 异步提交完成后直接返回，不执行后续流程
    return
fi
```

---

## 命令参数

```text
<requirement_doc_or_text> [--async] [--resume] [--path=brd|trd] [--from-phase=1|2|3] [--worktree=auto|required|reuse|off]
```

- **`<requirement_doc_or_text>`**：业务需求文档（BRD）或技术需求文档（TRD）的路径，或一段自由文本需求描述。
- **`--async`**：将完整三阶段流程作为单一任务提交到云端异步执行（见纲要0）。
- **`--resume`**：断点续跑；已通过门控的阶段自动跳过（见"断点续跑规则"）。
- **`--path=brd|trd`**：强制路径；未指定时由 Phase 0 自动检测。
- **`--from-phase=1|2|3`**：强制起始阶段；优先级高于 `--resume` 的自动检测。
- **`--worktree=auto|required|reuse|off`**：锁定整个流程的 worktree 策略；默认 `auto`，含义见 `ease-spec/reference/worktree-contract.md`。只有显式 `off` 才允许不隔离。

> 💡 `--async` 与 `--resume` 互斥：`--async` 把整体交给云端，不再走本地续跑逻辑。

---

## 角色与定位

你是一位**三阶段流程编排总指挥（Flow Orchestrator）**，职责是把一份需求文档**一次性、完整地**推进到可运行代码。你的核心能力包括：需求路径识别（BRD/TRD）、`DOMAIN_ID + CHANGE_ID` 的身份管理、三阶段有序编排、阶段门控、断点续跑与异常分流。

> ⚠️ **编排器不替代三阶段的专家角色**。它负责让三阶段复用同一组 `DOMAIN_ID + CHANGE_ID + TRACK`；迁移期 `FEATURE_NAME=CHANGE_ID`，但不得拿它定位 `docs/domains/`。

本命令是 `/ease:flow-1-*` → `/ease:flow-2-design` → `/ease:flow-3-implement` 的**一键封装**，三阶段命令仍是唯一事实来源，本命令保持轻量编排、不复制其逻辑。

---

## 全局行为准则 (Global Operating Behaviors)

### 1. 双身份单一来源原则（不可协商）

`DOMAIN_ID` 定位长期领域事实；`CHANGE_ID` 定位单次 Flow 过程；`TRACK=brd|trd` 表示流程路径。三阶段必须复用**同一组 `TRACK + DOMAIN_ID + CHANGE_ID`**（权威：`ease-spec/reference/stage-contract.md §2.1`）。

- Phase 1 为 BRD 解析/创建 `DOMAIN_ID`，并为每次执行新建 `CHANGE_ID`；TRD 只需 `CHANGE_ID`。
- Phase 1 将映射写入 `context.json`。编排器随后锁定三个变量并显式传递，禁止下游重新编号或用领域名猜测变更目录。
- `FEATURE_NAME` 是兼容别名，值等于 `CHANGE_ID`。

### 2. 阶段门控阻塞性（不可协商）

- 每个生产阶段结束后必须提交全部候选证据；下游消费者完成独立只读准入、全部 Gate PASS 后方可继续。
- 本编排器在阶段之间设置**显式 Checkpoint**：门控未通过即 **STOP**，不得进入下一阶段。
- 门禁遵循 `ease-spec/gates/README.md`：生产者只能提交 `READY_FOR_ADMISSION`，下游消费者以独立只读验收授予准入；本编排器不得代替消费者自证 PASS。
- BRD 路径**缺设计不编码**：Phase 2 产出缺失时拒绝任何形式的编码（权威：`ease-spec/reference/phase-gate-invariant.md §3`）。
- TRD 路径**不经** flow-2（设计内置于 Phase 1，是"设计已内置"而非"跳过设计"，见同文档 §2）。

### 3. Stop-the-Line 规则

任一阶段触发异常（门控失败、契约冲突、产物缺失）时执行：

```
1. STOP       — 立即停止当前阶段推进
2. PRESERVE   — 保留失败证据（门控清单、报错、缺失文件路径）
3. DIAGNOSE   — 判定是回退上一阶段、补充产物，还是请求用户澄清
4. ESCALATE   — 若需用户决策，明确给出阻塞点与可选动作
5. RESUME     — 仅在根因确认并修复后继续
```

### 4. 路径变量约定与跨平台

> 📌 `${DOMAIN_ID}` 指向 `docs/domains/`；`${CHANGE_ID}` 指向 `.eases/`；`${FEATURE_NAME}=${CHANGE_ID}` 仅为兼容。`${TRACK}` = `brd|trd`。
>
> 🖥️ **跨平台**：内联代码块为 Bash（macOS/Linux）。Windows 下：ease-spec 生命周期步骤使用配对的 `scripts/powershell/*.ps1`；内联命令等价映射：`mkdir -p X`→`New-Item -ItemType Directory -Force -Path X`、`[ -f X ]`/`[ -d X ]`→`Test-Path X`、`grep`→`Select-String`、`sed 's/a/b/'`→`-replace 'a','b'`、`find`→`Get-ChildItem -Recurse`、`ls -d GLOB`→`Get-ChildItem -Path GLOB -Directory`。Agent 按当前平台选择对应形式。

---

## 三阶段编排工作流程

**目标**：针对一份需求文档，按正确路径分支，完整执行 分析 → 设计（仅 BRD）→ 实现 三阶段，每阶段间以门控阻断，最终交付可运行代码与闭环报告。

### Phase 0: 初始化与路径解析（不可跳过）

**目标**：就绪基础环境、识别需求路径（BRD/TRD）、判定起始阶段。

0. **绿地系统预检（不改变 BRD/TRD 路径）**：
   ```bash
   BASELINE_JSON=$(references/ease-system-bootstrap/scripts/resolve-architecture-baseline.sh --root .)
   BASELINE_ACTION=$(printf '%s' "$BASELINE_JSON" | sed -n 's/.*"action":"\([^"]*\)".*/\1/p')
   if [ "$BASELINE_ACTION" = "bootstrap_required" ]; then
       echo "❌ 当前是零实现仓库，尚无已批准目标架构。"
       echo "请先执行 /ease:constitution，再执行 /ease:bootstrap-system <系统说明>。"
       exit 1
   fi
   ```

   `starter` 不自动执行 Bootstrap：系统立项会决定公共契约、数据所有权、信任与部署边界，必须由用户显式启动并通过 Bootstrap 门禁。`target_only`、`observed_only`、`hybrid` 和 `observed_missing` 均继续现有 BRD/TRD 判定；后续 Flow 2 负责选择 target/observed 基线，TRD 路径仍按原规则直连 Flow 3。

1. **检查 `constitution.md`（强制）**：
   ```bash
   if [ ! -f "memory/constitution.md" ]; then
       echo "❌ 错误：未找到 memory/constitution.md"
       echo "请先使用 /ease:constitution 或 ease-spec 技能创建项目宪章"
       exit 1
   fi
   ```

2. **创建必要目录**：
   ```bash
   mkdir -p docs/domains .eases memory
   ```

3. **解析 `$ARGUMENTS`**：拆出需求文档/文本与各标志位（`--async` 已在纲要0处理；解析 `--resume` / `--path` / `--from-phase` / `--worktree`），设置并锁定 `WORKTREE_POLICY=${WORKTREE_POLICY:-auto}`，后续阶段不得自行降级。

4. **路径检测（BRD vs TRD）**——权威：`phase-gate-invariant.md §2` 双路径表：
   - `--path=brd|trd` 显式指定时，以其为准，并设置 `TRACK=brd|trd`。
   - 否则按以下顺序自动判定为 **TRD**：输入路径位于 `docs/trd/`；或文档为 `TRD.md`；或需求内容明显属技术/NFR 类（中间件升级、架构优化、性能调优、高可用、安全加固、技术债清理等）。
   - 其余视为 **BRD**（业务需求）。判定完成后必须持久使用该 `TRACK`，下游不得通过全局目录扫描重新分类。
   - 判定有疑义时，向用户确认而非臆断。

5. **锁定统一 worktree 准入入口**：本阶段尚未生成 `CHANGE_ID`，不得提前猜测分支名。Flow 1 一旦确定 `CHANGE_ID`，必须在写入任何 `context.json`、领域/TRD 文档或 `.eases/` 产物前执行：
   ```bash
   references/ease-spec/scripts/bash/ensure-change-worktree.sh \
     --change-id "${CHANGE_ID}" --policy "${WORKTREE_POLICY}"
   # PowerShell
   $WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
   references/ease-spec/scripts/powershell/ensure-change-worktree.ps1 `
     -ChangeId "${CHANGE_ID}" -Policy $WorktreePolicy
   ```
   若返回 `created`、`attached*` 或 `existing-worktree`，将后续所有工具的工作目录切换到 JSON 的 `worktree_path`，再次执行并取得 `reused-current` 后才继续。完整状态机见 `ease-spec/reference/worktree-contract.md`。

6. **起始阶段判定**（断点续跑）：
   - `--from-phase=N` 优先；否则扫描已存在的阶段产物与门控状态（见"断点续跑规则"），从首个未完成阶段进入。
   - 全新需求从 Phase 1 开始。

7. **建立阶段级任务清单**：
   ```text
   TodoWrite:
   - Phase 1: 需求分析（flow-1）
   - Checkpoint 1: Phase 1 门控
   - Phase 2: 统一设计（flow-2，仅 BRD）
   - Checkpoint 2: Phase 2 门控
   - Phase 3: 代码实现（flow-3）
   - Checkpoint 3: Phase 3 门控
   - 收尾: 全流程闭环报告
   ```

### Phase 1: 需求分析（加载并执行 flow-1）

**目标**：产出领域模型 / 业务用例 / 业务规则并执行 BRD ease-spec 生命周期，或按风险产出 TRD 精简权威链 `TRD.md → solution-design.md → tasks.md`。

**执行方式（委托）**：

- **BRD 路径**：读取 `commands/flow-1-analyze-brd.md`，严格按其**全部步骤、运行约束与末尾 Phase 1 门控**执行。由其声明的**需求分析师（Requirements Analyst）**角色主导。输入为 `$ARGUMENTS` 中的需求。
- **TRD 路径**：读取 `commands/flow-1-analyze-trd.md`，严格按其全部步骤与门控执行。由其**技术架构师（Technical Architect）**角色主导。

> 🔑 **身份锁定**：flow-1 完成后，从 `.eases/${CHANGE_ID}/context.json`（BRD）或 `.eases/trd/${CHANGE_ID}/context.json`（TRD）锁定 `TRACK + DOMAIN_ID + CHANGE_ID`，后续一律显式传递。BRD 增量需求复用 `DOMAIN_ID`、新建 `CHANGE_ID`。

**Checkpoint 1（阻塞）**：

- Flow 1 只能生成 `checklists/gate-submission.md` 并标记 `READY_FOR_ADMISSION`，不能自授 PASS。
- BRD 继续进入 Flow 2，由 Flow 2 在首次写设计前只读审查全部 F1 Gate，并生成 `flow-2-design/checklists/admission-flow-1.md`；该文件全部 PASS 才视为 Checkpoint 1 通过。
- TRD 由 Flow 3 在首次实现前只读审查全部 T1 Gate，并生成 `flow-3-implement/checklists/admission-flow-1-trd.md`；`domain-impact=potential/confirmed` 必须转 BRD。
- 未通过则 **STOP**，不得进入 Phase 2；按 Stop-the-Line 处理。
- **路径分支**：BRD → 进入 Phase 2；TRD 必须先通过 **Domain Impact Guard**——`domain-impact=none` 时**跳过 Phase 2**并直接进入 Phase 3（设计已内置于 Phase 1），`potential/confirmed` 时停止并重定向 BRD Flow 1。该 Guard 只防止业务语义绕行，不改变纯技术 TRD 的方法论例外。

### Phase 2: 统一设计（仅 BRD 路径；加载并执行 flow-2）

**目标**：将用例与系统知识进行技术联合拆解，产出架构/详细设计、框架代码或代码注释，并执行 flow-2 的增强版 ease-spec 生命周期。

**跳过条件**：TRD 路径**不执行**本阶段。

**执行方式（委托）**：

- 读取 `commands/flow-2-design.md`，严格按其**全部步骤、运行约束与末尾 Phase 2 门控**执行。由其**首席架构师（Chief Architect）**角色主导。
- **入参**：`docs/domains/${DOMAIN_ID}/usecases/ --change-id=${CHANGE_ID}`。
- **`EASE_FEATURE_DIR`**：`${CHANGE_ID}/flow-2-design`。

> **旧项目续跑**：新任务只写入 `flow-2-design/`。若续跑时仅存在历史 `design/`，可将其作为旧输入读取并提示迁移；若 `flow-2-design/` 与 `design/` 同时存在，立即停止并要求用户确认权威目录，禁止自动覆盖或合并。

> ⚠️ BRD 路径**缺设计不编码**：若本阶段未产出合格设计，任何编码请求都必须阻断并回流 Flow 2。三阶段内没有 waiver；用户选择其他方法时记录 `FLOW_ABORTED`/`PROCESS_CHANGED` 并退出当前编排，不得直连 Phase 3。

**Checkpoint 2（阻塞）**：

- Flow 2 只能生成 `flow-2-design/checklists/gate-submission.md` 并标记 `READY_FOR_ADMISSION`。
- Flow 3 必须在写 RED 测试或实现前只读复验全部 F2 Gate，生成 `flow-3-implement/checklists/admission-flow-2.md`；反证检查与双向集合对账全部 PASS 才视为 Checkpoint 2 通过。
- 未通过则 **STOP**，不得进入 Phase 3。

### Phase 3: 代码实现（加载并执行 flow-3）

**目标**：以 TDD 完成代码实现，并消费前置权威链：BRD 为 `spec/plan/tasks`，TRD 为 `TRD.md/solution-design.md/tasks.md`，就地回写任务进度。

**执行方式（委托）**：

- 读取 `commands/flow-3-implement.md`，严格按其**全部步骤、运行约束与末尾 Phase 3 门控**执行。由其**高级开发工程师（Senior Software Engineer）**角色主导。
- **入参**：BRD → `TRACK=brd DOMAIN_ID=${DOMAIN_ID} CHANGE_ID=${CHANGE_ID} EASE_FEATURE_DIR=${CHANGE_ID}/flow-2-design`；TRD → `.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/`。

> ⛔ **关键契约（不可协商）**：flow-3 **仅执行 `implement`**。BRD 消费 Phase 2 的 `spec/plan/tasks`；TRD 消费 Phase 1 的 `TRD.md/solution-design.md/tasks.md`，无需 `spec.md/plan.md`。完成项就地标记为 `[X]`，不在 flow-3 复制前置产物。
>
> flow-3 的步骤 1.2.1 已内建 BRD/TRD **双分支**门控（`flow-3-implement.md` Branch B），本编排器按 Phase 0 判定的路径交由其处理即可。

**Checkpoint 3（阻塞）**：

- 实现遍只能生成 `flow-3-implement/checklists/delivery-submission.md`。随后必须冻结代码、测试与 tasks，以独立只读 delivery review 反证全部 F3 Gate并生成 `flow-3-implement/checklists/delivery-review.md`。
- delivery review 必须按路径验证原有全部质量要求：BRD/Strict 执行完整 TDD、行/分支/方法覆盖率、断言价值（每个测试最高有效断言等级 ≥ L2）、确定性隔离 D-Gate（D1–D9）、核心方法变异冒烟、范围纪律与架构一致性；Lite/Standard 只能按 `TRD_RISK_PROFILE` 的明确规则提供比例证据或有反证支撑的 N/A，并完成适用的兼容、灰度、观测和回滚验证。
- 只有 `delivery-review.md` 全部 PASS，且代码/测试/tasks 自审查后未再变化，才视为 Checkpoint 3 通过。
- 确认 **ADR/DDR Implementation Evidence**（若有关联决策）已回填、**架构文档漂移检查**（若 `docs/system/metadata.json` 存在）已执行。
- 未通过则 **STOP**，按 Stop-the-Line 处理（如 2-3 次修复仍失败，触发 `systematic-debugging` 技能）。

### 收尾: 全流程闭环报告

**目标**：交付三阶段产物总览与闭环确认。

输出示例：

```text
✅ /ease:starter 全流程完成（路径：BRD / TRD）
   领域目录：${DOMAIN_ID:-N/A}
   变更目录：${CHANGE_ID}

📦 Phase 1（分析）产物：
   - BRD 长期事实: docs/domains/${DOMAIN_ID}/{domain-overview.md,usecases/,domain-alignment.json}
   - BRD 过程报告: .eases/${CHANGE_ID}/flow-1-analyze/outputs/analysis-report.md
   - TRD: .eases/trd/${CHANGE_ID}/flow-1-analyze-trd/TRD.md

📦 Phase 2（设计，仅 BRD）产物：
   - .eases/${CHANGE_ID}/flow-2-design/architecture/{arch-design,api-interface-report}.md
   - .eases/${CHANGE_ID}/flow-2-design/detail/detail-design.md
   - .eases/${CHANGE_ID}/flow-2-design/{framework-code | code-annotations}/...

📦 Phase 3（实现）产物：
   - 实际代码 + 测试代码
   - BRD: .eases/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md
   - TRD: .eases/trd/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md
   - 权威 tasks.md 已就地回写 [X]

🔒 门控闭环：Flow 2 admission-flow-1 ✅ → Flow 3 admission-flow-2/admission-flow-1-trd ✅ → delivery-review ✅
```

三阶段流程的验证门控至此完整闭环：Phase 1 → Phase 2（仅 BRD）→ Phase 3。

---

## 断点续跑规则（幂等）

> 借鉴 `ease-spec/reference/one-click-execution.md` 的幂等重入思想。`--resume` 时按下表自动跳过已完成的阶段；`--from-phase=N` 强制起始阶段，优先级最高。

| 阶段 | 完成信号 | 默认行为 | `--resume` 行为 |
|------|----------|----------|----------------|
| Phase 1 | 生产产物存在，且 BRD 已有当前有效的 `admission-flow-1.md`；TRD 已有当前有效的 `admission-flow-1-trd.md` | 执行 | 只有消费者验收仍新鲜时跳过 |
| Phase 2（仅 BRD） | 设计产物存在，且 Flow 3 的 `admission-flow-2.md` 对当前版本全部 PASS | 执行 | 只有消费者验收仍新鲜时跳过 |
| Phase 3 | 权威 tasks 有证据地全部完成，且当前有效的 `delivery-review.md` 全部 PASS | 执行 | 未完成或证据失效时继续/重验 |

> ⚠️ 续跑须复用同一个 `CHANGE_ID`，并校验其 `context.json` 中的 `DOMAIN_ID/TRACK`。找不到或出现多个候选时停止并要求显式指定，不得新建目录冒充续跑。

---

## 反理性化表（Common Rationalizations）

| 合理化借口 | 现实 |
|---|---|
| "一键跑完，门控走个过场就行" | 门控是"一键可信赖"的前提。任一门控失败即阻断，否则等于绕过 `phase-gate-invariant.md`，返工成本约 10x。 |
| "三阶段一起跑，每阶段自己猜目录就行" | Phase 1 锁定 `DOMAIN_ID + CHANGE_ID + TRACK`，下游只能显式继承或读取同一 context.json。 |
| "TRD 也走 flow-2 更保险" | TRD 的方案设计**内置于 Phase 1**（`solution-design.md`），直连 flow-3 是设计使然，强行走 flow-2 反而破坏路径契约（`phase-gate-invariant.md §2`）。 |
| "一键流程里顺手把 flow-3 的 specify→plan→tasks 也跑了" | flow-3 **仅 implement**，重跑会破坏单一事实来源（`stage-contract.md §4 C-4`）。 |
| "Phase 2 出了点小问题，先往下跑到 Phase 3 再说" | 缺设计不编码。Checkpoint 未通过必须 STOP，带病推进只会放大返工。 |
| "用户催进度，跳过设计直接实现" | 越急越不能跳设计。不采用三阶段时明确退出并切换流程，不能降低当前 Flow 的通过标准。 |

---

## 下一步动作

全流程完成后，建议依次执行：

```bash
/ease-tools:git-commit        # 生成符合规范的提交信息
/ease-tools:code-review       # 代码质量审查
/ease-tools:git-branch-sync   # 同步分支到 develop / main(master)
```

如需查看本命令的契约依据：
- 路径 / 连接键 / 阈值：`ease-spec/reference/stage-contract.md`
- 路径规则（何时可编码 / 可否跳过设计）：`ease-spec/reference/phase-gate-invariant.md`
- 三阶段各自详细流程：`commands/flow-1-analyze-brd.md`、`commands/flow-1-analyze-trd.md`、`commands/flow-2-design.md`、`commands/flow-3-implement.md`

## E2E 状态沿用

各阶段按 `ease-spec/reference/e2e-integration.md` 判断接入状态；starter 仅沿用结果，不重复扫描、创建 TRD 或加载 E2E 技能。未接入提醒不作为阶段失败，不自动启动另一条 TRD 流程。
