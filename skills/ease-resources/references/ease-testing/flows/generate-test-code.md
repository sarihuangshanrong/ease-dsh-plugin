# 生成测试代码流程

本文档描述分析源代码并生成单元测试代码的标准流程，强调 MC/DC 原则和分轮覆盖率提升策略。

> **数据流定位**：本流程处于"测什么（What）→ 怎么测（How）"链路的下游。上游 `ease-test-case-design`（flow-2-design §4.5）若已产出 `test-case-document.md`，本流程**必须先消费它**（见 Step 0），将需求驱动的黑盒测试案例落地为测试代码，并保持 UC/BR 追溯链贯穿到代码。

## 长期 TC 接入（新任务）

执行前读取 `ease-test-case-design/references/durable-test-assets.md`（相对 `references/`）。领域 TC 保存在 `docs/domains/${DOMAIN_ID}/testcases/`，跨域/架构 TC 在 `docs/qa/testcases/`；不创建 docs/testing。任务只保存 test-selection 和执行证据。

新任务优先读取 BRD `flow-2-design/test-cases/test-selection.json` 或 TRD `flow-1-analyze-trd/validation/test-selection.json`，按 path/revision/hash 加载长期 TC；存在但无效不得回退。下文 `test-case-document.md` 对新任务仅指从所选 TC 生成的只读可读投影，旧任务无 selection 时才兼容旧权威案例文件。接口报告与测试方法必须引用同一集合，不能重新从代码推导并丢弃它。


## Step 0：加载上游测试案例文档（不可跳过的前置检查）

> ⚠️ 在进入"第 1. 项目分析阶段"之前，**必须先执行本步骤**。

### 0.1 检测测试案例文档

```bash
# FEATURE_NAME 为当前特性目录名（与 .eases/${CHANGE_ID}/flow-2-design/ 一致）
TC_DOC=".eases/${CHANGE_ID}/flow-2-design/test-cases/test-case-document.md"
TC_SELECTION="${TEST_SELECTION_PATH:-.eases/${CHANGE_ID}/flow-2-design/test-cases/test-selection.json}"
if [ -f "$TC_SELECTION" ]; then
  echo "Load and validate pinned durable TCs; do not fall back on invalid selection"
elif [ -f "$TC_DOC" ]; then
  echo "✓ 检测到上游测试案例文档：$TC_DOC（作为测试用例的首要来源）"
else
  echo "ℹ️ 未检测到测试案例文档，回退到纯白盒（从代码逆向推导测试用例）"
fi
```

### 0.2 文档存在时（需求驱动，首选）

1. **Read 完整文档**，提取以下结构化信息（字段对应 `ease-test-case-design` 模板）：
   - 追溯矩阵（第 2 章）：`TC-XXX-NNN → UC-XXX / BR-XXX / 测试技术 / 优先级 / 测试层次`
   - 业务功能测试案例（第 3 章）：Given-When-Then、测试数据、关联规则
   - 接口测试案例（第 4 章）：参数校验（ECP/BVA）、错误响应、幂等/并发
   - 场景测试案例（第 5 章）：跨用例端到端链路
2. **建立"案例 → 测试方法"映射表**（产出物，见 0.4），每个 `TC-XXX-NNN` 对应一个测试方法。
3. **按测试层次分流**：
   - `测试层次 = 单元` 的案例 → 在本流程生成单元测试（MUST 隔离 I/O，见 SKILL.md 依赖策略）
   - `测试层次 = 集成` 的案例 → 标注为集成测试（用真实/容器化依赖），按 `/ease-tools:generate-tests --integration` 处理
4. **按优先级排序**：P1 案例优先生成且必须覆盖正常 + 异常 + 边界。
5. **保留追溯**：在生成的测试方法上，用注释/方法名携带 `TC-XXX-NNN` 与 `UC-XXX/BR-XXX`（见 0.3）。

### 0.3 测试方法命名与追溯注释规范

测试方法名应能读出行为；追溯信息放在方法名后缀或注释中：

```java
// TC-ORDER-012 | UC-003 下单 | BR-007 库存校验
@Test
void should_reject_order_when_stock_insufficient() {
    // Given-When-Then 直接来自 test-case-document.md §3.x 的对应案例
}
```

```go
// TC-ORDER-012 (UC-003 / BR-007)
func TestRejectOrderWhenStockInsufficient(t *testing.T) { ... }
```

### 0.4 产出物：案例覆盖映射表

```markdown
## 测试案例 → 测试代码映射

| 案例ID | UC/BR | 测试技术 | 层次 | 生成的测试方法 | 状态 |
|--------|-------|---------|------|--------------|------|
| TC-ORDER-001 | UC-003 / BR-005 | BVA | 单元 | OrderServiceTest#should_accept_min_amount | ✅ |
| TC-ORDER-012 | UC-003 / BR-007 | 判定表 | 单元 | OrderServiceTest#should_reject_when_stock_insufficient | ✅ |
| TC-API-ORDER-020 | UC-003 / BR-009 | 基于用例 | 集成 | （转交集成测试流程） | ⏭️ |
```

