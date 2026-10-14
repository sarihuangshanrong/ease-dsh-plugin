# Python 编码最佳实践指南

本指南提供 Python 项目的编码规范、设计模式和最佳实践。

## 代码风格规范

### 命名规范（PEP 8）

```python
# 模块名：小写，下划线分隔
user_service.py
order_repository.py

# 类名：大驼峰命名
class UserService:
    pass

class OrderRepository:
    pass

# 函数和方法名：小写，下划线分隔
def get_user_by_id(user_id: int) -> User:
    pass

def calculate_total_price(items: list[OrderItem]) -> Decimal:
    pass

# 变量名：小写，下划线分隔
user_name = "张三"
order_list = []

# 常量：全大写，下划线分隔
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
DATABASE_URL = "postgresql://localhost/mydb"

# 私有变量/方法：单下划线前缀
_internal_cache = {}

def _validate_email(email: str) -> bool:
    pass

# 类私有变量：双下划线前缀（name mangling）
class MyClass:
    def __init__(self):
        self.__private_var = 1

# 特殊方法：双下划线包围
def __init__(self):
    pass

def __str__(self):
    pass
```

### 代码格式

```python
# 缩进：4 个空格
# 行宽：79-100 字符（推荐 88，Black 默认）
# 使用 Black、isort、flake8 进行格式化和检查

# 导入顺序：标准库、第三方库、本地模块
import os
import sys
from datetime import datetime
from typing import Optional, List

import requests
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.services import UserService

# 类型注解
def get_user(user_id: int) -> Optional[User]:
    pass

def process_items(items: List[str]) -> dict[str, int]:
    pass
```

## FastAPI 最佳实践

### Router 层

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """创建新用户"""
    service = UserService(db)
    return service.create_user(user_in)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """获取用户详情"""
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """更新用户信息"""
    service = UserService(db)
    user = service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除用户"""
    service = UserService(db)
    if not service.delete_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
```

### Pydantic Schema

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """用户基础模型"""
    name: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(..., min_length=8, max_length=50, description="密码")
    
    @validator("password")
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("密码必须包含至少一个大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含至少一个数字")
        return v


class UserUpdate(BaseModel):
    """更新用户请求"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$")
    
    class Config:
        # 允许部分更新
        extra = "forbid"


class UserResponse(UserBase):
    """用户响应"""
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # 支持 ORM 模型转换


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int
    page: int
    size: int
    items: list


class APIResponse(BaseModel):
    """统一响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None
```

### 依赖注入

```python
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用",
        )
    return current_user
```

## Service 层

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.exceptions import BusinessException, ErrorCode

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_in: UserCreate) -> UserResponse:
        """创建用户"""
        # 1. 业务校验
        if self._get_user_by_email(user_in.email):
            raise BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS)
        
        # 2. 密码加密
        hashed_password = pwd_context.hash(user_in.password)
        
        # 3. 创建实体
        user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=hashed_password,
            status="active",
        )
        
        # 4. 持久化
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """根据 ID 获取用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return UserResponse.model_validate(user)
    
    def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[UserResponse]:
        """更新用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 只更新非空字段
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.model_validate(user)
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def list_users(
        self,
        page: int = 1,
        size: int = 20,
        status: Optional[str] = None,
    ) -> tuple[List[UserResponse], int]:
        """分页查询用户列表"""
        query = self.db.query(User)
        
        if status:
            query = query.filter(User.status == status)
        
        total = query.count()
        users = query.offset((page - 1) * size).limit(size).all()
        
        return [UserResponse.model_validate(u) for u in users], total
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查询用户"""
        return self.db.query(User).filter(User.email == email).first()
```

## SQLAlchemy 模型

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 关联关系
    orders = relationship("Order", back_populates="user", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # 金额（分）
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
```

## 异常处理

### 自定义业务异常

