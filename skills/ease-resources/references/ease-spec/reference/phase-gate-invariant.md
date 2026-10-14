# 阶段门控不变式（Phase-Gate Invariant）

> 本文档是三阶段开发流程的**路径规则权威依据**。当需要判断"是否可以编码""是否可以跳过设计阶段"时，**以此为准**，并可在拒绝直接编码时引用本文档。
>
> 关联：`SKILL.md` Non-negotiables 第 7 项「路径不变式」；`commands/flow-1-analyze-brd.md`、`commands/flow-1-analyze-trd.md`、`agents/ease-agent.md`、`commands/flow-3-implement.md` 均反链本文档。

## 1. 为什么需要这条不变式

`/ease:flow-1-analyze-brd`（Phase 1）产出的领域模型、用例、业务规则，**只回答了"做什么"**，不含组件边界、接口契约、数据结构与实现步骤。直接基于 Phase 1 产物编码，会出现：

- 组件边界模糊 → 实现逐渐偏离设计意图；
- 接口契约缺失 → 跨用例冲突（数据模型/接口/状态机）无人裁决；
- Phase 3 返工成本约为先设计的 **10x**。

三阶段流程的真实泄漏往往不是"用户运行了错误的命令"，而是 **Phase 1 之后、Phase 2 产出缺失时，模型直接在对话里裸编码**（走 ease-coding 或 inline），绕过了 `/ease:flow-3-implement` 的门控。本不变式正是为了堵住这个泄漏面。

## 2. 双路径表（核心）

三阶段流程有两条路径，**设计阶段的归属不同**：

| 路径 | 入口命令 | 阶段序列 | 设计阶段归属 | 编码入口 |
|------|----------|----------|--------------|----------|
| **BRD**（业务需求） | `/ease:flow-1-analyze-brd` | 分析 → **设计** → 实现 | **独立、强制**（`/ease:flow-2-design`） | `/ease:flow-3-implement` |
| **TRD**（技术需求/NFR） | `/ease:flow-1-analyze-trd` | 分析 → 实现 | **内置于 Phase 1**（`solution-design` / 架构变更） | `/ease:flow-3-implement` |

> ⚠️ **关键区分**：TRD 路径**不经** `/ease:flow-2-design`，是因为 TRD 的方案设计在 Phase 1 内部已经完成（`TRD.md` + `solution-design.md`）。这是"设计已内置"，**不是"跳过设计"**。本不变式第 3 节的"缺设计不编码"规则**仅约束 BRD 路径**，不适用于 TRD 路径。

## 3. 核心规则（BRD 路径，不可协商）

1. **用例分析 ≠ 可编码。** Phase 1 仅产出领域模型 / 用例 / 业务规则 / spec·plan·tasks，**不含组件边界与接口契约**。
2. **设计阶段独立且强制。** BRD 路径必须经 `/ease:flow-2-design` 产出 `arch-design.md` / `detail-design.md` / 框架代码或代码注释后，方可进入编码。
3. **拒绝直接编码。** 在 Phase 1 产出已完成、Phase 2 产出**缺失**时，任何编码请求——含直接调用 ease-coding、对话内裸编码、`/ease:flow-3-implement`——都必须被阻断，并重定向到 `/ease:flow-2-design`。

### 3.1 判定流程（模型收到"编码"类请求时执行）

```
收到编码请求（"直接写吧"/"实现一下"/"开始 coding"…）
  │
  ├─ 当前在 TRD 路径？（flow-1-analyze-trd 产出 + solution-design 已完成）
  │     └─ 是 → 不受本规则约束，按 TRD 路径直连 flow-3-implement
  │
  ├─ 当前在 BRD 路径？
  │     ├─ Phase 2 产物存在（arch-design.md / detail-design.md / 框架代码或代码注释）？
  │     │     └─ 是 → 允许编码（引导 /ease:flow-3-implement）
  │     │     └─ 否 → 阻断，重定向到 /ease:flow-2-design
  │     │
  │     └─ 无法判定路径？
  │           └─ 先核验 .eases/${CHANGE_ID}/ 下产物，再判定；勿在未核验前编码
```

## 4. 流程切换，而非门禁豁免

三阶段 Flow 内不存在跳过强制阶段的 waiver。用户不希望继续完整三阶段时，可以**退出三阶段 Flow**并改用 `/ease:quick-develop` 或普通开发流程，但必须将当前运行记录为 `FLOW_ABORTED` 或 `PROCESS_CHANGED`；不得继续使用当前三阶段产物进入 Flow 3，也不得宣称阶段 PASS 或三阶段闭环。

这不是限制用户选择，而是保护流程语义：用户可以选择另一条流程，但不能降低这条流程的通过标准。

## 5. 各命令的执行点

| 位置 | 与本不变式的关系 |
|------|------------------|
| `commands/flow-1-analyze-brd.md` Step 7 | Phase 1 完成后，给出**唯一推荐下一步** `/ease:flow-2-design` + 可粘贴路径 + "用例分析 ≠ 可编码"告警 |
| `agents/ease-agent.md` 场景1 | 调度编码前核验 Phase 2 产物；缺失则禁止直接编码，引导 `/ease:flow-2-design` |
| `commands/flow-3-implement.md` 1.2.1 | Phase 1 & Phase 2 门控验证 = 本不变式的执行点；缺失 Phase 2 产物即阻断，并提示快速通道 |
| `commands/starter.md` Checkpoint 1/2/3 | 一键三阶段编排器在阶段间设置的阻塞检查点：每个阶段执行其自身门控（flow-1 末尾门控 / flow-2 §1.3.1+Phase 2 Gate / flow-3 §1.2.1+§9.6），未通过即 STOP，不进入下一阶段；BRD 路径缺设计同样拒绝推进至 Phase 3 |
| `commands/flow-1-analyze-trd.md` | TRD 路径例外说明（设计内置于 Phase 1，故直连 flow-3，不经 flow-2） |

## 6. 反理性化表（Common Rationalizations）

| 合理化借口 | 现实 |
|---|---|
| "用例已经够清楚了，直接写吧" | 用例不含组件边界与接口契约。跳过设计 = Phase 3 实现逐渐偏离意图，返工成本约 10x。 |
| "这只是个小改动，不用走完整设计" | 若确属琐碎改动（<200 行 / 单模块 / 无 API·数据模型变更），应由用户主动选择 `/ease:quick-develop`；一旦走上 BRD 路径，设计阶段不可省。 |
| "我在对话里直接写，又不走 flow-3，门控管不到我" | 这正是本不变式要堵的泄漏面。BRD 路径缺设计时，**任何**形式的编码（含对话内裸编码）都应被劝阻。 |
| "TRD 也跳过了 flow-2，BRD 为什么不能跳" | TRD 的方案设计**内置于 Phase 1**（solution-design），不是跳过设计。BRD 路径没有等价的内置设计产物。 |
| "用户催得急，先写代码再说" | 越急越不能跳设计——返工比先设计更慢。如不采用三阶段方法，应明确退出并切换流程。 |

## 7. 引用方式

拒绝直接编码时，引用本文档为依据：

> ⛔ BRD 路径缺设计不编码（见 `ease-spec/reference/phase-gate-invariant.md` §3 核心规则）。请先执行 `/ease:flow-2-design docs/domains/${DOMAIN_ID}/usecases/ --change-id=${CHANGE_ID}`；如不采用三阶段方法，请明确退出并切换流程（§4）。
