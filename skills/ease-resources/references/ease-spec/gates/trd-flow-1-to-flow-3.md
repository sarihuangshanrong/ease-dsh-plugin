# TRD Flow 1 → Flow 3 准入契约

TRD 的设计内置于 Flow 1。Flow 1 提交证据，Flow 3 在实现前只读验收；不得要求 BRD 的 spec/plan 或 Flow 2 产物。

| Gate ID | 必须验证的内容 | 反证与集合对账 | 失败回流 |
|---|---|---|---|
| T1-ID-01 | context、CHANGE_ID、track、需求来源一致 | 查找路径/身份错配和旧变更证据 | TRD Flow 1 初始化 |
| T1-REQ-01 | TRD 风险等级、范围、量化目标、基线和验收方式完整 | 寻找定性目标、缺失基线或不可执行验收 | TRD Flow 1 需求分析 |
| T1-DES-01 | solution-design 含模块/文件线索、方案、兼容、顺序、风险、回滚和验证 | `TRD 要求集合 = 设计响应集合 = tasks 集合` | TRD Flow 1 方案设计 |
| T1-TASK-01 | tasks 使用技术工作包、含路径/命令/证据/依赖且实现项初始未完成 | 查找 US/MVP 遗留、伪完成或无证据任务 | TRD Flow 1 tasks |
| T1-IMP-01 | Domain Impact Guard 内容有效且结果为 none | potential/confirmed 或理由不足即失败并转 BRD | BRD Flow 1 |
| T1-RISK-01 | Lite/Standard/Strict 与风险信号相符，高风险只升不降 | 数据迁移、安全、跨系统、不可逆、HA、事务/一致性、公共 API 任一信号均检查是否升级 Strict | TRD Flow 1 风险分级 |
| T1-MIG-01 | 历史 TRD 权威冲突和旧 tasks 已按规则迁移 | 寻找旧 spec/plan 与新权威冲突或无证据 `[X]` | TRD Flow 1 迁移 |

Flow 3 将结论写入 `admission-flow-1-trd.md`；全部 PASS 后才能实现。

## E2E 条件验收

按 `../reference/e2e-integration.md` 执行：未接入仅保留 docs 下的去重接入 TRD，不增加 E2E 门禁或 N/A 工件；已接入只验收本次选择的场景。设计核对范围、断言与执行条件，交付核对真实逐例结果及当前版本证据。必选案例 blocked/skipped 不算 PASS；只读验收不得补写提醒或测试资产。接入提醒路径作为明确允许的治理输出参与范围核对。
