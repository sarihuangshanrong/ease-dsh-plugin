# Go 项目代码分析指南

本指南用于指导从 Go 项目源代码中逆向提取领域模型和业务用例。

## 语言特征识别

### 项目类型判断

```bash
# Go 项目特征文件
- go.mod                     # Go Modules 项目
- go.sum                     # 依赖锁定文件
- *.go                       # Go 源文件
- main.go                    # 程序入口
- cmd/                       # 命令行入口目录
- internal/                  # 内部包目录
- pkg/                       # 公共包目录
```

### 框架识别

| 框架类型 | 特征导入/文件 | 分析重点 |
|---------|--------------|---------|
| Gin | `github.com/gin-gonic/gin` | 路由、Handler、中间件 |
| Echo | `github.com/labstack/echo` | 路由、Handler |
| Fiber | `github.com/gofiber/fiber` | 路由、Handler |
| gRPC | `google.golang.org/grpc`, `*.proto` | Service 定义、RPC 方法 |
| Go-Kit | `github.com/go-kit/kit` | Endpoint、Service、Transport |
| Go-Zero | `github.com/zeromicro/go-zero` | API 定义、RPC 服务 |
| GORM | `gorm.io/gorm` | 模型定义、数据操作 |
| Ent | `entgo.io/ent` | Schema 定义、关系 |

## 核心模块识别规则

### 1. 目录结构分析（Directory Structure）

> ⚠️ **不可协商**：必须基于目录结构识别多个独立的 Domain，禁止将整个项目视为单一 Domain。

#### 标准 Go 项目布局

```
project/
├── cmd/                     # 应用入口
│   ├── api/                 # API 服务入口
│   └── worker/              # 后台任务入口
├── internal/                # 内部包（不可被外部导入）
│   ├── user/                # Domain 1: 用户模块
│   │   ├── handler.go       # HTTP Handler
│   │   ├── service.go       # 业务逻辑
│   │   ├── repository.go    # 数据访问
│   │   └── model.go         # 数据模型
│   ├── order/               # Domain 2: 订单模块
│   │   ├── handler.go
│   │   ├── service.go
│   │   └── model.go
│   └── payment/             # Domain 3: 支付模块
│       └── ...
├── pkg/                     # 公共包
│   ├── middleware/          # 中间件（非独立 Domain）
│   └── utils/               # 工具函数
├── api/                     # API 定义（OpenAPI/Protobuf）
└── configs/                 # 配置文件
```

#### DDD 风格布局

```
project/
├── cmd/
├── internal/
│   ├── domain/              # 领域层
│   │   ├── user/            # Domain 1
│   │   │   ├── entity.go    # 实体
│   │   │   ├── repository.go # 仓储接口
│   │   │   └── service.go   # 领域服务
│   │   └── order/           # Domain 2
│   ├── application/         # 应用层
│   │   ├── user/            # 用户应用服务
│   │   └── order/           # 订单应用服务
│   ├── infrastructure/      # 基础设施层
│   │   ├── persistence/     # 持久化实现
│   │   └── external/        # 外部服务
│   └── interfaces/          # 接口层
│       ├── http/            # HTTP 接口
│       └── grpc/            # gRPC 接口
└── pkg/
```

#### 微服务布局

```
project/
├── services/
│   ├── user-service/        # Domain 1: 用户服务
│   │   ├── cmd/
│   │   ├── internal/
│   │   └── api/
│   ├── order-service/       # Domain 2: 订单服务
│   │   ├── cmd/
│   │   ├── internal/
│   │   └── api/
│   └── payment-service/     # Domain 3: 支付服务
└── shared/                  # 共享库
```

### 2. Domain 划分策略

> ⚠️ **强制要求**：必须将项目划分为多个 Domain，每个 Domain 对应一个独立的业务领域。

#### 划分依据

1. **按 internal 子目录划分**：
   - 识别 `internal/` 下的业务子目录
   - 每个业务子目录作为一个独立的 Domain

2. **按 services 划分（微服务）**：
   - 识别 `services/` 下的服务目录
   - 每个服务作为一个独立的 Domain

3. **按接口文件划分**：
   - 识别 `interface` 类型定义
   - 围绕核心接口划分 Domain 边界

#### 划分规则

```go
// 伪代码：Domain 划分逻辑
for each subdirectory in internal/ or services/:
    if is_business_module(subdirectory):  // 排除 pkg, utils, middleware 等
        create_domain(subdirectory.name)
        analyze_models(subdirectory)
        analyze_services(subdirectory)
        extract_usecases(subdirectory)
```

### 3. 实体识别规则

#### GORM 模型

```go
// 识别标记：gorm.Model 嵌入或 gorm tag
type User struct {
    gorm.Model                          // 内嵌基础字段
    Name     string `gorm:"size:100"`   // 字段约束
    Email    string `gorm:"uniqueIndex"` // 唯一索引
    Orders   []Order `gorm:"foreignKey:UserID"` // 关联关系
}

type Order struct {
    gorm.Model
    UserID   uint
    Amount   float64
    Status   OrderStatus
}
```

