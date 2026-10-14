# Java 测试生成参考文档

本指南提供了为 Java 项目生成单元测试代码的具体规范和最佳实践。

## 测试框架选择

### 主要测试框架

1. **JUnit 5**: 现代化的测试框架，推荐用于新项目
2. **Mockito**: Mock框架，用于创建和管理Mock对象
3. **AssertJ**: 流畅的断言库，提供更好的断言体验
4. **Testcontainers**: 用于集成测试的容器化依赖管理

### Maven依赖配置

```xml
<dependencies>
    <!-- JUnit 5 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>

    <!-- Mockito -->
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.7.0</version>
        <scope>test</scope>
    </dependency>

    <!-- AssertJ -->
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.24.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## 测试类结构规范

### 基础测试类模板

> **标准范式（JUnit 5 + Mockito）**：使用 `@ExtendWith(MockitoExtension.class)` + `@InjectMocks`，**不要**用旧式的 `MockitoAnnotations.openMocks(this)` 手动初始化。`MockitoExtension` 默认开启 **strict stubbing**，会自动抛出 `UnnecessaryStubbingException` 捕捉"无用的 mock 打桩"，从工具层防住过度 Mock（呼应 `testing-anti-patterns.md` 的"Mock without understanding"）。

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    // Mock依赖（由扩展自动初始化）
    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    // 被测对象（自动注入上面的 mock）
    @InjectMocks
    private UserService userService;

    @Test
    void getUserById_userExists_returnsUserWithExpectedFields() {
        // Given (准备测试数据 + 打桩)

        // When (执行被测方法)

        // Then (强断言：精确值/状态/交互，达到断言价值 L2+)
    }
}
```

> 若被测对象需要注入 `Clock`/`Random` 等不可由 `@InjectMocks` 自动提供的非 mock 依赖，则改用构造注入手动 `new UserService(userRepository, emailService, fixedClock)`（见"时间相关测试"）。

### 测试方法命名规范

采用 `testMethodName_Condition_ExpectedBehavior` 的命名模式：

```java
@Test
void getUserById_UserExists_ReturnsUser() {
    // 测试getUserById方法，当用户存在时，应该返回用户对象
}

@Test
void getUserById_UserNotFound_ThrowsException() {
    // 测试getUserById方法，当用户不存在时，应该抛出异常
}

@Test
void createUser_ValidUser_SendsWelcomeEmail() {
    // 测试createUser方法，当用户提供有效信息时，应该发送欢迎邮件
}
```

## Mock使用规范

### Mockito基本用法

```java
// Mock对象创建
@Mock
private UserRepository userRepository;

// Stub行为定义
when(userRepository.findById(1L)).thenReturn(Optional.of(user));

// 验证方法调用
verify(userRepository).findById(1L);

// 验证方法调用次数
verify(userRepository, times(1)).findById(1L);
verify(userRepository, never()).deleteById(anyLong());
```

### 常见Mock场景

#### 1. 返回固定值
```java
when(userRepository.findById(1L)).thenReturn(Optional.of(user));
```

#### 2. 抛出异常
```java
when(userRepository.findById(1L)).thenThrow(new UserNotFoundException("User not found"));
```

#### 3. 根据参数返回不同值
```java
when(userRepository.findById(1L)).thenReturn(Optional.of(user1));
when(userRepository.findById(2L)).thenReturn(Optional.of(user2));
```

#### 4. 使用参数匹配器
```java
when(userRepository.save(argThat(user -> user.getEmail().contains("@")))).thenReturn(savedUser);
```

## 断言规范

### 使用AssertJ进行断言

```java
// 基本断言
assertThat(result).isNotNull();
assertThat(name).isEqualTo("John");
assertThat(age).isGreaterThan(18);

// 集合断言
assertThat(users).hasSize(3);
assertThat(names).containsExactly("Alice", "Bob", "Charlie");

// 异常断言
assertThatThrownBy(() -> userService.getUserById(-1L))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessage("User ID must be positive");

// 对象属性断言
assertThat(user)
    .extracting(User::getName, User::getEmail)
    .containsExactly("John", "john@example.com");
```

## 测试数据管理

### 测试数据工厂

