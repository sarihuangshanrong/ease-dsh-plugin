# TypeScript 测试生成参考文档

本指南提供了为 TypeScript 项目生成单元测试代码的具体规范和最佳实践。

## 测试框架选择

### 主要测试框架

1. **Jest**: 功能全面的测试框架（推荐）
2. **Mocha**: 灵活的测试框架
3. **Jasmine**: 行为驱动开发(BDD)测试框架
4. **ts-mockito**: TypeScript专用的Mock框架

### 依赖安装

```bash
# Jest及相关工具
npm install --save-dev jest @types/jest ts-jest

# 或者使用yarn
yarn add --dev jest @types/jest ts-jest

# ts-mockito
npm install --save-dev ts-mockito
```

### Jest配置

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 85,
      lines: 80,
      statements: 80
    }
  }
};
```

## 测试文件命名规范

TypeScript测试文件遵循以下命名规范：

```
user.service.ts          -> user.service.spec.ts
order.controller.ts      -> order.controller.spec.ts
utils.ts                 -> utils.spec.ts
```

或者使用`__tests__`目录结构：

```
src/
  user/
    user.service.ts
    __tests__/
      user.service.spec.ts
```

## 测试函数命名规范

### Jest/Mocha风格

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a user with valid data', () => {
      // 测试逻辑
    });

    it('should throw an error when name is empty', () => {
      // 测试逻辑
    });
  });
});
```

### BDD风格

```typescript
describe('UserService', () => {
  describe('when creating a user', () => {
    context('with valid data', () => {
      it('should return the created user', () => {
        // 测试逻辑
      });
    });

    context('with invalid data', () => {
      it('should throw a validation error', () => {
        // 测试逻辑
      });
    });
  });
});
```

## 基础测试结构

### Jest基础测试示例

```typescript
import { UserService } from '../user.service';
import { User } from '../user.model';

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService();
  });

  describe('createUser', () => {
    it('should create a user with valid data', () => {
      // Given
      const userData = { name: 'John', email: 'john@example.com' };

      // When
      const user = userService.createUser(userData);

      // Then
      expect(user).toBeDefined();
      expect(user.name).toBe('John');
      expect(user.email).toBe('john@example.com');
    });

    it('should throw an error when name is empty', () => {
      // Given
      const userData = { name: '', email: 'john@example.com' };

      // When & Then
      expect(() => userService.createUser(userData)).toThrow('Name is required');
    });
  });
});
```

## Mock使用规范

### 使用Jest Mock

```typescript
import { UserRepository } from '../user.repository';
import { UserService } from '../user.service';

describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    // 创建Mock对象
    mockUserRepository = {
      save: jest.fn(),
      findById: jest.fn(),
      findAll: jest.fn()
    } as any;

    userService = new UserService(mockUserRepository);
  });

  describe('createUser', () => {
    it('should save user and return saved user', async () => {
      // Given
      const userData = { name: 'John', email: 'john@example.com' };
      const savedUser = { id: 1, ...userData };

      mockUserRepository.save.mockResolvedValue(savedUser);

      // When
      const result = await userService.createUser(userData);

      // Then
      expect(result).toEqual(savedUser);
      expect(mockUserRepository.save).toHaveBeenCalledWith(userData);
    });
  });
});
```

### 使用ts-mockito

```typescript
import { mock, instance, when, verify, capture, anything } from 'ts-mockito';
import { UserRepository } from '../user.repository';
import { UserService } from '../user.service';

describe('UserService', () => {
  let userService: UserService;
  let mockedUserRepository: UserRepository;

  beforeEach(() => {
    mockedUserRepository = mock(UserRepository);
    userService = new UserService(instance(mockedUserRepository));
  });

  describe('createUser', () => {
    it('should save user and return saved user', async () => {
      // Given
      const userData = { name: 'John', email: 'john@example.com' };
      const savedUser = { id: 1, ...userData };

      when(mockedUserRepository.save(anything())).thenResolve(savedUser);

      // When
      const result = await userService.createUser(userData);

      // Then（L4：用 capture 断言 save 收到的精确实参，而非 anything() 通配放过错误参数）
      expect(result).toEqual(savedUser);
      verify(mockedUserRepository.save(anything())).once();
      const savedArg = capture(mockedUserRepository.save).last();
      expect(savedArg).toMatchObject({ name: 'John', email: 'john@example.com' });
    });
  });
});
```

