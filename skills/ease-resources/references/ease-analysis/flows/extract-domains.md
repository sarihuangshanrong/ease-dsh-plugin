## 角色
你是一名系统架构师，负责分析项目源代码以抽取并记录领域模型、实体及其关系。

## 目标
分析项目代码库以识别：
- 领域模型与边界
- 各领域中的实体（关注 VO/BO/DTO 模式）
- 实体之间的关系
- 数据库模式（如存在）
- ORM 配置（如使用）

## 定义
- VO（Value Object，值对象）：不可变对象，表示领域中的描述性方面，无概念上的唯一身份
- BO（Business Object，业务对象）：封装业务逻辑与规则的对象
- DTO（Data Transfer Object，数据传输对象）：在不同层或系统之间传输数据的对象

## 任务管理与进度跟踪

> 本 flow 使用统一的任务管理标准。详细信息请参见 `../references/flow-execution-standards.md`

### 任务清单创建

**在开始第一步之前，使用 TodoWrite 工具创建完整的任务清单：**

请创建以下结构的待办事项，确保每个任务都有唯一的 ID、描述、优先级和初始状态：

**阶段1：项目准备（2个核心任务 + 1个质量检查）**
- 项目目录扫描 - 优先级：高
- 包与模块分析 - 优先级：高
- 阶段1质量检查：项目结构完整，领域识别准确 - 优先级：高

**阶段2：实体抽取（3个核心任务 + 1个质量检查）**
- VO 模式识别 - 优先级：高
- BO 模式识别 - 优先级：高
- DTO 模式识别 - 优先级：高
- 阶段2质量检查：实体分类完整，模式识别准确 - 优先级：高

**阶段3：关系分析（2个核心任务 + 1个质量检查）**
- 实体间关系识别 - 优先级：高
- 数据库模式分析 - 优先级：高
- 阶段3质量检查：关系映射正确，数据库实体对应清晰 - 优先级：高

**阶段4：文档生成（2个核心任务 + 1个质量检查）**
- 使用模板结构生成文档 - 优先级：高
- 检查现有文档并合并 - 优先级：高
- 最终质量检查：文档格式正确，内容完整 - 优先级：高

### 任务执行指南

**参见统一的执行标准和质量改进流程：`../references/flow-execution-standards.md`**

### 内容填充检查点（针对代码分析）

#### 系统领域模型文档检查清单

```
✓ 概述（Summary）
  ✓ 系统领域模型的简要概述已填写
  ✓ 已识别领域的总数已统计
  ✓ 使用的关键架构模式已列出
  ✓ 主要技术栈已说明（如 Java/Spring、Node.js/Express）

✓ 领域概览（Domain Overview）
  ✓ 系统领域地图已绘制
  ✓ 地图包含实际的领域名称
  ✓ 地图包含领域间的关系箭头
  ✓ 使用具体的领域名称

✓ 领域（Domains）章节
  每个领域都必须包含：
  ✓ 领域名称已填写（具体名称，如 "用户认证"、"订单管理"）
  ✓ 描述已填写（主要职责、业务语境、核心业务规则）
  ✓ 限界上下文已定义
  ✓ 实体列表已列出
  ✓ 每个实体都有：
    ✓ 实体名称和类型（VO/BO/DTO）
    ✓ 用途描述
    ✓ 源码位置（真实文件路径，如 com.example.order.Order）
    ✓ 关键属性表格（包含：属性、类型、描述、约束）
    ✓ 业务规则列表
    ✓ 关系表格（包含：关联实体、关系类型、基数、描述）
    ✓ 方法/操作（对于BO，列出关键业务方法）
  ✓ 领域服务表格已列出
  ✓ 领域事件表格已列出
  ✓ 仓储接口表格已列出
  ✓ 数据库模式已定义（如存在）
    ✓ 表名已填写
    ✓ 列映射表格已填写
    ✓ 索引已列出
    ✓ 外键已列出（如有）

✓ 跨领域关系（Cross-Domain Relationships）
  ✓ 集成点表格已列出
  ✓ 数据流模式已描述
  ✓ 共享内核已列出（如有）

✓ 聚合边界（Aggregate Boundaries）
  ✓ 每个聚合根都有：
    ✓ 聚合成员列表
    ✓ 不变式列表
    ✓ 事务边界定义

✓ 技术架构（Technical Architecture）
  ✓ 使用的模式已列出
  ✓ 技术栈表格已填写

✓ 防腐层（Anti-Corruption Layer, ACL）
  ✓ 外部系统与ACL组件表格已列出（如有外部集成）

✓ 性能考量（Performance Considerations）
  ✓ 关注点表格已列出

✓ 演进与维护（Evolution and Maintenance）
  ✓ 版本历史已记录
  ✓ 未来考量已列出

✓ 术语表（Glossary）
  ✓ 关键术语已列出
  ✓ 每个术语都有定义和语境
```

