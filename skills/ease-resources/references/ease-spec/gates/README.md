# 三阶段门禁证明协议

本目录是 Ease 三阶段 Flow 的**放行语义权威依据**。`stage-contract.md` 继续管理路径、连接键与阈值；本目录只规定谁有权放行、如何验收、证据何时失效以及失败回流到哪里。

## 1. 门禁所有权

- **生产者不得给自己的阶段授予 PASS**。Flow 1/2 完成生产后只能写 `gate-submission.md`，状态为 `READY_FOR_ADMISSION`；Flow 3 完成实现后只能写 `delivery-submission.md`。
- **消费者拥有准入决定权**：Flow 2 以只读验收决定是否接收 BRD Flow 1；Flow 3 以只读验收决定是否接收 BRD Flow 2 或 TRD Flow 1。
- 最终交付由 Flow 3 的独立只读 delivery review 决定。生产步骤和验收步骤不得混合为一次自检。
- `starter` 只编排、读取和汇总消费者结论，不得重新解释、删减或覆盖 Gate ID。

## 2. 两遍执行

1. **生产遍**：生成或修复产物；所有 Gate 保持 `PENDING`，只提交候选证据。
2. **只读验收遍**：冻结被验收产物，不得边审边改。逐项执行反证检查和集合对账，记录 `PASS` 或 `FAIL`。
3. 发现问题时先保存失败记录，再退出验收、回到指定 owner 修复；修复后必须重新执行完整验收遍。

## 3. 状态与证据

允许的状态只有：

- `PENDING`：尚未完成独立验收；默认状态。
- `READY_FOR_ADMISSION`：生产者已提交证据，但尚未获准进入下游。
- `PASS`：消费者完成只读反证审查，没有发现反例。
- `FAIL`：发现至少一个反例、集合差异、缺失证据或冲突。
- `N/A`：**仅允许门禁契约显式标注的条件项使用**，必须同时记录适用规则与反证事实；其他 Gate 不得自行降级为 N/A。

`基本通过`、`有条件通过`、空白状态和批量勾选均无效。每项 PASS 必须包含当前 `CHANGE_ID` 的可检查证据：文档使用“路径 + 章节/条目”，代码使用“路径 + 符号”，运行结果使用“命令 + 退出码 + 关键结果”。仅写“文件存在”不能证明内容门禁通过。

## 4. 反证与双向集合对账

验收者必须主动寻找一个足以推翻 PASS 的反例，并记录“检查对象全集、发现的反例、结论”。覆盖性门禁必须执行**双向集合对账**：

- `上游全集 - 下游证据集合` 必须为空，防止漏做；
- `下游证据集合 - 上游授权全集` 必须为空，防止擅自扩展。

若无法列出验收对象全集，就不能声称 100% 覆盖。

## 5. 证据新鲜度

每份提交和验收记录必须包含：`change_id`、`domain_id`（TRD 可空）、`track`、`requirement_source`、当前 Git HEAD（无 Git 时记录 `NO_GIT + 理由`）、被验收产物路径、当前 NEW/MOD UC/BR 集合，以及本次使用的运行证据时间。

被验收的需求、设计、代码、测试或权威任务发生变化后，相关旧结论立即恢复为 `PENDING`。测试必须晚于最后一次相关代码修改；不同 `CHANGE_ID` 的报告不得复用。

## 6. 失败回流

每个 Gate ID 只有一个权威 owner，并且只有一个**唯一回流**位置：

- `F1-*` → 对应 Flow 1；
- `F2-*` → Flow 2；
- `F3-*` → Flow 3；
- 在 Flow 2/3 发现 Actor、业务流程、验收标准或业务规则改变时，以 `F1-SEM-01` 回流 BRD Flow 1，不能在下游顺手修改领域事实。

验收者只能报告上游缺陷，不得静默修复上游权威产物。回流必须保留失败 Gate ID、反例、证据和修复后的重验结果。

## 7. 记录路径

| 路径 | 生产者提交 | 消费者验收 |
|---|---|---|
| BRD Flow 1 → Flow 2 | `flow-1-analyze/checklists/gate-submission.md` | `flow-2-design/checklists/admission-flow-1.md` |
| BRD Flow 2 → Flow 3 | `flow-2-design/checklists/gate-submission.md` | `flow-3-implement/checklists/admission-flow-2.md` |
| TRD Flow 1 → Flow 3 | `flow-1-analyze-trd/checklists/gate-submission.md` | `flow-3-implement/checklists/admission-flow-1-trd.md` |
| Flow 3 → 交付 | `flow-3-implement/checklists/delivery-submission.md` | `flow-3-implement/checklists/delivery-review.md` |