### Mock模块

```typescript
// 模拟整个模块
jest.mock('../email.service', () => {
  return {
    EmailService: jest.fn().mockImplementation(() => {
      return {
        sendWelcomeEmail: jest.fn().mockResolvedValue(undefined)
      };
    })
  };
});

// 部分模拟模块
jest.mock('../database', () => {
  const originalModule = jest.requireActual('../database');
  return {
    ...originalModule,
    connect: jest.fn().mockResolvedValue({ connected: true })
  };
});
```

## 断言规范

### Jest断言

```typescript
describe('User Validation', () => {
  it('should validate user properties correctly', () => {
    const user = new User('John', 'john@example.com');

    // 基本断言
    expect(user).toBeDefined();
    expect(user.name).toBe('John');
    expect(user.email).toEqual('john@example.com');
    expect(user.isActive).toBeTruthy();

    // 数组断言
    const users = ['Alice', 'Bob', 'Charlie'];
    expect(users).toContain('Alice');
    expect(users).toHaveLength(3);

    // 对象断言
    const userObj = { name: 'John', age: 30 };
    expect(userObj).toHaveProperty('name', 'John');
    expect(userObj).toMatchObject({ name: 'John' });

    // 异常断言
    expect(() => user.validate()).not.toThrow();
    expect(() => new User('', '')).toThrow('Name is required');
  });
});
```

### 异步断言

```typescript
describe('Async Operations', () => {
  it('should resolve with user data', async () => {
    // Given
    const userData = { id: 1, name: 'John' };
    const promise = Promise.resolve(userData);

    // When & Then
    await expect(promise).resolves.toBeDefined();
    await expect(promise).resolves.toEqual(userData);
  });

  it('should reject with error', async () => {
    // Given
    const error = new Error('User not found');
    const promise = Promise.reject(error);

    // When & Then
    await expect(promise).rejects.toThrow('User not found');
    await expect(promise).rejects.toBeInstanceOf(Error);
  });
});
```

## 测试夹具（Test Fixtures）

### 使用beforeEach/afterEach

```typescript
describe('UserService', () => {
  let userService: UserService;
  let databaseConnection: any;

  beforeAll(async () => {
    // 在所有测试之前执行一次
    databaseConnection = await connectToDatabase();
  });

  afterAll(async () => {
    // 在所有测试之后执行一次
    await databaseConnection.close();
  });

  beforeEach(() => {
    // 在每个测试之前执行
    userService = new UserService();
  });

  afterEach(() => {
    // 在每个测试之后执行
    jest.clearAllMocks();
  });

  it('should create user', () => {
    // 测试逻辑
  });
});
```

### 共享测试数据

```typescript
// test-fixtures.ts
export const validUserData = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  age: 30
};

export const invalidUserData = {
  name: '',
  email: 'invalid-email',
  age: -5
};

export const createUserFixture = (overrides = {}) => ({
  ...validUserData,
  ...overrides
});

// 在测试中使用
import { validUserData, createUserFixture } from './test-fixtures';

describe('UserService', () => {
  it('should create user with valid data', () => {
    const user = userService.createUser(validUserData);
    expect(user.name).toBe('John Doe');
  });

  it('should create user with custom data', () => {
    const customUser = createUserFixture({ name: 'Jane' });
    const user = userService.createUser(customUser);
    expect(user.name).toBe('Jane');
  });
});
```

## 参数化测试

### 使用test.each

```typescript
describe('UserService', () => {
  describe('validateEmail', () => {
    test.each([
      ['test@example.com', true],
      ['invalid-email', false],
      ['', false],
      ['test@.com', false],
      ['test@example.', false]
    ])('should validate email %s as %s', (email, expected) => {
      const result = userService.validateEmail(email);
      expect(result).toBe(expected);
    });
  });

  // 使用对象形式的参数化测试
  test.each([
    { name: 'John', email: 'john@example.com', isValid: true },
    { name: '', email: 'john@example.com', isValid: false },
    { name: 'John', email: 'invalid-email', isValid: false }
  ])('should validate user $name with email $email', ({ name, email, isValid }) => {
    const userData = { name, email };
    if (isValid) {
      expect(() => userService.createUser(userData)).not.toThrow();
    } else {
      expect(() => userService.createUser(userData)).toThrow();
    }
  });
});
```