> **闭环要求**：文档中标记的全部 P1 案例必须在映射表中有对应测试方法（或显式标注转交集成测试）。未落地的 P1 案例必须说明原因。

### 0.5 文档不存在时（回退路径）

直接进入"第 1. 项目分析阶段"，从代码逆向推导测试用例（纯白盒）。此时第 3 阶段的"设计测试用例"仍按 MC/DC + 边界值正常执行。

## 流程总览

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           测试生成流程                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │ 1.项目分析  │───▶│ 2.可测试性  │───▶│ 3.测试策略  │                  │
│  │             │    │   审查      │    │   制定      │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│        │                  │                  │                          │
│        ▼                  ▼                  ▼                          │
│   检测语言/框架      TDD原则检查         MC/DC设计                       │
│   建立TODO列表       必要时重构          场景分类                        │
│   基线覆盖率         依赖注入检查        参数化测试                       │
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │ 4.代码生成  │───▶│ 5.分轮提升  │───▶│ 6.验证保证  │                  │
│  │             │    │             │    │             │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘                  │
│        │                  │                  │                          │
│        ▼                  ▼                  ▼                          │
│   生成测试类          5轮迭代           编译检查                         │
│   实现测试方法        每轮验证          运行测试                         │
│   添加Mock           分析未覆盖         覆盖率报告                       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 快速参考

| 阶段 | 关键动作 | 产出 |
|------|----------|------|
| 1. 项目分析 | 检测语言、框架、结构 | TODO列表、基线覆盖率 |
| 2. 可测试性审查 | TDD原则检查、重构建议 | 重构计划（如需要） |
| 3. 测试策略 | MC/DC设计、场景分类 | 测试用例设计文档 |
| 4. 代码生成 | 生成测试类和方法 | 测试代码文件 |
| 5. 分轮提升 | 5轮迭代提升覆盖率 | 每轮覆盖率报告 |
| 6. 验证保证 | 编译、运行、报告 | 最终质量报告 |

## 详细步骤

### 1. 项目分析阶段

#### 1.1 检测项目类型

使用 Glob 工具检测项目根目录的特征文件：

| 语言 | 特征文件 | 源码目录 | 测试目录 |
|------|---------|----------|----------|
| Java | `pom.xml` / `build.gradle` | `src/main/java` | `src/test/java` |
| Go | `go.mod` | `.` | `.` (同目录 `*_test.go`) |
| Python | `requirements.txt` / `pyproject.toml` | `src/` 或 `.` | `tests/` |
| TypeScript | `package.json` + `tsconfig.json` | `src/` | `__tests__/` 或 `*.spec.ts` |

#### 1.2 识别测试框架

| 语言 | 检测方式 | 常见框架 |
|------|---------|----------|
| Java | `pom.xml` 依赖 | JUnit 5, TestNG, Spock |
| Go | `go.mod` 依赖 | testing (内置), testify |
| Python | `requirements.txt` | pytest, unittest |
| TypeScript | `package.json` devDependencies | Jest, Mocha, Jasmine |

#### 1.3 建立测试任务 TODO 列表

```markdown
# 测试任务列表

## 高优先级（核心业务）
- [ ] UserService.java - 用户管理核心逻辑 - 复杂度:高
- [ ] OrderService.java - 订单处理逻辑 - 复杂度:高

## 中优先级（辅助功能）
- [ ] ValidationUtils.java - 验证工具类 - 复杂度:中

## 低优先级（简单代码）
- [ ] UserDTO.java - 数据传输对象 - 复杂度:低
```

#### 1.4 运行基线覆盖率测试

| 语言 | 命令 | 报告位置 |
|------|------|----------|
| Java | `./mvnw test jacoco:report` | `target/site/jacoco/index.html` |
| Go | `go test -coverprofile=coverage.out ./...` | `coverage.out` |
| Python | `pytest --cov=. --cov-report=html` | `htmlcov/index.html` |
| TypeScript | `npm test -- --coverage` | `coverage/lcov-report/index.html` |

### 2. 测试计划制定阶段

#### 2.1 项目规模评估

| 规模 | 代码行数 | 策略 |
|------|----------|------|
| 小型 | < 500 行 | 一次性生成所有测试 |
| 中型 | 500-5000 行 | 按模块分批，每批 3-5 个文件 |
| 大型 | > 5000 行 | 按功能模块划分，优先核心逻辑 |

#### 2.2 优先级排序

| 优先级 | 代码类型 | 示例 |
|--------|----------|------|
| 🔴 高 | 核心业务逻辑、对外接口 | OrderService, PaymentGateway |
| 🟡 中 | 辅助方法、工具类 | ValidationUtils, DateHelper |
| 🟢 低 | POJO/DTO、简单 getter/setter | UserDTO, OrderVO |

