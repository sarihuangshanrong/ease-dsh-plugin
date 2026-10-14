# Go 编码最佳实践指南

本指南提供 Go 项目的编码规范、设计模式和最佳实践。

## 代码风格规范

### 命名规范

```go
// 包名：小写单词，不使用下划线或驼峰
package userservice
package httputil

// 导出标识符：大驼峰命名
type UserService struct {}
func NewUserService() *UserService {}

// 非导出标识符：小驼峰命名
type userRepository struct {}
func (s *UserService) validateEmail(email string) bool {}

// 接口命名：通常以 -er 结尾（单方法接口）
type Reader interface {
    Read(p []byte) (n int, err error)
}
type UserRepository interface {
    GetByID(ctx context.Context, id uint64) (*User, error)
    Save(ctx context.Context, user *User) error
}

// 常量：大驼峰（导出）或小驼峰（非导出）
const MaxRetryCount = 3
const defaultTimeout = 30 * time.Second

// 错误变量：Err 前缀
var ErrUserNotFound = errors.New("user not found")
var ErrInvalidEmail = errors.New("invalid email format")

// 缩略词保持全大写或全小写
type HTTPClient struct {}  // 导出
type httpClient struct {}  // 非导出
userID := 1               // 非导出变量
```

### 代码格式

```go
// 使用 gofmt/goimports 自动格式化
// 缩进：使用 Tab
// 行宽：建议不超过 100 字符

// 导入分组：标准库、第三方库、本地包
import (
    "context"
    "fmt"
    "time"

    "github.com/gin-gonic/gin"
    "gorm.io/gorm"

    "myproject/internal/domain"
    "myproject/pkg/utils"
)

// 函数声明：参数较多时换行
func NewUserService(
    repo UserRepository,
    cache Cache,
    logger *zap.Logger,
) *UserService {
    return &UserService{
        repo:   repo,
        cache:  cache,
        logger: logger,
    }
}
```

## 项目结构

### 标准布局

```
project/
├── cmd/                    # 应用入口
│   ├── api/
│   │   └── main.go
│   └── worker/
│       └── main.go
├── internal/               # 私有代码
│   ├── domain/             # 领域模型
│   │   ├── user.go
│   │   └── order.go
│   ├── service/            # 业务逻辑
│   │   ├── user_service.go
│   │   └── order_service.go
│   ├── repository/         # 数据访问
│   │   ├── user_repo.go
│   │   └── order_repo.go
│   └── handler/            # HTTP 处理器
│       ├── user_handler.go
│       └── order_handler.go
├── pkg/                    # 公共库
│   ├── middleware/
│   └── utils/
├── api/                    # API 定义（OpenAPI/Proto）
├── configs/                # 配置文件
├── go.mod
└── go.sum
```

## Gin 框架最佳实践

### Handler 层

```go
type UserHandler struct {
    userService *service.UserService
    logger      *zap.Logger
}

func NewUserHandler(userService *service.UserService, logger *zap.Logger) *UserHandler {
    return &UserHandler{
        userService: userService,
        logger:      logger,
    }
}

func (h *UserHandler) RegisterRoutes(r *gin.RouterGroup) {
    users := r.Group("/users")
    {
        users.POST("", h.CreateUser)
        users.GET("/:id", h.GetUser)
        users.PUT("/:id", h.UpdateUser)
        users.DELETE("/:id", h.DeleteUser)
    }
}

func (h *UserHandler) CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        h.logger.Warn("参数绑定失败", zap.Error(err))
        c.JSON(http.StatusBadRequest, Response{
            Code:    CodeParamError,
            Message: "参数错误: " + err.Error(),
        })
        return
    }

    user, err := h.userService.CreateUser(c.Request.Context(), &req)
    if err != nil {
        h.handleError(c, err)
        return
    }

    c.JSON(http.StatusCreated, Response{
        Code:    CodeSuccess,
        Message: "success",
        Data:    user,
    })
}

func (h *UserHandler) GetUser(c *gin.Context) {
    idStr := c.Param("id")
    id, err := strconv.ParseUint(idStr, 10, 64)
    if err != nil {
        c.JSON(http.StatusBadRequest, Response{
            Code:    CodeParamError,
            Message: "无效的用户 ID",
        })
        return
    }

    user, err := h.userService.GetUserByID(c.Request.Context(), id)
    if err != nil {
        h.handleError(c, err)
        return
    }

    c.JSON(http.StatusOK, Response{
        Code:    CodeSuccess,
        Message: "success",
        Data:    user,
    })
}

func (h *UserHandler) handleError(c *gin.Context, err error) {
    var bizErr *BizError
    if errors.As(err, &bizErr) {
        c.JSON(http.StatusBadRequest, Response{
            Code:    bizErr.Code,
            Message: bizErr.Message,
        })
        return
    }

    h.logger.Error("系统错误", zap.Error(err))
    c.JSON(http.StatusInternalServerError, Response{
        Code:    CodeSystemError,
        Message: "系统繁忙，请稍后重试",
    })
}
```