> Note: TodoList 执行严格性、质量改进流程、进度可视化等通用标准请参见 `../references/flow-execution-standards.md`

### 📋 本 Flow 特定的内容要求

**本 Flow 在通用标准基础上，还需要确保：**

1. **基于代码分析结果填充内容**：
   - 领域名称必须是具体的业务领域（如 "订单管理"、"用户认证"）
   - 实体名称必须是具体的代码类名（如 "Order"、"User"、"Product"）
   - 源码位置必须是真实的文件路径（如 `src/main/java/com/example/Order.java`）

2. **完整填充模板章节**：
   - 每个领域下必须包含：描述、限界上下文、实体、领域服务、领域事件、仓储接口、数据库模式
   - 每个实体都必须有关键属性表格，包含具体字段和类型

---

## 分析流程

### 第一步：项目目录扫描（Project Directory Scan）

首先识别当前项目目录并扫描其结构：

1. 获取当前工作目录
2. 列出所有源代码目录（排除 test/、tests/、*Test.java、*Spec.java）
3. 识别技术栈（Java/Spring、Node.js、Python 等）
4. 定位关键目录：
    - 对于 Java/Spring 项目：src/main/
    - 对于 Node.js 项目：app/、src/
    - models/、domain/ 目录
    - database/、migrations/、schema/ 目录

### 第二步：包与模块分析（Package and Module Analysis）

分析包/模块结构以识别领域：

1. 检查包命名模式（例如 com.company.product.domain.*）
2. 从包组织中识别限界上下文（Bounded Contexts）
3. 寻找领域特定的包/模块：
    - user、auth、authentication
    - order、payment、billing
    - product、catalog、inventory
    - notification、messaging
    - reporting、analytics

### 第三步：实体抽取（Entity Extraction）

针对每个识别出的领域，通过以下方式抽取实体：

- 3.1 VO 模式识别（VO Pattern Recognition）
  查找以下特征： - 具有 final/不可变字段 - 无 setter 方法 - equals() 与 hashCode() 基于值覆盖 - 命名含 *Value、*VO 后缀 - 构造函数中包含校验

- 3.2 BO 模式识别（BO Pattern Recognition）
  查找以下特征： - 包含业务逻辑方法 - 具备状态管理 - 命名含 *Service、*Manager、*Handler、*BO - 可编排多个实体 - 实现业务规则

- 3.3 DTO 模式识别（DTO Pattern Recognition）
  查找以下特征： - 命名含 *DTO、*Request、*Response、*Payload - 位于 api/、controller/、rest/ 包中 - 仅包含数据字段与 getters/setters - 具备序列化注解（@JsonProperty、@XmlElement）

### 第四步：关系分析（Relationship Analysis）

识别实体之间的关系：

1. 组合（Composition）：实体 A 包含实体 B
2. 聚合（Aggregation）：实体 A 引用实体 B
3. 关联（Association）：实体通过方法交互
4. 继承（Inheritance）：实体层次结构
5. 依赖（Dependency）：实体 A 在操作上依赖实体 B
   查找：
    - 实体之间的字段引用
    - 方法参数与返回类型
    - 集合关系（One-to-Many、Many-to-Many）
    - DTO 中的外键引用

### 第五步：数据库模式分析（Database Schema Analysis）