```python
from enum import Enum
from typing import Optional


class ErrorCode(Enum):
    """错误码枚举"""
    # 通用错误 1xxx
    SYSTEM_ERROR = (1000, "系统错误")
    PARAM_ERROR = (1001, "参数错误")
    
    # 用户相关 2xxx
    USER_NOT_FOUND = (2001, "用户不存在")
    EMAIL_ALREADY_EXISTS = (2002, "邮箱已被注册")
    PASSWORD_INCORRECT = (2003, "密码错误")
    
    # 订单相关 3xxx
    ORDER_NOT_FOUND = (3001, "订单不存在")
    INSUFFICIENT_STOCK = (3002, "库存不足")
    
    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message
    
    @property
    def code(self) -> int:
        return self._code
    
    @property
    def message(self) -> str:
        return self._message


class BusinessException(Exception):
    """业务异常"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        detail: Optional[str] = None,
    ):
        self.error_code = error_code
        self.detail = detail or error_code.message
        super().__init__(self.detail)
    
    @property
    def code(self) -> int:
        return self.error_code.code
    
    @property
    def message(self) -> str:
        return self.detail
```

### 全局异常处理

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import BusinessException

app = FastAPI()


@app.exception_handler(BusinessException)
async def business_exception_handler(
    request: Request,
    exc: BusinessException,
) -> JSONResponse:
    """业务异常处理"""
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """参数校验异常处理"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=400,
        content={
            "code": 1001,
            "message": "参数错误: " + "; ".join(errors),
            "data": None,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """通用异常处理"""
    # 记录日志
    import logging
    logging.error(f"未处理异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "code": 1000,
            "message": "系统繁忙，请稍后重试",
            "data": None,
        },
    )
```

## Django 最佳实践

### View 层

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from apps.users.services import UserService


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """创建用户"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UserService()
        user = service.create_user(serializer.validated_data)
        
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """激活用户"""
        user = self.get_object()
        service = UserService()
        user = service.activate_user(user)
        
        return Response(UserSerializer(user).data)
    
    @action(detail=False, methods=["get"])
    def me(self, request):
        """获取当前用户信息"""
        return Response(UserSerializer(request.user).data)
```

### Serializer

```python
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    
    class Meta:
        model = User
        fields = ["id", "name", "email", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ["name", "email", "password", "password_confirm"]
    
    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "密码不匹配"})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """更新用户序列化器"""
    
    class Meta:
        model = User
        fields = ["name", "phone"]
```

## 设计模式应用

### 策略模式

```python
from abc import ABC, abstractmethod
from typing import Protocol


class PaymentStrategy(Protocol):
    """支付策略协议"""
    
    def pay(self, order: "Order") -> "PaymentResult":
        ...


class AlipayStrategy:
    """支付宝支付策略"""
    
    def __init__(self, client: "AlipayClient"):
        self.client = client
    
    def pay(self, order: "Order") -> "PaymentResult":
        # 支付宝支付逻辑
        return self.client.create_payment(order)


class WechatPayStrategy:
    """微信支付策略"""
    
    def __init__(self, client: "WechatClient"):
        self.client = client
    
    def pay(self, order: "Order") -> "PaymentResult":
        # 微信支付逻辑
        return self.client.create_payment(order)


class PaymentService:
    """支付服务"""
    
    def __init__(self):
        self._strategies: dict[str, PaymentStrategy] = {}
    
    def register_strategy(self, name: str, strategy: PaymentStrategy) -> None:
        self._strategies[name] = strategy
    
    def pay(self, payment_type: str, order: "Order") -> "PaymentResult":
        strategy = self._strategies.get(payment_type)
        if not strategy:
            raise ValueError(f"不支持的支付方式: {payment_type}")
        return strategy.pay(order)


# 使用
payment_service = PaymentService()
payment_service.register_strategy("alipay", AlipayStrategy(alipay_client))
payment_service.register_strategy("wechat", WechatPayStrategy(wechat_client))

result = payment_service.pay("alipay", order)
```

### 工厂模式

```python
from abc import ABC, abstractmethod
from typing import Type


class Notification(ABC):
    """通知基类"""
    
    @abstractmethod
    def send(self, message: str, recipient: str) -> bool:
        pass


class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        # 发送邮件
        return True


class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        # 发送短信
        return True


class PushNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        # 发送推送
        return True


