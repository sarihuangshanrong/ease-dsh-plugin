# Python 测试生成参考文档

本指南提供了为 Python 项目生成单元测试代码的具体规范和最佳实践。

## 测试框架选择

### 主要测试框架

1. **unittest**: Python标准库自带的测试框架
2. **pytest**: 功能强大且流行的第三方测试框架（推荐）
3. **mock**: Python标准库中的Mock库（Python 3.3+集成在unittest中）
4. **coverage**: 代码覆盖率工具

### 依赖安装

```bash
# pytest及相关插件
pip install pytest pytest-cov pytest-mock

# 或者在requirements-dev.txt中添加
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

## 测试文件命名规范

Python测试文件遵循以下命名规范：

```
user.py          -> test_user.py
order_service.py -> test_order_service.py
handlers.py      -> test_handlers.py
```

或者使用tests目录结构：

```
src/
  user.py
  order_service.py
tests/
  test_user.py
  test_order_service.py
```

## 测试函数命名规范

### pytest风格

```python
def test_function_name():
    # 测试逻辑

def test_class_method_name():
    # 测试类方法
```

### unittest风格

```python
import unittest

class TestClassName(unittest.TestCase):
    def test_method_name(self):
        # 测试逻辑
```

## 基础测试结构

### pytest基础测试示例

```python
import pytest
from unittest.mock import Mock, patch
from user import UserService, User

def test_user_service_create_user():
    # Given
    user_service = UserService()
    user_data = {"name": "John", "email": "john@example.com"}

    # When
    user = user_service.create_user(user_data)

    # Then
    assert user is not None
    assert user.name == "John"
    assert user.email == "john@example.com"
```

### unittest基础测试示例

```python
import unittest
from unittest.mock import Mock, patch
from user import UserService, User

class TestUserService(unittest.TestCase):

    def setUp(self):
        self.user_service = UserService()

    def test_create_user(self):
        # Given
        user_data = {"name": "John", "email": "john@example.com"}

        # When
        user = self.user_service.create_user(user_data)

        # Then
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "John")
        self.assertEqual(user.email, "john@example.com")
```

## Mock使用规范

### 使用unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_user_service_send_welcome_email():
    # Given
    mock_email_service = Mock()
    user_service = UserService(email_service=mock_email_service)
    user = User(name="John", email="john@example.com")

    # When
    user_service.send_welcome_email(user)

    # Then
    mock_email_service.send.assert_called_once_with(
        to="john@example.com",
        subject="Welcome!",
        body="Welcome John!"
    )

# 使用装饰器进行patch
@patch('user.email_service.send')
def test_user_service_send_welcome_email_with_patch(mock_send):
    # Given
    user_service = UserService()
    user = User(name="John", email="john@example.com")

    # When
    user_service.send_welcome_email(user)

    # Then
    mock_send.assert_called_once_with(
        to="john@example.com",
        subject="Welcome!",
        body="Welcome John!"
    )
```

### 使用pytest-mock

```python
def test_user_service_create_user_with_mocker(mocker):
    # Given
    mock_repository = mocker.Mock()
    user_service = UserService(repository=mock_repository)
    user_data = {"name": "John", "email": "john@example.com"}

    mock_user = User(name="John", email="john@example.com")
    mock_repository.save.return_value = mock_user

    # When
    user = user_service.create_user(user_data)

    # Then
    assert user == mock_user
    # L4：验证 save 收到的对象携带正确字段（非仅"被调过"）
    saved = mock_repository.save.call_args.args[0]
    assert saved.name == "John"
    assert saved.email == "john@example.com"
```

## 断言规范

### pytest断言

```python
def test_user_validation():
    user = User(name="John", email="john@example.com")

    # 基本断言
    assert user is not None
    assert user.name == "John"
    assert user.email != ""
    assert len(user.name) > 0

    # 异常断言
    with pytest.raises(ValueError):
        user.validate()

    # 集合断言
    users = ["Alice", "Bob", "Charlie"]
    assert "Alice" in users
    assert len(users) == 3

    # 字典断言
    user_dict = {"name": "John", "age": 30}
    assert user_dict["name"] == "John"
    assert "name" in user_dict
```

### unittest断言