### 请求/响应结构

```go
// 请求结构
type CreateUserRequest struct {
    Name     string `json:"name" binding:"required,min=2,max=50"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,min=8"`
}

type UpdateUserRequest struct {
    Name  *string `json:"name" binding:"omitempty,min=2,max=50"`
    Phone *string `json:"phone" binding:"omitempty,e164"`
}

// 响应结构
type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

type UserResponse struct {
    ID        uint64    `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// 分页响应
type PageResponse struct {
    Total int64       `json:"total"`
    Page  int         `json:"page"`
    Size  int         `json:"size"`
    Items interface{} `json:"items"`
}

// 响应码
const (
    CodeSuccess     = 0
    CodeParamError  = 1001
    CodeSystemError = 1000

    CodeUserNotFound     = 2001
    CodeEmailExists      = 2002
    CodePasswordIncorrect = 2003
)
```

### 中间件

```go
// 认证中间件
func AuthMiddleware(jwtService *JWTService) gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, Response{
                Code:    CodeUnauthorized,
                Message: "未提供认证令牌",
            })
            return
        }

        claims, err := jwtService.ParseToken(strings.TrimPrefix(token, "Bearer "))
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, Response{
                Code:    CodeUnauthorized,
                Message: "无效的认证令牌",
            })
            return
        }

        c.Set("user_id", claims.UserID)
        c.Next()
    }
}

// 日志中间件
func LoggingMiddleware(logger *zap.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path

        c.Next()

        duration := time.Since(start)
        logger.Info("HTTP请求",
            zap.String("method", c.Request.Method),
            zap.String("path", path),
            zap.Int("status", c.Writer.Status()),
            zap.Duration("duration", duration),
            zap.String("client_ip", c.ClientIP()),
        )
    }
}

// 恢复中间件
func RecoveryMiddleware(logger *zap.Logger) gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if err := recover(); err != nil {
                logger.Error("Panic recovered",
                    zap.Any("error", err),
                    zap.String("stack", string(debug.Stack())),
                )
                c.AbortWithStatusJSON(http.StatusInternalServerError, Response{
                    Code:    CodeSystemError,
                    Message: "系统错误",
                })
            }
        }()
        c.Next()
    }
}
```

## Service 层

```go
type UserService struct {
    repo   UserRepository
    cache  Cache
    logger *zap.Logger
}

func NewUserService(repo UserRepository, cache Cache, logger *zap.Logger) *UserService {
    return &UserService{
        repo:   repo,
        cache:  cache,
        logger: logger,
    }
}

func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*UserResponse, error) {
    // 1. 业务校验
    exists, err := s.repo.ExistsByEmail(ctx, req.Email)
    if err != nil {
        return nil, fmt.Errorf("检查邮箱失败: %w", err)
    }
    if exists {
        return nil, NewBizError(CodeEmailExists, "邮箱已被注册")
    }

    // 2. 密码加密
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
    if err != nil {
        return nil, fmt.Errorf("密码加密失败: %w", err)
    }

    // 3. 构建实体
    user := &domain.User{
        Name:      req.Name,
        Email:     req.Email,
        Password:  string(hashedPassword),
        Status:    domain.UserStatusActive,
        CreatedAt: time.Now(),
    }

    // 4. 持久化
    if err := s.repo.Create(ctx, user); err != nil {
        return nil, fmt.Errorf("创建用户失败: %w", err)
    }

    s.logger.Info("用户创建成功",
        zap.Uint64("user_id", user.ID),
        zap.String("email", user.Email),
    )

    return s.toResponse(user), nil
}

func (s *UserService) GetUserByID(ctx context.Context, id uint64) (*UserResponse, error) {
    // 先查缓存
    cacheKey := fmt.Sprintf("user:%d", id)
    if cached, err := s.cache.Get(ctx, cacheKey); err == nil {
        var user UserResponse
        if json.Unmarshal([]byte(cached), &user) == nil {
            return &user, nil
        }
    }

    // 查数据库
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, NewBizError(CodeUserNotFound, "用户不存在")
        }
        return nil, fmt.Errorf("查询用户失败: %w", err)
    }

    resp := s.toResponse(user)

    // 写入缓存
    if data, err := json.Marshal(resp); err == nil {
        _ = s.cache.Set(ctx, cacheKey, string(data), time.Hour)
    }

    return resp, nil
}

func (s *UserService) toResponse(user *domain.User) *UserResponse {
    return &UserResponse{
        ID:        user.ID,
        Name:      user.Name,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
    }
}
```

## Repository 层（GORM）

```go
type UserRepository interface {
    Create(ctx context.Context, user *domain.User) error
    GetByID(ctx context.Context, id uint64) (*domain.User, error)
    GetByEmail(ctx context.Context, email string) (*domain.User, error)
    ExistsByEmail(ctx context.Context, email string) (bool, error)
    Update(ctx context.Context, user *domain.User) error
    Delete(ctx context.Context, id uint64) error
    List(ctx context.Context, filter *UserFilter) ([]*domain.User, int64, error)
}

type userRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) UserRepository {
    return &userRepository{db: db}
}

func (r *userRepository) Create(ctx context.Context, user *domain.User) error {
    return r.db.WithContext(ctx).Create(user).Error
}

func (r *userRepository) GetByID(ctx context.Context, id uint64) (*domain.User, error) {
    var user domain.User
    if err := r.db.WithContext(ctx).First(&user, id).Error; err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *userRepository) ExistsByEmail(ctx context.Context, email string) (bool, error) {
    var count int64
    err := r.db.WithContext(ctx).Model(&domain.User{}).
        Where("email = ?", email).
        Count(&count).Error
    return count > 0, err
}

func (r *userRepository) List(ctx context.Context, filter *UserFilter) ([]*domain.User, int64, error) {
    var users []*domain.User
    var total int64

    query := r.db.WithContext(ctx).Model(&domain.User{})

    // 动态条件
    if filter.Status != nil {
        query = query.Where("status = ?", *filter.Status)
    }
    if filter.Name != "" {
        query = query.Where("name LIKE ?", "%"+filter.Name+"%")
    }

    // 统计总数
    if err := query.Count(&total).Error; err != nil {
        return nil, 0, err
    }

    // 分页查询
    offset := (filter.Page - 1) * filter.Size
    if err := query.Offset(offset).Limit(filter.Size).Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}
```

## 领域模型

```go
package domain

import "time"

type User struct {
    ID        uint64     `gorm:"primaryKey"`
    Name      string     `gorm:"size:100;not null"`
    Email     string     `gorm:"size:255;uniqueIndex;not null"`
    Password  string     `gorm:"size:255;not null"`
    Phone     string     `gorm:"size:20"`
    Status    UserStatus `gorm:"size:20;not null;default:'active'"`
    CreatedAt time.Time  `gorm:"not null"`
    UpdatedAt *time.Time
}

func (User) TableName() string {
    return "users"
}

type UserStatus string

const (
    UserStatusActive   UserStatus = "active"
    UserStatusInactive UserStatus = "inactive"
    UserStatusBanned   UserStatus = "banned"
)
```

## 错误处理

### 自定义业务错误

```go
type BizError struct {
    Code    int
    Message string
}

func (e *BizError) Error() string {
    return e.Message
}

func NewBizError(code int, message string) *BizError {
    return &BizError{
        Code:    code,
        Message: message,
    }
}

// 预定义错误
var (
    ErrUserNotFound      = NewBizError(CodeUserNotFound, "用户不存在")
    ErrEmailExists       = NewBizError(CodeEmailExists, "邮箱已被注册")
    ErrPasswordIncorrect = NewBizError(CodePasswordIncorrect, "密码错误")
)
```

### 错误包装与传递

```go
func (s *UserService) GetUserByID(ctx context.Context, id uint64) (*UserResponse, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        // 判断特定错误
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, ErrUserNotFound
        }
        // 包装错误，保留上下文
        return nil, fmt.Errorf("查询用户失败: %w", err)
    }
    return s.toResponse(user), nil
}

// 在 handler 中判断错误类型
func (h *UserHandler) handleError(c *gin.Context, err error) {
    var bizErr *BizError
    if errors.As(err, &bizErr) {
        c.JSON(http.StatusBadRequest, Response{
            Code:    bizErr.Code,
            Message: bizErr.Message,
        })
        return
    }
    // 系统错误
    c.JSON(http.StatusInternalServerError, Response{
        Code:    CodeSystemError,
        Message: "系统繁忙",
    })
}
```

## 设计模式应用

### 选项模式（Functional Options）

```go
type ServerConfig struct {
    host         string
    port         int
    readTimeout  time.Duration
    writeTimeout time.Duration
    maxConns     int
}

type Option func(*ServerConfig)

func WithHost(host string) Option {
    return func(c *ServerConfig) {
        c.host = host
    }
}

func WithPort(port int) Option {
    return func(c *ServerConfig) {
        c.port = port
    }
}

func WithTimeout(read, write time.Duration) Option {
    return func(c *ServerConfig) {
        c.readTimeout = read
        c.writeTimeout = write
    }
}

func NewServer(opts ...Option) *Server {
    // 默认配置
    cfg := &ServerConfig{
        host:         "0.0.0.0",
        port:         8080,
        readTimeout:  30 * time.Second,
        writeTimeout: 30 * time.Second,
        maxConns:     100,
    }
    
    // 应用选项
    for _, opt := range opts {
        opt(cfg)
    }
    
    return &Server{config: cfg}
}

// 使用
server := NewServer(
    WithHost("localhost"),
    WithPort(3000),
    WithTimeout(10*time.Second, 10*time.Second),
)
```

### 依赖注入

```go
// 使用 wire 或手动注入
type App struct {
    server      *http.Server
    userHandler *handler.UserHandler
    db          *gorm.DB
}

func NewApp(cfg *config.Config) (*App, error) {
    // 初始化数据库
    db, err := gorm.Open(mysql.Open(cfg.DatabaseURL), &gorm.Config{})
    if err != nil {
        return nil, fmt.Errorf("数据库连接失败: %w", err)
    }

    // 初始化日志
    logger, _ := zap.NewProduction()

    // 初始化 Repository
    userRepo := repository.NewUserRepository(db)

    // 初始化 Service
    userService := service.NewUserService(userRepo, nil, logger)

    // 初始化 Handler
    userHandler := handler.NewUserHandler(userService, logger)

    // 初始化路由
    r := gin.New()
    r.Use(middleware.LoggingMiddleware(logger))
    r.Use(middleware.RecoveryMiddleware(logger))
    
    api := r.Group("/api/v1")
    userHandler.RegisterRoutes(api)

    return &App{
        server: &http.Server{
            Addr:    cfg.ServerAddr,
            Handler: r,
        },
        userHandler: userHandler,
        db:          db,
    }, nil
}
```

### 策略模式

```go
type PaymentStrategy interface {
    Pay(ctx context.Context, order *Order) (*PaymentResult, error)
}

type AlipayStrategy struct {
    client *alipay.Client
}

func (s *AlipayStrategy) Pay(ctx context.Context, order *Order) (*PaymentResult, error) {
    // 支付宝支付逻辑
    return &PaymentResult{}, nil
}

type WechatPayStrategy struct {
    client *wechat.Client
}

func (s *WechatPayStrategy) Pay(ctx context.Context, order *Order) (*PaymentResult, error) {
    // 微信支付逻辑
    return &PaymentResult{}, nil
}

type PaymentService struct {
    strategies map[PaymentType]PaymentStrategy
}

func (s *PaymentService) Pay(ctx context.Context, paymentType PaymentType, order *Order) (*PaymentResult, error) {
    strategy, ok := s.strategies[paymentType]
    if !ok {
        return nil, fmt.Errorf("不支持的支付方式: %s", paymentType)
    }
    return strategy.Pay(ctx, order)
}
```

## 并发处理

### Goroutine 和 Channel

```go
// Worker Pool 模式
func ProcessItems(ctx context.Context, items []Item, workers int) error {
    itemChan := make(chan Item, len(items))
    errChan := make(chan error, 1)
    var wg sync.WaitGroup

    // 启动 workers
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for item := range itemChan {
                if err := processItem(ctx, item); err != nil {
                    select {
                    case errChan <- err:
                    default:
                    }
                    return
                }
            }
        }()
    }

    // 发送任务
    for _, item := range items {
        itemChan <- item
    }
    close(itemChan)

    // 等待完成
    wg.Wait()

    select {
    case err := <-errChan:
        return err
    default:
        return nil
    }
}
```

### 使用 errgroup

```go
import "golang.org/x/sync/errgroup"

func FetchUserData(ctx context.Context, userID uint64) (*UserFullData, error) {
    g, ctx := errgroup.WithContext(ctx)

    var user *User
    var orders []*Order
    var profile *Profile

    g.Go(func() error {
        var err error
        user, err = userRepo.GetByID(ctx, userID)
        return err
    })

    g.Go(func() error {
        var err error
        orders, err = orderRepo.GetByUserID(ctx, userID)
        return err
    })

    g.Go(func() error {
        var err error
        profile, err = profileRepo.GetByUserID(ctx, userID)
        return err
    })

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return &UserFullData{
        User:    user,
        Orders:  orders,
        Profile: profile,
    }, nil
}
```

## 测试实践

### 单元测试

```go
func TestUserService_CreateUser(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)
    logger := zap.NewNop()
    service := NewUserService(mockRepo, nil, logger)

    tests := []struct {
        name    string
        req     *CreateUserRequest
        setup   func()
        wantErr bool
        errCode int
    }{
        {
            name: "成功创建用户",
            req: &CreateUserRequest{
                Name:     "test",
                Email:    "test@example.com",
                Password: "password123",
            },
            setup: func() {
                mockRepo.EXPECT().
                    ExistsByEmail(gomock.Any(), "test@example.com").
                    Return(false, nil)
                mockRepo.EXPECT().
                    Create(gomock.Any(), gomock.Any()).
                    Return(nil)
            },
            wantErr: false,
        },
        {
            name: "邮箱已存在",
            req: &CreateUserRequest{
                Name:     "test",
                Email:    "existing@example.com",
                Password: "password123",
            },
            setup: func() {
                mockRepo.EXPECT().
                    ExistsByEmail(gomock.Any(), "existing@example.com").
                    Return(true, nil)
            },
            wantErr: true,
            errCode: CodeEmailExists,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            tt.setup()

            result, err := service.CreateUser(context.Background(), tt.req)

            if tt.wantErr {
                require.Error(t, err)
                var bizErr *BizError
                require.True(t, errors.As(err, &bizErr))
                assert.Equal(t, tt.errCode, bizErr.Code)
            } else {
                require.NoError(t, err)
                assert.NotNil(t, result)
            }
        })
    }
}
```

### 表驱动测试

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name  string
        email string
        want  bool
    }{
        {"有效邮箱", "test@example.com", true},
        {"有效邮箱带子域名", "test@sub.example.com", true},
        {"缺少@", "testexample.com", false},
        {"缺少域名", "test@", false},
        {"空字符串", "", false},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := ValidateEmail(tt.email)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### HTTP 测试

```go
func TestUserHandler_CreateUser(t *testing.T) {
    gin.SetMode(gin.TestMode)

    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockService := mocks.NewMockUserService(ctrl)
    handler := NewUserHandler(mockService, zap.NewNop())

    r := gin.New()
    handler.RegisterRoutes(r.Group("/api/v1"))

    t.Run("创建用户成功", func(t *testing.T) {
        mockService.EXPECT().
            CreateUser(gomock.Any(), gomock.Any()).
            Return(&UserResponse{ID: 1, Name: "test"}, nil)

        body := `{"name":"test","email":"test@example.com","password":"password123"}`
        req := httptest.NewRequest("POST", "/api/v1/users", strings.NewReader(body))
        req.Header.Set("Content-Type", "application/json")
        w := httptest.NewRecorder()

        r.ServeHTTP(w, req)

        assert.Equal(t, http.StatusCreated, w.Code)

        var resp Response
        json.Unmarshal(w.Body.Bytes(), &resp)
        assert.Equal(t, CodeSuccess, resp.Code)
    })
}
```

## 注意事项

1. **遵循 Go 惯例**：使用 gofmt、命名规范、错误处理模式
2. **Context 传递**：所有 I/O 操作都应接受 context.Context
3. **错误处理**：不要忽略错误，使用 `%w` 包装错误保留上下文
4. **资源释放**：使用 defer 释放资源，注意 goroutine 泄漏
5. **并发安全**：使用 sync 包或 channel 保证并发安全
6. **接口设计**：接口应该小而精，在使用方定义接口

