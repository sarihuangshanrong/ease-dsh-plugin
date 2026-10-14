# Java 编码最佳实践指南

本指南提供 Java 项目的编码规范、设计模式和最佳实践。

## 代码风格规范

### 命名规范

```java
// 类名：大驼峰命名
public class UserService {}
public class OrderController {}

// 接口名：大驼峰命名，不加 I 前缀
public interface UserRepository {}

// 方法名：小驼峰命名，动词开头
public User getUserById(Long id) {}
public void createOrder(OrderDTO dto) {}
public boolean isValidEmail(String email) {}

// 变量名：小驼峰命名
private String userName;
private List<Order> orderList;

// 常量：全大写，下划线分隔
public static final int MAX_RETRY_COUNT = 3;
public static final String DEFAULT_CHARSET = "UTF-8";

// 枚举值：全大写
public enum OrderStatus {
    PENDING, PROCESSING, COMPLETED, CANCELLED
}
```

### 代码格式

```java
// 缩进：4 个空格
// 大括号：同行左括号
public class Example {
    public void method() {
        if (condition) {
            // 代码
        } else {
            // 代码
        }
    }
}

// 行宽限制：120 字符
// 方法长度：建议不超过 50 行
// 类长度：建议不超过 500 行
```

## Spring Boot 最佳实践

### Controller 层

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Tag(name = "用户管理", description = "用户相关的 API 接口")
public class UserController {

    private final UserService userService;