## 测试数据管理

### 测试数据工厂

```typescript
// test-factories.ts
import { User } from '../user.model';

interface UserFactoryOptions {
  id?: number;
  name?: string;
  email?: string;
  isActive?: boolean;
}

export class UserFactory {
  static create(options: UserFactoryOptions = {}): User {
    return new User(
      options.id || 1,  // 固定 id，保持确定性（禁止未 seed 随机，见 SKILL.md FIRST-Repeatable）
      options.name || 'Test User',
      options.email || 'test@example.com',
      options.isActive !== undefined ? options.isActive : true
    );
  }

  static createMany(count: number, options: UserFactoryOptions = {}): User[] {
    return Array.from({ length: count }, (_, i) =>
      this.create({ ...options, id: options.id || i + 1 })
    );
  }
}

// 在测试中使用
import { UserFactory } from './test-factories';

describe('UserService', () => {
  it('should process multiple users', () => {
    const users = UserFactory.createMany(5);
    const processedUsers = userService.processUsers(users);
    expect(processedUsers).toHaveLength(5);
  });
});
```

### 使用Builder模式

```typescript
class UserBuilder {
  private user: Partial<User> = {};

  withName(name: string): UserBuilder {
    this.user.name = name;
    return this;
  }

  withEmail(email: string): UserBuilder {
    this.user.email = email;
    return this;
  }

  withActive(isActive: boolean): UserBuilder {
    this.user.isActive = isActive;
    return this;
  }

  build(): User {
    return new User(
      this.user.id || 1,
      this.user.name || 'Default Name',
      this.user.email || 'default@example.com',
      this.user.isActive !== undefined ? this.user.isActive : true
    );
  }
}

// 在测试中使用
it('should create user with builder', () => {
  const user = new UserBuilder()
    .withName('John')
    .withEmail('john@example.com')
    .withActive(true)
    .build();

  expect(user.name).toBe('John');
  expect(user.email).toBe('john@example.com');
  expect(user.isActive).toBe(true);
});
```

## 不同类型代码的测试策略

### 1. 业务逻辑测试

```typescript
describe('OrderService', () => {
  let orderService: OrderService;

  beforeEach(() => {
    orderService = new OrderService();
  });

  describe('calculateTotal', () => {
    it('should calculate total for multiple items', () => {
      // Given
      const orderItems = [
        { price: 100, quantity: 2 },
        { price: 50, quantity: 1 }
      ];

      // When
      const total = orderService.calculateTotal(orderItems);

      // Then
      expect(total).toBe(250);
    });
  });
});
```

### 2. Express控制器测试

```typescript
import { Request, Response } from 'express';
import { UserController } from '../user.controller';
import { UserService } from '../user.service';

describe('UserController', () => {
  let userController: UserController;
  let mockUserService: jest.Mocked<UserService>;

  beforeEach(() => {
    mockUserService = {
      createUser: jest.fn(),
      getUserById: jest.fn()
    } as any;

    userController = new UserController(mockUserService);
  });

  describe('createUser', () => {
    it('should create user and return 201 status', async () => {
      // Given
      const req = {
        body: { name: 'John', email: 'john@example.com' }
      } as Request;

      const res = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      } as any as Response;

      const createdUser = { id: 1, name: 'John', email: 'john@example.com' };
      mockUserService.createUser.mockResolvedValue(createdUser);

      // When
      await userController.createUser(req, res);

      // Then
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalledWith(createdUser);
    });
  });
});
```

### 3. 数据库操作测试

