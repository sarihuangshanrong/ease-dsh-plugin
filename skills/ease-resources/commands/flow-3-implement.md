<!-- Converted from ease command: flow-3-implement. Read ../runtime.md first. -->

参数提示：`"[file_or_module_path] [--worktree=auto|required|reuse|off]"`

领域参考（按需读取）：`references/ease-coding/SKILL.md`、`references/ease-code-implement/SKILL.md`、`references/ease-spec/SKILL.md`、`references/test-driven-development/SKILL.md`、`references/ease-testing/SKILL.md`、`references/ease-qa/SKILL.md`

## E2E 接入状态分流

遵循 `ease-spec/reference/e2e-integration.md`（相对 `references/`）：在既有 worktree/上游准入之后轻量检查项目及本次服务的 `e2e/`。存在即自动按变更范围复用；不存在则在项目 `docs/trd/` 创建或复用一份接入待办 TRD，继续原流程，不生成 E2E 代码或加载专属技能。按契约执行本阶段职责；只读验收期间不得写入提醒。


## 纲要0: 异步检测逻辑

> ⚠️ **重要**：如果用户输入包含 `--async` 标记，则触发异步执行流程，否则正常执行。

### 触发条件

用户输入参数 `$ARGUMENTS` 中包含 `--async` 字符串

### 处理流程

1. 解析原始命令参数，去除 `--async` 标记
2. 提醒开发者确认前置阶段 `.eases` 产物已 commit 并 push 到当前远程分支
3. 开发者未确认前暂停，不得提交异步任务
4. 净化参数后，提示用户任务将被提交到云端异步执行
5. 调用 `ease:async-task` 技能
6. 返回任务提交结果

### 提交前 `.eases` 产物提醒（强制）

`.eases/` 通常被 `.gitignore` 忽略，仅存在本地的设计产物对云端任务不可见。提交 Flow3 异步任务前，必须根据开发路径提醒开发者：BRD 提交 `.eases/${CHANGE_ID}/flow-2-design/`，TRD 提交 `.eases/trd/${CHANGE_ID}/flow-1-analyze-trd/`。

```markdown
⚠️ Flow3 云端任务需要读取本地前置阶段产物。

请确认当前路径对应的阶段目录已加入 Git、commit 并 push 到当前远程分支。
如果该目录被 ignore，请只选择实际路径执行其中一条：

# BRD
git add -f -- ".eases/${CHANGE_ID}/flow-2-design"

# TRD
git add -f -- ".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"

然后由你完成 commit 和 push。请不要将整个 `.eases/` 加入 Git。
```

- 未提交或未推送前置产物时，必须暂停，不得调用 `ease:async-task`
- 只提醒并等待开发者确认；不自动执行 `git add`、commit 或 push
- 如果无法唯一确定 BRD/TRD 路径或 `${CHANGE_ID}`，先请开发者提供阶段产物目录

### 具体实现

```bash
# 检测用户输入是否包含 --async 标记
if echo "$ARGUMENTS" | grep -q "\-\-async"; then
    echo "检测到 --async 标记，任务将提交到云端异步执行..."
    echo "⚠️ 请先确认 BRD flow-2-design/ 或 TRD flow-1-analyze-trd/ 产物已 commit 并 push 到当前远程分支"
    echo "如尚未提交或推送，暂停流程，不得提交异步任务"
    # ⏸️ 在此暂停并等待开发者明确确认；未确认不得继续

    # 净化参数，去除 --async 标记
    CLEAN_ARGS=$(echo "$ARGUMENTS" | sed 's/--async//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # 构建异步任务描述
    TASK_DESC="/ease:flow-3-implement $CLEAN_ARGS"

    # 调用 async-task skill 提交到云端
    /ease:async-task $TASK_DESC

    # 异步提交完成后直接返回，不执行后续流程
    return
fi
```

---

你是一位资深的**高级开发工程师（Senior Software Engineer）**，专注于将设计转化为高质量的生产代码。你的核心能力包括：基于框架代码和注释完成详细实现、SOLID 原则与 Clean Code 的严格践行、安全编码与性能优化、现代语言特性的恰当运用。你遵循简单方案优于复杂方案的原则，避免过度设计，将安全作为第一优先级，代码应自解释并在必要时添加设计决策注释，严格遵循项目已有的代码风格和架构模式。

**你严格践行 TDD（测试驱动开发）原则**：没有先失败的测试，就不要写生产代码。你在写任何实现代码之前，先写测试并亲眼看着它失败，确认失败原因是"功能缺失"而非语法错误，然后只写最少的代码让测试通过，最后重构并保持测试全绿。

**所有单元测试代码必须严格遵循 `ease-testing` 技能的规范（不可协商）**：测试的模板、MC/DC 覆盖原则、AAA 结构、FIRST 原则与 Mock 策略均以 `ease-testing` 为准，不得随意发挥。
- **TDD RED 阶段**（生产代码尚不存在时）：按 `ease-testing` 的模板与规范**编写**首个失败测试——此时无源码可供白盒逆向，遵循规范即可，不要求走 ease-testing 的"基线覆盖率→分析源码"白盒流程。
- **GREEN 之后的覆盖率补强阶段**（已有实现代码时）：调用 `ease-testing` 的分轮覆盖率提升流程（白盒）补全 MC/DC 缺口。
- 若 Phase 2 已产出 `test-case-document.md`，RED 阶段优先按其中的 `TC-XXX-NNN` 案例编写测试（见 `ease-testing/flows/generate-test-code.md` Step 0）。

按照 **ease-code-implement** 的原子实现契约执行，并保留 **ease-coding** 作为向后兼容入口，根据开发模式完成代码的详细实现：
- **BRD 全新开发**：基于 `/ease:flow-2-design` 产出的框架代码和注释信息
- **BRD 增量开发**：基于 `/ease:flow-2-design` 在现有代码中添加的 TODO 注释
- **TRD 开发**：基于 `/ease:flow-1-analyze-trd` 内置的 `TRD.md`、`solution-design.md` 与权威 `tasks.md`，不经 Flow 2
并执行 ease-spec 的 **implement 阶段**——BRD 消费权威 spec/plan/tasks，TRD 消费 `TRD.md → solution-design.md → tasks.md`，就地回写任务进度且不重新生成前置产物。

## 全局行为准则 (Global Operating Behaviors)

### Stop-the-Line 规则

这是三阶段流程的最后一道关，错误会直接变成生产代码。因此 Stop-the-Line 规则在 Phase 3 更加严格：

```
1. STOP  — 立即停止编写实现代码
2. PRESERVE — 保留失败的测试输出、编译错误、堆栈信息
3. DIAGNOSE — 判断是设计缺陷反馈（BRD 回到 Phase 2；TRD 回到 Phase 1）、测试策略错误、还是实现 bug
4. FIX or ESCALATE — 2-3 次修复仍失败 → 触发 systematic-debugging 技能
5. RESUME — 仅在根因确认并修复后继续
```

**Stop-the-Line 触发条件**（任一满足即触发）：
- 测试失败 3 次以上仍无法修复（**强制触发 systematic-debugging 技能**）
- 编译错误经过 2-3 次修复仍无法通过
- 实现过程中发现权威设计（BRD 的 arch/detail design；TRD 的 solution-design）存在漏洞或矛盾
- 增量开发中修改破坏了现有测试（回归失败）
- 发现需要修改的代码量远超任务预估（范围偏离信号）
- 发现安全性或数据完整性风险
- 测试因环境/依赖问题无法运行（不解决环境，盲目写代码是无效工作）

**铁律**：
- **不要越过失败的测试去写下一个功能**。错误会叠加，最终变成一个无法调试的大泥球。
- **不要在根本原因不明的情况下进行"碰运气"式的修复**。第 4 次盲目尝试是被禁止的——触发 systematic-debugging 技能。
- **不要发现设计问题却继续按错误设计实现**。BRD 反馈给 Phase 2，TRD 反馈给 Phase 1，修正后再实现。

## Usage

### 实现指定文件的代码

```bash
/ease:flow-3-implement [file_path]
```

### 实现整个模块的代码

```bash
/ease:flow-3-implement [module_path]
```

### 实现所有待完成的代码

```bash
/ease:flow-3-implement
```

> ⚠️ **重要**：本命令只执行 ease-spec 的 `implement` 阶段。BRD 消费 Phase 2 的 `spec.md / plan.md / tasks.md`；TRD 消费 Phase 1 的 `TRD.md / solution-design.md / tasks.md`，无需 `spec.md` / `plan.md`。两条路径都只就地回写任务进度，不重新生成前置产物。

> 📌 **路径变量约定**：`${CHANGE_ID}` 是本次变更执行标识，`${DOMAIN_ID}` 是 BRD 的长期领域标识，`${TRACK}=brd|trd` 决定根路径。历史文档中的 `FEATURE_NAME` 占位符是 `CHANGE_ID` 的迁移期别名，仅用于读取旧产物；BRD 必须从 `context.json` 恢复 `DOMAIN_ID`，不得假设二者相同。
>
> 🖥️ **跨平台**：内联代码块为 Bash（macOS/Linux）。Windows 下：ease-spec 生命周期步骤使用配对的 `scripts/powershell/*.ps1`；内联命令等价映射：`mkdir -p X`→`New-Item -ItemType Directory -Force -Path X`、`[ -f X ]`/`[ -d X ]`→`Test-Path X`、`grep`→`Select-String`、`sed 's/a/b/'`→`-replace 'a','b'`、`find`→`Get-ChildItem -Recurse`、`ls -d GLOB`→`Get-ChildItem -Path GLOB -Directory`。Agent 按当前平台选择对应形式。

## 实现步骤

你必须严格按照以下步骤执行任务：

### 步骤 1: 环境检查与初始化（不可跳过）

#### 1.1 检查 constitution.md（强制）

```bash
# 检查 memory/constitution.md 是否存在
if [ ! -f "memory/constitution.md" ]; then
    echo "❌ 错误：未找到 memory/constitution.md"
    echo "请先执行 reference/project-constitution.md 创建项目宪章"
    # 参考 reference/project-constitution.md 执行创建
    exit 1
fi
```

> **原则**：没有 constitution.md 的项目，不允许执行后续流程。

#### 1.2 创建必要目录

```bash
# 创建目录结构
mkdir -p docs/domains
mkdir -p .eases
mkdir -p memory
```

#### 1.2.0 统一 Change Worktree 准入（强制）

从显式参数或当前 BRD/TRD `context.json` 恢复并唯一锁定 `CHANGE_ID` 后、写 RED 测试或修改任何任务/代码前，执行：

```bash
references/ease-spec/scripts/bash/ensure-change-worktree.sh \
  --change-id "${CHANGE_ID}" --policy "${WORKTREE_POLICY:-auto}"
# PowerShell
$WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
references/ease-spec/scripts/powershell/ensure-change-worktree.ps1 `
  -ChangeId "${CHANGE_ID}" -Policy $WorktreePolicy