如果存在数据库定义，分析：

1. DDL 文件（*.sql、迁移文件）
    - CREATE TABLE 语句
    - 外键约束
    - 索引与唯一约束

2. ORM 配置：
    - JPA/Hibernate 注解（@Entity、@Table、@OneToMany）
    - Sequelize 模型
    - Django 模型
    - TypeORM 实体

3. 抽取：
    - 表名与其对应的实体
    - 列映射
    - 关系映射

### 第六步：文档生成（Documentation Generation）

#### 6.1 使用模板结构（Use Template Structure）

**格式要求：** 必须严格使用模板结构 `../templates/system-domains-template.md` 生成 Markdown 格式的领域模型文档。**禁止使用 JSON、YAML 或其他非模板格式**。

输出文档必须包含模板中定义的所有章节，并按照模板的结构组织内容。任何代码分析结果都必须转换为符合模板格式的 Markdown 文档。

#### 6.2 检查现有文档（Check Existing Documentation）
``` bash
if [ -f "docs/analyze/system-domains.md" ]; then
# Read existing document
# Merge new findings with existing content
# Preserve manual additions and corrections
else
# Create new document from template
fi
```

## 执行说明（Execution Instructions）
执行该分析时：

- 保持系统化：在转到下一包/模块前，完整处理当前包/模块
- 聚焦业务逻辑：优先处理对业务至关重要的实体，而非基础设施代码
- 识别模式：寻找项目特有的命名约定与结构模式
- 验证关系：确保识别出的关系在代码中被实际使用
- 记录假设：标注分析过程中所做的任何假设

## 输出要求（Output Requirements）
生成全面的领域模型文档，包含：
- 所有识别出的 VO、BO 和 DTO
- 映射关系及基数（1:1、1:N、N:M）
- 清晰的领域边界

若与既有文档合并：
- 保留用户新增的章节
- 标注自动生成的更新
- 添加分析时间戳

- 代码分析示例（Code Analysis Patterns）
    - Java/Spring Boot

``` java 
// VO Example
@Value
public class Money {
BigDecimal amount;
Currency currency;
}

// BO Example
@Service
public class OrderService {
public Order processOrder(OrderRequest request) {
// Business logic
}
}

// DTO Example
@Data
public class OrderDTO {
private Long id;
private List<OrderItemDTO> items;
}
Node.js/TypeScript

// VO Example
export class Email {
constructor(private readonly value: string) {
this.validate(value);
}
}

// BO Example
export class OrderProcessor {
async processOrder(order: Order): Promise<ProcessedOrder> {
// Business logic
}
}

// DTO Example
export interface OrderResponseDTO {
id: string;
items: OrderItemDTO[];
total: number;
}
```
- Python

``` Python
# python
# VO Example
@dataclass(frozen=True)
class Address:
street: str
city: str
country: str

# BO Example
class OrderService:
def process_order(self, order: Order) -> ProcessedOrder:
# Business logic
pass

# DTO Example
class OrderDTO(BaseModel):
id: int
items: List[OrderItemDTO]
total_amount: Decimal
```

## 特别注意（Special Considerations）

- 微服务：若项目采用微服务架构，将每个服务视为潜在的限界上下文
- 事件驱动：识别可能表示领域事件的事件定义
- CQRS 模式：区分命令与查询模型
- 遗留代码：可能不遵循标准模式；基于行为使用启发式方法
- 多语言项目：针对各语言采用适当模式

## 质量检查（Quality Checks）
在最终定稿前：

- ✓ 已分析所有主要包/模块
- ✓ 正确分类实体类型（VO/BO/DTO）
- ✓ 关系具备清晰的基数
- ✓ 领域边界逻辑且内聚
- ✓ 文档遵循模板结构
- ✓ 交叉引用准确
- ✓ 数据库映射（如有）完整

## 命令执行（Command Execution）
执行此分析：
- 导航至项目根目录
- 按步骤 1-6 系统化进行代码分析
- 生成或更新 docs/analyze/system-domains.md
- 依据质量检查验证输出
- 报告任何需要人工审阅的歧义或区域