    @PostMapping
    @Operation(summary = "创建用户")
    public ResponseEntity<ApiResponse<UserVO>> createUser(
            @Valid @RequestBody CreateUserRequest request) {
        UserVO user = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(user));
    }

    @GetMapping("/{id}")
    @Operation(summary = "获取用户详情")
    public ResponseEntity<ApiResponse<UserVO>> getUser(
            @PathVariable("id") Long id) {
        UserVO user = userService.getUserById(id);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    @PutMapping("/{id}")
    @Operation(summary = "更新用户")
    public ResponseEntity<ApiResponse<UserVO>> updateUser(
            @PathVariable("id") Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        UserVO user = userService.updateUser(id, request);
        return ResponseEntity.ok(ApiResponse.success(user));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除用户")
    public ResponseEntity<Void> deleteUser(@PathVariable("id") Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }
}
```

**要点**：
- 使用 `@RequiredArgsConstructor` + `final` 字段实现构造器注入
- 使用 `@Valid` 进行参数校验
- 统一响应格式 `ApiResponse<T>`
- 使用 OpenAPI 注解文档化接口

### Service 层

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;

    @Override
    @Transactional
    public UserVO createUser(CreateUserRequest request) {
        // 1. 业务校验
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS);
        }

        // 2. 构建实体
        User user = User.builder()
                .name(request.getName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .status(UserStatus.ACTIVE)
                .createdAt(LocalDateTime.now())
                .build();

        // 3. 持久化
        user = userRepository.save(user);
        log.info("用户创建成功: userId={}, email={}", user.getId(), user.getEmail());

        // 4. 转换返回
        return userMapper.toVO(user);
    }

    @Override
    @Transactional(readOnly = true)
    public UserVO getUserById(Long id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return userMapper.toVO(user);
    }

    @Override
    @Transactional
    public UserVO updateUser(Long id, UpdateUserRequest request) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // 使用 Optional 处理部分更新
        Optional.ofNullable(request.getName()).ifPresent(user::setName);
        Optional.ofNullable(request.getPhone()).ifPresent(user::setPhone);
        
        user.setUpdatedAt(LocalDateTime.now());
        user = userRepository.save(user);
        
        return userMapper.toVO(user);
    }

    @Override
    @Transactional
    public void deleteUser(Long id) {
        if (!userRepository.existsById(id)) {
            throw new BusinessException(ErrorCode.USER_NOT_FOUND);
        }
        userRepository.deleteById(id);
        log.info("用户删除成功: userId={}", id);
    }
}
```

**要点**：
- 使用 `@Transactional` 管理事务，只读方法使用 `readOnly = true`
- 使用自定义业务异常 `BusinessException` 和错误码
- 使用 Builder 模式构建实体
- 添加关键操作日志

### Repository 层

```java
// JPA Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByEmail(String email);
    
    boolean existsByEmail(String email);
    
    @Query("SELECT u FROM User u WHERE u.status = :status AND u.createdAt > :since")
    List<User> findActiveUsersSince(
            @Param("status") UserStatus status,
            @Param("since") LocalDateTime since);
    
    @Modifying
    @Query("UPDATE User u SET u.status = :status WHERE u.id = :id")
    int updateStatus(@Param("id") Long id, @Param("status") UserStatus status);
}

// MyBatis Mapper
@Mapper
public interface UserMapper {
    
    @Select("SELECT * FROM users WHERE id = #{id}")
    User selectById(Long id);
    
    @Insert("INSERT INTO users(name, email, password) VALUES(#{name}, #{email}, #{password})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
    
    // 复杂查询使用 XML 映射
    List<User> selectByCondition(UserQueryCondition condition);
}
```

### Entity 设计

```java
@Entity
@Table(name = "users")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @Column(nullable = false)
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private UserStatus status;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Order> orders;
}
```

### DTO/VO 设计

```java
// 请求 DTO
@Data
public class CreateUserRequest {
    
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 50, message = "用户名长度必须在 2-50 之间")
    private String name;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @NotBlank(message = "密码不能为空")
    @Size(min = 8, max = 20, message = "密码长度必须在 8-20 之间")
    private String password;
}

// 响应 VO
@Data
@Builder
public class UserVO {
    private Long id;
    private String name;
    private String email;
    private String status;
    private LocalDateTime createdAt;
}

// 统一响应格式
@Data
@Builder
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;
    private LocalDateTime timestamp;

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
                .code(0)
                .message("success")
                .data(data)
                .timestamp(LocalDateTime.now())
                .build();
    }

    public static <T> ApiResponse<T> error(int code, String message) {
        return ApiResponse.<T>builder()
                .code(code)
                .message(message)
                .timestamp(LocalDateTime.now())
                .build();
    }
}
```

## 异常处理

### 自定义业务异常

```java
@Getter
public class BusinessException extends RuntimeException {
    
    private final ErrorCode errorCode;
    private final Object[] args;

    public BusinessException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.args = null;
    }

    public BusinessException(ErrorCode errorCode, Object... args) {
        super(String.format(errorCode.getMessage(), args));
        this.errorCode = errorCode;
        this.args = args;
    }
}

@Getter
@AllArgsConstructor
public enum ErrorCode {
    
    // 通用错误 1xxx
    SYSTEM_ERROR(1000, "系统错误"),
    PARAM_ERROR(1001, "参数错误: %s"),
    
    // 用户相关 2xxx
    USER_NOT_FOUND(2001, "用户不存在"),
    EMAIL_ALREADY_EXISTS(2002, "邮箱已被注册"),
    PASSWORD_INCORRECT(2003, "密码错误"),
    
    // 订单相关 3xxx
    ORDER_NOT_FOUND(3001, "订单不存在"),
    INSUFFICIENT_STOCK(3002, "库存不足");

    private final int code;
    private final String message;
}
```

### 全局异常处理

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException e) {
        log.warn("业务异常: code={}, message={}", e.getErrorCode().getCode(), e.getMessage());
        return ResponseEntity.badRequest()
                .body(ApiResponse.error(e.getErrorCode().getCode(), e.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidationException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldErrors().stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.joining(", "));
        log.warn("参数校验失败: {}", message);
        return ResponseEntity.badRequest()
                .body(ApiResponse.error(ErrorCode.PARAM_ERROR.getCode(), message));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception e) {
        log.error("系统异常", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.error(ErrorCode.SYSTEM_ERROR.getCode(), "系统繁忙，请稍后重试"));
    }
}
```

## 设计模式应用

### 策略模式

```java
// 策略接口
public interface PaymentStrategy {
    PaymentResult pay(Order order);
    PaymentType getType();
}

