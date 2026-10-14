# 业务场景分类体系

> **版本**: v1.0
> **适用范围**: design 阶段场景识别、架构模板匹配

## 场景分类总览

共定义 **8 种核心业务场景** + **1 种通用兜底场景**，覆盖常见业务系统 90% 以上的用例类型。

| 序号 | 场景类型 | 场景 ID | 典型用例 | 核心架构特征 |
|------|----------|---------|---------|-------------|
| 1 | 交易类 | `transaction` | 下单、支付、退款、转账 | 强一致性、ACID、幂等性 |
| 2 | 查询类 | `query` | 列表查询、详情、统计报表 | 读多写少、缓存优先、最终一致性 |
| 3 | 流程类 | `workflow` | 审批、工单流转、合同签署 | 状态机、事件驱动、长事务 |
| 4 | 消息类 | `messaging` | 通知推送、短信、邮件 | 异步处理、消息队列、幂等性 |
| 5 | 数据同步类 | `sync` | 数据导入导出、ETL、迁移 | 批处理、分片、断点续传 |
| 6 | 认证类 | `auth` | 登录、SSO、权限校验 | 安全第一、会话管理、RBAC/ABAC |
| 7 | 文件处理类 | `file` | 上传下载、图片处理、转码 | 对象存储、异步处理、CDN |
| 8 | 实时类 | `realtime` | 在线聊天、实时监控、协同编辑 | 长连接、低延迟、心跳检测 |
| 9 | 通用类（兜底） | `generic` | 无法匹配的用例 | 标准分层架构 |

---

## 场景关键词库

每种场景定义 **主关键词**（高权重）和 **辅助关键词**（低权重），用于多维度匹配。

### 1. transaction（交易类）

```yaml
primary_keywords:
  - 支付
  - 交易
  - 订单
  - 结算
  - 退款
  - 转账
  - 扣款
  - 充值
  - 库存扣减
  - 账户变更

secondary_keywords:
  - 金额
  - 余额
  - 流水
  - 对账
  - 冲正
  - 回滚

rule_indicators:
  - 涉及金额计算
  - 涉及库存变更
  - 涉及账户余额
  - 需要事务保证
  - 需要幂等性

data_flow: write_heavy
nfr_profile:
  consistency: strong
  idempotency: required
  concurrency: high
```

### 2. query（查询类）

```yaml
primary_keywords:
  - 查询
  - 列表
  - 详情
  - 搜索
  - 统计
  - 报表
  - 导出查看
  - 筛选

secondary_keywords:
  - 分页
  - 排序
  - 过滤
  - 聚合
  - 汇总
  - 仪表盘

rule_indicators:
  - 仅读取数据
  - 无状态变更
  - 需要缓存
  - 需要分页

data_flow: read_heavy
nfr_profile:
  consistency: eventual
  cache: required
  latency: low
```

### 3. workflow（流程类）

```yaml
primary_keywords:
  - 审批
  - 流程
  - 工单
  - 流转
  - 签署
  - 审核
  - 会签
  - 驳回

secondary_keywords:
  - 状态
  - 节点
  - 条件
  - 分支
  - 超时
  - 催办
  - 委托

rule_indicators:
  - 多状态流转
  - 审批链/审批人
  - 超时处理
  - 条件分支

data_flow: bidirectional
nfr_profile:
  consistency: eventual
  traceability: required
  timeout_handling: required
```

### 4. messaging（消息类）

```yaml
primary_keywords:
  - 通知
  - 推送
  - 消息
  - 短信
  - 邮件
  - 站内信
  - 提醒

secondary_keywords:
  - 模板
  - 渠道
  - 已读
  - 未读
  - 订阅
  - 退订
  - 频次

rule_indicators:
  - 异步发送
  - 多渠道分发
  - 消息模板
  - 频次控制

data_flow: write_heavy
nfr_profile:
  consistency: eventual
  async: required
  idempotency: required
```

### 5. sync（数据同步类）

