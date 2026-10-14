# Go 测试生成参考文档

本指南提供了为 Go 项目生成单元测试代码的具体规范和最佳实践。

## 测试框架选择

### 标准库测试包

Go语言内置了强大的测试支持，主要使用：
1. **testing**: 标准库测试包
2. **testify**: 第三方测试工具包，提供更丰富的断言和Mock功能

### 依赖安装

```bash
# testify包
go get github.com/stretchr/testify/assert
go get github.com/stretchr/testify/mock
go get github.com/stretchr/testify/suite
```

## 测试文件命名规范

Go测试文件遵循 `_test.go` 后缀命名规范：

```
user.go          -> user_test.go
order_service.go -> order_service_test.go
handler.go       -> handler_test.go
```

## 测试函数命名规范

测试函数必须以 `Test` 开头，并接受 `*testing.T` 参数：

```go
func TestFunctionName(t *testing.T) {
    // 测试逻辑
}

func TestStruct_MethodName(t *testing.T) {
    // 测试结构体方法
}
```

## 基础测试结构

### 简单测试示例

```go
package user

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestUserService_CreateUser(t *testing.T) {
    // Given
    userService := NewUserService()
    user := &User{Name: "John", Email: "john@example.com"}

    // When
    result, err := userService.CreateUser(user)

    // Then
    assert.NoError(t, err)
    assert.NotNil(t, result)
    assert.Equal(t, "John", result.Name)
}
```

### 表驱动测试

```go
func TestUserService_ValidateEmail(t *testing.T) {
    tests := []struct {
        name     string
        email    string
        expected bool
    }{
        {"Valid email", "test@example.com", true},
        {"Invalid email", "invalid-email", false},
        {"Empty email", "", false},
        {"Email with spaces", " test@example.com ", true},
    }

    userService := NewUserService()

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := userService.ValidateEmail(tt.email)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

## Mock使用规范

### 使用testify/mock创建Mock

```go
// 定义接口
type UserRepository interface {
    Save(user *User) error
    FindByID(id int) (*User, error)
}

// 创建Mock结构体
type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) Save(user *User) error {
    args := m.Called(user)
    return args.Error(0)
}

func (m *MockUserRepository) FindByID(id int) (*User, error) {
    args := m.Called(id)
    return args.Get(0).(*User), args.Error(1)
}

// 在测试中使用Mock
func TestUserService_CreateUser(t *testing.T) {
    // Given
    mockRepo := new(MockUserRepository)
    userService := NewUserService(mockRepo)
    user := &User{Name: "John", Email: "john@example.com"}

    mockRepo.On("Save", user).Return(nil)

    // When
    result, err := userService.CreateUser(user)

    // Then
    assert.NoError(t, err)
    assert.NotNil(t, result)
    mockRepo.AssertExpectations(t)
}
```

### 使用monkey进行打桩（谨慎使用）

```go
import "github.com/bouk/monkey"

func TestUserService_SendWelcomeEmail(t *testing.T) {
    // Given
    userService := NewUserService()
    user := &User{Name: "John", Email: "john@example.com"}

    // Mock外部函数
    monkey.Patch(sendEmail, func(to, subject, body string) error {
        return nil
    })
    defer monkey.UnpatchAll()

    // When
    err := userService.SendWelcomeEmail(user)

    // Then
    assert.NoError(t, err)
}
```

## 断言规范

### 使用testify/assert进行断言

```go
import "github.com/stretchr/testify/assert"

func TestUserValidation(t *testing.T) {
    user := &User{Name: "John", Email: "john@example.com"}

    // 基本断言
    assert.NotNil(t, user)
    assert.Equal(t, "John", user.Name)
    assert.NotEqual(t, "", user.Email)
    assert.True(t, len(user.Name) > 0)

    // 错误断言
    err := user.Validate()
    assert.NoError(t, err)

    // 切片断言
    users := []string{"Alice", "Bob", "Charlie"}
    assert.Contains(t, users, "Alice")
    assert.Len(t, users, 3)

    // Map断言
    userMap := map[string]int{"Alice": 25, "Bob": 30}
    assert.Equal(t, 25, userMap["Alice"])
    assert.Contains(t, userMap, "Alice")
}
```

## 测试套件（Test Suite）

### 使用testify/suite组织测试

```go
import (
    "testing"
    "github.com/stretchr/testify/suite"
)