```typescript
import { getRepository, getConnection } from 'typeorm';
import { User } from '../entities/user.entity';
import { UserRepository } from '../repositories/user.repository';

describe('UserRepository', () => {
  beforeAll(async () => {
    // 设置测试数据库
    await createTestDatabase();
  });

  afterAll(async () => {
    // 清理测试数据库
    await dropTestDatabase();
  });

  beforeEach(async () => {
    // 清理数据
    await getConnection().getRepository(User).clear();
  });

  describe('save', () => {
    it('should save user to database', async () => {
      // Given
      const userRepository = getRepository(User);
      const user = new User('John', 'john@example.com');

      // When
      const savedUser = await userRepository.save(user);

      // Then
      expect(savedUser.id).toBeDefined();
      expect(savedUser.name).toBe('John');

      // 验证数据确实保存到了数据库
      const retrievedUser = await userRepository.findOne(savedUser.id);
      expect(retrievedUser).toBeDefined();
      expect(retrievedUser!.name).toBe('John');
    });
  });
});
```

## 测试覆盖率要求

### 代码覆盖率指标

- **行覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 85%

### 覆盖率检查

```bash
# 运行测试并生成覆盖率报告
npm test -- --coverage

# 或者
yarn test --coverage

# 生成详细覆盖率报告
npm test -- --coverage --coverageReporters=text-summary --coverageReporters=html

# 设置覆盖率阈值
npm test -- --coverage --coverageThreshold='{"global":{"branches":70,"functions":85,"lines":80,"statements":80}}'
```

### 覆盖率配置

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
    '!src/**/*.interface.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 85,
      lines: 80,
      statements: 80
    }
  },
  coverageReporters: ['text', 'lcov', 'clover']
};
```

## 快照测试

### 组件快照测试

```typescript
import { renderComponent } from './test-utils';
import { UserCard } from '../components/UserCard';

describe('UserCard', () => {
  it('should render correctly', () => {
    // Given
    const user = { name: 'John', email: 'john@example.com' };

    // When
    const { container } = renderComponent(<UserCard user={user} />);

    // Then
    expect(container).toMatchSnapshot();
  });
});
```

### API响应快照测试

```typescript
describe('UserController', () => {
  describe('GET /users', () => {
    it('should return users in correct format', async () => {
      // Given
      const mockUsers = [
        { id: 1, name: 'John', email: 'john@example.com' },
        { id: 2, name: 'Jane', email: 'jane@example.com' }
      ];
      mockUserService.getAllUsers.mockResolvedValue(mockUsers);

      // When
      const response = await request(app).get('/users');

      // Then
      expect(response.status).toBe(200);
      expect(response.body).toMatchSnapshot();
    });
  });
});
```

## 异步测试

### 测试Promises

```typescript
describe('AsyncUserService', () => {
  describe('getUserById', () => {
    it('should resolve with user when user exists', async () => {
      // Given
      const userId = 1;
      const expectedUser = { id: 1, name: 'John' };
      mockUserRepository.findById.mockResolvedValue(expectedUser);

      // When
      const user = await userService.getUserById(userId);

      // Then
      expect(user).toEqual(expectedUser);
    });

    it('should reject when user not found', async () => {
      // Given
      const userId = 999;
      mockUserRepository.findById.mockRejectedValue(new Error('User not found'));

      // When & Then
      await expect(userService.getUserById(userId)).rejects.toThrow('User not found');
    });
  });
});
```

### 测试回调函数

```typescript
describe('FileService', () => {
  describe('readFile', () => {
    it('should call callback with file content', (done) => {
      // Given
      const filename = 'test.txt';
      const expectedContent = 'Hello World';

      // When
      fileService.readFile(filename, (error, content) => {
        // Then
        expect(error).toBeNull();
        expect(content).toBe(expectedContent);
        done();
      });
    });
  });
});
```

## 最佳实践

### 1. 测试组织

```typescript
// 按功能模块组织测试
describe('UserService', () => {
  // 按方法组织测试
  describe('createUser', () => {
    // 按场景组织测试
    describe('when given valid data', () => {
      it('should create and return user', () => {
        // 测试逻辑
      });
    });

    describe('when given invalid data', () => {
      it('should throw validation error', () => {
        // 测试逻辑
      });
    });
  });
});
```

### 2. 测试隔离

```typescript
describe('UserService', () => {
  beforeEach(() => {
    // 每个测试都从干净的状态开始
    jest.clearAllMocks();
  });

  it('should not affect other tests', () => {
    // 测试不应该修改全局状态
    // 应该使用Mock来隔离外部依赖
  });
});
```

### 3. 清晰的测试意图

```typescript
// 好的命名清楚表达了测试意图
it('should return discount percentage when order total exceeds threshold', () => {
  // 测试逻辑
});

