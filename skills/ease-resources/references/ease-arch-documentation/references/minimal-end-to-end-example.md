## Minimal End-to-End Example

本示例用于说明“首次生成 vs 增量更新”的最小闭环（不依赖真实仓库）。

### First run（首次全量生成）

1. **构建索引**：先生成 topology，再按证据生成基础索引和任务需要的 runtime/integration/security 等架构索引；缺失项写入 `coverage_gaps`。
2. **深度分析**：从 topology 和事实索引派生关键路径、不变量、质量属性场景、故障传播与演进热点，并记录 `derived_from`。
3. **生成文档**：按顺序产出 01-06 六份文档。
4. **质量门禁**：运行 `references/quality-gates.md` 中的机械门禁和架构深度语义门禁。
5. **落盘记忆**：写入 `metadata.json.last_generation.commit_id` + `generation_trace`（如实现）。

### Incremental run（增量更新）

输入：`metadata.json.last_generation.commit_id` 到 `HEAD` 的 diff。

1. diff 只包含接口入口文件 → 更新 `api_index`；若协议、安全或调用关系变化，同时更新 `integration_index`/`security_index`。
2. 重算受变更 claim 影响的关键路径和故障传播 → 更新 `03_API_INTERFACE.md` 及被语义影响的拓扑或模块文档。
3. 质量门禁：执行 API 索引对齐 + 随机反向验证。

### Failure fallback（失败回退）

当无法可靠收敛更新范围（例如大规模重构/目录迁移）时：

- 退化为“全量重建索引 + 受影响文档全量更新”。
