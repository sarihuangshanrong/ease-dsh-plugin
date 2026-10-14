# 系统领域模型（System Domain Model）

## 概述（Summary）

<!-- 
系统领域模型的简要概述，包括：
- 已识别领域的总数
- 使用的关键架构模式
- 主要技术栈
-->

## 领域概览（Domain Overview）

```
┌─────────────────────────────────────────────────────────┐
│                   系统领域地图（System Domain Map）      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐     ┌──────────────┐                   │
│  │   Domain A   │────►│   Domain B   │                   │
│  └──────────────┘     └──────────────┘                   │
│         │                     ▲                           │
│         ▼                     │                           │
│  ┌──────────────┐     ┌──────────────┐                   │
│  │   Domain C   │────►│   Domain D   │                   │
│  └──────────────┘     └──────────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 领域（Domains）

### 领域： [Domain Name]

#### 描述（Description）
<!-- 
描述该领域的：
- 主要职责
- 业务语境
- 核心业务规则
-->

#### 限界上下文（Bounded Context）
<!-- 定义该领域的边界与范围 -->

#### 实体（Entities）

##### [Entity Name]（类型：VO/BO/DTO）

**用途（Purpose）**:
<!-- 描述该实体在领域中的角色 -->

**源码位置（Source Location）**: `path/to/entity/file`

**关键属性（Key Attributes）**:

| 属性（Attribute） | 类型（Type） | 描述（Description） | 约束（Constraints） |
|-------------------|--------------|---------------------|---------------------|
| id | Long | 唯一标识符 | 主键、自动生成 |
| name | String | 实体名称 | 必填、最大 255 字符 |
| status | Enum | 当前状态 | 必填，取值：ACTIVE, INACTIVE |
| createdAt | DateTime | 创建时间戳 | 必填、不可变 |

**业务规则（Business Rules）**:
- <!-- 规则 1 -->
- <!-- 规则 2 -->

**关系（Relationships）**:

| 关联实体（Related Entity） | 关系类型（Relationship Type） | 基数（Cardinality） | 描述（Description） |
|----------------------------|-------------------------------|---------------------|---------------------|
| [Entity B] | Association（关联） | 1:N | 一个 [Entity] 可拥有多个 [Entity B] |
| [Entity C] | Composition（组合） | 1:1 | [Entity] 拥有 [Entity C] 的生命周期 |
| [Entity D] | Aggregation（聚合） | N:M | [Entity] 引用 [Entity D] |

**方法/操作（Methods/Operations）**:
<!-- 对于 BO，列出关键业务方法 -->
- `validate()`: 校验实体状态
- `calculateTotal()`: 基于业务规则计算总额

#### 领域服务（Domain Services）

| 服务名称（Service Name） | 类型（Type） | 职责（Responsibility） |
|--------------------------|--------------|------------------------|
| [ServiceName] | Application Service | 编排用例 |
| [ServiceName] | Domain Service | 实现领域逻辑 |
| [ServiceName] | Infrastructure Service | 处理技术性关注点 |

#### 领域事件（Domain Events）

| 事件名称（Event Name） | 触发条件（Trigger） | 消费端（Consumers） |
|------------------------|---------------------|---------------------|
| [EventName] | 当满足 [condition] 时 | [Domain B], [Domain C] |

#### 仓储接口（Repository Interfaces）

| 仓储（Repository） | 实体（Entity） | 操作（Operations） |
|--------------------|----------------|--------------------|
| [RepositoryName] | [Entity] | find, save, delete, findByStatus |

#### 数据库模式（Database Schema）

##### 表： [table_name]

| 列（Column） | 类型（Type） | 约束（Constraints） | 映射（Maps To） |
|--------------|--------------|---------------------|-----------------|
| id | BIGINT | PK, AUTO_INCREMENT | Entity.id |
| name | VARCHAR(255) | NOT NULL | Entity.name |
| status | VARCHAR(50) | NOT NULL | Entity.status |
| created_at | TIMESTAMP | NOT NULL | Entity.createdAt |

**索引（Indexes）**:
- `idx_status`: (status)
- `idx_created_at`: (created_at)

**外键（Foreign Keys）**:
- `fk_parent_id`: REFERENCES parent_table(id)

---

## 跨领域关系（Cross-Domain Relationships）

### 集成点（Integration Points）

| 源领域（Source Domain） | 目标领域（Target Domain） | 集成类型（Integration Type） | 通信模式（Communication Pattern） |
|-------------------------|---------------------------|------------------------------|----------------------------------|
| [Domain A] | [Domain B] | 直接 API 调用（Direct API Call） | 同步 REST（Synchronous REST） |
| [Domain B] | [Domain C] | 事件流（Event Stream） | 异步消息（Asynchronous Messaging） |
| [Domain C] | [Domain D] | 数据库视图（Database View） | 共享数据（Shared Data） |

### 数据流模式（Data Flow Patterns）

```
[User Request] 
    │
    ▼