```java
public class UserTestDataFactory {

    public static User createUser() {
        return createUser("John", "john@example.com");
    }

    public static User createUser(String name, String email) {
        User user = new User();
        user.setId(1L);
        user.setName(name);
        user.setEmail(email);
        // 测试数据用固定时间，保持确定性（避免读取系统时钟引入不可重复性）
        user.setCreatedAt(LocalDateTime.of(2026, 6, 30, 8, 0, 0));
        return user;
    }

    public static List<User> createUsers(int count) {
        List<User> users = new ArrayList<>();
        for (int i = 1; i <= count; i++) {
            User user = new User();
            user.setId((long) i);
            user.setName("User " + i);
            user.setEmail("user" + i + "@example.com");
            users.add(user);
        }
        return users;
    }
}
```

### 使用@TestInstance管理测试实例

```java
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class UserServiceIntegrationTest {

    private DatabaseContainer dbContainer;

    @BeforeAll
    void setUpAll() {
        dbContainer = new DatabaseContainer();
        dbContainer.start();
    }

    @AfterAll
    void tearDownAll() {
        dbContainer.stop();
    }
}
```

## 不同类型代码的测试策略

### 1. Service层测试

```java
@Test
void createUser_ValidUser_CreatesUserAndSendsEmail() {
    // Given
    UserDto userDto = new UserDto("John", "john@example.com");
    User user = UserTestDataFactory.createUser("John", "john@example.com");

    when(userRepository.save(any(User.class))).thenReturn(user);

    // When
    User result = userService.createUser(userDto);

    // Then
    assertThat(result).isNotNull();
    assertThat(result.getName()).isEqualTo("John");

    verify(userRepository).save(argThat(u ->
        u.getName().equals("John") && u.getEmail().equals("john@example.com")));
    verify(emailService).sendWelcomeEmail("john@example.com");
}
```

### 2. Controller层测试

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void getUserById_UserExists_ReturnsUser() throws Exception {
        // Given
        User user = UserTestDataFactory.createUser();
        when(userService.getUserById(1L)).thenReturn(user);

        // When & Then
        mockMvc.perform(get("/users/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("John"))
                .andExpect(jsonPath("$.email").value("john@example.com"));

        verify(userService).getUserById(1L);
    }
}
```

### 3. Repository层测试

```java
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_UserExists_ReturnsUser() {
        // Given
        User user = UserTestDataFactory.createUser();
        entityManager.persistAndFlush(user);

        // When
        Optional<User> result = userRepository.findByEmail("john@example.com");

        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getName()).isEqualTo("John");
    }
}
```

## 测试覆盖率要求

### 代码覆盖率指标

- **行覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 70%
- **方法覆盖率**: ≥ 85%

### 覆盖率检查配置

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.70</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## 常见测试模式

### 1. Builder模式测试

```java
@Test
void userBuilder_BuildsUserWithCorrectProperties() {
    User user = User.builder()
            .id(1L)
            .name("John")
            .email("john@example.com")
            .build();

    assertThat(user.getId()).isEqualTo(1L);
    assertThat(user.getName()).isEqualTo("John");
    assertThat(user.getEmail()).isEqualTo("john@example.com");
}
```

### 2. 异常测试

```java
@Test
void createUser_NullName_ThrowsIllegalArgumentException() {
    assertThatThrownBy(() -> userService.createUser(null, "john@example.com"))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessage("Name cannot be null or empty");
}
```

### 3. 时间相关测试（必须注入 Clock，禁止 now() 夹逼）

> ⚠️ **禁止** `LocalDateTime.now()` 夹逼断言（`isBetween(before, after)`）：它依赖真实时钟，结果非确定，违背 FIRST 的 Repeatable 原则。**正确做法是向被测代码注入 `java.time.Clock`，测试用 `Clock.fixed(...)` 固定时间**，断言精确值（L2）。

```java
// 生产代码：通过构造注入 Clock，不直接读取系统时钟
class UserService {
    private final Clock clock;
    private final UserRepository repository;

    UserService(UserRepository repository, Clock clock) {
        this.repository = repository;
        this.clock = clock;
    }

    User createUser(String name, String email) {
        User user = new User(name, email);
        user.setCreatedAt(LocalDateTime.now(clock));  // 用注入的 clock
        return repository.save(user);
    }
}
```

```java
@Test
void createUser_setsCreatedAtToFixedClockInstant() {
    // Given：固定时钟，使时间完全确定
    Instant fixedInstant = Instant.parse("2026-06-30T08:00:00Z");
    Clock fixedClock = Clock.fixed(fixedInstant, ZoneOffset.UTC);
    UserService userService = new UserService(userRepository, fixedClock);
    when(userRepository.save(any(User.class))).thenAnswer(inv -> inv.getArgument(0));

    // When
    User user = userService.createUser("John", "john@example.com");

    // Then：断言精确时间（L2），而非"落在某个区间"
    assertThat(user.getCreatedAt())
        .isEqualTo(LocalDateTime.ofInstant(fixedInstant, ZoneOffset.UTC));
}
```

> 同理，随机数应注入 `Random(seed)` 或 `RandomGenerator`，UUID 应注入 `Supplier<UUID>`，使测试可重复。

## 最佳实践

### 1. 测试隔离

```java
// 每个测试方法独立运行，不共享状态
@Test
void test1() {
    // 测试逻辑
}