// 具体策略
@Component
public class AlipayStrategy implements PaymentStrategy {
    @Override
    public PaymentResult pay(Order order) {
        // 支付宝支付逻辑
    }
    
    @Override
    public PaymentType getType() {
        return PaymentType.ALIPAY;
    }
}

@Component
public class WechatPayStrategy implements PaymentStrategy {
    @Override
    public PaymentResult pay(Order order) {
        // 微信支付逻辑
    }
    
    @Override
    public PaymentType getType() {
        return PaymentType.WECHAT;
    }
}

// 策略上下文
@Component
@RequiredArgsConstructor
public class PaymentContext {
    
    private final Map<PaymentType, PaymentStrategy> strategyMap;

    @Autowired
    public PaymentContext(List<PaymentStrategy> strategies) {
        this.strategyMap = strategies.stream()
                .collect(Collectors.toMap(PaymentStrategy::getType, Function.identity()));
    }

    public PaymentResult pay(PaymentType type, Order order) {
        PaymentStrategy strategy = strategyMap.get(type);
        if (strategy == null) {
            throw new BusinessException(ErrorCode.UNSUPPORTED_PAYMENT_TYPE);
        }
        return strategy.pay(order);
    }
}
```

### 建造者模式

```java
// 使用 Lombok @Builder
@Data
@Builder
public class Order {
    private Long id;
    private Long userId;
    private BigDecimal amount;
    private OrderStatus status;
    private List<OrderItem> items;
    private LocalDateTime createdAt;
}

// 使用
Order order = Order.builder()
        .userId(userId)
        .amount(calculateTotal(items))
        .status(OrderStatus.PENDING)
        .items(items)
        .createdAt(LocalDateTime.now())
        .build();
```

### 模板方法模式

```java
public abstract class AbstractExportService<T> {
    
    public final void export(ExportRequest request, OutputStream outputStream) {
        // 1. 查询数据
        List<T> data = queryData(request);
        
        // 2. 数据转换
        List<Map<String, Object>> rows = data.stream()
                .map(this::convertToRow)
                .collect(Collectors.toList());
        
        // 3. 写入文件
        writeToFile(rows, outputStream);
        
        // 4. 后置处理
        afterExport(request);
    }
    
    protected abstract List<T> queryData(ExportRequest request);
    
    protected abstract Map<String, Object> convertToRow(T item);
    
    protected void writeToFile(List<Map<String, Object>> rows, OutputStream outputStream) {
        // 默认 Excel 导出实现
    }
    
    protected void afterExport(ExportRequest request) {
        // 默认空实现，子类可选覆盖
    }
}

@Service
public class UserExportService extends AbstractExportService<User> {
    
    @Override
    protected List<User> queryData(ExportRequest request) {
        return userRepository.findAll();
    }
    
    @Override
    protected Map<String, Object> convertToRow(User user) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("ID", user.getId());
        row.put("用户名", user.getName());
        row.put("邮箱", user.getEmail());
        return row;
    }
}
```

## 性能优化

### 数据库查询优化

```java
// 1. 避免 N+1 问题：使用 JOIN FETCH
@Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = :id")
Optional<User> findByIdWithOrders(@Param("id") Long id);

// 2. 分页查询
Page<User> findByStatus(UserStatus status, Pageable pageable);

// 使用
Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
Page<User> users = userRepository.findByStatus(UserStatus.ACTIVE, pageable);

// 3. 只查询需要的字段
@Query("SELECT new com.example.dto.UserSimpleDTO(u.id, u.name) FROM User u")
List<UserSimpleDTO> findAllSimple();