```python
import unittest

class TestUserValidation(unittest.TestCase):

    def test_user_validation(self):
        user = User(name="John", email="john@example.com")

        # 基本断言
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "John")
        self.assertNotEqual(user.email, "")
        self.assertTrue(len(user.name) > 0)

        # 异常断言
        with self.assertRaises(ValueError):
            user.validate()

        # 集合断言
        users = ["Alice", "Bob", "Charlie"]
        self.assertIn("Alice", users)
        self.assertEqual(len(users), 3)
```

## 测试夹具（Fixtures）

### pytest fixtures

```python
import pytest
from user import UserService, UserRepository

@pytest.fixture
def user_repository():
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(user_repository):
    return UserService(repository=user_repository)

@pytest.fixture
def sample_user():
    return User(name="John", email="john@example.com")

def test_user_service_create_user(user_service, user_repository, sample_user):
    # Given
    user_data = {"name": "John", "email": "john@example.com"}
    user_repository.save.return_value = sample_user

    # When
    user = user_service.create_user(user_data)

    # Then
    assert user == sample_user
    # L4：验证 save 收到的对象携带正确字段
    saved = user_repository.save.call_args.args[0]
    assert saved.name == "John"
    assert saved.email == "john@example.com"
```

### 作用域fixtures

```python
@pytest.fixture(scope="session")
def database():
    """会话级别的fixture，整个测试会话只执行一次"""
    db = setup_test_database()
    yield db
    teardown_test_database(db)

@pytest.fixture(scope="module")
def user_service():
    """模块级别的fixture，每个测试模块执行一次"""
    service = UserService()
    return service

@pytest.fixture(scope="function")
def sample_user():
    """函数级别的fixture，每个测试函数执行一次（默认）"""
    return User(name="Test User", email="test@example.com")
```

## 参数化测试

### pytest参数化

```python
import pytest

@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("test@.com", False),
    ("test@example.", False),
])
def test_user_service_validate_email(user_service, email, expected):
    result = user_service.validate_email(email)
    assert result == expected

# 多参数参数化
@pytest.mark.parametrize("name,email,should_be_valid", [
    ("John", "john@example.com", True),
    ("", "john@example.com", False),
    ("John", "invalid-email", False),
    ("John", "", False),
])
def test_user_creation_validation(user_service, name, email, should_be_valid):
    if should_be_valid:
        user = user_service.create_user({"name": name, "email": email})
        assert user is not None
    else:
        with pytest.raises(ValueError):
            user_service.create_user({"name": name, "email": email})
```

### unittest参数化

```python
import unittest

class TestUserServiceValidation(unittest.TestCase):

    def test_validate_email_valid_cases(self):
        valid_emails = ["test@example.com", "user@domain.co.uk", "test123@test.org"]
        for email in valid_emails:
            with self.subTest(email=email):
                result = self.user_service.validate_email(email)
                self.assertTrue(result)

    def test_validate_email_invalid_cases(self):
        invalid_emails = ["invalid-email", "", "test@", "@example.com"]
        for email in invalid_emails:
            with self.subTest(email=email):
                result = self.user_service.validate_email(email)
                self.assertFalse(result)
```

## 测试数据管理

### 测试数据工厂

```python
# test_factories.py
import factory
from user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f"User {n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '')}@example.com")

# 或者简单的数据构建函数
class UserDataBuilder:
    def __init__(self):
        self.data = {
            "name": "Default Name",
            "email": "default@example.com"
        }

    def with_name(self, name):
        self.data["name"] = name
        return self

    def with_email(self, email):
        self.data["email"] = email
        return self

    def build(self):
        return self.data.copy()

# 在测试中使用
def test_user_service_create_user_with_builder():
    user_data = UserDataBuilder().with_name("John").with_email("john@example.com").build()
    user = user_service.create_user(user_data)
    assert user.name == "John"
```

### 使用fixtures管理测试数据

```python
@pytest.fixture
def valid_user_data():
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30
    }

@pytest.fixture
def invalid_user_data():
    return {
        "name": "",
        "email": "invalid-email",
        "age": -5
    }

def test_user_service_create_valid_user(user_service, valid_user_data):
    user = user_service.create_user(valid_user_data)
    assert user is not None
    assert user.name == valid_user_data["name"]

def test_user_service_reject_invalid_user(user_service, invalid_user_data):
    with pytest.raises(ValueError):
        user_service.create_user(invalid_user_data)
```

## 不同类型代码的测试策略