class NotificationFactory:
    """通知工厂"""
    
    _notification_types: dict[str, Type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    
    @classmethod
    def create(cls, notification_type: str) -> Notification:
        notification_class = cls._notification_types.get(notification_type)
        if not notification_class:
            raise ValueError(f"不支持的通知类型: {notification_type}")
        return notification_class()
    
    @classmethod
    def register(cls, name: str, notification_class: Type[Notification]) -> None:
        cls._notification_types[name] = notification_class


# 使用
notification = NotificationFactory.create("email")
notification.send("Hello", "user@example.com")
```

### 装饰器模式

```python
import functools
import time
import logging
from typing import Callable, TypeVar

T = TypeVar("T")

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"第 {attempt + 1} 次尝试失败: {e}"
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


def timer(func: Callable[..., T]) -> Callable[..., T]:
    """计时装饰器"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"{func.__name__} 执行耗时: {duration:.3f}s")
        return result
    return wrapper


def cache(ttl: int = 300):
    """缓存装饰器"""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        _cache: dict = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            key = str(args) + str(kwargs)
            now = time.time()
            
            if key in _cache:
                value, timestamp = _cache[key]
                if now - timestamp < ttl:
                    return value
            
            result = func(*args, **kwargs)
            _cache[key] = (result, now)
            return result
        return wrapper
    return decorator


# 使用
@retry(max_attempts=3, delay=0.5)
@timer
def fetch_data(url: str) -> dict:
    # 获取数据
    pass
```

## 异步编程

### asyncio 使用

```python
import asyncio
from typing import List

import httpx


async def fetch_url(client: httpx.AsyncClient, url: str) -> dict:
    """异步获取 URL"""
    response = await client.get(url)
    return response.json()


async def fetch_all(urls: List[str]) -> List[dict]:
    """并发获取多个 URL"""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]


# 使用
async def main():
    urls = [
        "https://api.example.com/users/1",
        "https://api.example.com/users/2",
        "https://api.example.com/users/3",
    ]
    results = await fetch_all(urls)
    print(results)


asyncio.run(main())
```

### 异步数据库操作

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

# 异步引擎
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/db",
    echo=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db():
    """异步数据库会话依赖"""
    async with AsyncSessionLocal() as session:
        yield session


class AsyncUserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_in: UserCreate) -> User:
        user = User(**user_in.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

## 测试实践

### 单元测试

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.core.exceptions import BusinessException, ErrorCode


class TestUserService:
    
    @pytest.fixture
    def mock_db(self):
        return MagicMock()
    
    @pytest.fixture
    def user_service(self, mock_db):
        return UserService(mock_db)
    
    def test_create_user_success(self, user_service, mock_db):
        # Arrange
        user_in = UserCreate(
            name="test",
            email="test@example.com",
            password="Password123",
        )
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = user_service.create_user(user_in)
        
        # Assert
        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_user_email_exists(self, user_service, mock_db):
        # Arrange
        user_in = UserCreate(
            name="test",
            email="existing@example.com",
            password="Password123",
        )
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
        # Act & Assert
        with pytest.raises(BusinessException) as exc_info:
            user_service.create_user(user_in)
        
        assert exc_info.value.error_code == ErrorCode.EMAIL_ALREADY_EXISTS


class TestValidateEmail:
    
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("test@sub.example.com", True),
        ("testexample.com", False),
        ("test@", False),
        ("", False),
    ])
    def test_validate_email(self, email: str, expected: bool):
        from app.utils.validators import validate_email
        assert validate_email(email) == expected
```

### API 测试

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.deps import get_db
from app.db.base import Base

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestUserAPI:
    
    def test_create_user(self, client):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "test",
                "email": "test@example.com",
                "password": "Password123",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test"
        assert data["email"] == "test@example.com"
    
    def test_get_user(self, client, db):
        # 先创建用户
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "test",
                "email": "test@example.com",
                "password": "Password123",
            },
        )
        user_id = response.json()["id"]
        
        # 获取用户
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404
```

## 注意事项

1. **遵循 PEP 8**：使用 Black、isort、flake8 保持代码风格一致
2. **类型注解**：使用类型注解提高代码可读性和 IDE 支持
3. **异常处理**：使用自定义业务异常，避免裸露的 Exception
4. **依赖注入**：使用 FastAPI 的 Depends 或自定义容器管理依赖
5. **异步优先**：I/O 密集型操作优先使用异步
6. **测试覆盖**：核心业务逻辑必须有单元测试