@Test
void test2() {
    // 独立的测试逻辑，不受test1影响
}
```

### 2. 避免测试间依赖

```java
// 不要在测试间共享数据或状态
class BadExample {
    private static User sharedUser; // 避免这样做

    @Test
    void test1() {
        sharedUser = createUser(); // 避免这样做
    }

    @Test
    void test2() {
        assertThat(sharedUser).isNotNull(); // 避免这样做
    }
}
```

### 3. 清晰的测试意图

```java
// 好的命名清楚表达了测试意图
@Test
void calculateDiscount_OrderOver100_Returns10PercentDiscount() {
    // 测试逻辑
}

// 避免模糊的命名
@Test
void test1() { // 不推荐
    // 测试逻辑
}
```

## MC/DC测试设计

### MC/DC原则说明

MC/DC (Modified Condition/Decision Coverage) 是一种严格的测试覆盖准则，要求：
- **条件独立性**：每个条件能**独立**影响决策结果——固定其余所有条件，仅翻转目标条件，决策结果必须随之改变
- **分支全覆盖**：所有分支路径都被测试
- **边界值测试**：测试输入域的边界及其附近值

### MC/DC 操作铁律（避免写出"假独立性"测试）

> ⚠️ 一个独立性测试**只能改动一个条件**。如果一个用例同时改了两个条件，它无法证明任何单一条件的独立影响——这是 MC/DC 最常见的错误。

**正确步骤**：
1. **先列真值表**：枚举条件组合 → 决策结果，找出每个条件的"独立对（independence pair）"——即仅该条件不同、决策结果也不同的两行。
2. **固定条件集**：对每个独立性测试，明确写出"**固定哪些条件、取什么值、为什么**"。
3. **仅翻转目标条件**：在两个断言之间，只改目标条件一个变量，其余逐字不变。

**关键技巧**：当目标条件在决策式中出现于某个子句，需让**其他子句恒为某固定值**，使决策结果完全由目标条件所在子句决定。

### 以 `(C1∧C2∧C3) ∨ (C1∧C4)` 为例的独立对真值表

| 用例 | C1 goodCredit | C2 goodDebtRatio | C3 stableEmployment | C4 reasonableAmount | 决策 | 证明谁独立 |
|------|------|------|------|------|------|-----------|
| T-C2a | T | **F** | T | F | **false** | C2（固定 C1=T,C3=T,C4=F → 子句2 false，结果由 C2 决定） |
| T-C2b | T | **T** | T | F | **true** | 同上，仅翻转 C2 |
| T-C3a | T | T | **F** | F | **false** | C3（固定 C1=T,C2=T,C4=F → 子句2 false，结果由 C3 决定） |
| T-C3b | T | T | **T** | F | **true** | 同上，仅翻转 C3 |
| T-C4a | T | **F** | F | **F** | **false** | C4（固定 C1=T,C2=F,C3=F → 子句1 恒 false，结果由 C4 决定） |
| T-C4b | T | F | F | **T** | **true** | 同上，仅翻转 C4 |
| T-C1a | **F** | T | T | T | **false** | C1（固定 C2=T,C3=T,C4=T，仅翻转 C1） |
| T-C1b | **T** | T | T | T | **true** | 同上，仅翻转 C1 |

> 注意 T-C4a/T-C4b：为隔离 C4，必须让子句1 `(C1∧C2∧C3)` 恒为 false（这里令 C2=F、C3=F），否则翻转 C4 不会改变已经为 true 的决策。**固定 C2=F、C3=F 是有意的设计，不是疏忽。**

### 复杂决策逻辑的MC/DC测试示例

```java
// 贷款审批决策逻辑
public boolean approveLoan(User user, LoanRequest request) {
    // 条件1: 信用评分 >= 650
    boolean goodCredit = user.getCreditScore() >= 650;
    // 条件2: 负债率 <= 0.43
    boolean goodDebtRatio = user.getDebtToIncomeRatio() <= 0.43;
    // 条件3: 就业稳定性 >= 2年
    boolean stableEmployment = user.getEmploymentYears() >= 2;
    // 条件4: 贷款金额合理
    boolean reasonableAmount = request.getAmount()
        .compareTo(user.getAnnualIncome().multiply(BigDecimal.valueOf(4))) <= 0;

    // 决策：(条件1 AND 条件2 AND 条件3) OR (条件1 AND 条件4)
    return (goodCredit && goodDebtRatio && stableEmployment) ||
           (goodCredit && reasonableAmount);
}
```

### MC/DC测试用例设计

```java
@Test
void testGoodCreditIndependence() {
    // 【固定条件集】固定 C2=true、C3=true、C4=true，仅翻转 C1。对应真值表 T-C1a / T-C1b。
    // 说明：C1 在两个子句中都出现。当 C1=false 时两子句皆 false → 决策 false；
    // C1=true 时子句1 (T∧T∧T)=true → 决策 true。故仅翻转 C1 即可改变决策，独立性成立。
    User user = User.builder()
        .id(1L)
        .name("Test User")
        .creditScore(600)         // C1 goodCredit = false
        .debtToIncomeRatio(0.35)  // C2 goodDebtRatio = true（固定）
        .employmentYears(5)       // C3 stableEmployment = true（固定）
        .annualIncome(new BigDecimal("50000"))
        .build();

    LoanRequest request = LoanRequest.builder()
        .id(1L)
        .amount(new BigDecimal("150000"))  // C4 reasonableAmount = true（固定）
        .build();

    assertThat(loanService.approveLoan(user, request)).isFalse();

    // 【仅翻转 C1】goodCredit = true，其余逐字不变
    user.setCreditScore(700);
    assertThat(loanService.approveLoan(user, request)).isTrue();
}

