# BRD Flow 1 → Flow 2 准入契约

Flow 1 提交候选证据，Flow 2 在首次创建设计工件前执行只读准入。以下所有 Gate 均为必做且不可 N/A；增量专属 Gate 仅当 `REQUIREMENT_MODE=incremental-domain` 时启用。

| Gate ID | 必须验证的内容 | 反证与集合对账 | 失败回流 |
|---|---|---|---|
| F1-ENV-01 | 宪章存在并包含 MUST/SHOULD；领域目录结构合规 | 找出缺失原则或非法目录 | Flow 1 环境初始化 |
| F1-DOM-01 | 核心/支撑/通用域、限界上下文、上下文映射、聚合根/实体/值对象、统一语言均完成 | 逐项列出领域建模全集，任一缺失即失败 | Flow 1 领域分析 |
| F1-REQ-01 | 每个用例有 Actor、Goal、主成功路径、异常/边界；每条规则可验证；成功标准可量化 | 逐 UC/BR 寻找模糊、无 Actor、无失败路径或主观指标的反例 | Flow 1 用例分析 |
| F1-TRC-01 | `context.json` 有效；分析报告索引完整；specify→plan→tasks 完整且文件非空 | `子领域/UC 文档集合 = 报告索引集合`；生命周期产物逐一复核 | Flow 1 规格生命周期 |
| F1-BASE-01 | 领域基线有效；活动 UC/BR 来源、ID、状态、DDR 完整 | `本次 NEW/MOD 集合 = 基线 NEW/MOD 集合`，且无未知/重复/废弃误用 | Flow 1 领域基线 |
| F1-DELTA-01 | 增量模式、匹配领域、delta-analysis、MOD 前后/原因、规则历史、追加标记均完成 | `delta-analysis 变更集合 = 文档 Δ 标记集合 = 基线变更集合` | Flow 1 增量分析 |
| F1-SEM-01 | 阻断性歧义、假设和业务语义冲突已获得确认 | 列出开放问题全集；非空即失败 | Flow 1 需求拷问 |

Flow 1 的 `gate-submission.md` 只能写 `READY_FOR_ADMISSION`。Flow 2 的 `admission-flow-1.md` 必须逐 Gate 记录当前证据、尝试寻找的反例、集合差异和结论；全部 PASS 后才允许首次写设计工件。