#### 2.3 执行计划模板

```markdown
# 测试生成执行计划

## 项目概览
- 语言: [Java/Go/Python/TypeScript]
- 文件数: [N] 个 | 代码行数: [M] 行
- 当前覆盖率: [X]%
- 目标覆盖率: [Y]%

## 批次计划
| 批次 | 目标文件 | 预期提升 | 关键测试点 |
|------|----------|----------|------------|
| 1 | UserService, OrderService | +15% | 用户创建、订单处理 |
| 2 | ValidationUtils | +5% | 边界值验证 |

## 风险与应对
| 风险 | 应对措施 |
|------|----------|
| 代码耦合度高 | 先重构，引入依赖注入 |
| 外部依赖多 | 使用 TestContainers |
```

### 3. 代码可测试性审查阶段

#### 3.1 TDD原则检查清单
- [ ] 单一职责原则（SRP）：类/函数只做一件事
- [ ] 依赖注入：支持外部依赖注入而非硬编码
- [ ] 接口隔离：使用接口抽象外部依赖
- [ ] 无全局状态：避免使用单例、全局变量
- [ ] 纯函数优先：相同输入产生相同输出

#### 3.2 代码重构模式
```java
// ❌ 不可测试：硬编码依赖
class UserService {
    private Database db = new MySQLDatabase();
    private EmailService email = new EmailService();
}

// ✅ 可测试：依赖注入
class UserService {
    private final Database db;
    private final EmailService email;

    @Inject
    public UserService(Database db, EmailService email) {
        this.db = db;
        this.email = email;
    }
}
```

#### 3.3 可测试性重构
- 提取方法：将大函数拆分为小函数
- 引入接口：为外部依赖创建接口
- 移除静态调用：改为实例方法调用
- 消除全局状态：使用参数传递

### 4. 测试策略制定阶段

> **与上游案例对齐（Step 0 已加载文档时）**：本阶段的 MC/DC / 边界值设计应作为黑盒案例的**补充**，而非替代。
> - 已有 `TC-XXX-NNN` 案例 → 直接转化为测试方法，不重新发明。
> - 白盒分析发现"案例文档未覆盖的代码分支"（如防御性分支、异常兜底）→ 作为**补充案例**加入，并在映射表中标注来源为"白盒补充"。
> - 若白盒发现的关键分支与需求案例冲突，停下来核对 `usecase.md/rules.md`，可能是需求理解偏差，按 Stop-the-Line 反馈。

#### 4.1 确定测试范围
根据代码复杂度和重要性确定测试优先级：
1. **高优先级**: 核心业务逻辑、对外接口、数据处理
2. **中优先级**: 辅助方法、工具类、配置类
3. **低优先级**: 简单getter/setter、POJO类

#### 4.2 设计测试用例
为每个方法设计以下类型的测试用例：
- **正常情况**: 输入有效数据，期望正常输出
- **边界情况**: 输入边界值，如空值、最大值、最小值
- **异常情况**: 输入无效数据，期望抛出异常
- **依赖情况**: 模拟外部依赖的不同响应

#### 4.3 MC/DC测试设计
```java
// 示例：复杂决策逻辑
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

// MC/DC测试用例设计
@Test
void testGoodCreditIndependence() {
    // 基线：goodCredit=false, 其他条件=true
    User user = User.builder()
        .creditScore(600)  // goodCredit = false
        .debtToIncomeRatio(0.35)  // goodDebtRatio = true
        .employmentYears(5)  // stableEmployment = true
        .build();
    LoanRequest request = LoanRequest.builder()
        .amount(user.getAnnualIncome().multiply(BigDecimal.valueOf(3)))
        .build();

    assertFalse(approvalService.approveLoan(user, request));

    // 改变条件1：goodCredit=true, 保持其他不变
    user.setCreditScore(700);
    assertTrue(approvalService.approveLoan(user, request));
}
```

#### 4.4 测试场景分类
1. **正常场景（Happy Path）**
   - 典型业务流程
   - 标准输入值
   - 成功路径验证

2. **异常场景（Error Cases）**
   - 无效输入
   - 业务规则违反
   - 系统异常处理

3. **边界值测试（Boundary Values）**
   - 最小值、最小值-1、最小值+1
   - 最大值、最大值-1、最大值+1
   - 零值、null、空集合

4. **随机值测试（Random Values）**
   - 使用固定种子的随机数生成器
   - 覆盖更多组合场景
   - 确保可重现

5. **并发场景（Concurrency）**
   - 多线程访问
   - 竞态条件
   - 死锁检测

#### 4.5 选择测试模式
根据被测代码的特点选择合适的测试模式：
- **状态验证**: 验证对象的状态变化
- **行为验证**: 验证方法的调用行为
- **交互验证**: 验证对象间的交互过程

