# 场景架构模板库

> 本目录包含 `flow-2-design` 阶段使用的内置场景化架构模板。模板仅供 Agent 参考使用，不会生成到用户项目中。

## 可用模板

| 场景类型 | 模板文件 | 适用用例 |
|----------|---------|---------|
| 交易类 | [transaction-template.md](./transaction-template.md) | 支付、订单、退款、转账 |
| 查询类 | [query-template.md](./query-template.md) | 列表查询、详情、统计报表 |
| 流程类 | [workflow-template.md](./workflow-template.md) | 审批、工单流转、合同签署 |
| 消息类 | [messaging-template.md](./messaging-template.md) | 通知推送、短信、邮件 |
| 数据同步类 | [sync-template.md](./sync-template.md) | 数据导入导出、ETL、迁移 |
| 认证类 | [auth-template.md](./auth-template.md) | 登录、SSO、权限校验 |
| 文件处理类 | [file-template.md](./file-template.md) | 上传下载、图片处理 |
| 实时类 | [realtime-template.md](./realtime-template.md) | 在线聊天、实时监控 |
| 通用类 | [generic-template.md](./generic-template.md) | 兜底方案（无法匹配特定场景时） |

## 使用方式

1. **自动使用**: `/ease:flow-2-design` 在步骤 3.5 中自动识别用例场景类型，从此内置目录加载对应模板
2. **手动参考**: 开发人员可直接阅读模板，了解特定场景的架构最佳实践

## 模板结构说明

每个模板包含以下标准章节：

1. **模板元数据** - 场景类型、适用用例、版本
2. **架构模式推荐** - 核心模式、备选模式、不推荐模式
3. **技术栈推荐** - 数据库、缓存、消息队列
4. **组件清单** - 核心组件、扩展组件（含必需性标注）
5. **数据流设计** - Mermaid 序列图/流程图
6. **接口契约模板** - 典型 API 设计
7. **安全考虑** - 场景相关的安全要点
8. **性能优化** - 关键指标与优化策略
9. **可观测性** - 指标、告警阈值
10. **测试策略** - 各类型测试重点
11. **定制化参数** - 可调参数与默认值

## 相关文档

- [场景分类体系](../scenario-classification.md) - 场景识别规则与匹配算法
- [内置模板维护指南](../generate-scenario-templates.md) - 内置模板的维护流程
- [模板编写指南](../scenario-template-writing-guide.md) - 新增/修改模板的规范