type UserServiceSuite struct {
    suite.Suite
    userService *UserService
    mockRepo    *MockUserRepository
}

func (suite *UserServiceSuite) SetupTest() {
    suite.mockRepo = new(MockUserRepository)
    suite.userService = NewUserService(suite.mockRepo)
}

func (suite *UserServiceSuite) TestCreateUser_Success() {
    user := &User{Name: "John", Email: "john@example.com"}
    suite.mockRepo.On("Save", user).Return(nil)

    result, err := suite.userService.CreateUser(user)

    suite.NoError(err)
    suite.NotNil(result)
    suite.Equal("John", result.Name)
}

func (suite *UserServiceSuite) TestCreateUser_SaveError() {
    user := &User{Name: "John", Email: "john@example.com"}
    suite.mockRepo.On("Save", user).Return(errors.New("save failed"))

    result, err := suite.userService.CreateUser(user)

    suite.Error(err)
    suite.Nil(result)
}

func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceSuite))
}
```

## 测试数据管理

### 测试数据工厂

```go
// testdata/user.go
package testdata

import "time"

func CreateUser() *User {
    return &User{
        ID:        1,
        Name:      "John",
        Email:     "john@example.com",
        CreatedAt: time.Date(2026, 6, 30, 8, 0, 0, 0, time.UTC),  // 固定时间，保持确定性（D3）
    }
}

func CreateUsers(count int) []*User {
    users := make([]*User, count)
    for i := 0; i < count; i++ {
        users[i] = &User{
            ID:        i + 1,
            Name:      fmt.Sprintf("User %d", i+1),
            Email:     fmt.Sprintf("user%d@example.com", i+1),
            CreatedAt: time.Date(2026, 6, 30, 8, 0, 0, 0, time.UTC),  // 固定时间，保持确定性（D3）
        }
    }
    return users
}

func CreateValidUserDTO() *CreateUserDTO {
    return &CreateUserDTO{
        Name:  "John",
        Email: "john@example.com",
    }
}
```

### 使用构建器模式

```go
type UserBuilder struct {
    user *User
}

func NewUserBuilder() *UserBuilder {
    return &UserBuilder{
        user: &User{
            Name:  "Default Name",
            Email: "default@example.com",
        },
    }
}

func (ub *UserBuilder) WithName(name string) *UserBuilder {
    ub.user.Name = name
    return ub
}

func (ub *UserBuilder) WithEmail(email string) *UserBuilder {
    ub.user.Email = email
    return ub
}

func (ub *UserBuilder) WithID(id int) *UserBuilder {
    ub.user.ID = id
    return ub
}

func (ub *UserBuilder) Build() *User {
    return ub.user
}