@Test
void testGoodDebtRatioIndependence() {
    // 【固定条件集】为隔离 C2，需让子句2 (C1∧C4) 恒为 false。
    // 这里固定 C1=true、C3=true、C4=false（金额超标 → 子句2 false），仅翻转 C2。对应 T-C2a / T-C2b。
    User user = User.builder()
        .id(1L)
        .name("Test User")
        .creditScore(700)         // C1 goodCredit = true（固定）
        .debtToIncomeRatio(0.50)  // C2 goodDebtRatio = false
        .employmentYears(5)       // C3 stableEmployment = true（固定）
        .annualIncome(new BigDecimal("50000"))
        .build();

    // C4=false：金额 250000 > 4×50000 → 子句2 恒 false，结果由子句1（含 C2）决定
    LoanRequest request = LoanRequest.builder()
        .id(1L)
        .amount(new BigDecimal("250000"))
        .build();

    assertThat(loanService.approveLoan(user, request)).isFalse();

    // 【仅翻转 C2】goodDebtRatio = true → 子句1 (T∧T∧T)=true → 决策 true
    user.setDebtToIncomeRatio(0.35);
    assertThat(loanService.approveLoan(user, request)).isTrue();
}

@Test
void testStableEmploymentIndependence() {
    // 【固定条件集】为隔离 C3，需让子句2 (C1∧C4) 恒为 false。
    // 固定 C1=true、C2=true、C4=false（金额超标），仅翻转 C3。对应 T-C3a / T-C3b。
    User user = User.builder()
        .id(1L)
        .name("Test User")
        .creditScore(700)         // C1 goodCredit = true（固定）
        .debtToIncomeRatio(0.35)  // C2 goodDebtRatio = true（固定）
        .employmentYears(1)       // C3 stableEmployment = false
        .annualIncome(new BigDecimal("50000"))
        .build();

    // C4=false：金额 250000 > 4×50000 → 子句2 恒 false，结果由子句1（含 C3）决定
    LoanRequest request = LoanRequest.builder()
        .id(1L)
        .amount(new BigDecimal("250000"))
        .build();

    assertThat(loanService.approveLoan(user, request)).isFalse();

    // 【仅翻转 C3】stableEmployment = true → 子句1 (T∧T∧T)=true → 决策 true
    user.setEmploymentYears(3);
    assertThat(loanService.approveLoan(user, request)).isTrue();
}