**提取要点**：
- struct 名 → 实体名称
- 字段 → 属性列表
- gorm tag → 数据约束
- 关联字段 → 实体关系

#### Ent Schema

```go
// ent/schema/user.go
func (User) Fields() []ent.Field {
    return []ent.Field{
        field.String("name").NotEmpty(),
        field.String("email").Unique(),
        field.Time("created_at").Default(time.Now),
    }
}

func (User) Edges() []ent.Edge {
    return []ent.Edge{
        edge.To("orders", Order.Type),
    }
}
```

**提取要点**：
- Schema 名 → 实体名称
- Fields() → 属性列表及验证规则
- Edges() → 实体关系

### 4. 服务识别规则

#### 接口定义

```go
// service.go
type UserService interface {
    CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error)
    GetUser(ctx context.Context, id uint64) (*User, error)
    UpdateUser(ctx context.Context, id uint64, req *UpdateUserRequest) error
    DeleteUser(ctx context.Context, id uint64) error
    ListUsers(ctx context.Context, filter *UserFilter) ([]*User, error)
}
```

**提取要点**：
- 方法名 → 用例名称
- 参数 → 输入数据
- 返回值 → 输出数据
- 方法注释 → 业务描述

#### HTTP Handler（Gin）

```go
func (h *UserHandler) RegisterRoutes(r *gin.RouterGroup) {
    users := r.Group("/users")
    {
        users.POST("", h.CreateUser)      // 用例：创建用户
        users.GET("/:id", h.GetUser)      // 用例：获取用户
        users.PUT("/:id", h.UpdateUser)   // 用例：更新用户
        users.DELETE("/:id", h.DeleteUser) // 用例：删除用户
    }
}

func (h *UserHandler) CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        // 输入验证
    }
    // 业务逻辑
}
```

**提取要点**：
- HTTP 方法 + 路径 → API 设计
- 请求绑定 → 输入规范
- 响应结构 → 输出规范

#### gRPC Service

```protobuf
// api/user/v1/user.proto
service UserService {
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
    rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
}
```

**提取要点**：
- service 定义 → 服务边界
- rpc 方法 → 用例
- message 定义 → 数据模型

### 5. 业务规则识别

#### 从验证器中提取

```go
type CreateUserRequest struct {
    Name     string `json:"name" binding:"required,min=2,max=50"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=8"`
    Age      int    `json:"age" binding:"gte=0,lte=150"`
}
```

**提取规则**：
- `required` → 必填规则
- `min/max` → 长度限制
- `email` → 格式校验
- `gte/lte` → 范围限制

#### 从业务逻辑中提取

```go
func (s *orderService) CreateOrder(ctx context.Context, req *CreateOrderRequest) (*Order, error) {
    // 规则1：库存检查
    stock, err := s.inventoryRepo.GetStock(ctx, req.ProductID)
    if err != nil {
        return nil, err
    }
    if stock < req.Quantity {
        return nil, ErrInsufficientStock
    }
    
    // 规则2：价格计算
    price := s.calculatePrice(req)
    
    // 规则3：VIP 折扣
    user, _ := s.userRepo.GetByID(ctx, req.UserID)
    if user.IsVIP {
        price = price * 0.9 // 9折
    }
    
    // 规则4：订单状态初始化
    order := &Order{
        Status: OrderStatusPending,
        // ...
    }
    
    return s.orderRepo.Create(ctx, order)
}
```

#### 从错误定义中提取

```go
var (
    ErrUserNotFound      = errors.New("user not found")
    ErrEmailAlreadyUsed  = errors.New("email already used")
    ErrInvalidPassword   = errors.New("invalid password")
    ErrInsufficientStock = errors.New("insufficient stock")
)
```

**提取要点**：
- 错误类型 → 业务约束
- 错误消息 → 规则描述

## 分析输出模板

### Domain 识别报告

```markdown
## 识别的 Domain 列表

### Domain 1: [domain-name]
- **目录路径**: internal/user
- **核心实体**: User, UserProfile, Session
- **主要服务**: UserService, AuthService
- **API 入口**: UserHandler
- **用例数量**: 10

### Domain 2: [domain-name]
...
```

### 用例提取模板

```markdown
## [Domain Name] - 用例列表

### 001-[subdomain]/001-[usecase-name].md

**来源**: UserService.CreateUser()
**描述**: 创建新用户账户
**参与者**: 系统管理员、注册用户
**前置条件**: 用户邮箱未被注册
**主流程**:
1. 验证用户输入数据
2. 检查邮箱唯一性
3. 加密用户密码
4. 保存用户信息
5. 发送激活邮件
**业务规则**:
- BR001: 邮箱必须唯一
- BR002: 密码长度至少 8 位
```

## 注意事项

1. **禁止单一 Domain**：必须识别并划分多个独立的业务 Domain
2. **关注接口定义**：Go 的 interface 是理解模块边界的关键
3. **分析 internal 目录**：internal 包通常包含核心业务逻辑
4. **注意错误处理**：错误类型定义反映业务约束
5. **查看 proto 文件**：如果使用 gRPC，proto 文件是 API 定义的权威来源
6. **识别中间件**：中间件通常包含横切关注点（认证、日志、限流等）