// 在测试中使用
func TestUserService_ProcessUser(t *testing.T) {
    user := NewUserBuilder().
        WithName("John").
        WithEmail("john@example.com").
        WithID(1).
        Build()

    // 测试逻辑
}
```

## 不同类型代码的测试策略

### 1. 业务逻辑测试

```go
func TestOrderService_CalculateTotal(t *testing.T) {
    // Given
    order := &Order{
        Items: []OrderItem{
            {Price: 100, Quantity: 2},
            {Price: 50, Quantity: 1},
        },
    }
    orderService := NewOrderService()

    // When
    total := orderService.CalculateTotal(order)

    // Then
    assert.Equal(t, float64(250), total)
}
```

### 2. HTTP处理器测试

```go
func TestUserHandler_CreateUser(t *testing.T) {
    // Given
    mockService := new(MockUserService)
    handler := NewUserHandler(mockService)

    userDTO := &CreateUserDTO{Name: "John", Email: "john@example.com"}
    jsonBytes, _ := json.Marshal(userDTO)

    req := httptest.NewRequest(http.MethodPost, "/users", bytes.NewBuffer(jsonBytes))
    req.Header.Set("Content-Type", "application/json")

    mockService.On("CreateUser", userDTO).Return(&User{ID: 1, Name: "John", Email: "john@example.com"}, nil)

    // When
    rr := httptest.NewRecorder()
    handler.CreateUser(rr, req)

    // Then
    assert.Equal(t, http.StatusCreated, rr.Code)
    mockService.AssertExpectations(t)
}
```

### 3. 数据库操作测试

```go
func TestUserRepository_Save(t *testing.T) {
    // Given
    db := setupTestDB()
    defer teardownTestDB(db)

    repo := NewUserRepository(db)
    user := testdata.CreateUser()

    // When
    err := repo.Save(user)

    // Then
    assert.NoError(t, err)
    assert.NotZero(t, user.ID)

    // 验证数据确实保存到了数据库
    savedUser, err := repo.FindByID(user.ID)
    assert.NoError(t, err)
    assert.Equal(t, user.Name, savedUser.Name)
}
```

## 测试覆盖率要求

### 代码覆盖率指标

- **语句覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 85%

### 覆盖率检查

```bash
# 运行测试并生成覆盖率报告
go test -coverprofile=coverage.out ./...

# 查看覆盖率详情
go tool cover -func=coverage.out

# 在浏览器中查看HTML格式的覆盖率报告
go tool cover -html=coverage.out

# 设置覆盖率阈值
go test -covermode=atomic -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//' | awk '{if ($1 < 80) exit 1}'
```

## 基准测试

### 编写基准测试

```go
func BenchmarkUserService_CreateUser(b *testing.B) {
    userService := NewUserService()
    user := testdata.CreateUser()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        userService.CreateUser(user)
    }
}

func BenchmarkUserRepository_FindByID(b *testing.B) {
    db := setupTestDB()
    defer teardownTestDB(db)
    repo := NewUserRepository(db)

    // 插入测试数据
    user := testdata.CreateUser()
    repo.Save(user)

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        repo.FindByID(user.ID)
    }
}
```

### 运行基准测试

```bash
# 运行基准测试
go test -bench=.

# 运行特定基准测试
go test -bench=BenchmarkUserService_CreateUser