### 5. 分轮覆盖率提升阶段

> **覆盖率是目标（行≥80/分支≥70/方法≥85，或项目配置），断言价值是独立门禁。**
> 标准覆盖率工具只能证明执行，不能把每一行机械归因到某个断言；因此每个必需业务分支还必须映射到
> 至少一个绑定 BR-XXX 的 L2+ 测试。覆盖率、断言价值、确定性隔离、变异冒烟联合放行
> （见 §输出标准·放行判定）。

执行最多5轮提升，每轮1%-5%（百分比仅为节奏参考，非硬指标）：

#### Round 1: 快速胜利（+5%）
- 添加基础测试用例
- 覆盖明显的代码路径
- 测试公共API

#### Round 2: 核心逻辑（+5%）
- 覆盖业务逻辑分支
- 添加错误处理测试
- 测试边界条件

#### Round 3: 边界和异常（+3%）
- 完善边界值测试
- 异常场景覆盖
- 空值/null处理

#### Round 4: 复杂场景（+2%）
- 集成测试覆盖
- 并发访问测试
- 复杂条件组合

#### Round 5: 收尾（覆盖剩余分支，每个新增覆盖点必须 L2+ 断言或记豁免）
- 覆盖剩余**公共分支**与异常兜底（仍能绑定 BR-XXX 的部分）
- Hard-to-reach 代码：优先**重构提升可测性**（抽方法 / 注入依赖 / 去静态），而非为覆盖而测
- **不直接测私有/静态方法**：通过其公共调用方间接验证；若逻辑复杂到值得直接测，说明应提取为独立可测单元（SRP）。直接测私有方法属于"测试实现细节"，与 `testing-typescript.md` §4 相悖
- 仍达不到的部分：记为**已豁免**并说明原因（如已废弃、纯防御性兜底），而非写脆弱测试凑覆盖率

每轮后：
1. 运行完整测试套件：确保所有测试通过
2. 生成覆盖率报告：分析未覆盖代码
3. 输出**未覆盖分支清单**：每个分配 `补 L2+ 测试 / 豁免`——未覆盖缺口 = 测试缺口，不允许"安全忽略"
4. 识别下轮目标：优先 P1 业务分支的未覆盖点

### 6. 测试代码生成阶段

#### 6.1 生成测试类结构
```java
// Java示例（JUnit 5 + Mockito 标准范式：MockitoExtension + InjectMocks）
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    // Mock对象（由扩展自动初始化；strict stubbing 自动捕捉无用打桩）
    @Mock
    private UserRepository userRepository;

    // 被测对象（自动注入上面的 mock）
    @InjectMocks
    private UserService userService;

    // 测试方法（Assert 阶段必须达到断言价值 L2+，见 §6.5）
    @Test
    void getUserById_userExists_returnsUserWithExpectedFields() {
        // Arrange

        // Act

        // Assert（断言精确值/状态/交互，绑定 BR-XXX）
    }
}
```
> 不要用旧式 `MockitoAnnotations.openMocks(this)`。若需注入 `Clock`/`Random` 等非 mock 依赖，改为构造注入手动 `new`。

#### 6.2 实现具体测试方法
按照AAA模式实现每个测试方法：

**Arrange (准备阶段)**:
- 初始化测试数据
- 创建Mock对象和期望行为
- 构造被测对象

**Act (执行阶段)**:
- 调用被测方法
- 获取执行结果

**Assert (断言阶段)**:
- 验证返回结果
- 验证Mock对象的调用行为
- 验证系统状态变化

#### 6.3 添加测试数据管理
```java
// 测试数据工厂模式
public class TestDataFactory {

    public static User createUser() {
        User user = new User();
        user.setId(1L);
        user.setName("Test User");
        user.setEmail("test@example.com");
        return user;
    }

    public static List<User> createUsers(int count) {
        List<User> users = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            User user = new User();
            user.setId((long)i);
            user.setName("Test User " + i);
            user.setEmail("test" + i + "@example.com");
            users.add(user);
        }
        return users;
    }
}
```

#### 6.5 断言价值门禁（Assertion Strength Gate）—— 单测质量的核心

> ⚠️ **这是单测生成最关键的一步**。覆盖率回答"代码跑到了吗"，断言回答"行为对吗"。一个执行了代码却没有有效断言的测试是**假阳性**：它永远通过、虚增覆盖率、却抓不到任何 bug。**没有有价值的断言，再高的覆盖率都是自欺。**

##### 6.5.1 断言价值阶梯（每个测试必须达到 L2 及以上）

