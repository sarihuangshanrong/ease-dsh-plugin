## 目的（Purpose）
依据领域驱动设计（DDD，Domain-Driven Design）原则，将原始需求与领域/架构文档转化为完整的项目设计与骨架代码框架。

## 输入要求（Input Requirements）
1. **原始需求（Raw Requirements）：** 用户提供的用例文档：$ARGUMENTS
2. **领域模型文档（Domain Model Document）：** `doc/analyze/system_domains.md`
3. **架构文档（Architecture Document）：** `ARCHITECTURE.md`

## 输出交付物（Output Deliverables）
1. **项目设计文档（Project Design Documentation）**
2. **框架骨架代码（Framework Skeleton Code）**，包含详细的 TODO 注释
3. **临时过程文档（Temporary Process Documents）**，存放于 Ease 契约临时目录（`ease-spec/reference/stage-contract.md` §2.7）以供评审：Flow 内为 `.eases/${CHANGE_ID}/flow-2-design/.tmp/ease-architecture/`，独立执行为 `.eases/.tmp/${RUN_ID}/ease-architecture/`；禁止写入 `/tmp`

## 流程总览（Process Overview）

### 阶段 1：拆解与分析（Phase 1: Deconstruction & Analysis）
**目标（Goal）：** 澄清“构建什么（what to build）”与“系统边界（system boundaries）”

1. **识别限界上下文（Identify Bounded Contexts）**
    - 分析业务需求与架构文档
    - 定义系统模块/微服务
    - 输出：模块划分与服务边界
    - 文档：`.eases/${CHANGE_ID}/flow-2-design/.tmp/ease-architecture/bounded_contexts.md`

2. **抽取用例（Extract Use Cases）**
    - 将用户用例文档转化为具体动作
    - 为每个用例映射 API 端点
    - 输出：完整的 API 入口点列表

### 阶段 2：架构分层（Phase 2: Architecture Layering）
**目标（Goal）：** 建立物理与逻辑的代码结构

基于 Clean Architecture 原则与 `ARCHITECTURE.md`：

```
project/
├── controller/             # Interface Layer (Controllers, RPC Handlers)
├── action/                 # Combined Service Layer (Use Case Orchestration)
├── service/                # Application Service Layer (Core Business Logic)
├── common/                 # Common Layer
    ├── dto/                # Domain Layer (DTOs, Business Rules)
    ├── util/               # Util Layer  (Utilities)
├── integration/            
    ├── dao/                # Data Access Layer
    └── sao/                # Service Access Layer (External Services)
```

**关键规则（Key Rules）：**
- 组合服务（Combined Service）可以跨模块调用各类服务（Services）
- 组合服务不得调用其他模块的组合服务
- 应用服务（Application Service）采用贫血模型模式（Anemic Model Pattern，服务替代实体的行为）
- 在 `.eases/${CHANGE_ID}/flow-2-design/.tmp/ease-architecture/architecture_layers.md` 中记录结构文档

### 阶段 3：领域对象映射（Phase 3: Domain Object Mapping）
**目标（Goal）：** 将领域模型文档转化为代码类

1. **定义 DTO（Data Transfer Objects）**
   ```java
   public class OrderDTO extends BaseDTO {
       // Properties only
       private String id;
       private OrderStatus status;
       // Method signatures without implementation
       public void pay(Money amount);
   }
   ```

2. **识别聚合根（Identify Aggregate Roots）**
    - 确定一致性边界
    - 定义聚合根实体

3. **定义仓储接口（Define Repository Interfaces）**
   ```java
   public interface OrderDAO {
       OrderDTO findById(String id);
       void save(OrderDTO order);
       // No SQL implementation at this stage
   }
   ```

在 `.eases/${CHANGE_ID}/flow-2-design/.tmp/ease-architecture/domain_mappings.md` 中记录映射文档