# 运行基准测试并分析内存分配
go test -bench=. -benchmem
```

## 示例测试

### 编写示例测试

```go
func ExampleUserService_CreateUser() {
    userService := NewUserService()
    user := &User{Name: "John", Email: "john@example.com"}

    result, err := userService.CreateUser(user)
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("Created user: %s\n", result.Name)
    // Output: Created user: John
}
```

## 最佳实践

### 1. 测试表驱动

```go
func TestUserService_ValidateUser(t *testing.T) {
    tests := []struct {
        name          string
        user          *User
        expectValid   bool
        expectedError string
    }{
        {
            name:          "Valid user",
            user:          testdata.CreateUser(),
            expectValid:   true,
            expectedError: "",
        },
        {
            name:          "User without name",
            user:          &User{Email: "test@example.com"},
            expectValid:   false,
            expectedError: "name is required",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            valid, err := ValidateUser(tt.user)

            if tt.expectValid {
                assert.True(t, valid)
                assert.NoError(t, err)
            } else {
                assert.False(t, valid)
                assert.Error(t, err)
                assert.Contains(t, err.Error(), tt.expectedError)
            }
        })
    }
}
```

### 2. 并行测试

```go
func TestUserService_ConcurrentOperations(t *testing.T) {
    userService := NewUserService()

    t.Parallel() // 标记测试可以并行运行

    // 测试并发安全
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            user := &User{Name: fmt.Sprintf("User%d", id), Email: fmt.Sprintf("user%d@example.com", id)}
            _, err := userService.CreateUser(user)
            assert.NoError(t, err)
        }(i)
    }
    wg.Wait()
}
```

### 3. 子测试

```go
func TestUserService_CRUD(t *testing.T) {
    userService := NewUserService()

    t.Run("Create", func(t *testing.T) {
        user := testdata.CreateUser()
        result, err := userService.CreateUser(user)
        assert.NoError(t, err)
        assert.NotNil(t, result)
    })

    t.Run("Read", func(t *testing.T) {
        user, err := userService.GetUserByID(1)
        assert.NoError(t, err)
        assert.NotNil(t, user)
    })

    t.Run("Update", func(t *testing.T) {
        user := testdata.CreateUser()
        user.Name = "Updated Name"
        result, err := userService.UpdateUser(user)
        assert.NoError(t, err)
        assert.Equal(t, "Updated Name", result.Name)
    })

    t.Run("Delete", func(t *testing.T) {
        err := userService.DeleteUser(1)
        assert.NoError(t, err)
    })
}
```

## MC/DC测试设计

### MC/DC原则说明

MC/DC (Modified Condition/Decision Coverage) 是一种严格的测试覆盖准则，要求：
- **条件独立性**：每个条件独立影响决策结果
- **分支全覆盖**：所有分支路径都被测试
- **边界值测试**：测试输入域的边界及其附近值

### 复杂决策逻辑的MC/DC测试示例

```go
// 贷款审批决策逻辑
func ApproveLoan(user User, request LoanRequest) bool {
    // 条件1: 信用评分 >= 650
    goodCredit := user.CreditScore >= 650
    // 条件2: 负债率 <= 0.43
    goodDebtRatio := user.DebtToIncomeRatio <= 0.43
    // 条件3: 就业稳定性 >= 2年
    stableEmployment := user.EmploymentYears >= 2
    // 条件4: 贷款金额合理
    reasonableAmount := request.Amount.Cmp(user.AnnualIncome.Mul(decimal.NewFromInt(4))) <= 0

    // 决策：(条件1 AND 条件2 AND 条件3) OR (条件1 AND 条件4)
    return (goodCredit && goodDebtRatio && stableEmployment) ||
           (goodCredit && reasonableAmount)
}
```

### MC/DC测试用例设计

```go
func TestApproveLoan_GoodCreditIndependence(t *testing.T) {
    // 基线：goodCredit=false, 其他条件=true
    user := User{
        ID:               1,
        Name:             "Test User",
        CreditScore:      600,  // goodCredit = false
        DebtToIncomeRatio: 0.35,  // goodDebtRatio = true
        EmploymentYears:   5,     // stableEmployment = true
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(150000),  // 合理金额
    }

    assertFalse(t, ApproveLoan(user, request))

    // 改变条件1：goodCredit=true, 保持其他不变
    user.CreditScore = 700  // goodCredit = true
    assertTrue(t, ApproveLoan(user, request))
}

func TestApproveLoan_GoodDebtRatioIndependence(t *testing.T) {
    // 基线：goodDebtRatio=false；为隔离 C2 须让子句2 (C1∧C4) 恒 false → C4=false（金额超标）
    user := User{
        ID:               1,
        Name:             "Test User",
        CreditScore:      700,  // goodCredit = true
        DebtToIncomeRatio: 0.50,  // goodDebtRatio = false
        EmploymentYears:   5,     // stableEmployment = true
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(250000),  // 不合理（250000 > 4×50000=200000 → C4=false，隔离子句1）
    }

    assertFalse(t, ApproveLoan(user, request))

    // 改变条件2：goodDebtRatio=true, 保持其他不变
    user.DebtToIncomeRatio = 0.35  // goodDebtRatio = true
    assertTrue(t, ApproveLoan(user, request))
}

func TestApproveLoan_StableEmploymentIndependence(t *testing.T) {
    // 基线：stableEmployment=false；为隔离 C3 须让子句2 (C1∧C4) 恒 false → C4=false（金额超标）
    user := User{
        ID:               1,
        Name:             "Test User",
        CreditScore:      700,  // goodCredit = true
        DebtToIncomeRatio: 0.35,  // goodDebtRatio = true
        EmploymentYears:   1,     // stableEmployment = false
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(250000),  // 不合理（250000 > 4×50000=200000 → C4=false，隔离子句1）
    }

    assertFalse(t, ApproveLoan(user, request))

    // 改变条件3：stableEmployment=true, 保持其他不变
    user.EmploymentYears = 3  // stableEmployment = true
    assertTrue(t, ApproveLoan(user, request))
}