| 等级 | 名称 | 验证内容 | 判定 |
|------|------|---------|------|
| **L0** | 空验证 | 什么都不验证（无断言 / 仅 `assertDoesNotThrow`） | ❌ 禁止作为唯一断言 |
| **L1** | 存在性 | "有东西返回"（`isNotNull` / `hasSize(>0)` / `isPresent`） | ⚠️ 不得作为唯一断言 |
| **L2** | 精确值/状态 | 返回值或副作用后的状态 **等于预期业务值** | ✅ 抓住"算错值"的 bug |
| **L3** | 语义+边界 | 在业务边界处的精确值，且失败侧验证错误码/消息 | ✅✅ 抓住差一错误、契约漂移 |
| **L4** | 交互契约 | 协作者被正确次数、正确参数（`argThat` 精确匹配）调用，且无多余交互 | ✅✅✅ 抓住"副作用缺失/重复" |

**铁律**：每个测试**至少有一个 L2+ 断言，且该断言绑定到案例的业务规则（BR-XXX）**。只有 `isNotNull` 的测试一律驳回重写。

##### 6.5.2 弱断言 → 强断言改写对照表（生成时直接套用）

| 弱断言（拒绝） | 为什么弱 | 强断言（采用） |
|--------------|---------|--------------|
| `assertThat(result).isNotNull();` | 只证明"没返回 null"，算错值也通过 | `assertThat(result.getStatus()).isEqualTo(OrderStatus.PAID);`（L2） |
| `assertThat(list).isNotEmpty();` | 不验证内容、顺序、数量 | `assertThat(list).extracting(Item::getSku).containsExactly("A","B");`（L2/L3） |
| `assertThat(opt).isPresent();` | 不验证装的是什么 | `assertThat(opt).get().extracting(User::getEmail).isEqualTo("a@b.com");`（L2） |
| `verify(repo).save(any());` | 参数才是业务行为，`any()` 放过错误参数 | `verify(repo).save(argThat(u -> u.getName().equals("John") && u.isActive()));`（L4） |
| `assertDoesNotThrow(() -> svc.run());` | 不验证 run 做了什么 | 断言 run 后的具体状态变更 + 关键交互（L2+L4） |
| `assertThat(resp.getCode()).isNotNull();` | 错误码存在 ≠ 错误码正确 | `assertThat(resp.getCode()).isEqualTo("INSUFFICIENT_STOCK");`（L3） |
| 仅 `assertEquals(expected, actual)` 比 `toString()` | 字符串相等掩盖字段级语义 | 对编码规则的具体字段逐一断言，或 `extracting(多字段)` 分组断言 |

##### 6.5.3 断言必须覆盖的"三个面"

对每个测试，逐项自问并补齐（至少命中与该行为相关的那一面到 L2+）：

```
1. 返回值（Output）   — 方法返回了正确的值吗？（含类型、字段、错误码）
2. 状态变更（State）  — 被测对象/聚合根的内部状态变成预期了吗？
3. 交互（Interaction）— 该调用的协作者调用了吗？参数对吗？不该调的没调吗？
```

- **纯函数/查询方法**：聚焦"返回值"面，必须断言精确值。
- **命令/有副作用的方法**：必须断言"状态变更"和/或"交互"面（`argThat` 精确参数 + `verify(no...)` 排除多余调用）。
- **决策/分支方法**：每个分支的断言必须能区分该分支与相邻分支的结果（否则分支测试是"哑"的，见 §7.5 变异自检）。

##### 6.5.4 反"自我应验"检查（Tautology Guard）

> 断言验证的必须是**被测代码做了什么**，而不是**测试自己塞给 mock 的值**。

```
生成断言前自问：
  我断言的这个值，是 SUT（被测系统）计算/转换/决策出来的，
  还是我在 when(...).thenReturn(X) 里写死、然后又 assertEquals(X) 的？

  如果是后者 → 这是自我应验的同义反复，删掉，改为断言 SUT 的真实加工结果。
```

详见 `references/test-driven-development/testing-anti-patterns.md`（Anti-Pattern 1：Testing Mock Behavior）。

##### 6.5.5 断言价值自检清单（每个测试方法写完即执行）

- [ ] 至少一个 L2+ 断言，且绑定到 BR-XXX
- [ ] 没有"仅存在性"（L1）作为唯一验证
- [ ] 边界用例验证了边界两侧的不同结果（L3）
- [ ] 有副作用的方法验证了交互契约（`argThat` 精确参数，必要时 `verifyNoMoreInteractions`）（L4）
- [ ] 断言的不是 mock 的固定返回值（非同义反复）
- [ ] 一个测试只验证一个行为（多字段用分组断言，不堆叠多行为）

### 7. 测试验证阶段

#### 7.1 运行测试
```bash
# Java项目
./mvnw test

# 或者
./gradlew test

# Go项目
go test ./...

# Python项目
python -m pytest

# TypeScript项目
npm test
```

#### 7.2 检查测试覆盖率
```bash
# Java (JaCoCo)
./mvnw jacoco:report

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Python
coverage run -m pytest
coverage report

# TypeScript
npm test -- --coverage
```