// 避免模糊的命名
it('should work', () => { // 不推荐
  // 测试逻辑
});

// 使用描述性的测试名称
it('should calculate 10% discount for orders over $100', () => {
  // 测试逻辑
});
```

### 4. 避免测试实现细节

```typescript
// 不好的做法 - 测试实现细节
it('should call userRepository.save method', () => {
  userService.createUser(userData);
  expect(mockUserRepository.save).toHaveBeenCalled(); // 过度指定（反例展示，lint:ignore）
});

// 好的做法 - 测试行为
it('should save user to repository', () => {
  const user = userService.createUser(userData);
  expect(user).toBeDefined();
  expect(user.id).toBeDefined();
  // 验证结果而不是具体的调用
});
```

## MC/DC 测试设计

### MC/DC 原则说明

MC/DC (Modified Condition/Decision Coverage) 是一种严格的测试覆盖准则，要求：
- **条件独立性**：每个条件独立影响决策结果
- **分支全覆盖**：所有分支路径都被测试
- **边界值测试**：测试输入域的边界及其附近值

### 复杂决策逻辑的 MC/DC 测试示例

```typescript
// loan.service.ts
interface User {
  id: number;
  name: string;
  creditScore: number;
  debtToIncomeRatio: number;
  employmentYears: number;
  annualIncome: number;
}

interface LoanRequest {
  id: number;
  amount: number;
}

