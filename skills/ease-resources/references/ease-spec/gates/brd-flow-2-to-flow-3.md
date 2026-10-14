# BRD Flow 2 → Flow 3 准入契约

Flow 2 提交候选证据，Flow 3 在写任何实现代码或测试前执行只读准入。所有 Gate 必做；标注“按模式”的 Gate 只能按契约选择适用分支，不能省略整项。

| Gate ID | 必须验证的内容 | 反证与集合对账 | 失败回流 |
|---|---|---|---|
| F2-ART-01 | arch/detail/API 报告全部章节、owner、风险、迁移、回滚和 handoff 完整 | 逐工件寻找空章节、占位符、无 owner 或无失败语义的反例 | Flow 2 设计工件 |
| F2-ADR-01 | 每个重大决策比较≥2方案，含证据、风险、可逆性、ADR及追溯 | `重大决策集合 = ADR/等价记录集合` | Flow 2 决策设计 |
| F2-NFR-01 | 每项 NFR 有量化目标与验证方法 | `NFR 需求集合 = 设计响应集合 = 验证计划集合` | Flow 2 NFR 设计 |
| F2-DELTA-01 | 增量摘要、接口/流程/数据/TODO 的 Δ 标记与 Flow 1 一致 | `Flow 1 Δ 集合 = 设计 Δ 集合 = 代码定位 Δ 集合` | Flow 2 增量设计 |
| F2-CLR-01 | 入口决策、clarify、用例冲突、场景分类和低置信度人工确认均完成 | 开放架构决策集合必须为空 | Flow 2 澄清 |
| F2-ENV-01 | 独立 GitFlow 特性分支及工作目录已验证 | 查找错误分支、错误 worktree 或身份不一致 | Flow 2 环境准备 |
| F2-MODE-01 | new：可编译骨架、UC/BR TODO、失败测试骨架和 manifests 完整；incremental：精准 code mapping、TODO、manifest、Chesterton 与兼容分析完整 | 按模式列出目标符号全集并逐一对账 | Flow 2 框架/注释生成 |
| F2-TRC-01 | ≥80% 设计要点追溯；NEW/MOD UC/BR 设计覆盖100%；无孤儿/废弃引用；生命周期完整 | `NEW/MOD UC/BR = design matrix`；`设计项 = UC/BR/NFR 来源项` | Flow 2 追溯设计 |
| F2-TST-01 | 测试文档、UC/BR 映射、≥2技术、风险优先级、接口覆盖与分层案例全部合格 | `API 报告接口集合 = testcase 接口集合` 双向相等 | Flow 2 测试设计 |
| F2-SEM-01 | Flow 2 未静默改变业务事实 | 对比 Flow 1 基线与设计语义；发现变化以 F1-SEM-01 回流 | BRD Flow 1 |

Flow 2 的 `gate-submission.md` 只能写 `READY_FOR_ADMISSION`。Flow 3 的 `admission-flow-2.md` 全部 PASS 后才能进入 TDD RED；任何缺设计情况均无三阶段内部豁免。

## TC 与架构证据补充验收

按 `ease-test-case-design/references/durable-test-assets.md` 验证 selection 与长期 TC，反向从本次 UC/BR/接口/适用架构约束恢复 obligations 全集。高风险义务没有案例或验证缺口未处理不得 PASS。新任务执行 manage_test_assets.py；旧任务显式兼容旧案例来源。Flow 3 另对账当前执行快照、案例 revision/hash 和真实运行证据，不能把转交或跳过当通过。

ADR 实现证据与 decision_findings 必须在最后只读验收之前冻结；生效 ADR 冲突和缺证据不得被普通文档过期提醒替代。已验收的案例、设计或证据变化恢复 PENDING。

## E2E 条件验收

按 `../reference/e2e-integration.md` 执行：未接入仅保留 docs 下的去重接入 TRD，不增加 E2E 门禁或 N/A 工件；已接入只验收本次选择的场景。设计核对范围、断言与执行条件，交付核对真实逐例结果及当前版本证据。必选案例 blocked/skipped 不算 PASS；只读验收不得补写提醒或测试资产。接入提醒路径作为明确允许的治理输出参与范围核对。