#### 7.3 修复失败测试
分析失败的测试用例，可能的原因：
- 测试数据不正确
- Mock行为设置有误
- 断言条件不准确
- 被测代码存在缺陷

#### 7.3.5 断言价值门禁验证（放行前必检，不可跳过）

> 覆盖率达标 ≠ 测试有效。放行前，对**每个生成的测试方法**逐项核对 §6.5 的断言价值标准。

**逐方法核对**（建议输出为表格）：

| 测试方法 | 关联 BR | 最高断言等级 | 覆盖的面（值/状态/交互） | 是否同义反复 | 判定 |
|---------|---------|-------------|----------------------|-------------|------|
| OrderServiceTest#should_reject_when_stock_insufficient | BR-007 | L3 | 值+交互 | 否 | ✅ |
| OrderServiceTest#should_create_order | BR-005 | **L1** | 仅存在性 | — | ❌ 重写 |

**阻断条件（任一命中即不得放行，必须回到 §6.5 改写）**：
- 存在仅 L0/L1 断言的测试方法
- 边界用例未验证边界两侧的差异（L3 未达）
- 有副作用的方法未验证交互契约（`verify` 用 `any()` 而非 `argThat` 精确匹配）
- 断言的是 mock 的固定返回值（同义反复）

> **与覆盖率的关系**：覆盖率必须达标，且每个必需业务分支必须映射到至少一个 BR-linked L2+ 测试。
> 两者联合放行但分别计量：覆盖率工具负责“是否执行”，断言价值门禁负责“是否验证”，不伪造一条
> 无法机械计算的“行 → 断言”映射。

#### 7.3.6 确定性隔离门禁（D-Gate，放行前必检，不可跳过）

> 断言价值门禁（§7.3.5）验"测得对"；本门禁验"测得稳"。两者并列，**任一不过不得放行**。
> 总纲：每个测试必须能作为该类**唯一被执行的测试**而通过。对齐 `SKILL.md` D1–D9。

**逐项核对**（输出为表，命中任一 ❌ 即回对应禁令修复）：

| 禁令 | 核对点 | 通过条件 |
|------|--------|---------|
| D1 顺序无关 | 无 `@Order`/排序注解；无测试间数据或状态依赖 | 单测独跑可通过 |
| D2 无共享可变状态 | 无 static 可变字段；静态/单例已 `@BeforeEach` 重置并注释；`mockStatic`/`mockConstruction` 已 try-with-resources 或 `@AfterEach` `close()` | 无跨测试状态泄漏 |
| D3 无真实时间 | 无 `now()`/`currentTimeMillis()`/`nanoTime()`；时间注入 `Clock.fixed`；断言无运行时时间表达式 | 时间确定 |
| D4 无无序集合顺序依赖 | `HashMap`/`HashSet` 遍历未直接比有序；需顺序用 `LinkedHashMap` 或显式排序 | 顺序变化不破断言 |
| D5 无 sleep 同步 | 无 `sleep`/`setTimeout`；异步用 `CountDownLatch`/`Awaitility`；超时不依赖机器 | 异步确定 |
| D6 无非确定输入 | 断言数据非 `Random`/`UUID.randomUUID`/自增；随机已 seed | 输入确定 |
| D7 无共享外部资源 | 端口/临时文件用 `@TempDir`/随机端口；DB 自带准备+清理；不依赖既有数据或固定自增 ID | 资源自包含 |
| D8 无环境隐式依赖 | 时区/Locale/编码/行分隔符/大小写显式指定 | 环境无关 |
| D9 无类级可变状态 | `@BeforeAll`/`@AfterAll` 只建不可变 fixture | 类级钩子纯净 |

**阻断条件（任一命中即不得放行）**：
- 跨测试状态依赖或排序注解（D1）
- `mockStatic`/`mockConstruction` 未 close——会污染其他测试（D2）
- 断言含 `now()` 或运行时时间表达式（D3）
- 有序断言建立在 `HashMap`/`HashSet` 遍历上（D4）
- 用 `sleep` 等异步或机器相关超时（D5）
- 断言数据来自未 seed 的随机或自增序列（D6）

> lint（🔒 C1/C3/C4/C5）已机械化 D1/D3/D5/D6 的明显模式；D2/D4/D7/D8/D9 及 D3 的语义部分
> 由本门禁人工兜底——它们需作用域/数据流判断，正则误报率高。

#### 7.4 质量保证验证
```bash
# 最终验证步骤
1. 编译检查
   Java: mvn compile 或 gradle build
   Python: python -m py_compile
   Go: go build ./...
   Rust: cargo check

2. 运行测试套件
   Java: mvn test
   Python: pytest -v
   Go: go test -v ./...
   Rust: cargo test

3. 生成覆盖率报告
   Java: mvn jacoco:report
   Python: pytest --cov=app --cov-report=html
   Go: go tool cover -html=coverage.out
   Rust: cargo tarpaulin --out Html

4. 变异测试（核心方法必做，见 §7.5.1；进联合放行判定）
   Java: mvn org.pitest:pitest-maven:mutationCoverage
   Python: mutmut run
   Go: go-mutesting ./...
```