### 阶段 4：契约与接口设计（Phase 4: Contract & Interface Design）
**目标（Goal）：** 定义连接用例的输入/输出契约

1. **定义请求/响应 DTO（Define Request/Response DTOs）**
   ```java
   public class CreateOrderCommand {
       // Request fields
   }
   
   public class CreateOrderResponse {
       // Response fields
   }
   ```

2. **定义服务接口（Define Service Interfaces）**
   ```java
   public interface OrderApplicationService {
       CreateOrderResponse createOrder(CreateOrderCommand command);
   }
   ```

将契约记录在 `.eases/${CHANGE_ID}/flow-2-design/.tmp/ease-architecture/contracts.md`

### 阶段 5：生成带文档的骨架代码（Phase 5: Skeleton Code Generation with Documentation）
**目标（Goal）：** 生成“自说明（self-documenting）”的框架代码

#### API 层骨架（API Layer Skeleton）
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderCombinedService orderCombinedService;
    
    /**
     * Create new order
     * Permissions: USER_ROLE
     * Rate Limit: 100/min
     * Use Case: UC-001
     */
    @PostMapping
    public ResponseEntity<CreateOrderResponse> createOrder(@RequestBody CreateOrderRequest request) {
        // TODO: 1. Validate request
        // TODO: 2. Convert to command
        // TODO: 3. Call combined service
        // TODO: 4. Handle response
        throw new UnsupportedOperationException("TODO: implement");
    }
}
```

#### 组合服务层骨架（Combined Service Layer Skeleton）
```java
@Service
@Transactional
public class OrderCombinedService {
    
    @Autowired
    private OrderService orderService;
    @Autowired
    private InventoryService inventoryService;
    @Autowired
    private PaymentService paymentService;
    
    public CreateOrderResponse placeOrder(PlaceOrderCommand cmd) {
        // TODO: 1. Start transaction
        
        // TODO: 2. Validation: Check user exists
        // UserContext.validateUser(cmd.getUserId())
        
        // TODO: 3. Domain Logic: Build Order aggregate
        // OrderDTO order = OrderFactory.create(cmd)
        
        // TODO: 4. External Service: Check inventory
        // boolean available = inventoryService.checkAvailability(cmd.getItems())
        // if (!available) throw new InsufficientInventoryException()
        
        // TODO: 5. External Service: Reserve inventory
        // inventoryService.reserve(cmd.getItems())
        
        // TODO: 6. Domain Logic: Calculate pricing
        // Money totalAmount = pricingService.calculate(order)
        
        // TODO: 7. Persistence: Save order
        // orderService.save(order)
        
        // TODO: 8. Event: Publish OrderCreatedEvent
        // eventPublisher.publish(new OrderCreatedEvent(order))
        
        // TODO: 9. Return response DTO
        throw new UnsupportedOperationException("TODO: implement");
    }
}
```

#### 应用服务层骨架（Application Service Layer Skeleton）
```java
@Service
public class OrderService {
    
    @Autowired
    private OrderDAO orderDAO;
    
    public void save(OrderDTO order) {
        // TODO: 1. Validate business rules
        // order.validate()
        
        // TODO: 2. Apply domain invariants
        // if (order.getStatus() != OrderStatus.DRAFT) {
        //     throw new InvalidOrderStateException()
        // }
        
        // TODO: 3. Persistence
        // orderDAO.save(order)
        
        // TODO: 4. Log operation
        // auditLog.record("Order saved", order.getId())
        
        throw new UnsupportedOperationException("TODO: implement");
    }
    
    public OrderDTO findById(String orderId) {
        // TODO: 1. Input validation
        // Validator.notNull(orderId)
        
        // TODO: 2. Query from repository
        // OrderDTO order = orderDAO.findById(orderId)
        
        // TODO: 3. Check existence
        // if (order == null) throw new OrderNotFoundException()
        
        // TODO: 4. Return result
        throw new UnsupportedOperationException("TODO: implement");
    }
}
```

#### 领域层骨架（Domain Layer Skeleton）
```java
public class OrderDTO extends BaseDTO {
    