```

- `reused-current` 才代表准入通过。
- 返回 `created`、`attached*` 或 `existing-worktree` 时，把后续所有工具调用的工作目录切换到 JSON 的绝对 `worktree_path`，再次执行并要求 `reused-current`。
- 当前位于其他 `feature/*`、工作区脏、身份不唯一或其他错误时立即 Stop-the-Line。
- Flow 3 只复用 Flow 1 创建的 `feature/${CHANGE_ID}`；不得按阶段另建分支。只有用户显式选择 `off` 才能豁免，并须写入实现总结。完整契约见 `ease-spec/reference/worktree-contract.md`。

#### 1.2.1 Phase 1 & Phase 2 门控验证（强制）

> ⚠️ **前置条件**：进入 Phase 3 前，必须确认前置阶段门控已通过。**门控按来源路径分两条分支校验**（见 `ease-spec/reference/phase-gate-invariant.md` §2 双路径表 与 `stage-contract.md` §3）。
>
> **消费者准入所有权**：Flow 3 必须在编写 RED 测试、生产代码或修改权威 tasks 前冻结上游产物并执行独立只读第二遍。BRD 按 `ease-spec/gates/brd-flow-2-to-flow-3.md` 验收并写入 `${IMPLEMENTATION_ARTIFACT_DIR}/checklists/admission-flow-2.md`；TRD 按 `gates/trd-flow-1-to-flow-3.md` 验收并写入 `${IMPLEMENTATION_ARTIFACT_DIR}/checklists/admission-flow-1-trd.md`。上游的 `gate-submission.md` 只是候选证据，不是 PASS。

**首先判定来源路径**：

```bash
# FEATURE_NAME 始终是裸 [编号]-[模块名]，TRACK/EASE_FEATURE_DIR 决定当前来源路径。
# 禁止通过扫描其他 TRD 特性来推断当前特性类型。
FEATURE_NAME="${FEATURE_NAME#trd/}"
CHANGE_ID="$FEATURE_NAME"
DOMAIN_ID=""
TRD_SOURCE_DIR=".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"
BRD_SOURCE_DIR=".eases/${CHANGE_ID}/flow-2-design"
LEGACY_BRD_SOURCE_DIR=".eases/${CHANGE_ID}/design"
BRD_FEATURE_DIR="${CHANGE_ID}/flow-2-design"

# 新任务只写 flow-2-design/；旧 design/ 仅用于在途项目只读兼容。
# 两者同时存在会形成两份权威 tasks.md，必须阻断，禁止静默择一。
if [ -d "$BRD_SOURCE_DIR" ] && [ -d "$LEGACY_BRD_SOURCE_DIR" ] && \
   [ "${TRACK:-}" != "trd" ] && \
   [[ "${EASE_FEATURE_DIR:-}" != "trd/${CHANGE_ID}/flow-1-analyze-trd" ]] && \
   [[ "$ARGUMENTS" != *".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"* ]]; then
    echo "❌ 新旧 Flow 2 目录同时存在：${BRD_SOURCE_DIR} 与 ${LEGACY_BRD_SOURCE_DIR}"
    echo "请人工确认权威目录并合并或移走另一目录后重试，禁止自动覆盖"
    exit 1
elif [ ! -d "$BRD_SOURCE_DIR" ] && [ -d "$LEGACY_BRD_SOURCE_DIR" ] && \
     [ "${TRACK:-}" != "trd" ] && \
     [[ "${EASE_FEATURE_DIR:-}" != "trd/${CHANGE_ID}/flow-1-analyze-trd" ]] && \
     [[ "$ARGUMENTS" != *".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"* ]]; then
    BRD_SOURCE_DIR="$LEGACY_BRD_SOURCE_DIR"
    BRD_FEATURE_DIR="${CHANGE_ID}/design"
    echo "⚠️ 兼容读取旧目录 ${LEGACY_BRD_SOURCE_DIR}；新任务将统一使用 flow-2-design/"
fi

if [ "${TRACK:-}" = "trd" ] || \
   [[ "${EASE_FEATURE_DIR:-}" = "trd/${CHANGE_ID}/flow-1-analyze-trd" ]] || \
   [[ "$ARGUMENTS" = *".eases/trd/${CHANGE_ID}/flow-1-analyze-trd"* ]]; then
    SOURCE_PATH="trd"
elif [ "${TRACK:-}" = "brd" ] || \
     [[ "${EASE_FEATURE_DIR:-}" = "${CHANGE_ID}/flow-2-design" ]] || \
     [[ "${EASE_FEATURE_DIR:-}" = "${CHANGE_ID}/design" ]] || \
     [[ "$ARGUMENTS" = *".eases/${CHANGE_ID}/flow-2-design"* ]] || \
     [[ "$ARGUMENTS" = *".eases/${CHANGE_ID}/design"* ]]; then
    SOURCE_PATH="brd"
elif [ -s "${TRD_SOURCE_DIR}/TRD.md" ] && [ ! -s "${BRD_SOURCE_DIR}/tasks.md" ]; then
    SOURCE_PATH="trd"
elif [ -s "${BRD_SOURCE_DIR}/tasks.md" ] && [ ! -s "${TRD_SOURCE_DIR}/TRD.md" ]; then
    SOURCE_PATH="brd"
elif [ -s "${TRD_SOURCE_DIR}/TRD.md" ] && [ -s "${BRD_SOURCE_DIR}/tasks.md" ]; then
    echo "❌ 当前 FEATURE_NAME 同时存在 BRD 与 TRD 产物，无法安全推断来源"
    echo "请显式传入 TRACK=brd|trd 或对应的 EASE_FEATURE_DIR"
    exit 1
else
    echo "❌ 无法定位当前特性的权威任务目录"
    echo "请传入 BRD flow-2-design 目录或 TRD flow-1-analyze-trd 目录"
    exit 1
fi

if [ "$SOURCE_PATH" = "trd" ]; then
    TRACK="trd"
    export EASE_FEATURE_DIR="trd/${CHANGE_ID}/flow-1-analyze-trd"
    IMPLEMENTATION_ARTIFACT_DIR=".eases/trd/${CHANGE_ID}/flow-3-implement"
    CONTEXT_FILE=".eases/trd/${CHANGE_ID}/context.json"
    if [ -f "$CONTEXT_FILE" ]; then
        python3 references/ease-analysis/scripts/validate_flow_context.py \
          --input "$CONTEXT_FILE" --change "$CHANGE_ID" --track trd || exit 1
    else
        echo "⚠️ 未找到 TRD context.json，按旧项目只读兼容"
    fi
    TRD_RISK_PROFILE=$(sed -nE 's/^\*\*风险级别\*\*[：:][[:space:]]*(Lite|Standard|Strict).*/\1/p' \
      "${TRD_SOURCE_DIR}/TRD.md" | head -1)
    TRD_RISK_PROFILE="${TRD_RISK_PROFILE:-Standard}"  # 历史 TRD 默认 Standard
    case "$TRD_RISK_PROFILE" in
      Lite|Standard|Strict) ;;
      *) echo "❌ 无效 TRD 风险级别：$TRD_RISK_PROFILE"; exit 1 ;;
    esac
else
    TRACK="brd"
    export EASE_FEATURE_DIR="$BRD_FEATURE_DIR"
    IMPLEMENTATION_ARTIFACT_DIR=".eases/${CHANGE_ID}/flow-3-implement"
    CONTEXT_FILE=".eases/${CHANGE_ID}/context.json"
    if [ -f "$CONTEXT_FILE" ]; then
        DOMAIN_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["domain_id"])' "$CONTEXT_FILE")
        python3 references/ease-analysis/scripts/validate_flow_context.py \
          --input "$CONTEXT_FILE" --change "$CHANGE_ID" --domain "$DOMAIN_ID" --track brd || exit 1
    else
        DOMAIN_ID="$CHANGE_ID"  # 旧项目只读兼容；新执行必须有 context.json
        echo "⚠️ 未找到 context.json，按旧布局临时使用 DOMAIN_ID=CHANGE_ID"
    fi
fi
export SOURCE_PATH TRACK FEATURE_NAME CHANGE_ID DOMAIN_ID TRD_SOURCE_DIR BRD_SOURCE_DIR TRD_RISK_PROFILE
export LEGACY_BRD_SOURCE_DIR BRD_FEATURE_DIR IMPLEMENTATION_ARTIFACT_DIR
```

**分支 A — BRD 路径**（`SOURCE_PATH=brd`，须经 Phase 2 设计）：

验证 Phase 1 产出：
- [ ] `docs/domains/[编号]-[module_name]/usecases/` 包含用例文档（usecase.md + rules.md）
- [ ] `.eases/${CHANGE_ID}/flow-1-analyze/` 下 spec.md / plan.md / tasks.md 均存在

验证 Phase 2 产出（**BRD 路径强制**）：
- [ ] `${BRD_SOURCE_DIR}/architecture/arch-design.md` 存在且非空
- [ ] `${BRD_SOURCE_DIR}/detail/detail-design.md` 存在且非空
- [ ] `${BRD_SOURCE_DIR}/spec.md` 含 `Clarifications` 章节
- [ ] `${BRD_SOURCE_DIR}/tasks.md` 存在且非空（新目录为 `flow-2-design/`；仅在新目录不存在时兼容旧 `design/`）
- [ ] 开发模式明确（new / incremental），对应产物存在

除存在性定位外，必须逐项反证 `F2-ART-01` 至 `F2-SEM-01`，对 NEW/MOD→设计、API→testcase、设计授权→目标符号执行双向集合对账。无法列出全集、发现任一反例或证据属于旧 CHANGE_ID 时均为 FAIL，并回流契约指定 owner。

**分支 B — TRD 路径**（`SOURCE_PATH=trd`，设计内置于 Phase 1，**不经 Phase 2**）：

> ⚠️ TRD 路径**不校验** `usecases/` 与 `flow-2-design/`（这是 BRD 专属产物）；其方案设计在 Phase 1 的 `TRD.md` + `solution-design.md` 内（`phase-gate-invariant.md` §2 例外）。

- [ ] `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/TRD.md` 存在且非空
- [ ] `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/artifacts/solution-design.md` 存在且非空
- [ ] `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/tasks.md` 存在且使用技术工作包格式；存在 `[ ]` 时继续实现，全部 `[X]` 时验证完成证据后直接进入收尾
- [ ] `.eases/trd/[编号]-[trd_name]/flow-1-analyze-trd/validation/domain-impact.json` 校验为 `none`

除存在性定位外，必须逐项反证 `T1-ID-01` 至 `T1-MIG-01`，尤其验证风险信号是否触发 Strict、TRD→设计→tasks 是否双向对账，以及 Domain Impact 是否以充分理由为 none。

TRD 不要求 `spec.md` / `plan.md`；不得因这两个 BRD 生命周期文件缺失而阻断实现。
历史 TRD 若仍含 `spec.md` / `plan.md`，只读保留且不参与门禁；发现其与 `TRD.md` / `solution-design.md` 冲突时必须停止并回 Flow 1 迁移，禁止静默选择旧文件。

旧 tasks 迁移门禁：若 `${TRD_SOURCE_DIR}/tasks.md` 仍含 `[US1]`、用户故事/MVP 分段，或旧 spec/plan 存在且 tasks 已全部 `[X]` 却没有实现/测试证据，停止并返回 TRD Flow 1 执行“历史 TRD 一次性迁移”。迁移须保留旧 ID 映射，按技术工作包恢复无证据任务为 `[ ]`，并写入 `migration/legacy-trd-lifecycle.md`；Flow 3 不得现场猜测或静默改写。

如果对应分支任一条件不满足：
```
❌ Phase 门控未通过（来源路径：$SOURCE_PATH）。以下条件不满足：
  - [列出具体缺失项]