#### 7.5 测试有效性自检（变异冒烟）—— 证明断言真的能抓 bug

> 断言价值门禁（§7.3.5）是**静态**检查"断言够不够强"；本步骤是**动态**验证"断言是否真的会因 bug 而失败"。两者互补：前者看代码，后者看行为。

##### 7.5.1 手动变异冒烟（核心业务方法必做，进联合放行判定第 ③ 要件）

对每个**核心业务方法**（支付、权限、库存、金额计算、状态流转等高风险逻辑），做一次"故意制造 bug，看测试是否失败"：

```
对该方法注入一个微小变异（改一处即可），运行其测试：
  - 边界：把 >= 改成 >（或 <= 改成 <）
  - 决策：把 return true 改成 return false
  - 算术：把 + 改成 -、* 改成 /
  - 条件：把 && 改成 ||
  - 调用：删掉一行有副作用的调用（如 repo.save(...)）

预期：至少有一个测试因此变红（FAIL）。
  ✅ 有测试失败 → 该分支/行为的断言是"活"的，恢复变异。
  ❌ 没有任何测试失败 → 该断言是"哑"的（only L0/L1，或漏了交互验证）。
     回到 §6.5，补一个能区分"变异前/变异后"结果的 L2+ 断言。
```

> **为什么有效**：能跑通的测试 + 达标的覆盖率，都无法证明"代码错了测试会红"。手动变异是用最低成本验证这一点的方法——一个无法被任何变异杀死的测试，就是假阳性。

##### 7.5.2 自动变异测试（推荐，针对高价值模块）

对核心模块运行变异测试工具，关注 **mutation score（变异杀死率）** 而非仅覆盖率：

| 语言 | 工具 | 命令 |
|------|------|------|
| Java | PITest | `mvn org.pitest:pitest-maven:mutationCoverage` |
| Python | mutmut | `mutmut run` |
| Go | go-mutesting | `go-mutesting ./...` |
| TypeScript | Stryker | `npx stryker run` |

**存活变异（surviving mutant）= 测试盲区**：每个存活变异都意味着"代码这样改了，但没有测试发现"。逐个分析存活变异，补对应断言（通常正是缺失的 L2+/边界/交互断言）。

> **目标参考**：核心业务模块变异杀死率建议 ≥ 70%（项目可覆盖）。变异分数比行覆盖率更能反映测试的真实价值。

## 最佳实践

### 1. 测试代码质量
- 保持测试代码简洁易懂
- 避免在测试中包含复杂逻辑
- 使用描述性的测试方法名
- 每个测试方法只测试一个功能点

### 2. 测试维护
- 定期更新失效的测试
- 删除不再需要的测试
- 重构重复的测试代码
- 保持测试与生产代码同步

### 3. 性能优化
- 避免在测试中进行网络请求
- 使用内存数据库替代真实数据库
- 重用测试资源和对象
- 并行执行独立的测试

### 4. 资源层依赖策略（按测试类型分流，不可混淆）

> ⚠️ 资源层（DB/Redis/MQ/网络/时间）是否 Mock，**取决于测试类型**，不存在"一刀切"答案。本节与 `SKILL.md` 的 "Test Type → Dependency Strategy" 表保持一致。

| 测试类型 | 资源层处理 | 目的 |
|---------|-----------|------|
| **单元测试** | **MUST 隔离所有 I/O**：DB/Redis/MQ/网络/时间一律用 Mock/Fake/注入时钟 | 快（毫秒级）、确定性、可重复（FIRST 原则） |
| **集成测试** | **PREFER 真实/容器化依赖**：TestContainers、embedded、docker-compose；不可用时声明回退策略 | 验证真实组件交互 |

- **外部服务（第三方 API）**：无论单元还是集成，均使用 Mock/WireMock/MockServer 隔离，避免依赖外网。
- **常见错误**：在单元测试里用 TestContainers 拉起真实 DB —— 这违背单元测试的 FIRST（Fast）原则，应改为 Mock/Fake；反之，集成测试若把资源层全 Mock 则失去了集成测试的意义。

## 常见问题及解决方案

### 1. 依赖注入问题
**问题**: 被测类依赖太多外部服务
**解决方案**: 使用依赖注入框架或手动注入Mock对象

### 2. 时间相关测试
**问题**: 测试涉及时间相关的逻辑
**解决方案**: **注入 `Clock`（或等价时钟抽象）**，测试用固定时钟（如 Java `Clock.fixed(...)`、Go 传入时间函数、Python `freezegun`/注入 `now` 函数、TS 注入 clock 或 `jest.useFakeTimers`），断言**精确时间值**。**禁止** `now()` 夹逼断言（`isBetween(before, after)`）——它非确定、违背 FIRST 的 Repeatable 原则。