### 1. 业务逻辑测试

```python
def test_order_service_calculate_total():
    # Given
    order_items = [
        {"price": 100, "quantity": 2},
        {"price": 50, "quantity": 1}
    ]
    order_service = OrderService()

    # When
    total = order_service.calculate_total(order_items)

    # Then
    assert total == 250
```

### 2. Web API测试

```python
import pytest
from flask import Flask
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_user_endpoint(client, mocker):
    # Given
    mock_user_service = mocker.patch('app.user_service')
    mock_user = User(name="John", email="john@example.com")
    mock_user_service.create_user.return_value = mock_user

    user_data = {"name": "John", "email": "john@example.com"}

    # When
    response = client.post('/users', json=user_data)

    # Then
    assert response.status_code == 201
    assert response.json['name'] == "John"
    mock_user_service.create_user.assert_called_once_with(user_data)
```

### 3. 数据库操作测试

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def dbsession(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_user_repository_save(dbsession):
    # Given
    user = User(name="John", email="john@example.com")
    repository = UserRepository(dbsession)

    # When
    saved_user = repository.save(user)

    # Then
    assert saved_user.id is not None
    assert saved_user.name == "John"

    # 验证数据确实保存到了数据库
    retrieved_user = dbsession.query(User).filter_by(name="John").first()
    assert retrieved_user is not None
    assert retrieved_user.email == "john@example.com"
```

## 测试覆盖率要求

### 代码覆盖率指标

- **行覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 85%

### 覆盖率检查

```bash
# 运行测试并生成覆盖率报告
pytest --cov=.

# 生成详细覆盖率报告
pytest --cov=. --cov-report=html

# 设置覆盖率阈值
pytest --cov=. --cov-fail-under=80

# 排除某些文件
pytest --cov=. --cov-config=.coveragerc
```

### .coveragerc配置文件

```ini
[run]
source = .
omit =
    */tests/*
    */venv/*
    */.venv/*
    */migrations/*
    */settings/*
    manage.py
    */test_*.py
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## 性能测试

### 编写性能测试

```python
import pytest
import time

def test_user_service_create_user_performance(user_service):
    # Given
    user_data = {"name": "John", "email": "john@example.com"}

    # When
    start_time = time.time()
    for _ in range(1000):
        user_service.create_user(user_data)
    end_time = time.time()

    # Then
    execution_time = end_time - start_time
    assert execution_time < 1.0  # 应该在1秒内完成1000次操作

# 使用pytest-benchmark插件
def test_user_service_create_user_benchmark(user_service, benchmark):
    user_data = {"name": "John", "email": "john@example.com"}

    def create_user():
        return user_service.create_user(user_data)

    result = benchmark(create_user)
    assert result is not None
```

## 异步测试

### 异步测试示例

```python
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_user_service_create_user():
    # Given
    mock_db = AsyncMock()
    user_service = AsyncUserService(database=mock_db)
    user_data = {"name": "John", "email": "john@example.com"}

    # When
    user = await user_service.create_user(user_data)

    # Then
    assert user is not None
    # L4：验证 save 收到的对象携带正确字段
    saved = mock_db.save.await_args.args[0]
    assert saved.name == "John"

# 测试异步HTTP客户端
@pytest.mark.asyncio
async def test_async_api_call(client):
    response = await client.get('/users')
    assert response.status == 200
```

## 最佳实践

### 1. 测试组织

```python
# conftest.py - 共享的fixtures
import pytest

@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动应用于所有测试的fixture"""
    # 设置测试环境
    yield
    # 清理测试环境

# test_user_service.py
import pytest

class TestUserService:
    """UserService的测试套件"""

    class TestCreateUser:
        """create_user方法的测试子集"""

        def test_creates_user_with_valid_data(self, user_service):
            # 测试逻辑

        def test_raises_error_with_invalid_data(self, user_service):
            # 测试逻辑

    class TestUpdateUser:
        """update_user方法的测试子集"""

        def test_updates_existing_user(self, user_service):
            # 测试逻辑
```

### 2. 测试隔离

```python
def test_user_creation_does_not_affect_other_tests(user_service):
    # 每个测试都应该独立，不影响其他测试
    initial_count = user_service.count_users()

    user_service.create_user({"name": "John", "email": "john@example.com"})

    # 不要在测试之间共享状态
    # 下一个测试应该从干净的状态开始
```

### 3. 清晰的测试意图

```python
# 好的命名清楚表达了测试意图
def test_user_service_create_user_returns_created_user_when_given_valid_data():
    # 测试逻辑

# 避免模糊的命名
def test_create():  # 不推荐
    # 测试逻辑

# 使用描述性的测试名称
def test_calculate_discount_returns_10_percent_for_orders_over_100_dollars():
    # 测试逻辑
```

### 4. 测试数据管理

```python
# 使用常量管理测试数据
VALID_USER_EMAIL = "test@example.com"
INVALID_USER_EMAIL = "invalid-email"
USER_NAME = "Test User"

def test_user_service_validate_email_with_constants():
    assert user_service.validate_email(VALID_USER_EMAIL) is True
    assert user_service.validate_email(INVALID_USER_EMAIL) is False
```

## MC/DC 测试设计

### MC/DC 原则说明

MC/DC (Modified Condition/Decision Coverage) 是一种严格的测试覆盖准则，要求：
- **条件独立性**：每个条件独立影响决策结果
- **分支全覆盖**：所有分支路径都被测试
- **边界值测试**：测试输入域的边界及其附近值

### 复杂决策逻辑的 MC/DC 测试示例

```python
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    credit_score: int
    debt_to_income_ratio: float
    employment_years: int
    annual_income: Decimal

@dataclass
class LoanRequest:
    id: int
    amount: Decimal

class LoanService:
    def approve_loan(self, user: User, request: LoanRequest) -> bool:
        """
        贷款审批决策逻辑
        决策：(条件1 AND 条件2 AND 条件3) OR (条件1 AND 条件4)
        """
        # 条件1: 信用评分 >= 650
        good_credit = user.credit_score >= 650
        # 条件2: 负债率 <= 0.43
        good_debt_ratio = user.debt_to_income_ratio <= 0.43
        # 条件3: 就业稳定性 >= 2年
        stable_employment = user.employment_years >= 2
        # 条件4: 贷款金额合理 (<= 4倍年收入)
        reasonable_amount = request.amount <= user.annual_income * 4
        
        return (good_credit and good_debt_ratio and stable_employment) or \
               (good_credit and reasonable_amount)
```

### MC/DC 测试用例设计

```python
import pytest
from decimal import Decimal

class TestLoanServiceMCDC:
    """MC/DC 测试用例 - 验证每个条件独立影响决策"""
    
    def setup_method(self):
        self.loan_service = LoanService()
    
    def test_good_credit_independence(self):
        """测试条件1（信用评分）的独立影响"""
        # 基线：good_credit=False, 其他条件=True
        user = User(
            id=1,
            name="Test User",
            credit_score=600,  # good_credit = False
            debt_to_income_ratio=0.35,  # good_debt_ratio = True
            employment_years=5,  # stable_employment = True
            annual_income=Decimal("50000")
        )
        request = LoanRequest(id=1, amount=Decimal("150000"))  # 合理金额
        
        assert self.loan_service.approve_loan(user, request) is False
        
        # 改变条件1：good_credit=True, 保持其他不变
        user.credit_score = 700  # good_credit = True
        assert self.loan_service.approve_loan(user, request) is True
    
    def test_good_debt_ratio_independence(self):
        """测试条件2（负债率）的独立影响"""
        # 基线：good_debt_ratio=False, 其他条件=True
        user = User(
            id=1,
            name="Test User",
            credit_score=700,  # good_credit = True
            debt_to_income_ratio=0.50,  # good_debt_ratio = False
            employment_years=5,  # stable_employment = True
            annual_income=Decimal("50000")
        )
        # 设置不合理金额，确保条件4也为False
        request = LoanRequest(id=1, amount=Decimal("250000"))
        
        assert self.loan_service.approve_loan(user, request) is False
        
        # 改变条件2：good_debt_ratio=True, 保持其他不变
        user.debt_to_income_ratio = 0.35  # good_debt_ratio = True
        assert self.loan_service.approve_loan(user, request) is True
    
    def test_stable_employment_independence(self):
        """测试条件3（就业稳定性）的独立影响"""
        # 基线：stable_employment=False, 其他条件=True
        user = User(
            id=1,
            name="Test User",
            credit_score=700,  # good_credit = True
            debt_to_income_ratio=0.35,  # good_debt_ratio = True
            employment_years=1,  # stable_employment = False
            annual_income=Decimal("50000")
        )
        # 设置不合理金额，确保条件4也为False
        request = LoanRequest(id=1, amount=Decimal("250000"))
        
        assert self.loan_service.approve_loan(user, request) is False
        
        # 改变条件3：stable_employment=True, 保持其他不变
        user.employment_years = 3  # stable_employment = True
        assert self.loan_service.approve_loan(user, request) is True
    
    def test_reasonable_amount_independence(self):
        """测试条件4（贷款金额合理性）的独立影响"""
        # 基线：reasonable_amount=False, 条件3=False（测试备选路径）
        user = User(
            id=1,
            name="Test User",
            credit_score=700,  # good_credit = True
            debt_to_income_ratio=0.35,  # good_debt_ratio = True
            employment_years=1,  # stable_employment = False
            annual_income=Decimal("50000")
        )
        request = LoanRequest(id=1, amount=Decimal("250000"))  # 不合理金额
        
        assert self.loan_service.approve_loan(user, request) is False
        
        # 改变条件4：reasonable_amount=True, 保持其他不变
        request.amount = Decimal("150000")  # 合理金额
        assert self.loan_service.approve_loan(user, request) is True


class TestLoanServiceBoundaryValues:
    """边界值测试"""
    
    def setup_method(self):
        self.loan_service = LoanService()
    
    @pytest.mark.parametrize("credit_score,expected", [
        (649, False),  # 边界值 - 1
        (650, True),   # 边界值
        (651, True),   # 边界值 + 1
    ])
    def test_credit_score_boundary_values(self, credit_score, expected):
        """测试信用评分边界值"""
        user = User(
            id=1,
            name="Test User",
            credit_score=credit_score,
            debt_to_income_ratio=0.35,
            employment_years=5,
            annual_income=Decimal("50000")
        )
        request = LoanRequest(id=1, amount=Decimal("150000"))
        
        assert self.loan_service.approve_loan(user, request) is expected
    
    @pytest.mark.parametrize("debt_ratio,expected", [
        (0.44, False),  # 边界值 + 0.01
        (0.43, True),   # 边界值
        (0.42, True),   # 边界值 - 0.01
    ])
    def test_debt_ratio_boundary_values(self, debt_ratio, expected):
        """测试负债率边界值"""
        user = User(
            id=1,
            name="Test User",
            credit_score=700,
            debt_to_income_ratio=debt_ratio,
            employment_years=5,
            annual_income=Decimal("50000")
        )
        request = LoanRequest(id=1, amount=Decimal("150000"))
        
        assert self.loan_service.approve_loan(user, request) is expected
```

### MC/DC 测试模板

```python
def test_condition_independence(self):
    """
    MC/DC 测试模板 - 验证单个条件的独立影响
    """
    # 基线：目标条件=False, 其他条件设置为使决策依赖目标条件
    test_data = create_test_data(
        target_condition=False,
        other_conditions=True
    )
    
    assert service.evaluate_decision(test_data) is False
    
    # 改变目标条件：目标条件=True, 保持其他不变
    test_data.target_condition = True
    assert service.evaluate_decision(test_data) is True
```

## 确定性隔离要点（Python，对齐 SKILL.md D1–D9）

- **D2** `mock.patch` 用上下文管理器（`with patch(...) as m:`）或 `mocker` fixture（自动 stop）；勿用裸 `patch.start()` 而不 stop。
- **D3** 时间用 `freezegun.freeze_time("2026-06-30 08:00:00")` 或注入 `now` 函数，勿调 `datetime.now()`。
- **D7** 临时文件用 `tmp_path` fixture（pytest 内建，自动清理）；DB 用 transaction rollback fixture。
- **D8** 显式 `locale`/编码，但修改进程级 locale 时必须恢复：fixture 先保存
  `previous = locale.setlocale(locale.LC_ALL)`，在 `try/finally` 的 `finally` 中执行
  `locale.setlocale(locale.LC_ALL, previous)`；字节串显式 `encode("utf-8")`。并行测试优先
  避免修改全局 locale，改为向格式化组件注入 locale。

> D1/D5/D6 由 lint 机械化（🔒 C1/C4/C5）。

通过遵循这些规范和最佳实践，可以生成高质量、可维护的Python单元测试代码。