@Test
void testReasonableAmountIndependence() {
    // 【固定条件集】为隔离 C4(reasonableAmount)，必须让子句1 (C1∧C2∧C3) 恒为 false，
    // 使决策完全由子句2 (C1∧C4) 决定：固定 C1=true、C2=false、C3=false，仅翻转 C4。
    // 对应真值表 T-C4a / T-C4b。
    User user = User.builder()
        .id(1L)
        .name("Test User")
        .creditScore(700)         // C1 goodCredit = true（子句2 需要）
        .debtToIncomeRatio(0.50)  // C2 goodDebtRatio = false（有意：使子句1 恒 false）
        .employmentYears(1)       // C3 stableEmployment = false（有意：使子句1 恒 false）
        .annualIncome(new BigDecimal("50000"))
        .build();

    // C4=false：金额 250000 > 4×50000 → reasonableAmount = false
    LoanRequest request = LoanRequest.builder()
        .id(1L)
        .amount(new BigDecimal("250000"))
        .build();

    // 子句1 false ∧ 子句2(C1∧C4)=true∧false=false → 决策 false
    assertThat(loanService.approveLoan(user, request)).isFalse();

    // 【仅翻转 C4】金额 150000 ≤ 4×50000 → reasonableAmount = true，其余逐字不变
    request.setAmount(new BigDecimal("150000"));
    // 子句2 (C1∧C4)=true∧true=true → 决策 true，证明 C4 独立改变了结果
    assertThat(loanService.approveLoan(user, request)).isTrue();
}
```

### 边界值测试示例（优先参数化 + 强断言）

> 边界值是"同一行为、多组输入"，**优先用 `@ParameterizedTest`**（见后文"参数化测试"），断言用 `isEqualTo(expected)`（L3，区分边界两侧）。避免在一个方法里堆叠多次 `setXxx` + `assertTrue/assertFalse`——既弱又掩盖失败定位。

```java
// creditScore 边界（650 为阈值）：其余条件固定为可批准基线
@ParameterizedTest(name = "creditScore={0} → approved={1}")
@CsvSource({
    "649, false",  // 边界下侧
    "650, true",   // 边界值（>= 命中）
    "651, true"    // 边界上侧
})
void approveLoan_creditScoreBoundary(int creditScore, boolean expected) {
    User user = baseEligibleUser().toBuilder().creditScore(creditScore).build();
    LoanRequest request = reasonableRequest();

    assertThat(loanService.approveLoan(user, request)).isEqualTo(expected);
}

// debtToIncomeRatio 边界（0.43 为阈值）
@ParameterizedTest(name = "debtRatio={0} → approved={1}")
@CsvSource({
    "0.44, false",  // 边界上侧（超过上限）
    "0.43, true",   // 边界值（<= 命中）
    "0.42, true"    // 边界下侧
})
void approveLoan_debtRatioBoundary(double debtRatio, boolean expected) {
    User user = baseEligibleUser().toBuilder().debtToIncomeRatio(debtRatio).build();
    LoanRequest request = reasonableRequest();

    assertThat(loanService.approveLoan(user, request)).isEqualTo(expected);
}
```

> `baseEligibleUser()` / `reasonableRequest()` 为测试数据工厂方法，提供"除被测边界字段外其余均满足批准条件"的基线，使断言只受被测边界字段影响。

## 参数化测试（边界值/等价类首选）

> 边界值分析（BVA）和等价类划分（ECP）天然是"同一行为、多组输入"，**应优先用 `@ParameterizedTest` 而非复制多个单值测试方法**。这样既减少重复，又让边界数据集中、易补充。

### `@CsvSource`：边界值表

```java
@ParameterizedTest(name = "creditScore={0} → approved={1}")
@CsvSource({
    "649, false",   // 边界下侧
    "650, true",    // 边界值（含等于）
    "651, true"     // 边界上侧
})
void approveLoan_creditScoreBoundary(int creditScore, boolean expected) {
    User user = baseEligibleUser().toBuilder().creditScore(creditScore).build();
    LoanRequest request = reasonableRequest();

    // 强断言（L3）：边界两侧结果不同
    assertThat(loanService.approveLoan(user, request)).isEqualTo(expected);
}
```

### `@MethodSource`：复杂对象/多字段等价类

```java
static Stream<Arguments> paymentMethodCases() {
    return Stream.of(
        Arguments.of(PaymentMethod.CREDIT_CARD, true),
        Arguments.of(PaymentMethod.DEBIT_CARD, true),
        Arguments.of(PaymentMethod.E_WALLET, true),
        Arguments.of(PaymentMethod.UNKNOWN, false)   // 无效等价类
    );
}