func TestApproveLoan_ReasonableAmountIndependence(t *testing.T) {
    // 基线：reasonableAmount=false, 其他条件=true（除了条件3）
    user := User{
        ID:               1,
        Name:             "Test User",
        CreditScore:      700,  // goodCredit = true
        DebtToIncomeRatio: 0.35,  // goodDebtRatio = true
        EmploymentYears:   1,     // stableEmployment = false
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(250000),  // 不合理金额 (> 4倍年收入)
    }

    assertFalse(t, ApproveLoan(user, request))

    // 改变条件4：reasonableAmount=true, 保持其他不变
    request.Amount = decimal.NewFromInt(150000)  // 合理金额
    assertTrue(t, ApproveLoan(user, request))
}
```

### 边界值测试示例

```go
func TestApproveLoan_CreditScoreBoundaryValues(t *testing.T) {
    user := User{
        ID:               1,
        Name:             "Test User",
        DebtToIncomeRatio: 0.35,
        EmploymentYears:   5,
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(150000),
    }

    // 边界值测试：649 (失败)
    user.CreditScore = 649
    assertFalse(t, ApproveLoan(user, request))

    // 边界值测试：650 (成功)
    user.CreditScore = 650
    assertTrue(t, ApproveLoan(user, request))

    // 边界值测试：651 (成功)
    user.CreditScore = 651
    assertTrue(t, ApproveLoan(user, request))
}

func TestApproveLoan_DebtToIncomeRatioBoundaryValues(t *testing.T) {
    user := User{
        ID:               1,
        Name:             "Test User",
        CreditScore:      700,
        EmploymentYears:   5,
        AnnualIncome:      decimal.NewFromInt(50000),
    }

    request := LoanRequest{
        ID:     1,
        Amount: decimal.NewFromInt(150000),
    }

    // 边界值测试：0.44 (失败)
    user.DebtToIncomeRatio = 0.44
    assertFalse(t, ApproveLoan(user, request))

    // 边界值测试：0.43 (成功)
    user.DebtToIncomeRatio = 0.43
    assertTrue(t, ApproveLoan(user, request))

    // 边界值测试：0.42 (成功)
    user.DebtToIncomeRatio = 0.42
    assertTrue(t, ApproveLoan(user, request))
}
```

### MC/DC测试模板

```go
func TestFunction_ConditionIndependence(t *testing.T) {
    // 基线：目标条件=false, 其他条件=true
    testData := TestData{
        TargetCondition: false,  // 目标条件设为false
        OtherConditions: true,   // 其他条件设为true
    }

    assertFalse(t, service.EvaluateDecision(testData))

    // 改变目标条件：目标条件=true, 保持其他不变
    testData.TargetCondition = true  // 目标条件设为true
    assertTrue(t, service.EvaluateDecision(testData))
}

// 辅助断言函数
func assertTrue(t *testing.T, condition bool) {
    if !condition {
        t.Errorf("Expected true, but got false")
    }
}

func assertFalse(t *testing.T, condition bool) {
    if condition {
        t.Errorf("Expected false, but got true")
    }
}

## 确定性隔离要点（Go，对齐 SKILL.md D1–D9）

- **D2** 被测包级变量（全局状态）须在测试开头重置并注释，如 `Config.count = 0 // D2：重置全局`；`monkey` 打桩务必 `defer monkey.UnpatchAll()`。
- **D5** 等待异步用 `sync.WaitGroup` / channel / `errgroup`，勿用 sleep。
- **D7** 临时文件用 `t.TempDir()`（自动清理），端口用 `net.Listen("tcp", ":0")` 取随机端口。
- **D8** 时间断言用注入的时钟函数或固定 `time.Date(...)`，勿用真实时钟；格式化显式 `time.UTC`。

> D1/D6 由 lint 机械化（🔒 C1/C5）。

通过遵循这些规范和最佳实践，可以生成高质量、可维护的Go单元测试代码。