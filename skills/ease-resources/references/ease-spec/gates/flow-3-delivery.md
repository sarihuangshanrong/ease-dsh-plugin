# Flow 3 交付门禁契约

实现步骤只能提交 `delivery-submission.md`。随后切换到只读 delivery review，冻结代码和测试，将权威结论写入 `delivery-review.md`。

| Gate ID | 必须验证的内容 | 反证与集合对账 | 失败回流 |
|---|---|---|---|
| F3-TDD-01 | BRD/Strict 完整 TDD；Lite/Standard 按风险比例执行并提供合法 N/A 依据 | 逐变更行为检查 RED 原因、GREEN、重构及证据时序 | Flow 3 TDD |
| F3-TST-01 | 测试全绿、输出干净、覆盖率、L2、D-Gate、核心方法变异冒烟满足适用规则 | 寻找仅 L0/L1、非确定性、未杀死变异、阈值不足或旧报告 | Flow 3 测试补强 |
| F3-QLT-01 | TODO/死代码清理，错误处理、日志和敏感信息合规 | 扫描并逐反例审查 | Flow 3 实现 |
| F3-SCP-01 | git diff 仅含任务范围，无顺手修改 | `实际变更文件/符号集合 - 设计授权集合 = ∅` | Flow 3 范围修复 |
| F3-ARC-01 | 实现与权威设计一致，无未授权模式/依赖，文档漂移已处理 | `实现组件/接口/依赖集合 - 设计集合 = ∅` | Flow 2；纯实现偏差回 Flow 3 |
| F3-DELTA-01 | 增量优先级、Chesterton、回归、持久 Δ 标记和统计完整 | `设计 Δ 集合 = 实现 Δ 集合` | Flow 3 增量实现 |
| F3-TASK-01 | 权威 tasks 全部有真实完成证据；未重生 spec/plan/tasks；总结与清单完整 | `权威任务集合 = 有完成证据任务集合` | Flow 3 任务执行 |
| F3-TRC-01 | NEW/MOD UC/BR 的设计、代码、测试证据均100%，无孤儿/废弃/未知引用 | `NEW/MOD 集合 = design refs = code refs = test refs` | Flow 3；业务事实问题回 Flow 1 |
| F3-DRIFT-01 | 不存在未解决领域漂移或静默业务语义变化 | 主动比较需求、设计、diff 与语义裁决 | BRD Flow 1 |
| F3-RLS-01 | TRD 风险要求的兼容、灰度、观测、回滚证据完整 | `风险集合 = 缓解/验证/回滚集合` | TRD Flow 1 设计缺陷；否则 Flow 3 |

只有全部必做 Gate 为 PASS，且契约明确允许的条件项具有可验证 N/A 理由时，才能宣告交付完成。任何被验收代码、测试或任务状态变化都会使 `delivery-review.md` 恢复 PENDING。

## TC 与架构证据补充验收

按 `ease-test-case-design/references/durable-test-assets.md` 验证 selection 与长期 TC，反向从本次 UC/BR/接口/适用架构约束恢复 obligations 全集。高风险义务没有案例或验证缺口未处理不得 PASS。新任务执行 manage_test_assets.py；旧任务显式兼容旧案例来源。Flow 3 另对账当前执行快照、案例 revision/hash 和真实运行证据，不能把转交或跳过当通过。

ADR 实现证据与 decision_findings 必须在最后只读验收之前冻结；生效 ADR 冲突和缺证据不得被普通文档过期提醒替代。已验收的案例、设计或证据变化恢复 PENDING。

## E2E 条件验收

按 `../reference/e2e-integration.md` 执行：未接入仅保留 docs 下的去重接入 TRD，不增加 E2E 门禁或 N/A 工件；已接入只验收本次选择的场景。设计核对范围、断言与执行条件，交付核对真实逐例结果及当前版本证据。必选案例 blocked/skipped 不算 PASS；只读验收不得补写提醒或测试资产。接入提醒路径作为明确允许的治理输出参与范围核对。