@ParameterizedTest
@MethodSource("paymentMethodCases")
void validatePayment_byMethod(PaymentMethod method, boolean expectedValid) {
    assertThat(paymentValidator.isSupported(method)).isEqualTo(expectedValid);
}
```

> **何时不要参数化**：当每组输入需要**不同的断言逻辑**或不同的交互验证时（如一个返回值、一个抛异常），拆成独立测试更清晰；参数化仅适用于"同一断言形态、不同数据"的场景。

## 测试生成模板

### Service测试模板

```java
@Test
void methodName_Condition_ExpectedResult() {
    // Given
    // 准备测试数据和Mock行为

    // When
    // 调用被测方法

    // Then
    // 验证结果和Mock调用
}
```

### Controller测试模板

```java
@Test
void endpoint_Condition_ReturnsExpectedResponse() throws Exception {
    // Given
    // 准备测试数据和Mock行为

    // When & Then
    mockMvc.perform(post("/endpoint")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"key\":\"value\"}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.result").value("expected"));
}
```

### MC/DC测试模板

```java
@Test
void testConditionIndependence() {
    // 基线：目标条件=false, 其他条件=true
    TestData testData = TestData.builder()
        .targetCondition(false)  // 目标条件设为false
        .otherConditions(true)   // 其他条件设为true
        .build();

    assertThat(service.evaluateDecision(testData)).isFalse();

    // 改变目标条件：目标条件=true, 保持其他不变
    testData.setTargetCondition(true);  // 目标条件设为true
    assertThat(service.evaluateDecision(testData)).isTrue();
}
```

## 确定性隔离禁令速查（Java，对齐 SKILL.md D1–D9）

> D1/D3/D5/D6 由 lint 机械化（🔒 C1/C3/C4/C5）。下面补 D2/D4/D7/D8/D9 的 Java 正例。

### D2：mockStatic / mockConstruction 必须 close

```java
@Test
void should_stub_clock_static() {
    // ✅ try-with-resources：离开即 close，静态状态恢复，不污染其他测试
    try (MockedStatic<LocalDateTime> ms = mockStatic(LocalDateTime.class)) {
        ms.when(LocalDateTime::now)
          .thenReturn(LocalDateTime.of(2026, 6, 30, 8, 0, 0));
        // ... act + assert
    }
}
```

> 被测代码若持有静态/单例状态，须在 `@BeforeEach` 显式重置并注释，如 `StateHolder.resetForTest(); // D2：重置单例`。

### D4：无序集合不得直接比有序

```java
Map<String, Integer> actual = service.groupByCategory(items);  // 返回 HashMap

// ❌ 遍历顺序不定，偶发失败
assertThat(actual.keySet()).containsExactly("food", "toy", "book");

// ✅ 不关心顺序用 containsOnlyKeys；需顺序则源用 LinkedHashMap 再 containsExactly
assertThat(actual).containsOnlyKeys("food", "toy", "book");
```

### D7：端口 / 临时文件由框架分配

```java
@Test
void export_to_temp_dir(@TempDir Path dir) throws IOException {
    Path out = dir.resolve("export.csv");   // 框架分配，测试后自动清理
    service.export(out);
    assertThat(out).hasContent("id,name");
}

// Spring Boot 随机端口，避免端口冲突
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
```

### D8：时区 / Locale 显式指定

```java
// ❌ 依赖系统默认——CI 与本地不同即失败
LocalDateTime.parse("2026-06-30T08:00:00").atZone(ZoneId.systemDefault());
String.format(Locale.getDefault(), "%.1f", 1.5);

// ✅ 显式指定
LocalDateTime.parse("2026-06-30T08:00:00").atZone(ZoneOffset.UTC);
String.format(Locale.US, "%.1f", 1.5);
```

### D9：@BeforeAll 只建不可变 fixture

```java
// ❌ 类级钩子里建可变共享状态——破坏隔离
private static List<User> shared;
@BeforeAll static void init() { shared = new ArrayList<>(); shared.add(new User(...)); }

// ✅ 类级只保存真正不可变的值对象；record 的字段不可重新赋值
private record UserFixture(long id, String name) {}
private static final UserFixture BASE = new UserFixture(1L, "John");

// 可变领域对象仍然每测重建，不因引用 final 就误称为不可变
private User user;
@BeforeEach void setUp() { user = new User(BASE.id(), BASE.name()); }
```

通过遵循这些规范和最佳实践，可以生成高质量、可维护的Java单元测试代码。
