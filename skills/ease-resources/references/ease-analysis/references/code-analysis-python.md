# Python 项目代码分析指南

本指南用于指导从 Python 项目源代码中逆向提取领域模型和业务用例。

## 语言特征识别

### 项目类型判断

```bash
# Python 项目特征文件
- requirements.txt           # pip 依赖
- setup.py / setup.cfg       # 包配置
- pyproject.toml             # 现代 Python 项目配置
- poetry.lock                # Poetry 依赖锁定
- Pipfile / Pipfile.lock     # Pipenv 依赖
- *.py                       # Python 源文件
- __init__.py                # 包标识文件
```

### 框架识别

| 框架类型 | 特征导入/文件 | 分析重点 |
|---------|--------------|---------|
| Django | `django`, `settings.py`, `urls.py` | Models、Views、URLs |
| Flask | `flask`, `app.py` | Routes、Blueprints |
| FastAPI | `fastapi`, `main.py` | Routers、Pydantic Models |
| SQLAlchemy | `sqlalchemy` | ORM Models、Relationships |
| Django REST Framework | `rest_framework` | Serializers、ViewSets |
| Celery | `celery` | Tasks、异步处理 |
| Pydantic | `pydantic` | 数据模型、验证规则 |

## 核心模块识别规则

### 1. 目录结构分析（Directory Structure）

> ⚠️ **不可协商**：必须基于目录结构识别多个独立的 Domain，禁止将整个项目视为单一 Domain。

#### Django 项目布局

```
project/
├── manage.py
├── config/                  # 项目配置
│   ├── settings.py
│   └── urls.py
├── apps/                    # 应用目录
│   ├── users/               # Domain 1: 用户模块
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # 视图/API
│   │   ├── serializers.py   # 序列化器
│   │   ├── urls.py          # 路由
│   │   └── admin.py         # 管理后台
│   ├── orders/              # Domain 2: 订单模块
│   │   ├── models.py
│   │   ├── views.py
│   │   └── ...
│   └── payments/            # Domain 3: 支付模块
│       └── ...
└── common/                  # 公共模块（非独立 Domain）
    ├── utils.py
    └── middleware.py
```

#### FastAPI 项目布局

```
project/
├── main.py                  # 应用入口
├── app/
│   ├── api/                 # API 路由
│   │   ├── v1/
│   │   │   ├── users.py     # Domain 1 API
│   │   │   ├── orders.py    # Domain 2 API
│   │   │   └── payments.py  # Domain 3 API
│   │   └── deps.py          # 依赖注入
│   ├── models/              # 数据模型
│   │   ├── user.py          # Domain 1 模型
│   │   ├── order.py         # Domain 2 模型
│   │   └── payment.py       # Domain 3 模型
│   ├── schemas/             # Pydantic 模型
│   │   ├── user.py
│   │   ├── order.py
│   │   └── payment.py
│   ├── services/            # 业务逻辑
│   │   ├── user_service.py
│   │   ├── order_service.py
│   │   └── payment_service.py
│   └── core/                # 核心配置（非独立 Domain）
│       ├── config.py
│       └── security.py
└── tests/
```

#### Flask 项目布局

```
project/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── users/               # Domain 1: Blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── services.py
│   ├── orders/              # Domain 2: Blueprint
│   │   └── ...
│   └── payments/            # Domain 3: Blueprint
│       └── ...
├── config.py
└── run.py
```

### 2. Domain 划分策略

> ⚠️ **强制要求**：必须将项目划分为多个 Domain，每个 Domain 对应一个独立的业务领域。

#### 划分依据

1. **按 Django App 划分**：
   - 识别 `apps/` 或根目录下的 Django 应用
   - 每个应用作为一个独立的 Domain

2. **按 Blueprint/Router 划分**：
   - 识别 Flask Blueprint 或 FastAPI Router
   - 每个 Blueprint/Router 作为一个 Domain

3. **按模型文件划分**：
   - 识别 `models/` 目录下的模型文件
   - 围绕核心模型划分 Domain 边界

#### 划分规则

```python
# 伪代码：Domain 划分逻辑
for each app_or_module in project:
    if is_business_module(app_or_module):  # 排除 common, utils, core 等
        create_domain(app_or_module.name)
        analyze_models(app_or_module)
        analyze_services(app_or_module)
        extract_usecases(app_or_module)
```

### 3. 实体识别规则

#### Django Model

```python
# models.py
from django.db import models

class User(models.Model):
    """用户实体"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'

class Order(models.Model):
    """订单实体"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
```

**提取要点**：
- 类名 → 实体名称
- 字段 → 属性列表
- ForeignKey/ManyToMany → 实体关系
- docstring → 业务描述
- Meta.verbose_name → 中文名称

#### SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric(10, 2))
    
    user = relationship("User", back_populates="orders")
```

**提取要点**：
- 类名 → 实体名称
- Column 定义 → 属性及约束
- relationship → 实体关系

#### Pydantic Model（FastAPI）

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserCreate(BaseModel):
    """创建用户请求"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """用户响应"""
    id: int
    name: str
    email: str
    orders: List['OrderResponse'] = []
    
    class Config:
        from_attributes = True
```

**提取要点**：
- 类名 → DTO/VO 名称
- Field 约束 → 验证规则
- docstring → 业务描述

### 4. 服务识别规则

#### Django View/ViewSet

```python
# views.py
from rest_framework import viewsets
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活用户账户"""
        # 用例：激活用户
        pass
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        # 用例：获取个人信息
        pass
```

**提取要点**：
- ViewSet 类 → 资源/实体
- CRUD 方法 → 标准用例
- @action 装饰器 → 自定义用例

#### FastAPI Router

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 用例：创建用户
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户详情"""
    # 用例：获取用户
    pass

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    # 用例：更新用户
    pass
```

**提取要点**：
- 路由装饰器 → API 设计
- 函数参数 → 输入规范
- response_model → 输出规范
- docstring → 用例描述

#### Service 层

```python
# services/user_service.py
class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, data: UserCreate) -> User:
        """创建用户
        
        业务规则：
        1. 邮箱必须唯一
        2. 密码需要加密存储
        """
        # 规则1：检查邮箱唯一性
        if self.db.query(User).filter(User.email == data.email).first():
            raise ValueError("邮箱已被使用")
        
        # 规则2：密码加密
        hashed_password = hash_password(data.password)
        
        user = User(
            name=data.name,
            email=data.email,
            password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        return user
```

**提取要点**：
- 方法名 → 用例名称
- docstring → 业务规则
- 异常处理 → 业务约束

### 5. 业务规则识别

#### 从 Pydantic 验证器中提取

```python
from pydantic import BaseModel, validator, root_validator

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)  # 规则：数量必须大于0
    
    @validator('quantity')
    def check_quantity(cls, v):
        if v > 100:
            raise ValueError('单次订购数量不能超过100')  # 规则：数量限制
        return v
    
    @root_validator
    def check_total(cls, values):
        # 规则：总金额校验
        pass
```

#### 从 Django 验证器中提取

```python
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    price = models.DecimalField(
        validators=[MinValueValidator(0.01)],  # 规则：价格必须大于0
        max_digits=10,
        decimal_places=2
    )
    stock = models.IntegerField(
        validators=[MinValueValidator(0)]  # 规则：库存不能为负
    )
    
    def clean(self):
        # 自定义验证规则
        if self.price > 10000:
            raise ValidationError('价格不能超过10000')
```

#### 从业务逻辑中提取

```python
def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
    """创建订单"""
    # 规则1：用户状态检查
    user = self.user_repo.get(user_id)
    if not user.is_active:
        raise BusinessError("用户账户已被禁用")
    
    # 规则2：库存检查
    for item in items:
        product = self.product_repo.get(item.product_id)
        if product.stock < item.quantity:
            raise BusinessError(f"商品 {product.name} 库存不足")
    
    # 规则3：VIP 折扣
    total = sum(item.price * item.quantity for item in items)
    if user.is_vip:
        total *= 0.9  # 9折优惠
    
    # 规则4：最低订单金额
    if total < 10:
        raise BusinessError("订单金额不能低于10元")
    
    return self.order_repo.create(Order(
        user_id=user_id,
        items=items,
        total=total,
        status=OrderStatus.PENDING
    ))
```

## 分析输出模板

### Domain 识别报告

```markdown
## 识别的 Domain 列表

### Domain 1: [domain-name]
- **目录路径**: apps/users 或 app/api/v1/users.py
- **核心实体**: User, UserProfile, Session
- **主要服务**: UserService, AuthService
- **API 入口**: UserViewSet / user_router
- **用例数量**: 12

### Domain 2: [domain-name]
...
```

### 用例提取模板

```markdown
## [Domain Name] - 用例列表

### 001-[subdomain]/001-[usecase-name].md

**来源**: UserService.create_user() / UserViewSet.create()
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
- BR003: 用户名长度 2-100 字符
```

## 注意事项

1. **禁止单一 Domain**：必须识别并划分多个独立的业务 Domain
2. **关注 docstring**：Python 的 docstring 是重要的业务描述来源
3. **分析装饰器**：装饰器（如 `@validator`, `@action`）通常包含业务规则
4. **识别 Django App**：每个 Django App 通常对应一个业务领域
5. **查看 Pydantic 模型**：Pydantic 模型定义了数据验证规则
6. **注意类型注解**：Python 3 的类型注解提供了数据结构信息