Phase 3 是最后一个阶段——如果前置阶段的产出不完整，本阶段的实现将建立在不可靠的基础上。
请回到失败 Gate 的唯一 owner 补齐证据，再重新执行本步骤的完整只读准入验收。
```

> 🔗 **本门控即「BRD 路径缺设计不编码」不变式的执行点**（见 `ease-spec/reference/phase-gate-invariant.md` §3）。
>
> **若缺失的是 Phase 2 设计产物**：唯一正解是先补 `/ease:flow-2-design docs/domains/${DOMAIN_ID}/usecases/ --change-id=${CHANGE_ID}`，再回到本命令。三阶段内不接受豁免；如用户选择其他方法，必须退出当前 Flow 并记录 `FLOW_ABORTED`/`PROCESS_CHANGED`。
>
> 💡 **快速通道提示（信息性，非自动改道）**：若本次确属琐碎改动（<200 行 / 单模块 / 无 API·数据模型变更），更合适的做法是改用官方快速通道 `/ease:quick-develop` 从头处理；但若已走 BRD 路径，请勿在 Phase 1 之后中途裸编码。

**未通过前置门控前，严禁继续 Phase 3 流程。**

#### 1.3 开发模式检测（强制，按 BRD/TRD 分支）

```bash
# 复用步骤 1.2.1 已解析并锁定的 FEATURE_NAME；禁止在后续步骤重新推导或覆盖。
: "${FEATURE_NAME:?步骤 1.2.1 必须先解析 FEATURE_NAME}"

# 检测开发模式。TRD 的设计内置于 Phase 1，不得要求 BRD 专属 Flow 2 产物。
DEVELOPMENT_MODE="new"
IS_INCREMENTAL="false"

if [ "$SOURCE_PATH" = "trd" ]; then
    if [ ! -s "${TRD_SOURCE_DIR}/TRD.md" ] || \
       [ ! -s "${TRD_SOURCE_DIR}/artifacts/solution-design.md" ] || \
       [ ! -s "${TRD_SOURCE_DIR}/tasks.md" ]; then
        echo "❌ TRD Phase 1 产物不完整：需要 TRD.md、solution-design.md、tasks.md"
        exit 1
    fi

    # TRD 通常修改现有系统；若存在常见源码目录则按增量实现，否则按全新实现。
    if [ -d "src" ] || [ -d "app" ] || [ -d "lib" ]; then
        DEVELOPMENT_MODE="incremental"
        IS_INCREMENTAL="true"
    fi
    echo "✓ TRD 路径：从 ${TRD_SOURCE_DIR} 读取内置设计与权威任务，不检查 Phase 2 目录"
elif [ -f "${BRD_SOURCE_DIR}/code-annotations/code-annotation-manifest.md" ]; then
    echo "✓ 检测到代码注释清单，确定为增量开发模式"
    DEVELOPMENT_MODE="incremental"
    IS_INCREMENTAL="true"
elif [ -d "${BRD_SOURCE_DIR}/framework-code" ] && [ -n "$(ls -A "${BRD_SOURCE_DIR}/framework-code/" 2>/dev/null)" ]; then
    echo "✓ 检测到框架代码，确定为全新开发模式"
else
    echo "⚠️ 未检测到 BRD Phase 2 设计输出，请先执行 /ease:flow-2-design"
    exit 1
fi

