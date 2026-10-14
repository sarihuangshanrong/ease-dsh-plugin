# [TC ID] [验证目标]

```json tc
{
  "id": "TC-D001-0001",
  "title": "重复投递只产生一次状态变更",
  "owner": "order",
  "revision": 1,
  "status": "draft",
  "origin_change": "001-order-change",
  "basis": [{"id": "BR-001-idempotency", "path": "docs/domains/001-order/usecases/001-submit/rules.md"}],
  "architecture_refs": [],
  "given": "相同业务键已成功提交，使用隔离测试数据",
  "when": "再次投递同一业务请求",
  "then": "状态变更仅一次；响应遵循已批准契约",
  "level": "integration",
  "environment": "真实隔离数据库；每测准备和清理数据",
  "test_methods": [],
  "supersedes": []
}
```

说明模板中的业务预期仅是示例，创建案例前必须以 basis 中的真实规则替换；没有批准依据时保留问题，不把示例当业务规则。