[API Gateway]
    │
    ├──► [Domain A: DTO] ──► [Domain A: BO] ──► [Domain A: Entity]
    │                              │
    │                              ▼
    │                    [Domain A: Repository]
    │                              │
    │                              ▼
    └──────────────────► [Database]
```

### 共享内核（Shared Kernel）

<!-- 列出跨领域使用的共享概念、值对象或工具 -->

| 组件（Component） | 类型（Type） | 使用者（Used By） | 目的（Purpose） |
|-------------------|--------------|-------------------|-----------------|
| Money | 值对象（Value Object） | Order, Payment, Billing | 表示货币数值 |
| Address | 值对象（Value Object） | User, Order, Shipping | 表示物理地址 |

## 聚合边界（Aggregate Boundaries）

### [Aggregate Root Name]

**聚合成员（Aggregate Members）**:
- [Entity A]（根，Root）
    - [Entity B]
    - [Value Object C]

**不变式（Invariants）**:
- <!-- 必须始终成立的业务规则 -->
- <!-- 一致性边界 -->

**事务边界（Transaction Boundary）**:
<!-- 定义必须一起持久化的内容 -->

## 技术架构（Technical Architecture）

### 使用的模式（Patterns Used）

| 模式（Pattern） | 实现方式（Implementation） | 适用领域（Domains） |
|-----------------|----------------------------|---------------------|
| Repository Pattern | JPA/Hibernate | 所有领域 |
| Factory Pattern | 静态工厂（Static factories） | Order, Product |
| Strategy Pattern | 支付处理（Payment processing） | Payment 领域 |
| Observer Pattern | 领域事件（Domain events） | 事件驱动领域 |

### 技术栈（Technology Stack）

| 层（Layer） | 技术（Technology） | 目的（Purpose） |
|-------------|---------------------|-----------------|
| 表现层（Presentation） | REST API / GraphQL | API 端点 |
| 应用层（Application） | Spring Boot / Express | 应用服务 |
| 领域层（Domain） | Plain Java/TypeScript | 领域逻辑 |
| 基础设施层（Infrastructure） | PostgreSQL / MongoDB | 数据持久化 |

## 防腐层（Anti-Corruption Layer, ACL）

<!-- 定义如何在不污染领域的前提下集成外部系统 -->

| 外部系统（External System） | ACL 组件（ACL Component） | 转换（Translation） |
|-----------------------------|---------------------------|---------------------|
| Legacy System | LegacyAdapter | 将遗留 DTO 转换为领域实体 |
| Third-party API | APIClient | 将外部响应映射到领域对象 |

## 性能考量（Performance Considerations）

| 关注点（Concern） | 解决方案（Solution） | 影响（Impact） |
|-------------------|----------------------|----------------|
| N+1 查询 | 预加载（Eager loading）、批量抓取（Batch fetching） | 减少数据库调用 |
| 大型聚合 | 聚合拆分（Aggregate splitting） | 改善写入性能 |
| 复杂查询 | CQRS、读模型（Read models） | 优化读取操作 |

## 演进与维护（Evolution and Maintenance）

### 版本历史（Version History）

| 版本（Version） | 日期（Date） | 变更（Changes） |
|-----------------|--------------|-----------------|
| 1.0.0 | YYYY-MM-DD | 初始领域模型 |
| 1.1.0 | YYYY-MM-DD | 新增 [Domain X] |

### 未来考量（Future Considerations）

- <!-- 计划的领域变更 -->
- <!-- 潜在的重构需求 -->
- <!-- 可扩展性考量 -->

## 术语表（Glossary）

| 术语（Term） | 定义（Definition） | 语境（Context） |
|--------------|---------------------|-----------------|
| [Term] | [业务定义（Business definition）] | [使用位置（Where used）] |

## 附录（Appendix）

### A. 实体关系图（Entity Relationship Diagram, ERD）

```
[如有，请包含 ERD]
```

### B. 类图（Class Diagrams）

```
[为复杂领域包含 UML 类图]
```

### C. 时序图（Sequence Diagrams）

```
[为关键流程包含时序图]