# BRD 路径继续检查代码注释或框架代码；TRD 以 solution-design + tasks 为定位依据。
if [ "$SOURCE_PATH" = "brd" ] && [ "$DEVELOPMENT_MODE" = "incremental" ]; then
    echo "✓ 开发模式：增量开发（基于现有代码中的TODO注释）"
    # 检查实际项目中是否有TODO注释
    TODO_COUNT=$(grep -r "// TODO\|# TODO\|<!-- TODO" --include="*.java" --include="*.kt" --include="*.scala" --include="*.py" --include="*.go" --include="*.rs" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" --include="*.rb" --include="*.c" --include="*.cpp" . 2>/dev/null | wc -l || echo "0")
    if [ "$TODO_COUNT" -eq "0" ]; then
        echo "⚠️ 警告：未在项目代码中找到TODO注释，但存在代码注释清单"
        echo "请确认 /ease:flow-2-design 命令已成功添加代码注释"
    else
        echo "✓ 在项目代码中找到 $TODO_COUNT 个TODO注释"
    fi
elif [ "$SOURCE_PATH" = "brd" ]; then
    echo "✓ 开发模式：全新开发（基于生成的框架代码）"
    # 检查框架代码中的TODO标记
    if [ -d "${BRD_SOURCE_DIR}/framework-code/src" ]; then
        TODO_COUNT=$(find "${BRD_SOURCE_DIR}/framework-code" -type f \( -name "*.java" -o -name "*.kt" -o -name "*.scala" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \) -exec grep -l "TODO" {} \; | wc -l || echo "0")
        echo "✓ 在框架代码中找到 $TODO_COUNT 个包含TODO的文件"
    fi
fi

# 导出变量供后续使用
export DEVELOPMENT_MODE
export IS_INCREMENTAL
```

> **开发模式处理原则**：
> - **TRD 路径**：直接消费 `${TRD_SOURCE_DIR}/TRD.md`、`artifacts/solution-design.md` 与权威 `tasks.md`，不得检查或要求 BRD 专属 Flow 2 目录、框架代码或代码注释清单
> - **增量开发**：基于现有代码中的TODO注释进行实现，优先查找实际项目代码中的TODO标记
> - **全新开发**：基于生成的框架代码进行实现，在`${BRD_SOURCE_DIR}/framework-code/`目录中操作
> - **BRD 必须优先执行 Flow 2**：仅 BRD 未检测到设计输出时阻断；TRD 以 Phase 1 内置设计为准

#### 1.4 需求模式检测（增量变动追踪，强制）

> 🎯 **目标**：检测本次实现是"全新领域"还是"对已有 domain/UC 的增量改动"。需求模式（`REQUIREMENT_MODE`）决定实现优先级排序和代码变动标注。
>
> ⚠️ **区分概念**：`DEVELOPMENT_MODE`（代码层面：是否有现有代码）vs `REQUIREMENT_MODE`（领域层面：是否涉及已有 UC 变动）。

```bash
# 检查 Phase 1 是否生成了增量变动分析报告
REQUIREMENT_MODE="new-domain"

if [ -f ".eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md" ]; then
    REQUIREMENT_MODE="incremental-domain"
    echo "✓ 检测到 delta-analysis.md，本次为增量领域改动"
    echo "  - 实现顺序：优先 [Δ-NEW]（风险低），后 [Δ-MOD]（需回归保护）"
    echo "  - 每个 [Δ-MOD] 完成后立即运行受影响的已有测试"
else
    echo "✓ 未检测到 delta-analysis.md，本次为全新领域"
fi
```

**变量输出**：
- `REQUIREMENT_MODE`: `"new-domain"` | `"incremental-domain"`

### 步骤 2: 准备工作

1. 使用 TodoWrite 工具创建任务列表，跟踪实现进度（根据开发模式调整）：
   ```bash
   TodoWrite:
     todos: [
       {content: "检查/创建 constitution.md", status: "pending"},
       {content: "创建 docs/domains 和 eases 目录", status: "pending"},
       {content: "检测开发模式（增量/全新）", status: "pending"},
       {content: "检测需求模式（new-domain / incremental-domain）", status: "pending"},
       {content: "检查待实现代码和注释信息", status: "pending"},
       {content: "收集上下文信息", status: "pending"},
       {content: "制定实现计划", status: "pending"},
       {content: "执行代码实现", status: "pending"},
       {content: "代码质量检查", status: "pending"},
       {content: "生成实现总结", status: "pending"},
       {content: "定位权威任务列表（Phase 2 flow-2-design/tasks.md 或 TRD tasks.md）", status: "pending"},
       {content: "执行 ease-spec implement 阶段：消费权威 tasks 并就地回写进度", status: "pending"},
       {content: "产出 Phase 3 实现校验清单", status: "pending"}
     ]
   ```

2. 根据来源路径与开发模式检查待实现信息：
   - **TRD 路径**（`SOURCE_PATH=trd`）：
     - 读取 `${TRD_SOURCE_DIR}/TRD.md`
     - 读取 `${TRD_SOURCE_DIR}/artifacts/solution-design.md`
     - 以 `${TRD_SOURCE_DIR}/tasks.md` 为权威实现清单
     - 根据 solution-design 与 tasks 中的文件/模块线索定位代码；**不要求** Flow 2 的 TODO 注释或框架代码
   - **增量开发模式**（`DEVELOPMENT_MODE=incremental`）：
     - 搜索项目代码中包含 `// TODO`、`# TODO` 或 `<!-- TODO -->` 标记的文件
     - BRD 路径检查代码注释清单：`${BRD_SOURCE_DIR}/code-annotations/code-annotation-manifest.md`
     - 验证TODO注释是否包含完整的用例引用和规则映射
   - **全新开发模式**（`DEVELOPMENT_MODE=new`）：
     - 检查框架代码目录：`${BRD_SOURCE_DIR}/framework-code/`
     - 搜索框架代码中的 `TODO` 标记
     - 检查框架代码清单：`framework-code-manifest.md`

3. 如果 BRD 路径未找到足够的待实现代码或注释信息：
   - **增量开发**：提示用户先执行 `/ease:flow-2-design` 命令添加代码注释
   - **全新开发**：提示用户先执行 `/ease:flow-2-design` 命令生成框架代码
   - 停止执行，等待用户操作

### 步骤 3: 收集上下文信息

按照以下顺序收集实现所需的上下文：

#### 3.0 增量变动优先上下文（仅 `REQUIREMENT_MODE=incremental-domain`）

> 📌 增量领域模式下，上下文收集应**优先加载变动点**，确保对 `[Δ-MOD]` 的修改有充分理解。

```
增量专属上下文（仅 REQUIREMENT_MODE=incremental-domain）：
├── delta-analysis.md              — 快速了解全局变动范围（UC/BR/Subdomain 变动明细）
├── arch-design.md 中 [Δ-MOD] 标记的章节  — 重点理解修改点（变更来源、原始设计、当前设计）
├── detail-design.md 中 [Δ-MOD] 标记的章节 — 重点理解修改实现细节
└── 已有代码的 git blame            — 理解原始实现意图（Chesterton's Fence，配合步骤 5.1.1）
```

**关键约束**：实现 `[Δ-MOD]` 时，必须先理解 delta-analysis.md 中记录的"变更前/变更后/原因"，确保不偏离需求意图。

#### 3.1 读取设计文档

1. BRD：读取 `${BRD_SOURCE_DIR}/` 与 `docs/domains/${DOMAIN_ID}/` 下相关设计/领域文档
2. TRD：读取 `${TRD_SOURCE_DIR}/TRD.md`、`artifacts/solution-design.md`、影响分析、风险与验证文档
3. 理解需求、数据流和设计约束
4. 识别关键的业务规则或技术约束

#### 3.2 分析待实现代码（根据开发模式）

##### 3.2.0 TRD 路径（`SOURCE_PATH=trd`，优先于开发模式分支）

1. 从 `${TRD_SOURCE_DIR}/tasks.md` 获取实现顺序与验收条件
2. 从 `artifacts/solution-design.md` 提取受影响模块、文件线索、兼容性与回滚约束
3. 在当前代码库定位实际实现点并建立任务到文件的映射
4. 不搜索或依赖 BRD 专属的 UC/BR TODO 注释；若任务缺少可定位信息，触发 Stop-the-Line 回到 TRD Phase 1 补充

> 完成本节后，TRD 路径跳过 3.2.1/3.2.2；以下两个开发模式分支仅适用于 BRD。

##### 3.2.1 BRD 增量开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=incremental`）

1. **读取现有代码中的TODO注释**：
   - 在项目代码中搜索包含 `TODO` 标记的文件
   - 读取代码注释清单：`${BRD_SOURCE_DIR}/code-annotations/code-annotation-manifest.md`
   - 定位实际代码文件中的TODO注释位置

2. **分析代码注释内容**：
   - 解析TODO注释中的用例引用（UC-XXX）
   - 提取业务规则映射（BR-XXX）
   - 理解实现步骤描述
   - 识别需要新增或修改的代码位置

3. **理解现有代码结构**：
   - 分析类之间的依赖关系和数据流
   - 检查现有方法的签名和实现
   - 确定代码修改的影响范围

4. **生成增量实现任务**：
   - 基于TODO注释创建具体的实现任务
   - 标记需要新增的方法、修改的方法、新增的类

##### 3.2.2 BRD 全新开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=new`）

1. **读取框架代码**：
   - 读取框架代码目录：`${BRD_SOURCE_DIR}/framework-code/`
   - 分析框架代码清单：`framework-code-manifest.md`
   - 定位包含 `TODO` 标记的文件

2. **分析代码注释中的业务流程步骤**：
   - 解析方法注释中的实现步骤
   - 提取业务规则映射
   - 理解类之间的依赖关系和数据流

3. **识别所有 `TODO` 标记的位置**：
   - 在框架代码中搜索 `TODO` 标记
   - 记录每个TODO标记的上下文和所属方法

4. **理解框架代码结构**：
   - 分析生成的类层次结构
   - 检查方法签名和参数
   - 确定实现顺序和依赖关系

#### 3.3 读取编码规范

参考 `references/ease-coding/references/coding-java.md` 中定义的编码规范，确保实现符合以下标准：

- 代码风格（Google Java Style Guide）
- 命名规范（类、方法、变量、常量）
- SOLID 原则和 Clean Code 原则
- 错误处理和日志记录规范
- 现代 Java 特性使用（Lombok、Optional、Stream API）

### 步骤 4: 制定实现计划

基于收集的信息和开发模式，制定详细的实现计划：

> **TRD 优先规则**：当 `SOURCE_PATH=trd` 时，直接按 `${TRD_SOURCE_DIR}/tasks.md` 制定实现计划，并把兼容性、回滚和验证约束映射到每个任务；完成后跳过 4.1/4.2，不套用依赖 Flow 2 manifest/framework-code 的 BRD 模板。

#### 4.0 增量变动优先级排序（仅 `REQUIREMENT_MODE=incremental-domain`）

> 📌 增量领域模式下，实现计划必须按变动类型排序，降低回归风险。

**增量实现顺序策略**：

```
1. 先实现 [Δ-NEW] 的独立新功能
   - 风险低，不触碰已有代码
   - 可独立测试，不影响现有功能

2. 再实现 [Δ-MOD] 的修改
   - 风险高，必须 Chesterton's Fence 检查（理解原始实现意图）
   - 修改前定位所有调用该方法的上下游代码（影响范围分析）
   - 每完成一个 [Δ-MOD]，立即运行受影响的已有测试（回归验证）

3. 变动任务标注
   - 在 TodoWrite 中每个任务标注 [Δ-NEW] 或 [Δ-MOD]
   - [Δ-MOD] 任务附加"影响范围"和"回归测试清单"
```

**回归保护**：所有 `[Δ-MOD]` 任务实现前，**必须**确认受影响的已有测试存在且通过（建立绿色基线）；实现后再次运行，确认无回归。

##### 4.1 BRD 增量开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=incremental`）

1. **识别增量实现任务**：
   - 基于代码注释清单（`code-annotation-manifest.md`）列出所有需要实现的方法和类
   - 区分任务类型：新增方法、修改现有方法、新增类
   - 按照依赖关系和影响范围排序（先修改底层服务，再修改上层接口）

2. **规划增量实现顺序**：
   - **数据层修改**：如果需要修改数据模型或Repository
   - **服务层修改**：修改或新增Service方法
   - **接口层修改**：修改或新增Controller方法
   - **集成测试**：确保现有功能不受影响

3. **更新 TodoWrite**：
   - 将所有增量实现任务添加到 todo 列表
   - 标记当前正在进行的任务
   - 特别标注需要小心处理的现有代码修改点

##### 4.2 BRD 全新开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=new`）

1. **识别实现任务**：
   - 基于框架代码清单（`framework-code-manifest.md`）列出所有需要实现的方法和类
   - 按照依赖关系和优先级排序（先实现底层 Integration 和 Service，再实现 Action 和 Controller）

2. **规划实现顺序**：
   - Integration 层：外部系统集成、数据访问
   - Service 层：核心业务逻辑
   - Action 层（Combined Service）：业务流程编排
   - Controller 层：API 接口

3. **更新 TodoWrite**：
   - 将所有实现任务添加到 todo 列表
   - 标记当前正在进行的任务

### 步骤 5: 代码实现（TDD 驱动，不可协商）

> ⚠️ **强制要求**：遵循 `test-driven-development` skill 的核心原则 —— **没有先失败的测试，就不要写生产代码**。
>
> ⚠️ **强制要求**：**所有单元测试代码必须严格遵循 `ease-testing` 技能的规范（不可协商）** —— 模板、MC/DC 覆盖、AAA 结构、FIRST 与 Mock 策略均以 ease-testing 为准。RED 阶段（无源码）按规范编写失败测试；GREEN 后用 ease-testing 的分轮白盒流程补强覆盖率。

TRD 按 `TRD_RISK_PROFILE` 使用比例门禁：

| Profile | 实施验证要求 |
|---|---|
| **Lite** | 必须先取得失败复现或变更前基线，再运行相关回归、构建/静态检查和依赖/运行时兼容验证。修改生产逻辑时对改变的行为执行 TDD；仅依赖/配置/构建变更且没有新增或修改方法时，不虚构“每个方法”测试，覆盖率、D-Gate、变异冒烟记 `N/A + 理由`。 |
| **Standard** | 对新增/修改行为执行 TDD，验证变更范围的适用覆盖率；触及 DB/Redis/MQ/网络/时间时执行 D-Gate；仅对新增/修改的核心方法做变异冒烟。 |
| **Strict** | 执行完整 TDD、覆盖率、断言价值、D-Gate、核心方法变异、兼容/迁移、灰度观测和回滚演练。 |

BRD 继续执行完整门禁。下文“每个方法”的绝对要求适用于 BRD/Strict；Lite/Standard 以上表为裁剪权威，不能用裁剪跳过实际发生的生产逻辑变化。

对适用范围内每个待实现的方法，**必须严格遵循 TDD 红-绿-重构循环**：

```
┌─────────────────────────────────────────────────────────────────┐
│                    TDD 循环（每个方法必须执行）                    │
├─────────────────────────────────────────────────────────────────┤
│  1. RED    → 先写测试，运行，看着它失败                          │
│  2. 验证RED → 确认失败原因是"功能缺失"，不是语法/拼写错误          │
│  3. GREEN  → 写最少的代码让测试通过                              │
│  4. 验证GREEN → 运行测试，确认通过，其他测试仍然通过              │
│  5. REFACTOR → 重构代码，保持测试全绿                            │
│  6. 重复   → 下一个测试方法，回到步骤 1                          │
└─────────────────────────────────────────────────────────────────┘
```

**TDD 铁律**：
- 在写测试之前就写了代码？**删掉它，从头开始**
- 测试一上来就通过？**测试写错了，修正测试**
- 跳过验证 RED 阶段？**停止，重新开始**

#### 5.1 实现前检查（根据开发模式）

##### 5.1.0 TRD 路径（`SOURCE_PATH=trd`）

先验证当前任务可追溯到 `${TRD_SOURCE_DIR}/tasks.md` 和 `artifacts/solution-design.md`，再基于实际代码建立 RED 基线；不要求 BRD 的 TODO 注释或测试框架骨架。完成后跳过 5.1.1/5.1.2。

##### 5.1.1 BRD 增量开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=incremental`）

> ⚠️ **Chesterton's Fence（切斯特顿栅栏原则）**：增量开发的第一步不是修改代码，而是理解为什么现有代码以当前方式存在。未理解就修改是增量开发中回归 bug 的首要来源。

**Chesterton's Fence 前置检查**：

1. **快速扫描 TODO 注释，确定修改范围**：
   - 扫描所有 TODO 注释，列出涉及的文件和方法（只定位，不深入实现细节）
   - 基于扫描结果确定需要修改的文件清单

2. **对修改范围内的文件执行 Chesterton's Fence 检查**：
   - 对于清单中的每个文件，运行 `git blame` 查看关键代码行的最后一次提交：
     - 原始提交的上下文是什么？当时的 PR/Issue 描述了什么？
     - 这段代码是修复了什么 bug？还是实现了什么特性？
   - 理解隐式约束：
     - 为什么用这个数据结构（例如为什么是 `Map` 而不是 `List`）？
     - 为什么错误处理方式跟周围代码不同？（可能有兼容性约束）
     - 为什么某些看似“多余”的校验存在？（可能线上出过事故）
   - 确认理解后，记录关键发现，供后续实现者参考

**如果你无法解释"为什么这段代码以这种方式存在"，不要修改它。先问，后改。**

3. **阅读TODO注释上下文**：
   - 阅读TODO注释中的用例引用和规则映射
   - 理解新增或修改的需求背景
   - 检查TODO注释是否标记了完整的实现步骤

4. **分析现有代码结构**：
   - 检查方法所在的类及其依赖关系
   - 理解现有代码的逻辑和风格
   - 识别可能受影响的现有功能
   - 基于 Chesterton's Fence 检查结果，确认修改不会破坏原有意图

5. **检查方法签名和位置**：
   - 如果是新增方法：检查方法签名是否符合现有代码规范
   - 如果是修改方法：检查现有方法的签名和实现
   - 确定代码修改的边界和影响范围

6. **识别依赖项和集成点**：
   - 识别需要调用的现有服务或组件
   - 检查数据访问层是否需要修改
   - 确定测试策略（单元测试、集成测试）

7. **【TDD 准备】检查测试框架代码**：
   - 查找对应的测试类和测试方法
   - 如果没有测试框架代码，**必须先编写测试**
   - 确认测试方法包含 `fail("TODO: ...")` 或断言占位符

##### 5.1.2 BRD 全新开发模式（`SOURCE_PATH=brd && DEVELOPMENT_MODE=new`）

1. **阅读方法的 Javadoc 注释**，理解其职责
2. **检查方法签名**（参数、返回值、异常）
3. **阅读业务流程步骤注释**
4. **识别需要的依赖项**
5. **【TDD 准备】定位对应的测试框架代码**：
   - 在 `src/test/` 目录中找到对应的测试类
   - 阅读测试方法的 `// Given-When-Then` 注释
   - 确认测试方法当前状态为失败（包含 `fail("TODO: ...")`）

#### 5.2 TDD 红-绿-重构循环（每个方法必须执行）

> **核心原则**：先写测试。看着它失败。再写最少的代码让它通过。
> **测试编写**：调用 `ease-testing` skill，遵循 MC/DC 覆盖原则和 AAA 模式。

##### 5.2.1 RED 阶段 - 编写/完善失败的测试

> ⚠️ **强制要求（不可协商）**：**RED 阶段的测试必须严格遵循 `ease-testing` 技能的模板与规范编写**（MC/DC、AAA、FIRST、Mock 策略）。此时生产代码尚不存在，无法走 ease-testing 的白盒逆向流程，因此是"按规范编写"而非"白盒生成"；GREEN 之后再用 ease-testing 的分轮覆盖率流程补强。

**按 `ease-testing` skill 的规范编写测试**：

- **参考流程**：`references/ease-testing/flows/generate-test-code.md`
- **语言参考**：`references/ease-testing/references/testing-[language].md`
- **模板参考**：`references/ease-testing/templates/`

1. **定位测试方法**：
   - 找到对应的测试类和测试方法
   - 如果测试框架代码已存在，移除 `fail("TODO: ...")` 并**按 `ease-testing` 规范完善**测试逻辑
   - 如果没有测试，**必须按 `ease-testing` 的模板与覆盖原则编写测试**（参见 `templates/` 和 `references/testing-[language].md`），不得脱离规范随意发挥
   - 若存在 `test-case-document.md`，优先按其中对应的 `TC-XXX-NNN` 案例编写（Step 0）

2. **遵循 `ease-testing` 的 AAA 模式编写测试**：
   ```
   Arrange  → 准备测试数据和环境
   Act      → 执行被测方法
   Assert   → 验证结果符合预期
   ```

3. **遵循 `ease-testing` 的 MC/DC 原则**：
   - 条件独立性：每个条件独立影响决策结果
   - 分支全覆盖：所有分支路径都被测试
   - 边界值测试：测试边界及其附近值

4. **遵循 `ease-testing` 的 Mock 策略（按测试类型分流，不可混淆）**：
   - **本步骤是 TDD 单元测试**：资源层（DB/Redis/MQ/网络/时间）✅ **MUST 隔离**，用 Mock/Fake/注入时钟，保证毫秒级、确定性（FIRST 原则）
   - 外部服务（第三方 API）：✅ Mock，使用 WireMock/MockServer
   - 业务依赖（内部服务）：✅ Mock，隔离测试
   - **集成测试场景另行处理**：资源层 PREFER 真实/容器化依赖（TestContainers），通过 `/ease-tools:generate-tests --integration` 进入 `ease-testing` 权威流程。不要在单元测试里拉起真实 DB。

5. **测试要求**（遵循 `ease-testing` 的 FIRST 原则）：
   - **F**ast：毫秒级完成
   - **I**ndependent：测试间无依赖
   - **R**epeatable：任何环境结果一致
   - **S**elf-validating：Pass/Fail，无需人工检查
   - **T**imely：先写测试，再写实现

##### 5.2.2 验证 RED 阶段 - 看着测试失败（不可跳过）

**必须执行测试并确认失败**：

```bash
# 运行单个测试
npm test path/to/test.test.ts
# 或
mvn test -Dtest=UserServiceTest#should_reject_empty_email
# 或
./gradlew test --tests "UserServiceTest.should_reject_empty_email"
```

**检查失败原因**：
- ✅ 测试失败（fail），原因是"功能缺失"（方法未实现、返回值不对）
- ❌ 测试报错（error），原因是语法/编译/拼写错误 → **先修复错误，重新运行**
- ❌ 测试通过（pass） → **测试写错了，修正测试，确保它测的是新功能**

> **如果你没有亲眼看着测试失败，你就无法确认它是否真的在测你想测的东西。**

> ⚠️ **编译/运行异常无法解决时**：如果遇到编译错误、运行时异常或测试失败，且经过多次尝试仍无法解决，**立即调用 `systematic-debugging` 技能**进行系统性根因分析，禁止继续盲目尝试修复。

##### 5.2.3 GREEN 阶段 - 写最少的代码让测试通过

**编写实现代码**，遵循以下原则：

**基础原则**

- **单一职责**：一个方法只做一件事
- **方法短小**：控制在 20-40 行以内
- **清晰命名**：使用 camelCase，动词或动词短语
- **参数验证**：使用 `@NonNull`、`@Valid` 等注解，必要时进行边界检查
- **最小实现**：只写刚好够让测试通过的代码，不要额外加功能

**错误处理**

- 使用自定义异常表达业务错误（参考设计文档中定义的异常类型）
- 不返回 null，使用 `Optional<T>` 表示可能不存在的值
- 提供清晰的错误消息，包含上下文信息

**日志记录**

- 使用 SLF4J 进行日志记录
- ERROR: 严重问题，可能导致功能中断
- WARN: 潜在问题或非预期状态
- INFO: 重要的业务事件
- DEBUG: 详细的调试信息
- 禁止记录敏感信息（密码、密钥、PII 等）

**现代 Java 特性**

- 优先使用 Lombok 注解（`@Builder`, `@RequiredArgsConstructor`, `@Data`）
- 使用 `Optional<T>` 替代可能为 null 的返回值
- 使用 Stream API 处理集合操作
- 使用方法引用替代 lambda 表达式（如 `User::getName`）

**安全性**

- 防止 SQL 注入：使用参数化查询或 ORM
- 防止 XSS：对用户输入进行转义
- 防止命令注入：避免直接拼接命令字符串
- 敏感数据加密：使用安全的加密算法

##### 5.2.4 验证 GREEN 阶段 - 看着测试通过（不可跳过）

**必须执行测试并确认通过**：

```bash
# 运行测试
npm test path/to/test.test.ts
# 或
mvn test -Dtest=UserServiceTest
```

**检查结果**：
- ✅ 当前测试通过
- ✅ 其他测试仍然通过（无回归）
- ✅ 输出干净（无错误、无警告）

**测试失败？** 修代码，不要改测试。
**其他测试失败？** 立刻修，别拖。

> ⚠️ **多次修复仍失败时**：如果尝试 2-3 次修复仍无法解决问题，**停止盲目尝试**，调用 `systematic-debugging` 技能进行系统性调试（参考 `plugins/ease-tools/skills/systematic-debugging/SKILL.md`）。

##### 5.2.5 REFACTOR 阶段 - 清理重构

只在"全绿"之后做：
- 移除重复代码
- 改进命名
- 提取辅助方法
- 简化复杂逻辑

**重构后必须再次运行测试**，确保仍然全绿。

##### 5.2.6 重复循环

为下一个功能点/测试方法重复 RED → 验证 RED → GREEN → 验证 GREEN → REFACTOR 循环。

#### 5.3 添加必要的导入和依赖

1. 添加所需的 import 语句（禁止使用通配符 `*`）
2. 如果需要新的依赖项，注入到构造函数（使用 `@RequiredArgsConstructor`）

#### 5.4 范围纪律 (Range Discipline)

> ⚠️ **Rule 0.5：只触碰任务要求的代码**。实现阶段最容易犯的错误是"顺手修一下"。

**严禁的行为**：
- "顺便"清理相邻代码的格式问题
- 重构正在实现的方法所调用的下游模块（除非是该需求的必然部分）
- "边写边优化"——在实现需求时顺带重构无关代码
- 删除 lint 工具报告的但不属于本次变更范围的 warning
- "既然看到了就修一下"——这是范围蠕变最常见的模式

**正确做法**——发现值得改进但不在范围内的代码时：

```
NOTICED BUT NOT TOUCHING（实现中注意到但不触碰）:
- src/service/NotificationService.java 缺少速率限制（安全风险，但不属当前需求范围）
- src/controller/UserController.java 的错误消息格式与项目标准不一致（代码风格问题）
→ 已记录为独立发现。是否需要我为这些创建独立任务？
```

**为什么在实现阶段范围纪律比任何其他阶段都重要**：
1. 混合提交不可审计：如果 PR 同时包含"实现需求"和"修了一个无关的代码格式"，reviewer 必须花时间区分哪个是哪个
2. 回滚困难：如果需求上线后需要回滚，无关的格式修改也会被一起回滚
3. 回归来源不明：如果混合提交引入回归，无法快速判断是需求实现导致的还是无关修改导致的
4. TDD 循环被破坏：无关修改没有对应测试覆盖，等于引入了未测试代码

**范围蠕变自查（每个方法实现完成后执行）**：
- [ ] 我修改的文件都在任务计划（tasks.md）之内吗？
- [ ] 如果我删掉了"顺手"改的那几行，功能仍然完整吗？
- [ ] 本次 diff 足够干净，reviewer 能一眼看出核心变更吗？

#### 5.5 完成实现后（根据开发模式）

##### 5.5.1 增量开发模式（`DEVELOPMENT_MODE=incremental`）

1. **删除TODO标记**：
   - 删除代码中的 `// TODO`、`# TODO` 或 `<!-- TODO -->` 标记
   - 保留方法级 Javadoc/文档注释中的用例引用（UC-XXX）和规则映射（BR-XXX），作为实现背景的持久化记录；删除行内 TODO 步骤标记（如 `// TODO: 步骤1 - ...`）
   - 清理临时注释标记（如 `====== 增量修改开始 ======`，来源于 flow-2-design 增量开发注释格式，仅在修改现有方法时存在）

2. **完善代码注释**：
   - 添加或完善 Javadoc/文档注释
   - 在注释中标注增量开发的背景（基于哪个用例）
   - 记录重要的设计决策和注意事项

3. **变动标记保留（仅 `REQUIREMENT_MODE=incremental-domain`）**：
   - 删除 `// TODO` 步骤标记，**但保留** Javadoc 级别的 `[Δ-NEW]` / `[Δ-MOD]` 标记作为持久化变动记录
   - 标准格式：
     ```java
     /**
      * [Δ-MOD] 需求#NNN: [变更说明]
      * 变动来源：UC-XXX [Δ-MOD], BR-XXX [Δ-NEW]
      * @since [版本/日期]
      */
     ```
   - 保留这些标记的价值：未来迭代时可快速识别该方法的变更历史，避免重复分析

4. **TDD 验证**：
   - **运行所有相关测试**，确保全部通过
   - 确保现有功能不受影响（无回归）
   - 检查测试覆盖率是否达标

5. **标记任务完成**：
   - 在代码注释清单中标记对应任务已完成
   - 更新任务状态

##### 5.5.2 全新开发模式（`DEVELOPMENT_MODE=new`）

1. **删除对应的 `// TODO` 标记**
2. **添加或完善 Javadoc 注释**
3. **TDD 验证**：
   - 运行当前方法的所有测试，确认全绿
   - 运行整个测试套件，确认无回归
4. **标记该任务为已完成**

### 步骤 6: 代码质量检查（含 TDD 验证）

对每个实现的代码进行自我审查：

#### 6.1 TDD 验证检查（不可协商）

> 遵循 `test-driven-development` skill 的验证检查列表
>
> BRD/Strict 全量执行；Lite/Standard 按步骤 5 的比例门禁执行，并在不适用项记录 `N/A + 理由`，不得伪造测试或指标。

- [ ] 每个新函数/方法有测试
- [ ] 在实现之前亲眼看着每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，不是拼写错误）
- [ ] 只写最少的实现让每个测试通过
- [ ] 所有测试通过
- [ ] 输出干净（无错误、无警告）
- [ ] 测试尽量用真实代码（仅在不可避免时使用 mock）
- [ ] 覆盖边缘情况和错误

**不能勾完所有框？说明你跳过了 TDD。删除实现代码，重新开始。**

#### 6.1.1 覆盖率检查（遵循 `ease-testing` 标准）

> 参考 `references/ease-testing/SKILL.md` 的覆盖率目标
>
> BRD/Strict 使用全量阈值；Standard 对变更代码使用适用阈值；Lite 未修改生产逻辑时不强制覆盖率，记录基线、相关回归和兼容验证证据。

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 行覆盖率 | ≥ 80% | ___ | ☐ |
| 分支覆盖率 | ≥ 70% | ___ | ☐ |
| 方法覆盖率 | ≥ 85% | ___ | ☐ |

**覆盖率不达标？** 调用 `ease-testing` skill 的分轮提升策略补充测试。

#### 6.2 功能性检查

- 代码逻辑是否正确
- 是否处理了所有边界条件
- 是否符合设计文档中的业务规则

#### 6.3 代码质量检查

- 是否遵循编码规范（Google Java Style Guide）
- 方法长度是否适中（不超过 40 行）
- 是否存在代码重复（DRY 原则）
- 是否遵循 SOLID 原则

#### 6.4 安全性检查

- 是否存在潜在的安全漏洞
- 是否正确处理了敏感数据
- 是否进行了必要的权限检查

#### 6.5 性能检查

- 算法复杂度是否合理
- 是否存在不必要的数据库查询
- 是否存在内存泄漏风险

### 步骤 7: 生成实现总结

完成所有实现后，在当前变更的 `flow-3-implement/outputs/` 下生成过程总结，不写入 `docs/`。

输出格式见模板：`references/ease-coding/templates/implementation-summary-template.md`（生成前 Read 该文件获取完整骨架）

### 步骤 8：执行实现并回写任务进度（ease-spec implement 阶段）

> ⚠️ **核心原则（不可协商）**：Phase 3 不重新生成前置需求、设计或任务。BRD 的权威链是 `spec → plan → tasks`；TRD 的权威链是 `TRD.md → solution-design.md → tasks.md`。Phase 3 只消费权威链、就地回写任务进度，并新增实现总结与实现校验清单。
>
> 📌 **为什么改为"消费 + 回写"**：早先版本在此处再次调用 `create-new-feature.sh` 重跑生命周期，会新建分支/编号并产生第三套 spec/plan/tasks，与 Phase 1/2 的同名产物语义重叠、破坏单一事实来源（见 `ease-spec/reference/stage-contract.md` §4 C-4）。

#### 8.1 定位权威任务列表（按来源路径）

```bash
# 与步骤 1.2.1 判定的 SOURCE_PATH 一致
if [ "$SOURCE_PATH" = "trd" ]; then
    # TRD 路径：任务列表来自 Phase 1（TRD 设计内置）
    export EASE_FEATURE_DIR="trd/${CHANGE_ID}/flow-1-analyze-trd"
else
    # BRD 路径：任务列表来自 Phase 2 设计
    export EASE_FEATURE_DIR="$BRD_FEATURE_DIR"
fi
```

#### 8.2 implement 阶段 - 执行实现并回写进度

- 入口文档：ease-spec 技能包内的 `reference/execute-implementation.md`
- 输入（权威，来自前置阶段，**不重新生成**）：
  - BRD：`${EASE_FEATURE_DIR}/{spec,plan,tasks}.md`
  - TRD：`${TRD_SOURCE_DIR}/TRD.md`、`${TRD_SOURCE_DIR}/artifacts/solution-design.md`、`${TRD_SOURCE_DIR}/tasks.md`
- 前置校验（不创建新产物）：
  ```bash
  if [ "$SOURCE_PATH" = "trd" ]; then
      test -s "${TRD_SOURCE_DIR}/TRD.md"
      test -s "${TRD_SOURCE_DIR}/artifacts/solution-design.md"
      test -s "${TRD_SOURCE_DIR}/tasks.md"
      python3 references/ease-analysis/scripts/validate_domain_impact.py \
        --input "${TRD_SOURCE_DIR}/validation/domain-impact.json"
  else
      references/ease-spec/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
      # PowerShell: check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
  fi
  ```
- 执行与回写：
  - 按权威 `tasks.md` 执行 TDD 实现（步骤 5），完成项**就地**在该 `tasks.md` 中标记为 `[X]`
  - 验证测试通过与覆盖率达标（见 §6.1.1 阈值）
  - 如发现实现与权威需求/设计不一致 → 触发 Stop-the-Line：BRD 回 Flow 2 修复 spec/plan，TRD 回 Flow 1 修复 TRD/solution-design；Phase 3 不私自改写前置权威文档

#### 8.3 产出 Phase 3 专属工件（实现总结 + 校验清单）

> Phase 3 仅新增"实现侧"工件，不复制需求/计划/任务。

- 实现总结：BRD 写入 `.eases/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`；TRD 写入 `.eases/trd/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`（步骤 7 已生成）
- 实现校验清单：`${IMPLEMENTATION_ARTIFACT_DIR}/checklists/implementation.md`
  ```bash
  mkdir -p "${IMPLEMENTATION_ARTIFACT_DIR}/checklists"
  # 写入 TDD 验证、覆盖率、范围纪律、架构一致性等校验结果（见步骤 9.6 门控）
  ```

> 📌 **TRD 路径说明**：TRD 的权威任务目录在 `.eases/trd/.../flow-1-analyze-trd/`；Phase 3 仍只回写该 tasks.md 进度，并在同一 `CHANGE_ID` 的 `flow-3-implement/outputs/` 产出总结。

### 步骤 9：完成验证

1. 标记所有任务为完成
2. 向用户提供实现总结报告
3. 列出已实现的文件和方法
4. 提供后续建议（如编写测试用例、运行代码审查等）

**实现完成审批标准**：

审批不是寻找完美的代码，而是确认代码**确实改善了整体代码健康度**——即使有改进空间。

**批准条件（满足所有即批准）**：
- 所有适用测试/验证通过且输出干净；生产逻辑变更已完成 TDD
- BRD/Strict 覆盖率达到行 ≥80%、分支 ≥70%、方法 ≥85%；Lite/Standard 按 `TRD_RISK_PROFILE` 提供比例证据或有依据的 N/A
- 实现行为与权威设计一致（BRD：arch-design.md + detail-design.md；TRD：solution-design.md）
- 无已知安全漏洞或数据完整性风险
- 代码可被另一个工程师理解（无需作者解释关键逻辑）

**不应因以下原因驳回**：
- "这个变量名可以更好"（如果它准确描述了内容）——命名偏好不是缺陷
- "这个 35 行的方法可以拆成两个"（如果它职责清晰）——方法长度是方向不是铁律
- "这里用了显式循环而不是 Stream API"（如果逻辑清晰）——风格选择，不是对错

**必须驳回的情况**：
- 实现行为与设计文档有实质性偏离
- 适用关键分支未覆盖，或 Lite/Standard 缺少要求的基线、回归、构建/兼容证据
- 发生生产逻辑变化却跳过 TDD（有代码无对应测试，或测试一上来就通过）
- 范围纪律被破坏（diff 中包含与需求无关的修改）
- 存在安全性或数据完整性漏洞

### 步骤 9.4.5：领域实现证据与漂移检查（BRD 强制）

> TRD 且明确 `domain-impact=none` 时记录 N/A；一旦技术任务改变角色、业务规则、状态机或业务结果，必须停止并转回 BRD Flow 1。

TRD 路径必须重新运行 `validate_domain_impact.py` 校验 Phase 1 的 `validation/domain-impact.json`。只有 `none` 可继续；这保持原“TRD 内置设计直连实现”方法论，同时阻止业务变化借 TRD 绕行。

1. 读取 `docs/domains/${DOMAIN_ID}/domain-alignment.json` 与 Flow 2 的 `alignment/domain-design-matrix.json`。
2. 使用 `ease-analysis/templates/domain-implementation-alignment-template.json` 生成 `.eases/${CHANGE_ID}/flow-3-implement/checklists/domain-implementation-alignment.json`。
3. 为每个本次 `NEW`/`MOD` UC/BR 填写至少一个 `code_refs` 和一个 `test_refs`；不得引用不存在、已废弃或未进入基线的 ID。
4. 若实现行为与 UC/BR 冲突：代码错误则修代码；设计遗漏则返回 Flow 2；业务定义变化则返回 Flow 1。禁止在 Flow 3 直接改写领域事实。
5. 执行：

```bash
python3 references/ease-analysis/scripts/validate_domain_alignment.py --manifest "docs/domains/${DOMAIN_ID}/domain-alignment.json" --phase flow-3 --matrix ".eases/${CHANGE_ID}/flow-2-design/alignment/domain-design-matrix.json" --implementation ".eases/${CHANGE_ID}/flow-3-implement/checklists/domain-implementation-alignment.json"
```

任何未解决的领域漂移均为阻断项，校验失败不得完成 Flow 3。

## 长期 TC 接入（新任务）

执行前读取 `ease-test-case-design/references/durable-test-assets.md`（相对 `references/`）。领域 TC 保存在 `docs/domains/${DOMAIN_ID}/testcases/`，跨域/架构 TC 在 `docs/qa/testcases/`；不创建 docs/testing。任务只保存 test-selection 和执行证据。

新任务优先读取 BRD `flow-2-design/test-cases/test-selection.json` 或 TRD `flow-1-analyze-trd/validation/test-selection.json`，按 path/revision/hash 加载长期 TC；存在但无效不得回退。下文 `test-case-document.md` 对新任务仅指从所选 TC 生成的只读可读投影，旧任务无 selection 时才兼容旧权威案例文件。接口报告与测试方法必须引用同一集合，不能重新从代码推导并丢弃它。


### 步骤 9.4.6：长期 TC 执行对账与 ADR 证据（最终门禁前）

读取 `ease-test-case-design/references/durable-test-assets.md` 与 `ease-arch-documentation/references/evidence-and-decision-contract.md`。将下文步骤 9.7 的 ADR/DDR 实施证据补充提前在此执行；9.7 仅为定义，不得在门禁 PASS 后再次改动被验收证据。

按 selection 锁定长期 TC，生成 `${IMPLEMENTATION_ARTIFACT_DIR}/testing/{test-execution,execution-snapshot}.json`，运行 manage_test_assets.py 执行校验。缺失/过期/blocked/skipped 的必做案例不得算 PASS。纯技术 TC 可追溯 ADR/NFR，无须虚构 UC/BR。

用 check_architecture_drift.py --base <本次准入commit> --mode worktree --policy block 校验当前批准 ADR，结合当前 assessment；将输出附加交付审查。无 metadata 仍检查 ADR。文档 stale 与决策冲突分别报告；独立 review 对照适用范围复核，不能仅凭生成报告自证。

### 步骤 9.5：架构文档漂移检查（自动执行）

> 完成代码实现后，自动检测架构文档是否因本次变更而产生漂移。

1. 检测 `docs/system/metadata.json` 是否存在。若不存在，跳过此步骤。
2. 若存在，执行架构文档漂移检查（流程见 `ease-arch-documentation` 技能的漂移检测章节）：
   - 读取 `metadata.json` 中各文档的基线 commit_id
   - `check_architecture_drift.py --base <oldest_commit> --mode worktree` 获取包含暂存、未暂存和新增文件的变更；按文档各自基线判断
   - 判断哪些架构文档受影响
3. 将漂移状态附加在交付报告末尾。若存在漂移，建议用户执行 `/ease:arch-docs` 更新受影响的文档。
4. 更新 `metadata.json.drift_status`。

### 步骤 9.6：Phase 3 完成门控（强制）

> ⚠️ **强制要求**：实现生产遍必须提交以下全部候选证据，随后由独立只读 delivery review 决定是否完成。这是三阶段流程的最后一道质量关卡。
>
> **两遍交付**：实现角色完成生产遍后，只能把 `F3-TDD-01`、`F3-TST-01`、`F3-QLT-01`、`F3-SCP-01`、`F3-ARC-01`、适用时的 `F3-DELTA-01`、`F3-TASK-01`、`F3-TRC-01`、`F3-DRIFT-01`、适用时的 `F3-RLS-01` 候选证据写入 `${IMPLEMENTATION_ARTIFACT_DIR}/checklists/delivery-submission.md`，状态为 `READY_FOR_ADMISSION`。随后切换为只读 delivery review，冻结代码/测试/tasks，按 `ease-spec/gates/flow-3-delivery.md` 主动寻找反例和执行双向集合对账，权威结论写入 `${IMPLEMENTATION_ARTIFACT_DIR}/checklists/delivery-review.md`。
>
> 评审中发现问题必须先保存 FAIL，再退出评审回到唯一 owner 修复；不得边审边改后直接 PASS。代码、测试、设计或 tasks 任何变化都会使旧 `delivery-review.md` 恢复 PENDING并要求完整重验。

#### 在 delivery review 中使用 ease-qa

由本步骤的独立只读评审角色调用 **ease-qa**，承担证据判断、主动反证和缺口分析。调用技能本身不证明审查独立性；必须先结束实现遍并冻结待审对象，再执行 review。原 Gate ID、阈值、适用性、失败回流和交付状态仍由本命令与 `ease-spec/gates/flow-3-delivery.md` 决定。

1. **传入完整验收上下文**：BRD/TRD 与 Strict/Standard/Lite 级别、交付范围及当前版本/工作区变更、权威需求/设计/tasks、`delivery-submission.md`、下列清单与门禁契约的全部适用条件（含 TC 和 ADR 补充验收）。同时提供真实代码 diff、测试选择与执行快照、运行日志/退出码、覆盖率与适用变异结果、追溯及漂移检查证据；不得仅凭实现者总结评审。
2. **逐 Gate 给出 QA 判断**：每项记录 `SUPPORTED` / `NEEDS_WORK` / `INCONCLUSIVE`、证据定位、反例搜索、集合对账、残余风险与未验证范围。风险排序用于分配审查深度，不能跳过强制项；遇到条件项，先核对契约是否允许 N/A 及其依据。受工具或环境限制无法验证时如实记录，不以推测补齐结果。
3. **按原契约形成正式结论**：QA 总体 `SUPPORTED` 不直接等于交付 PASS。只有全部必做项证据充分、机械检查通过且证据对应冻结版本，才由评审角色逐项写入 `delivery-review.md`；`NEEDS_WORK` 对应 Gate FAIL 并记录修复 owner。`INCONCLUSIVE` 不得映射为 PASS 或 N/A：实际验收缺少必需证据按原契约记 FAIL；尚未执行的评审保持 PENDING。保存失败后按既有回流处理，修复或证据变化后完整重验。

直接在现有 `delivery-review.md` 中保留上述依据，不额外建立一套 QA 放行状态或重复审查轮次。

```markdown
## Phase 3 验证门控

### BRD / Strict TRD 完整 TDD 验证
- [ ] 所有单元测试代码遵循 ease-testing 规范（模板/MC-DC/AAA/FIRST/Mock 策略）；GREEN 后已用 ease-testing 分轮流程补强覆盖率
- [ ] 每个方法经历了完整的 RED → 验证RED → GREEN → 验证GREEN → REFACTOR 循环
- [ ] RED 阶段确认失败原因是"功能缺失"（非语法/拼写错误）
- [ ] 所有测试通过且输出干净（无错误、无警告）
- [ ] 覆盖率达标：行 ≥ 80%，分支 ≥ 70%，方法 ≥ 85%
- [ ] 断言价值门禁通过：每个测试最高有效断言等级 ≥ L2；允许辅助 L1，但不存在仅 L0/L1 的测试
- [ ] 确定性隔离 D-Gate 通过：D1–D9 机械 lint 与人工检查均无阻断项
- [ ] 核心方法变异冒烟通过：每个核心业务方法至少有 1 个变异被测试杀死

### Lite / Standard TRD 比例门禁
- [ ] 已读取并记录 `TRD_RISK_PROFILE`
- [ ] Lite：失败复现/变更前基线、相关回归、构建/静态检查、兼容验证均有证据；修改生产逻辑时仍对变更行为执行 TDD
- [ ] Lite：未新增/修改核心方法时，覆盖率、D-Gate、变异冒烟以 `N/A + 理由` 记录；一旦触及对应风险立即恢复门禁
- [ ] Standard：新增/修改行为已执行 TDD并验证适用覆盖率；触及外部资源时 D-Gate 通过；新增/修改核心方法已通过变异冒烟
- [ ] Strict：D-Gate 与变异冒烟不得按 Lite/Standard 理由省略；完整门禁、灰度和回滚演练均通过

### 代码质量
- [ ] 所有 TODO 标记已删除（全新开发）或增量标记已清理（增量开发）
- [ ] 无死代码残留（未使用的 import、不可达分支、注释掉的代码块）
- [ ] 错误处理与设计文档一致
- [ ] 日志记录完整且不包含敏感信息

### 范围纪律验证
- [ ] 仅修改了任务范围内的文件（检查 git diff）
- [ ] 无"顺手清理"的无关变更
- [ ] 如有范围外的发现，已记录为独立任务而非混入本次提交

### 架构一致性
- [ ] 架构文档漂移检查已执行（如 metadata.json 存在）
- [ ] 实现与权威设计一致（BRD：arch-design/detail-design；TRD：solution-design）
- [ ] 未引入设计文档之外的架构模式或依赖

### 增量变动实现（仅 `REQUIREMENT_MODE=incremental-domain`）
- [ ] `REQUIREMENT_MODE` 已检测并判定为 `incremental-domain`（步骤 1.4）
- [ ] 实现按变动优先级排序：先 `[Δ-NEW]`，后 `[Δ-MOD]`（步骤 4.0）
- [ ] 所有 `[Δ-MOD]` 的实现已通过 Chesterton's Fence 检查（理解原始实现意图）
- [ ] 所有 `[Δ-MOD]` 的实现已执行回归测试且全部通过（无现有功能破坏）
- [ ] 代码注释中保留了 `[Δ-NEW]`/`[Δ-MOD]` 标记（Javadoc 级别，作为持久化变动记录）
- [ ] 实现总结报告包含"变动实现统计"章节（步骤 7）
- [ ] git commit message 包含变动标记和关联 UC/BR（推荐）

### 可追溯性
- [ ] 实现总结报告已生成（BRD：`.eases/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`；TRD：`.eases/trd/${CHANGE_ID}/flow-3-implement/outputs/implementation-summary.md`）
- [ ] 已消费权威任务列表（Phase 2 `flow-2-design/tasks.md` 或 TRD `flow-1-analyze-trd/tasks.md`）并就地回写进度（完成项标记 `[X]`）
- [ ] **未重新生成** spec/plan/tasks（Phase 3 不重跑 specify，保持单一事实来源）
- [ ] `${IMPLEMENTATION_ARTIFACT_DIR}/checklists/` 下实现校验清单完整

### 领域一致性（BRD 强制；纯技术 TRD 可 N/A）
- [ ] `domain-implementation-alignment.json` 已生成并通过确定性校验
- [ ] 本次变更 UC/BR 的代码证据与测试证据覆盖率均为 100%
- [ ] 不存在孤儿、废弃或未知 UC/BR 引用
- [ ] 不存在未解决的领域漂移；业务语义变化已回流 Flow 1，而非在实现阶段静默修文档

### 阻断条件
如果任一门控未通过，必须：
1. 列出未通过的门控项
2. 说明缺失的具体内容
3. 回到对应步骤补充
4. 重新验证所有门控

**三阶段流程的验证门控至此完整闭环：Phase 1 → Phase 2 → Phase 3。**
```

### 步骤 9.7：ADR Implementation Evidence 补充（重大架构变更时执行）

> **前提**：本步骤仅在 flow-2-design 已在 `docs/adr/` 下创建 ADR 文件时执行。若无关联 ADR，跳过。

**执行步骤**：

1. 检查 `docs/adr/` 下是否存在与本次实现关联的 ADR 文件（通过 change_refs、适用组件/契约和 scope 显式关联；不根据 ADR 编号猜测功能编号）
2. 如存在，更新该 ADR 的 `## Implementation Evidence` 部分：
   - **Actual Implementation**：实际代码实现方式（文件路径、关键类/方法）
   - **Deviations from Design**：实现与设计的偏差及原因（无偏差则注明"实现与设计一致"）
   - **Runtime Data**：运行时数据（性能指标、测试覆盖率、构建状态等，如可用）
   - **Implementation Date**：当前日期
3. 不因实现完成将 `Proposed` 改为 `Accepted`；Accepted 只能依据可追溯批准记录。另记 realization_status 与快照证据。
4. **不修改已有 ADR 的决策内容**，仅补充 Implementation Evidence；替代决策回架构设计创建新 ADR。

### 步骤 9.7.1：DDR Implementation Evidence 补充（存在关联 DDR 时执行）

1. 从 `domain-alignment.json` 的 `decision_refs` 定位本次 UC/BR 关联 DDR。
2. 仅更新 DDR 的 `Implementation Evidence`：实际代码/测试路径、与领域决策的偏差、验证结果和日期。
3. 不修改 Context、Decision 或 Business Rationale；若实现证明业务决策本身需要变化，必须回到 Flow 1 新建替代 DDR，并用 `Supersedes` 连接历史。

## 输出位置

所有输出文件必须严格遵循以下目录结构：

```
.eases/
├── ${CHANGE_ID}/                                # BRD 单次变更
│   ├── flow-2-design/                           # ← 权威 spec/plan/tasks（新目录）
│   │   └── tasks.md                             #   Phase 3 就地把完成项标记为 [X]
│   └── flow-3-implement/
│       ├── outputs/implementation-summary.md    # 本次实现过程总结
│       └── checklists/
│           ├── implementation.md                # 实现质量清单
│           └── domain-implementation-alignment.json # UC/BR → 代码/测试证据
└── trd/${CHANGE_ID}/                            # TRD 单次变更
    ├── flow-1-analyze-trd/tasks.md              # ← 权威任务列表
    └── flow-3-implement/
        ├── outputs/implementation-summary.md
        └── checklists/implementation.md
```

旧项目仅在新路径不存在时只读兼容历史 `docs` 实现总结；新执行禁止继续创建或双写这些文件。

> ⚠️ **不再在 `flow-3-implement/` 下生成 spec.md / plan.md / tasks.md**。BRD 权威来源是 Phase 2 的 `flow-2-design/`（旧项目可只读兼容 `design/`）；TRD 权威来源是 Phase 1 的 `TRD.md`、`solution-design.md`、`tasks.md`，无需 spec.md / plan.md。Phase 3 只消费并回写权威 `tasks.md`。

## 重要提示

- **首次使用必须创建 constitution.md**（不可协商）
- **单元测试代码必须严格遵循 ease-testing 技能的规范（不可协商）**：模板、MC/DC 覆盖、AAA、FIRST、Mock 策略均以 ease-testing 为准。RED 阶段按规范编写失败测试（无源码可逆向）；GREEN 后用 ease-testing 的分轮白盒流程补强覆盖率；有 test-case-document.md 时优先按案例编写。
- **TDD 必须严格执行**（不可协商）：
  - 没有先失败的测试，就不要写生产代码
  - 在写测试之前就写了代码？删掉它，从头开始
  - 测试一上来就通过？测试写错了，修正测试
  - 跳过验证 RED/GREEN 阶段？停止，重新开始
- **优先级**: 简单方案优于复杂方案，避免过度设计
- **安全第一**: 所有实现必须考虑安全性，防止常见漏洞
- **代码可读**: 代码应自解释，必要时添加注释说明设计决策
- **错误处理**: 使用自定义异常和全局异常处理机制
- **日志完善**: 在关键业务节点添加日志，便于问题排查
- **遵循规范**: 严格遵循项目已有的代码风格和架构模式
- **使用 UTF-8**: 所有文件使用 UTF-8 字符集
- **消费权威产物，不重跑前置生命周期**（不可协商）：BRD 消费 Phase 2 spec/plan/tasks；TRD 消费 TRD.md/solution-design.md/tasks.md，并就地回写任务进度
- **增量领域必须按变动标记实现并保留记录**（不可协商）：
  - 通过步骤 1.4 检测 `REQUIREMENT_MODE`（new-domain / incremental-domain）
  - 当 `incremental-domain` 时，按 `[Δ-NEW]` → `[Δ-MOD]` 优先级实现（步骤 4.0）
  - 实现后保留 Javadoc 级 `[Δ-NEW]`/`[Δ-MOD]` 标记（步骤 5.5.1）
  - 实现总结报告包含"变动实现统计"（步骤 7）
  - **git commit message 包含变动标记**（推荐）：
    ```
    feat([domain]): [Δ-MOD] [简述]

    UC-XXX [Δ-MOD]: [变更说明]
    BR-XXX [Δ-NEW]: [新增规则说明]

    变更点：
    - [类.方法] [变更描述]

    关联 delta-analysis: .eases/${CHANGE_ID}/flow-1-analyze/delta-analysis.md
    ```

## 检查清单

在开始实现前，根据来源路径与开发模式确认以下事项：

### 通用检查项（所有路径）：
- [ ] 已检查/创建 `memory/constitution.md`
- [ ] 已解析并锁定 `TRACK + FEATURE_NAME`
- [ ] 已按路径定位权威链（BRD：spec/plan/tasks；TRD：TRD/solution-design/tasks）
- [ ] 已理解需求、设计约束和验收标准
- [ ] 已按项目实际语言/框架配置开发环境并加载对应编码规范

### BRD 路径检查项（`SOURCE_PATH=brd`）：
- [ ] 已执行 `/ease:flow-2-design` 并生成设计输出
- [ ] 已阅读 `arch-design.md`、`detail-design.md` 与测试案例

### TRD 路径检查项（`SOURCE_PATH=trd`）：
- [ ] 已阅读 `${TRD_SOURCE_DIR}/TRD.md`
- [ ] 已阅读 `${TRD_SOURCE_DIR}/artifacts/solution-design.md`
- [ ] 已确认 `${TRD_SOURCE_DIR}/tasks.md` 是权威任务列表
- [ ] 已确认 TRD 无需 `spec.md` / `plan.md`，未用其缺失作为阻断条件
- [ ] 未要求 TRD 路径提供 BRD 专属的 Flow 2 目录、框架代码或注释 manifest

### TDD 检查项（不可协商，遵循 `test-driven-development` + `ease-testing` skill）：
- [ ] **已确认：所有单元测试代码将严格遵循 `ease-testing` 技能的规范（模板/MC-DC/AAA/FIRST/Mock）**——RED 阶段按规范编写，GREEN 后用分轮白盒流程补强覆盖率
- [ ] 已定位现有测试；若上游提供 `test-framework-manifest.md` 则已读取，否则从首个 RED 测试开始
- [ ] 已理解 TDD 红-绿-重构循环
- [ ] 已阅读 `ease-testing` skill 的语言参考文档
- [ ] 已理解 MC/DC 覆盖原则和 AAA 模式
- [ ] 已理解 Mock 策略（资源层不 Mock，外部服务 Mock）
- [ ] 已准备好运行测试的命令（`npm test` / `mvn test` / `./gradlew test`）
- [ ] 已承诺：不写没有测试的代码，不跳过验证步骤

### BRD 增量开发模式检查项（`SOURCE_PATH=brd && DEVELOPMENT_MODE=incremental`）：
- [ ] 已检测到代码注释清单（`code-annotation-manifest.md`）
- [ ] 已在项目代码中找到TODO注释
- [ ] 已理解现有代码结构和需要修改的位置
- [ ] 已制定增量开发测试策略（确保现有功能不受影响）
- [ ] 已为新增功能准备测试（或定位现有测试）

### BRD 全新开发模式检查项（`SOURCE_PATH=brd && DEVELOPMENT_MODE=new`）：
- [ ] 已检测到框架代码目录（`framework-code/`）
- [ ] 框架代码包含详细的注释和 `TODO` 标记
- [ ] 已分析框架代码清单（`framework-code-manifest.md`）
- [ ] 已确认测试框架代码存在（`src/test/` 目录）
- [ ] 已确定实现顺序和依赖关系（先测试，后实现）

### 增量领域变动检查项（`REQUIREMENT_MODE=incremental-domain`）：
- [ ] 已检测到 `delta-analysis.md` 并理解 UC/BR 变动明细
- [ ] 已阅读 arch-design.md / detail-design.md 中 `[Δ-MOD]` 标记的章节
- [ ] 已按变动优先级排序实现任务（先 `[Δ-NEW]`，后 `[Δ-MOD]`）
- [ ] 已为每个 `[Δ-MOD]` 任务建立回归测试绿色基线
- [ ] 已确认理解被修改代码的原始实现意图（Chesterton's Fence）
- [ ] 将在实现后保留 `[Δ-NEW]`/`[Δ-MOD]` 的 Javadoc 标记
- [ ] 将在实现总结报告中填写"变动实现统计"

## 反理性化表 (Common Rationalizations)

在实现过程中，Agent 容易陷入以下"自我合理化"陷阱：

| 合理化借口 | 现实 |
|---|---|
| "这个改动太小了，不用写测试" | 小改动也会坏。30 秒写完一个测试的代价远小于"它悄悄坏了三个月才发现"的代价。TDD 铁律没有例外条款。 |
| "代码已经自解释，不需要删除TODO注释" | 保留已实现的 TODO 注释是技术债务。下一个读者会浪费 30 秒判断"这个 TODO 完成了吗？"——乘以 100 次阅读就是半个工作日。 |
| "我只是顺便修一下隔壁文件的格式问题" | 范围纪律（Range Discipline）：只触碰任务要求的代码。顺手修格式制造 diff 噪声，增加 review 负担，且可能引入意外回归。如有值得修的问题，记录并提交独立 PR。 |
| "重构放在 RED 之前做更高效" | TDD 循环顺序不可颠倒：RED → GREEN → REFACTOR。在测试通过前重构是"在黑暗中改代码"——不知道改对了还是改坏了。 |
| "这个 Optional/Optional 判断多层嵌套太复杂？我能看懂就行" | 如果连你自己都需要"想一想"才能看懂，下一个读者需要三倍时间。清晰优于聪明。20 行的显式 if/else 优于 5 行的嵌套三元表达式链。 |
| "日志太多了，上线后会影响性能" | 结构化日志的成本在微秒级，而缺少日志导致的一次线上故障排查成本在小时级。只删除包含敏感信息的日志（密码、令牌、PII），其余保留。 |
| "测试失败是因为测试写得不对，我应该改测试" | 如果代码是你刚写的，测试失败大概率是你代码的问题。先假设代码有错，三思之后再怀疑测试。如果改测试，确认它在 RED 阶段确实失败了。 |
| "已经试了 3 次了，再试一次也许就对了" | 第 4 次盲目尝试是低效调试的核心特征。3 次失败 = 触发系统性调试流程（systematic-debugging）。停止猜测，开始诊断。 |
| "CI/CD 的总行覆盖率只要求 80%，这个分支不测了" | 覆盖率门槛是底线不是目标。关键分支（如支付、权限、数据删除）的未覆盖路径是生产事故的定时炸弹。用 MC/DC 原则判断，而非只盯数字。 |
| "这只是修改已有 UC 的一个小变动，不用管变动标记和回归测试" | `[Δ-MOD]` 的修改是增量开发中回归 bug 的首要来源。跳过回归测试 = 把现有功能当赌注。每改一个 `[Δ-MOD]`，立即跑受影响的已有测试。delta-analysis.md 和 `[Δ-NEW]`/`[Δ-MOD]` 标记是未来迭代的导航图，不是负担。 |

## TDD 危险信号

出现以下任何情况，**立即停止并重新开始**：

| 危险信号 | 正确做法 |
|----------|----------|
| **脱离 ease-testing 规范编写测试（无视模板/MC-DC/AAA/Mock 策略）** | **对照 ease-testing 的模板与覆盖原则重写测试** |
| **GREEN 后未用 ease-testing 分轮流程补强覆盖率** | **调用 ease-testing 白盒流程补全 MC/DC 缺口** |
| 在写测试之前就写了代码 | 删掉代码，先写测试 |
| 测试一上来就通过 | 测试写错了，修正测试 |
| 跳过"看着测试失败"步骤 | 必须运行测试并确认失败 |
| 说"就这一次跳过 TDD" | 这是自我合理化，坚持 TDD |
| "太简单，不用测" | 简单代码也会坏，写测试只要 30 秒 |
| "我之后再补测试" | 后补的测试证明不了任何东西 |
| "先留着代码当参考" | 删除就是删除，不要看它 |
| "删掉 X 小时的工作太浪费" | 沉没成本谬误，保留未验证代码是技术债务 |
| 编译错误尝试 3+ 次修复仍失败 | **停止猜测，调用 `systematic-debugging` 技能** |
| 测试失败原因不明，盲目改代码 | **系统性调试优先，先定位根因再修复** |
| "再试一个修复看看" | 3 次失败即触发系统性调试，禁止第 4 次盲目尝试 |

## 错误处理

### 如果未找到 constitution.md

```
❌ 错误: 未找到 memory/constitution.md

请先执行 reference/project-constitution.md 创建项目宪章。
```

### 如果未找到待实现代码（BRD 开发模式）

#### BRD 增量开发模式错误：
```
⚠️ 错误: 未找到代码注释或注释信息不足

请先执行以下命令进行设计并添加代码注释:
/ease:flow-2-design [用例文档路径]

该命令将：
1. 分析现有代码结构，找到需要修改的位置
2. 在现有代码中添加包含用例引用和规则映射的TODO注释
3. 生成代码注释清单

添加代码注释后，再执行此命令进行详细实现。
```

#### BRD 全新开发模式错误：
```
⚠️ 错误: 未找到框架代码或注释信息不足

请先执行以下命令进行设计并生成框架代码:
/ease:flow-2-design [用例文档路径]

该命令将：
1. 生成架构设计和详细设计文档
2. 创建完整的框架代码骨架
3. 在框架代码中添加详细的TODO注释

生成框架代码后，再执行此命令进行详细实现。
```

### 如果缺少设计文档

```
⚠️ 警告: 未找到设计文档

BRD：返回 /ease:flow-2-design，补齐 arch-design.md / detail-design.md。
TRD：返回 /ease:flow-1-analyze-trd，补齐 TRD.md / artifacts/solution-design.md。
设计是阻断条件，不得仅凭零散注释继续实现。
```

### 如果编译错误或运行异常无法解决

当代码实现过程中遇到以下情况时，**必须调用 `systematic-debugging` 技能**：

1. **编译错误无法解决**：
   - 依赖冲突、类型不匹配、找不到符号等错误
   - 尝试 2-3 次修复仍无法通过编译

2. **运行时异常难以定位**：
   - 空指针异常、类型转换异常、资源未找到等
   - 堆栈信息指向的位置与预期不符

3. **测试失败原因不明**：
   - 测试失败但错误信息不清晰
   - 多个测试同时失败且原因相互关联

```
⚠️ 触发系统性调试: 编译/运行异常多次修复失败

当前问题: [问题描述]
已尝试修复: [修复尝试次数]

调用 systematic-debugging 技能进行系统性根因分析：
- Phase 1: 根本原因调查（仔细阅读错误、稳定复现、检查变更）
- Phase 2: 模式分析（找到工作示例、识别差异）
- Phase 3: 假设与实验（形成假设、最小化验证）
- Phase 4: 最小修复（只修复根因，验证后完成）

参考: plugins/ease-tools/skills/systematic-debugging/SKILL.md
```

**铁律**：没有根本原因调查就没有修复。禁止在不理解问题的情况下继续尝试"碰运气"的修复。
