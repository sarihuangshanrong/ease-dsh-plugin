# 架构文档生成路由
> 新生成以 [证据与决策强化契约](evidence-and-decision-contract.md) 的 2.2 快照、依赖闭包和独立语义验收为准；下文历史示例用于兼容。



本文件只负责把生成任务路由到单一事实来源，避免重复定义工作流。

## 执行顺序

1. 读取 `generate-topology.md`，识别仓库、构建、部署和业务边界。
2. 读取 `generate-project-index.md`，构建当前任务需要的基础索引与架构索引。
3. 按目标文档读取对应规范：

| 文档 | 生成规范 |
|---|---|
| `01_SYSTEM_OVERVIEW.md` | `generate-system-overview.md` |
| `02_CORE_MODULES.md` | `generate-core-modules.md` |
| `03_API_INTERFACE.md` | `generate-api-interface.md` |
| `04_DATA_MODEL.md` | `generate-data-model.md` |
| `05_CONFIG_MANAGEMENT.md` | `generate-config-management.md` |
| `06_UTILS_LIBRARIES.md` | `generate-utils-libraries.md` |

4. 使用 `quality-gates.md` 和 `scripts/validate_arch_docs.py` 校验。
5. 门禁通过后更新 metadata 的 per-doc 基线、索引 hash/counts 和漂移状态。

## 共同内容契约

- 描述当前状态，不替团队设计新架构
- 区分 `observed`、`approved_intent`、`inferred`、`unknown`
- 每份文档包含范围与基线、风险与待确认
- 正文输出架构摘要，全量资产清单写入外置索引
- 占位骨架和“不适用”不能替代项目证据