// 4. 批量操作
@Modifying
@Query("UPDATE User u SET u.status = :status WHERE u.id IN :ids")
int batchUpdateStatus(@Param("ids") List<Long> ids, @Param("status") UserStatus status);
```

### 缓存使用

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    
    @Override
    @Cacheable(value = "users", key = "#id")
    public UserVO getUserById(Long id) {
        // 查询逻辑
    }
    
    @Override
    @CacheEvict(value = "users", key = "#id")
    public UserVO updateUser(Long id, UpdateUserRequest request) {
        // 更新逻辑
    }
    
    @Override
    @Caching(evict = {
        @CacheEvict(value = "users", key = "#id"),
        @CacheEvict(value = "userList", allEntries = true)
    })
    public void deleteUser(Long id) {
        // 删除逻辑
    }
}
```

### 异步处理

```java
@Service
@RequiredArgsConstructor
public class NotificationService {
    
    private final EmailSender emailSender;
    
    @Async("taskExecutor")
    public CompletableFuture<Void> sendWelcomeEmail(User user) {
        emailSender.send(user.getEmail(), "欢迎注册", "...");
        return CompletableFuture.completedFuture(null);
    }
}

// 配置线程池
@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(20);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
}
```

## 安全实践

### 输入验证

```java
// 使用 Bean Validation
@Data
public class CreateUserRequest {
    
    @NotBlank
    @Size(max = 100)
    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "用户名只能包含字母、数字和下划线")
    private String username;
    
    @NotBlank
    @Email
    private String email;
    
    @NotBlank
    @Size(min = 8, max = 50)
    private String password;
}
```

### SQL 注入防护

```java
// 正确：使用参数化查询
@Query("SELECT u FROM User u WHERE u.name = :name")
List<User> findByName(@Param("name") String name);

// 错误：字符串拼接（SQL 注入风险）
// "SELECT * FROM users WHERE name = '" + name + "'"
```

### 敏感数据处理

```java
// 响应中脱敏
@Data
public class UserVO {
    private Long id;
    private String name;
    
    @JsonSerialize(using = EmailMaskSerializer.class)
    private String email;  // 显示为 t***@example.com
    
    // 不返回密码字段
}

// 日志脱敏
log.info("用户登录: email={}", maskEmail(user.getEmail()));
```

## 测试实践

### 单元测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceImplTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private PasswordEncoder passwordEncoder;
    
    @InjectMocks
    private UserServiceImpl userService;
    
    @Test
    void createUser_Success() {
        // Given
        CreateUserRequest request = new CreateUserRequest();
        request.setName("test");
        request.setEmail("test@example.com");
        request.setPassword("password123");
        
        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(passwordEncoder.encode(anyString())).thenReturn("encodedPassword");
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(1L);
            return user;
        });
        
        // When
        UserVO result = userService.createUser(request);
        
        // Then
        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("test", result.getName());
        verify(userRepository).save(any(User.class));
    }
    
    @Test
    void createUser_EmailExists_ThrowsException() {
        // Given
        CreateUserRequest request = new CreateUserRequest();
        request.setEmail("existing@example.com");
        
        when(userRepository.existsByEmail(request.getEmail())).thenReturn(true);
        
        // When & Then
        BusinessException exception = assertThrows(BusinessException.class,
                () -> userService.createUser(request));
        assertEquals(ErrorCode.EMAIL_ALREADY_EXISTS, exception.getErrorCode());
    }
}
```

### 集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    void createUser_Success() throws Exception {
        CreateUserRequest request = new CreateUserRequest();
        request.setName("test");
        request.setEmail("test@example.com");
        request.setPassword("password123");
        
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.name").value("test"))
                .andExpect(jsonPath("$.data.email").value("test@example.com"));
    }
}
```

## 注意事项

1. **遵循项目规范**：优先遵循项目已有的代码风格和架构模式
2. **保持简单**：不要过度设计，优先选择简单方案
3. **关注性能**：数据库查询、缓存使用需要根据实际场景优化
4. **安全第一**：输入验证、SQL 注入防护、敏感数据处理是必须的
5. **测试覆盖**：核心业务逻辑必须有单元测试覆盖

