# TRD 示例

## 示例: 数据库连接池优化

**建议文件名**: `docs/003-hikari-pool-optimization.md`

---

# [TRD-003] HikariCP 连接池优化

> **日期**: 2024-01-15
> **状态**: Draft
> **影响范围**: order-service, user-service

## 1. 背景

**现状问题**: 高峰期数据库连接等待超时频发，日志显示 `Connection is not available, request timed out after 30000ms`，最大连接数 10 已无法满足并发需求。

**技术目标**: 连接等待超时率降至 0.1% 以下，P99 连接获取时间 < 100ms。

## 2. 方案设计

### 2.1 整体思路

扩大连接池容量，优化连接生命周期参数，增加连接泄漏检测。

### 2.2 代码变更

| 模块/文件 | 变更类型 | 变更说明 |
|:----------|:---------|:---------|
| `order-service/src/main/resources/application.yml` | 修改 | HikariCP 参数调整 |
| `user-service/src/main/resources/application.yml` | 修改 | HikariCP 参数调整 |

### 2.3 关键实现

无代码变更，仅配置调整。

### 2.4 配置变更

| 配置项 | 变更前 | 变更后 |
|:-------|:-------|:-------|
| `spring.datasource.hikari.maximum-pool-size` | 10 | 30 |
| `spring.datasource.hikari.minimum-idle` | 5 | 10 |
| `spring.datasource.hikari.connection-timeout` | 30000 | 10000 |
| `spring.datasource.hikari.leak-detection-threshold` | (未设置) | 60000 |

## 3. 影响分析

### 3.1 上下游影响

| 方向 | 系统/模块 | 影响说明 | 是否需协调 |
|:-----|:----------|:---------|:-----------|
| 上游 | - | 无 | 否 |
| 下游 | MySQL | 连接数增加，需确认 max_connections | 是 |

### 3.2 兼容性

- **API 兼容**: 兼容，无接口变更
- **数据兼容**: 兼容，无数据结构变更

## 4. 风险与对策

| 风险 | 等级 | 对策 |
|:-----|:-----|:-----|
| 数据库 max_connections 不足 | 中 | 提前确认 MySQL 配置，预留 buffer |
| 连接池过大导致内存增加 | 低 | 监控 JVM 内存使用 |

## 5. 验证要点

- [ ] 压测验证连接获取 P99 < 100ms
- [ ] 观察连接泄漏告警是否触发
- [ ] 确认 MySQL 连接数在安全范围内