    private String orderId;
    private OrderStatus status;
    private List<OrderItemDTO> items;
    private Money totalAmount;
    private LocalDateTime createdAt;
    
    /**
     * Business Rule: Order can only be paid when status is PENDING
     * and payment amount matches total
     * 
     * @param payment Payment details
     * @throws InvalidOrderStateException if not in PENDING status
     * @throws PaymentAmountMismatchException if amount doesn't match
     */
    public void pay(PaymentDTO payment) {
        // TODO: 1. Check status == PENDING
        // if (this.status != OrderStatus.PENDING) {
        //     throw new InvalidOrderStateException()
        // }
        
        // TODO: 2. Validate payment amount
        // if (!payment.getAmount().equals(this.totalAmount)) {
        //     throw new PaymentAmountMismatchException()
        // }
        
        // TODO: 3. Update status
        // this.status = OrderStatus.PAID
        
        // TODO: 4. Record payment time
        // this.paidAt = LocalDateTime.now()
        
        // TODO: 5. Register domain event
        // this.addDomainEvent(new OrderPaidEvent(this))
        
        throw new UnsupportedOperationException("TODO: implement");
    }
    
    /**
     * Business Rule: Order can only be cancelled when not shipped
     */
    public void cancel(String reason) {
        // TODO: Implementation with business rules
        throw new UnsupportedOperationException("TODO: implement");
    }
}
```

## 执行说明（Execution Instructions）

1. **从分析开始（Start with Analysis）**
    - 彻底阅读所有输入文档
    - 在 `/tmp` 目录生成分析文档
    - 与领域专家校验理解

2. **先创建包结构（Create Package Structure First）**
    - 构建完整目录结构
    - 初始不编写实现代码
    - 专注于正确的关注点分离（Separation of Concerns）

3. **生成骨架类（Generate Skeleton Classes）**
    - 创建所有类与空方法
    - 添加全面的 TODO 注释
    - 将业务规则以文档/注释形式记录

4. **完整记录（Document Everything）**
    - 方法签名配合 JavaDoc/注释
    - 业务规则以注释保留领域知识
    - 清晰标注各集成点（Integration Points）

5. **评审检查点（Review Checkpoint）**
    - 所有 `/tmp` 文档具备可追溯性
    - 骨架代码可进入实现阶段
    - 为开发者提供清晰的 TODO 路线图

## 关键原则（Key Principles）

1. **不做具体实现（No Concrete Implementation）** —— 仅提供结构与契约
2. **全面 TODO（Comprehensive TODOs）** —— 指导后续实现
3. **业务规则入注释（Business Rules as Comments）** —— 保留领域知识
4. **清晰架构（Clean Architecture）** —— 严格维持层级边界
5. **DDD 聚焦（DDD Focus）** —— 以领域模型驱动设计

## 成功判定标准（Success Criteria）

- [ ] 目录结构完整且与架构匹配
- [ ] 所有用例映射到服务方法
- [ ] 领域对象包含业务规则文档化
- [ ] 数据访问对象（DAO）接口不含 SQL
- [ ] 服务访问对象（SAO）接口不含具体实现
- [ ] 服务骨架具备 TODO 工作流
- [ ] 控制器具备路由定义
- [ ] `/tmp` 目录的过程文档可供评审
- [ ] 不含任何真实业务逻辑实现
- [ ] 通过 TODO 明确实现路线图

## 备注（Notes）

- 将临时文档生成到 `/tmp` 以便过程评审
- 参考 `ARCHITECTURE.md` 中的具体模式
- 使用 `system_domains.md` 作为领域对象的事实来源（Source of Truth）
- 骨架代码应通过结构与注释实现“自说明（Self-Documenting）”
- 聚焦契约与边界，而非实现细节