class LoanService {
  /**
   * 贷款审批决策逻辑
   * 决策：(条件1 AND 条件2 AND 条件3) OR (条件1 AND 条件4)
   */
  approveLoan(user: User, request: LoanRequest): boolean {
    // 条件1: 信用评分 >= 650
    const goodCredit = user.creditScore >= 650;
    // 条件2: 负债率 <= 0.43
    const goodDebtRatio = user.debtToIncomeRatio <= 0.43;
    // 条件3: 就业稳定性 >= 2年
    const stableEmployment = user.employmentYears >= 2;
    // 条件4: 贷款金额合理 (<= 4倍年收入)
    const reasonableAmount = request.amount <= user.annualIncome * 4;
    
    return (goodCredit && goodDebtRatio && stableEmployment) ||
           (goodCredit && reasonableAmount);
  }
}
```

### MC/DC 测试用例设计

```typescript
// loan.service.spec.ts
describe('LoanService', () => {
  let loanService: LoanService;

  beforeEach(() => {
    loanService = new LoanService();
  });

  describe('approveLoan - MC/DC Tests', () => {
    describe('条件独立性测试', () => {
      it('should demonstrate goodCredit independence', () => {
        // 基线：goodCredit=false, 其他条件=true
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 600,  // goodCredit = false
          debtToIncomeRatio: 0.35,  // goodDebtRatio = true
          employmentYears: 5,  // stableEmployment = true
          annualIncome: 50000
        };
        const request: LoanRequest = {
          id: 1,
          amount: 150000  // 合理金额
        };

        expect(loanService.approveLoan(user, request)).toBe(false);

        // 改变条件1：goodCredit=true, 保持其他不变
        user.creditScore = 700;  // goodCredit = true
        expect(loanService.approveLoan(user, request)).toBe(true);
      });

      it('should demonstrate goodDebtRatio independence', () => {
        // 基线：goodDebtRatio=false, 其他条件=true
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 700,  // goodCredit = true
          debtToIncomeRatio: 0.50,  // goodDebtRatio = false
          employmentYears: 5,  // stableEmployment = true
          annualIncome: 50000
        };
        // 设置不合理金额，确保条件4也为false
        const request: LoanRequest = {
          id: 1,
          amount: 250000  // 不合理金额
        };

        expect(loanService.approveLoan(user, request)).toBe(false);

        // 改变条件2：goodDebtRatio=true, 保持其他不变
        user.debtToIncomeRatio = 0.35;  // goodDebtRatio = true
        expect(loanService.approveLoan(user, request)).toBe(true);
      });

      it('should demonstrate stableEmployment independence', () => {
        // 基线：stableEmployment=false, 其他条件=true
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 700,  // goodCredit = true
          debtToIncomeRatio: 0.35,  // goodDebtRatio = true
          employmentYears: 1,  // stableEmployment = false
          annualIncome: 50000
        };
        // 设置不合理金额，确保条件4也为false
        const request: LoanRequest = {
          id: 1,
          amount: 250000  // 不合理金额
        };

        expect(loanService.approveLoan(user, request)).toBe(false);

        // 改变条件3：stableEmployment=true, 保持其他不变
        user.employmentYears = 3;  // stableEmployment = true
        expect(loanService.approveLoan(user, request)).toBe(true);
      });

      it('should demonstrate reasonableAmount independence', () => {
        // 基线：reasonableAmount=false, 条件3=false（测试备选路径）
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 700,  // goodCredit = true
          debtToIncomeRatio: 0.35,  // goodDebtRatio = true
          employmentYears: 1,  // stableEmployment = false
          annualIncome: 50000
        };
        const request: LoanRequest = {
          id: 1,
          amount: 250000  // 不合理金额 (> 4倍年收入)
        };

        expect(loanService.approveLoan(user, request)).toBe(false);

        // 改变条件4：reasonableAmount=true, 保持其他不变
        request.amount = 150000;  // 合理金额
        expect(loanService.approveLoan(user, request)).toBe(true);
      });
    });

    describe('边界值测试', () => {
      test.each([
        [649, false],  // 边界值 - 1
        [650, true],   // 边界值
        [651, true],   // 边界值 + 1
      ])('creditScore %i should result in %s', (creditScore, expected) => {
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore,
          debtToIncomeRatio: 0.35,
          employmentYears: 5,
          annualIncome: 50000
        };
        const request: LoanRequest = { id: 1, amount: 150000 };

        expect(loanService.approveLoan(user, request)).toBe(expected);
      });

      test.each([
        [0.44, false],  // 边界值 + 0.01
        [0.43, true],   // 边界值
        [0.42, true],   // 边界值 - 0.01
      ])('debtToIncomeRatio %f should result in %s', (debtRatio, expected) => {
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 700,
          debtToIncomeRatio: debtRatio,
          employmentYears: 5,
          annualIncome: 50000
        };
        const request: LoanRequest = { id: 1, amount: 150000 };

        expect(loanService.approveLoan(user, request)).toBe(expected);
      });

      test.each([
        [1, false],  // 边界值 - 1
        [2, true],   // 边界值
        [3, true],   // 边界值 + 1
      ])('employmentYears %i should result in %s', (years, expected) => {
        const user: User = {
          id: 1,
          name: 'Test User',
          creditScore: 700,
          debtToIncomeRatio: 0.35,
          employmentYears: years,
          annualIncome: 50000
        };
        // 设置不合理金额，确保只测试条件3
        const request: LoanRequest = { id: 1, amount: 250000 };

        expect(loanService.approveLoan(user, request)).toBe(expected);
      });
    });
  });
});
```

### MC/DC 测试模板

```typescript
describe('conditionIndependence', () => {
  it('should demonstrate target condition independence', () => {
    // 基线：目标条件=false, 其他条件设置为使决策依赖目标条件
    const testData = createTestData({
      targetCondition: false,
      otherConditions: true
    });

    expect(service.evaluateDecision(testData)).toBe(false);

    // 改变目标条件：目标条件=true, 保持其他不变
    testData.targetCondition = true;
    expect(service.evaluateDecision(testData)).toBe(true);
  });
});
```

## 确定性隔离要点（TypeScript，对齐 SKILL.md D1–D9）

- **D5** 异步用 `await` / `expect().resolves`；需伪时钟用 `jest.useFakeTimers()` + `jest.advanceTimersByTime()`，并在 `afterEach` 还原 `jest.useRealTimers()`。
- **D2** 模块级共享状态：`jest.config` 设 `resetModules: true` 或用 `jest.isolateModules()`，避免模块级单例跨测试泄漏。
- **D8** 时区/编码显式：时间用注入的 `now`，字符串比较前 `normalize()`。

> D1/D6 由 lint 机械化（🔒 C1/C5）。

通过遵循这些规范和最佳实践，可以生成高质量、可维护的TypeScript单元测试代码。
