# Java 项目代码分析指南

本指南用于指导从 Java 项目源代码中逆向提取领域模型和业务用例。

## 语言特征识别

### 项目类型判断

```bash
# Java 项目特征文件
- pom.xml                    # Maven 项目
- build.gradle / build.gradle.kts  # Gradle 项目
- *.java                     # Java 源文件
- src/main/java/             # 标准源码目录
```

### 框架识别

| 框架类型 | 特征文件/依赖 | 分析重点 |
|---------|--------------|---------|
| Spring Boot | `@SpringBootApplication`, `spring-boot-starter-*` | Controller、Service、Repository |
| Spring MVC | `@Controller`, `@RestController` | 请求映射、视图层 |
| Spring Cloud | `spring-cloud-*` | 微服务边界、服务调用 |
| MyBatis | `*Mapper.java`, `*Mapper.xml` | 数据访问层、SQL映射 |
| JPA/Hibernate | `@Entity`, `@Repository` | 实体关系、持久化 |
| Dubbo | `@DubboService`, `@DubboReference` | RPC接口、服务提供者/消费者 |

## 核心模块识别规则

### 1. 包结构分析（Package Structure）

> ⚠️ **不可协商**：必须基于包结构识别多个独立的 Domain，禁止将整个项目视为单一 Domain。

#### 标准分层架构

```
com.example.project/
├── controller/          # 表现层 → 识别 API 入口
├── service/             # 业务层 → 识别业务逻辑
│   └── impl/            # 实现类
├── repository/          # 数据层 → 识别数据操作
├── entity/              # 实体层 → 识别领域实体
├── dto/                 # 数据传输对象
├── vo/                  # 视图对象
└── config/              # 配置类
```

#### DDD 分层架构

```
com.example.project/
├── application/         # 应用层 → 识别应用服务
│   └── service/
├── domain/              # 领域层 → 核心业务逻辑
│   ├── model/           # 领域模型
│   ├── service/         # 领域服务
│   └── repository/      # 仓储接口
├── infrastructure/      # 基础设施层
│   ├── persistence/     # 持久化实现
│   └── external/        # 外部服务
└── interfaces/          # 接口层
    ├── api/             # API 接口
    └── facade/          # 门面
```

#### 模块化架构（多 Domain 识别）

```
com.example.project/
├── user/                # Domain 1: 用户管理
│   ├── controller/
│   ├── service/
│   └── entity/
├── order/               # Domain 2: 订单管理
│   ├── controller/
│   ├── service/
│   └── entity/
├── payment/             # Domain 3: 支付处理
│   ├── controller/
│   ├── service/
│   └── entity/
└── common/              # 通用模块（非独立 Domain）
    ├── util/
    └── exception/
```

### 2. Domain 划分策略

> ⚠️ **强制要求**：必须将项目划分为多个 Domain，每个 Domain 对应一个独立的业务领域。

#### 划分依据

1. **按业务模块划分**：
   - 识别顶层包下的业务子包（如 `user`, `order`, `payment`）
   - 每个业务子包作为一个独立的 Domain

2. **按聚合根划分**：
   - 识别核心实体（Entity）和聚合根（Aggregate Root）
   - 围绕聚合根划分 Domain 边界

3. **按服务边界划分**：
   - 识别独立的 Service 接口
   - 每组相关的 Service 作为一个 Domain

#### 划分规则

```
# 伪代码：Domain 划分逻辑
for each top_level_package in project:
    if is_business_module(top_level_package):  # 排除 common, util, config 等
        create_domain(top_level_package.name)
        analyze_entities(top_level_package)
        analyze_services(top_level_package)
        extract_usecases(top_level_package)
```

### 3. 实体识别规则

#### JPA 实体

```java
// 识别标记
@Entity
@Table(name = "xxx")
public class User {
    @Id
    private Long id;
    
    @Column
    private String name;
    
    @OneToMany  // 关联关系
    private List<Order> orders;
}
```

**提取要点**：
- 类名 → 实体名称
- 字段 → 属性列表
- 关联注解 → 实体关系

#### MyBatis 实体

```java
// 通常在 entity/model/domain 包下
public class User {
    private Long id;
    private String name;
    // getter/setter
}

// 对应 Mapper
@Mapper
public interface UserMapper {
    User selectById(Long id);
    int insert(User user);
}
```

**提取要点**：
- Mapper 接口方法 → 数据操作用例
- XML 中的 SQL → 业务规则

### 4. 服务识别规则

#### Service 接口

```java
public interface UserService {
    User createUser(UserDTO dto);           // 用例：创建用户
    User getUserById(Long id);              // 用例：查询用户
    void updateUser(Long id, UserDTO dto);  // 用例：更新用户
    void deleteUser(Long id);               // 用例：删除用户
    List<User> searchUsers(SearchCriteria criteria);  // 用例：搜索用户
}
```

**提取要点**：
- 方法名 → 用例名称
- 参数 → 输入数据
- 返回值 → 输出数据
- 方法注释 → 业务描述

#### Controller 接口

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody UserDTO dto) {
        // 用例：创建用户
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        // 用例：获取用户详情
    }
}
```

**提取要点**：
- HTTP 方法 + 路径 → API 设计
- 请求体/参数 → 输入规范
- 响应体 → 输出规范

### 5. 业务规则识别

#### 从注解中提取

```java
@NotNull(message = "用户名不能为空")           // 规则：必填校验
@Size(min = 2, max = 50)                      // 规则：长度限制
@Pattern(regexp = "^[a-zA-Z0-9]+$")           // 规则：格式校验
@Email                                         // 规则：邮箱格式
```

#### 从业务逻辑中提取

```java
public void createOrder(OrderDTO dto) {
    // 规则1：库存检查
    if (inventory.getStock(dto.getProductId()) < dto.getQuantity()) {
        throw new InsufficientStockException();
    }
    
    // 规则2：价格计算
    BigDecimal total = calculateTotal(dto);
    
    // 规则3：折扣应用
    if (user.isVip()) {
        total = total.multiply(VIP_DISCOUNT);
    }
}
```

## 分析输出模板

### Domain 识别报告

```markdown
## 识别的 Domain 列表

### Domain 1: [domain-name]
- **包路径**: com.example.project.user
- **核心实体**: User, UserProfile, UserRole
- **主要服务**: UserService, UserAuthService
- **API 入口**: UserController
- **用例数量**: 12

### Domain 2: [domain-name]
...
```

### 用例提取模板

```markdown
## [Domain Name] - 用例列表

### 001-[subdomain]/001-[usecase-name].md

**来源**: UserService.createUser()
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
- BR002: 密码长度 8-20 位
```

## 注意事项

1. **禁止单一 Domain**：必须识别并划分多个独立的业务 Domain
2. **深度分析**：不仅分析接口，还要深入实现类理解业务逻辑
3. **关注注释**：Java 代码中的 Javadoc 注释是重要的业务描述来源
4. **识别模式**：注意常见的设计模式（工厂、策略、观察者等）
5. **事务边界**：`@Transactional` 注解标识的方法通常是完整的业务操作