### 3. 随机数据问题
**问题**: 测试中使用随机数据导致不稳定
**解决方案**: 固定种子或使用确定性数据

### 4. 覆盖率提升瓶颈
**问题**: 难以覆盖某些代码分支
**解决方案**（把"难测"当作代码质量信号，而非绕过）:
- 某分支难用 L2+ 断言覆盖（私有方法 / 静态耦合 / 深嵌套）→ **不写脆弱测试绕过**，触发 §3 可测试性重构（抽方法 / 注入依赖 / 去静态 / 拆小）
- 只有重构后仍不可达的分支（已废弃、纯防御兜底）才记豁免，并附理由
- 用 Mock 覆盖的是"难以到达的 I/O 分支"（如超时、第三方异常），**不是**为凑覆盖率去覆盖日志 / 监控 / 简单 getter

## 输出标准

生成的测试代码应满足以下标准：

### 测试统计摘要
```
测试文件创建/修改: XX个
新增测试用例: XX个
测试执行时间: XX秒
测试通过率: 100%
```

### 覆盖率提升报告（与断言价值报告联合放行，见下方「放行判定」）
```
语言: Java/Python/Go/Rust
测试前覆盖率: XX%
测试后覆盖率: XX%
提升幅度: +XX%

行覆盖率: XX%
分支覆盖率: XX%
函数覆盖率: XX%
```

### 未覆盖代码分析（强制 checklist：每个未覆盖分支必须处置）
```
| 未覆盖分支（文件:行/分支）        | 处置        | 理由 / 关联 BR          |
|----------------------------------|-------------|------------------------|
| OrderService.java:42 超额分支     | 补 L2+ 测试 | BR-012 超额拒绝        |
| LegacyImporter.java:88           | 记豁免      | 已废弃，计划下线       |
```

> 处置**只允许两值**：**补 L2+ 测试（标 BR-XXX）** 或 **记豁免（理由：已废弃 / 纯防御兜底 / 不可达，需复核）**。
> 禁止"可以安全忽略"这种无理由跳过——未覆盖缺口 = 测试缺口。难用 L2+ 覆盖的分支先触发 §3 可测性重构，而非写脆弱测试。

### 断言价值报告（必出，优先级高于覆盖率）
```
断言价值分布:
  L4 交互契约: XX 个
  L3 语义+边界: XX 个
  L2 精确值/状态: XX 个
  L1 辅助断言: XX 个   ← 允许存在，但不得成为任何测试的最高有效断言
  L0 空验证:   0 个   ← 必须为 0

最高有效断言等级 < L2 的测试: 0 个（阻断项）
同义反复（断言 mock 固定值）的测试: 0 个（阻断项）
有副作用方法已验证交互契约（argThat）: XX/XX

变异自检:
  核心方法手动变异冒烟: 通过 XX/XX（每个核心方法均有测试被变异杀死）
  自动变异杀死率（如运行）: XX%（核心模块建议 ≥70%）
  存活变异（测试盲区）: XX 个 → [已补断言 / 已记录]
```

### 放行判定（Release Decision，四者 AND，任一不过不放行）

| 要件 | 通过条件 | 来源 |
|------|---------|------|
| ① 覆盖率达标 | 行 ≥ 目标 / 分支 ≥ 目标（默认 80/70，或项目配置） | 覆盖率报告 |
| ② 断言价值达标 | 每个测试最高有效断言等级 ≥ L2、L0-only = 0、无同义反复；必需业务分支映射到 BR-linked L2+ 测试；有副作用方法已验证交互契约（argThat） | §7.3.5 + 断言价值报告 |
| ③ 核心方法变异冒烟通过 | 每个核心业务方法（支付/权限/库存/金额/状态流转）至少 1 个变异被测试杀死 | §7.5.1 + 变异自检 |
| ④ 确定性隔离 D-Gate 通过 | D1–D9 逐项通过；机械 lint 与人工门禁均无阻断项 | §7.3.6 + D-Gate 报告 |

> 未覆盖分支处置统计：已补 L2+ 测试 XX / 已豁免 XX（每个豁免带理由，见未覆盖代码分析）。
> 四者必须同时满足：覆盖率达标但测试最高有效断言仍低于 L2、确定性隔离失败，或核心方法变异全存活，
> 都**不放行**。

### 测试质量评估
```
✅ 测试覆盖了所有公共API
✅ 异常场景测试完整（失败侧验证了错误码/消息，非仅"抛异常"）
✅ 边界值测试充分（验证了边界两侧的不同结果，L3）
✅ 每个测试至少有一个 L2+ 断言并绑定 BR-XXX
✅ 有副作用的方法验证了交互契约（argThat 精确参数）
✅ 单元测试已隔离所有 I/O（无真实 DB/网络/时钟）
⚠️  建议添加更多并发场景
```