```yaml
primary_keywords:
  - 同步
  - 导入
  - 导出
  - 迁移
  - ETL
  - 批量
  - 对接

secondary_keywords:
  - 映射
  - 转换
  - 清洗
  - 校验
  - 断点
  - 增量
  - 全量

rule_indicators:
  - 批量数据处理
  - 数据格式转换
  - 外部系统对接
  - 定时任务

data_flow: batch
nfr_profile:
  consistency: eventual
  fault_tolerance: required
  resumable: required
```

### 6. auth（认证类）

```yaml
primary_keywords:
  - 登录
  - 注册
  - 认证
  - 授权
  - 权限
  - 鉴权
  - SSO
  - OAuth

secondary_keywords:
  - 角色
  - 菜单
  - 资源
  - 令牌
  - 会话
  - 验证码
  - 多因素

rule_indicators:
  - 身份验证
  - 权限控制
  - 会话管理
  - 安全策略

data_flow: read_heavy
nfr_profile:
  security: critical
  session_management: required
  audit: required
```

### 7. file（文件处理类）

```yaml
primary_keywords:
  - 上传
  - 下载
  - 文件
  - 附件
  - 图片
  - 视频
  - 文档

secondary_keywords:
  - 预览
  - 缩略图
  - 转码
  - 压缩
  - 水印
  - 存储
  - CDN

rule_indicators:
  - 文件存取操作
  - 格式转换
  - 大文件处理
  - 存储策略

data_flow: write_heavy
nfr_profile:
  storage: object_storage
  async_processing: required
  cdn: recommended
```

### 8. realtime（实时类）

```yaml
primary_keywords:
  - 实时
  - WebSocket
  - 在线
  - 聊天
  - 协同
  - 监控
  - 直播

secondary_keywords:
  - 心跳
  - 连接
  - 房间
  - 频道
  - 广播
  - 在线状态

rule_indicators:
  - 双向通信
  - 低延迟要求
  - 长连接维护
  - 实时推送

data_flow: bidirectional
nfr_profile:
  latency: ultra_low
  connection: long_lived
  heartbeat: required
```

---

## 场景识别规则

### 多维度识别策略

场景识别通过 **4 个维度** 综合打分，选择得分最高的场景类型。

#### 维度 1：用例名称关键词匹配（权重 40%）

从用例文档的以下位置提取关键词：
- 用例标题（`title`）
- 用例描述（`description`）
- 参与者（`actors`）
- 前置/后置条件

匹配规则：
- **主关键词命中** → 该维度得分 0.9
- **辅助关键词命中** → 该维度得分 0.5
- **多个关键词命中** → 取最高分 + 0.05 × (额外命中数)，上限 1.0

#### 维度 2：业务规则类型分析（权重 30%）

分析用例文档中的业务规则（`rules.md`），检查 `rule_indicators`：
- **≥2 个指标命中** → 该维度得分 0.9
- **1 个指标命中** → 该维度得分 0.6
- **0 个指标命中** → 该维度得分 0.0

#### 维度 3：数据流特征分析（权重 20%）

分析用例的主成功路径（flow steps）中的操作类型：
- 统计读操作步骤数和写操作步骤数
- 与场景的 `data_flow` 特征比对：
  - 匹配 → 0.8
  - 部分匹配 → 0.4
  - 不匹配 → 0.0

#### 维度 4：NFR 要求匹配（权重 10%）

从用例文档或需求规范中提取非功能性要求：
- 与场景的 `nfr_profile` 比对
- 每匹配一项 → +0.2（上限 1.0）

### 综合评分公式

```
final_score = keyword_score × 0.4
            + rule_score × 0.3
            + dataflow_score × 0.2
            + nfr_score × 0.1
```

### 匹配决策规则

1. **最高分 ≥ 0.6** → 采用该场景类型
2. **最高分 < 0.6 且 ≥ 0.4** → 采用该场景类型，但标注 `低置信`，建议人工确认
3. **最高分 < 0.4** → 使用 `generic`（通用）场景兜底
4. **前两名分差 < 0.1** → 标注 `多场景候选`，列出候选列表供人工选择

### 混合场景处理

当用例同时匹配多个场景（如"支付+审批"）：
1. 取得分最高的作为 **主场景**
2. 得分第二高的作为 **辅场景**（如果分差 < 0.2）
3. 架构设计时：主场景模板为基础，辅场景模板的关键要素作为补充
