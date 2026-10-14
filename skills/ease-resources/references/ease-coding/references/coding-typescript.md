# TypeScript/JavaScript 编码最佳实践指南

本指南提供 TypeScript/JavaScript 项目的编码规范、设计模式和最佳实践。

## 代码风格规范

### 命名规范

```typescript
// 类名：大驼峰命名
class UserService {}
class OrderController {}

// 接口名：大驼峰命名，不加 I 前缀（推荐）
interface User {}
interface UserRepository {}

// 类型别名：大驼峰命名
type UserRole = 'admin' | 'user' | 'guest';
type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

// 函数名：小驼峰命名
function getUserById(id: number): User {}
async function createOrder(dto: CreateOrderDto): Promise<Order> {}

// 变量名：小驼峰命名
const userName = '张三';
let orderList: Order[] = [];

// 常量：全大写或小驼峰（根据项目规范）
const MAX_RETRY_COUNT = 3;
const DEFAULT_PAGE_SIZE = 20;
// 或
const maxRetryCount = 3;
const defaultPageSize = 20;

// 枚举：大驼峰命名，成员也是大驼峰或全大写
enum UserStatus {
  Active = 'active',
  Inactive = 'inactive',
  Banned = 'banned',
}

// 布尔变量：使用 is/has/can/should 前缀
const isActive = true;
const hasPermission = false;
const canEdit = true;

// 私有属性：使用 # 或 _ 前缀
class MyClass {
  #privateField = 1;
  private _anotherPrivate = 2;
}
```

### 代码格式

```typescript
// 使用 ESLint + Prettier 进行格式化
// 缩进：2 个空格
// 分号：可选（保持项目一致性）
// 引号：单引号（推荐）或双引号

// 导入顺序：Node 内置模块、第三方库、本地模块
import path from 'path';
import fs from 'fs';

import express from 'express';
import { Injectable } from '@nestjs/common';

import { UserService } from './user.service';
import { User } from '../models/user';
import { CreateUserDto } from '../dto/create-user.dto';

// 类型导入使用 type 关键字
import type { Request, Response } from 'express';
```

## 项目结构

### Node.js/NestJS 项目布局

```
project/
├── src/
│   ├── main.ts                 # 应用入口
│   ├── app.module.ts           # 根模块
│   ├── common/                 # 公共模块
│   │   ├── decorators/
│   │   ├── filters/
│   │   ├── guards/
│   │   ├── interceptors/
│   │   └── pipes/
│   ├── config/                 # 配置
│   │   └── configuration.ts
│   ├── modules/                # 业务模块
│   │   ├── user/
│   │   │   ├── user.module.ts
│   │   │   ├── user.controller.ts
│   │   │   ├── user.service.ts
│   │   │   ├── user.repository.ts
│   │   │   ├── entities/
│   │   │   │   └── user.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-user.dto.ts
│   │   │       └── update-user.dto.ts
│   │   └── order/
│   │       └── ...
│   └── shared/                 # 共享模块
│       ├── database/
│       └── logger/
├── test/                       # 测试文件
├── package.json
├── tsconfig.json
└── .eslintrc.js
```

### React 项目布局

```
project/
├── src/
│   ├── index.tsx              # 应用入口
│   ├── App.tsx
│   ├── components/            # 通用组件
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styles.ts
│   │   │   └── index.ts
│   │   └── Modal/
│   ├── features/              # 功能模块
│   │   ├── user/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   ├── slice.ts       # Redux slice
│   │   │   └── types.ts
│   │   └── order/
│   ├── hooks/                 # 通用 hooks
│   ├── services/              # API 服务
│   ├── store/                 # Redux store
│   ├── types/                 # 全局类型定义
│   └── utils/                 # 工具函数
├── package.json
└── tsconfig.json
```

## NestJS 最佳实践

### Controller 层

```typescript
import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
  HttpCode,
  HttpStatus,
  ParseIntPipe,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';

import { UserService } from './user.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { PaginationDto } from '../common/dto/pagination.dto';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard';
import { CurrentUser } from '../common/decorators/current-user.decorator';

@ApiTags('用户管理')
@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: '创建用户' })
  @ApiResponse({ status: 201, type: UserResponseDto })
  async create(@Body() createUserDto: CreateUserDto): Promise<UserResponseDto> {
    return this.userService.create(createUserDto);
  }

  @Get()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取用户列表' })
  async findAll(@Query() pagination: PaginationDto): Promise<{
    items: UserResponseDto[];
    total: number;
  }> {
    return this.userService.findAll(pagination);
  }

  @Get(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '获取用户详情' })
  async findOne(
    @Param('id', ParseIntPipe) id: number,
  ): Promise<UserResponseDto> {
    return this.userService.findOne(id);
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '更新用户' })
  async update(
    @Param('id', ParseIntPipe) id: number,
    @Body() updateUserDto: UpdateUserDto,
  ): Promise<UserResponseDto> {
    return this.userService.update(id, updateUserDto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: '删除用户' })
  async remove(@Param('id', ParseIntPipe) id: number): Promise<void> {
    return this.userService.remove(id);
  }
}
```

### DTO 定义

```typescript
import {
  IsEmail,
  IsNotEmpty,
  IsOptional,
  IsString,
  MinLength,
  MaxLength,
  Matches,
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional, PartialType } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({ description: '用户名', minLength: 2, maxLength: 50 })
  @IsNotEmpty({ message: '用户名不能为空' })
  @IsString()
  @MinLength(2, { message: '用户名至少 2 个字符' })
  @MaxLength(50, { message: '用户名最多 50 个字符' })
  name: string;

  @ApiProperty({ description: '邮箱' })
  @IsNotEmpty({ message: '邮箱不能为空' })
  @IsEmail({}, { message: '邮箱格式不正确' })
  email: string;

  @ApiProperty({ description: '密码', minLength: 8 })
  @IsNotEmpty({ message: '密码不能为空' })
  @MinLength(8, { message: '密码至少 8 个字符' })
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
    message: '密码必须包含大小写字母和数字',
  })
  password: string;
}

export class UpdateUserDto extends PartialType(CreateUserDto) {
  @ApiPropertyOptional({ description: '手机号' })
  @IsOptional()
  @Matches(/^1[3-9]\d{9}$/, { message: '手机号格式不正确' })
  phone?: string;
}

export class UserResponseDto {
  @ApiProperty()
  id: number;

  @ApiProperty()
  name: string;

  @ApiProperty()
  email: string;

  @ApiProperty()
  status: string;

  @ApiProperty()
  createdAt: Date;
}
```

### Service 层

```typescript
import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';

import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UserResponseDto } from './dto/user-response.dto';
import { PaginationDto } from '../common/dto/pagination.dto';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async create(createUserDto: CreateUserDto): Promise<UserResponseDto> {
    // 1. 业务校验
    const existingUser = await this.userRepository.findOne({
      where: { email: createUserDto.email },
    });
    if (existingUser) {
      throw new ConflictException('邮箱已被注册');
    }

    // 2. 密码加密
    const hashedPassword = await bcrypt.hash(createUserDto.password, 10);

    // 3. 创建实体
    const user = this.userRepository.create({
      ...createUserDto,
      password: hashedPassword,
      status: 'active',
    });

    // 4. 持久化
    const savedUser = await this.userRepository.save(user);

    return this.toResponseDto(savedUser);
  }

  async findAll(pagination: PaginationDto): Promise<{
    items: UserResponseDto[];
    total: number;
  }> {
    const { page = 1, size = 20 } = pagination;

    const [users, total] = await this.userRepository.findAndCount({
      skip: (page - 1) * size,
      take: size,
      order: { createdAt: 'DESC' },
    });

    return {
      items: users.map(user => this.toResponseDto(user)),
      total,
    };
  }

  async findOne(id: number): Promise<UserResponseDto> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException('用户不存在');
    }
    return this.toResponseDto(user);
  }

  async update(id: number, updateUserDto: UpdateUserDto): Promise<UserResponseDto> {
    const user = await this.userRepository.findOne({ where: { id } });
    if (!user) {
      throw new NotFoundException('用户不存在');
    }

    // 更新字段
    Object.assign(user, updateUserDto);
    const savedUser = await this.userRepository.save(user);

    return this.toResponseDto(savedUser);
  }

  async remove(id: number): Promise<void> {
    const result = await this.userRepository.delete(id);
    if (result.affected === 0) {
      throw new NotFoundException('用户不存在');
    }
  }

  private toResponseDto(user: User): UserResponseDto {
    return {
      id: user.id,
      name: user.name,
      email: user.email,
      status: user.status,
      createdAt: user.createdAt,
    };
  }
}
```

### Entity 定义（TypeORM）

```typescript
import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
  Index,
} from 'typeorm';

import { Order } from '../../order/entities/order.entity';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100 })
  name: string;

  @Index({ unique: true })
  @Column({ length: 255 })
  email: string;

  @Column({ length: 255 })
  password: string;

  @Column({ length: 20, nullable: true })
  phone: string;

  @Column({ length: 20, default: 'active' })
  status: string;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @UpdateDateColumn({ name: 'updated_at' })
  updatedAt: Date;

  @OneToMany(() => Order, order => order.user)
  orders: Order[];
}
```

## React 最佳实践

### 函数组件

```typescript
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import styled from 'styled-components';

interface UserListProps {
  initialPage?: number;
  onUserSelect?: (user: User) => void;
}

export const UserList: React.FC<UserListProps> = ({
  initialPage = 1,
  onUserSelect,
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(initialPage);
  const [error, setError] = useState<string | null>(null);

  // 获取用户列表
  const fetchUsers = useCallback(async (pageNum: number) => {
    setLoading(true);
    setError(null);
    try {
      const response = await userApi.getUsers({ page: pageNum });
      setUsers(response.data.items);
    } catch (err) {
      setError('获取用户列表失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers(page);
  }, [page, fetchUsers]);

  // 缓存计算结果
  const activeUsers = useMemo(
    () => users.filter(user => user.status === 'active'),
    [users],
  );

  const handleUserClick = useCallback(
    (user: User) => {
      onUserSelect?.(user);
    },
    [onUserSelect],
  );

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={() => fetchUsers(page)} />;
  }

  return (
    <Container>
      <UserGrid>
        {users.map(user => (
          <UserCard key={user.id} onClick={() => handleUserClick(user)}>
            <UserAvatar src={user.avatar} alt={user.name} />
            <UserName>{user.name}</UserName>
            <UserEmail>{user.email}</UserEmail>
          </UserCard>
        ))}
      </UserGrid>
      <Pagination
        current={page}
        onChange={setPage}
      />
    </Container>
  );
};

// Styled Components
const Container = styled.div`
  padding: 24px;
`;

const UserGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
`;

const UserCard = styled.div`
  padding: 16px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;
```

### Custom Hooks

```typescript
import { useState, useEffect, useCallback, useRef } from 'react';

// 通用请求 Hook
interface UseRequestOptions<T> {
  manual?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseRequestResult<T, P extends any[]> {
  data: T | undefined;
  loading: boolean;
  error: Error | null;
  run: (...args: P) => Promise<T>;
  refresh: () => Promise<T>;
}

export function useRequest<T, P extends any[] = []>(
  service: (...args: P) => Promise<T>,
  options: UseRequestOptions<T> = {},
): UseRequestResult<T, P> {
  const { manual = false, onSuccess, onError } = options;
  const [data, setData] = useState<T>();
  const [loading, setLoading] = useState(!manual);
  const [error, setError] = useState<Error | null>(null);
  const argsRef = useRef<P>();

  const run = useCallback(
    async (...args: P): Promise<T> => {
      argsRef.current = args;
      setLoading(true);
      setError(null);
      try {
        const result = await service(...args);
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        onError?.(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [service, onSuccess, onError],
  );

  const refresh = useCallback(async (): Promise<T> => {
    if (argsRef.current) {
      return run(...argsRef.current);
    }
    return run(...([] as unknown as P));
  }, [run]);

  useEffect(() => {
    if (!manual) {
      run(...([] as unknown as P));
    }
  }, [manual, run]);

  return { data, loading, error, run, refresh };
}

// 防抖 Hook
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

// 本地存储 Hook
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      setStoredValue(prev => {
        const valueToStore = value instanceof Function ? value(prev) : value;
        localStorage.setItem(key, JSON.stringify(valueToStore));
        return valueToStore;
      });
    },
    [key],
  );

  return [storedValue, setValue];
}
```

### 状态管理（Redux Toolkit）

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

import { userApi } from '../api';
import type { User, CreateUserDto, UpdateUserDto } from '../types';

interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  users: [],
  currentUser: null,
  loading: false,
  error: null,
};

// 异步 Thunk
export const fetchUsers = createAsyncThunk(
  'user/fetchUsers',
  async (params: { page: number; size: number }) => {
    const response = await userApi.getUsers(params);
    return response.data;
  },
);

export const createUser = createAsyncThunk(
  'user/createUser',
  async (dto: CreateUserDto, { rejectWithValue }) => {
    try {
      const response = await userApi.createUser(dto);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || '创建失败');
    }
  },
);

// Slice
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setCurrentUser: (state, action: PayloadAction<User | null>) => {
      state.currentUser = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchUsers
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload.items;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取用户列表失败';
      })
      // createUser
      .addCase(createUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createUser.fulfilled, (state, action) => {
        state.loading = false;
        state.users.push(action.payload);
      })
      .addCase(createUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { setCurrentUser, clearError } = userSlice.actions;
export default userSlice.reducer;
```

## 异常处理

### 自定义异常（NestJS）

```typescript
import { HttpException, HttpStatus } from '@nestjs/common';

export enum ErrorCode {
  // 通用错误 1xxx
  SYSTEM_ERROR = 1000,
  PARAM_ERROR = 1001,

  // 用户相关 2xxx
  USER_NOT_FOUND = 2001,
  EMAIL_ALREADY_EXISTS = 2002,
  PASSWORD_INCORRECT = 2003,

  // 订单相关 3xxx
  ORDER_NOT_FOUND = 3001,
  INSUFFICIENT_STOCK = 3002,
}

export class BusinessException extends HttpException {
  constructor(
    public readonly errorCode: ErrorCode,
    message: string,
    statusCode: HttpStatus = HttpStatus.BAD_REQUEST,
  ) {
    super(
      {
        code: errorCode,
        message,
      },
      statusCode,
    );
  }
}

// 使用
throw new BusinessException(ErrorCode.USER_NOT_FOUND, '用户不存在');
throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS, '邮箱已被注册');
```

### 全局异常过滤器

```typescript
import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Request, Response } from 'express';

import { BusinessException } from './business.exception';

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(GlobalExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let status: number;
    let code: number;
    let message: string;

    if (exception instanceof BusinessException) {
      status = exception.getStatus();
      code = exception.errorCode;
      message = exception.message;
      this.logger.warn(`业务异常: ${code} - ${message}`);
    } else if (exception instanceof HttpException) {
      status = exception.getStatus();
      code = status;
      const responseBody = exception.getResponse();
      message =
        typeof responseBody === 'string'
          ? responseBody
          : (responseBody as any).message || exception.message;
      this.logger.warn(`HTTP 异常: ${status} - ${message}`);
    } else {
      status = HttpStatus.INTERNAL_SERVER_ERROR;
      code = 1000;
      message = '系统繁忙，请稍后重试';
      this.logger.error('未处理异常', exception);
    }

    response.status(status).json({
      code,
      message,
      data: null,
      timestamp: new Date().toISOString(),
      path: request.url,
    });
  }
}
```

## 设计模式应用

### 策略模式

```typescript
// 策略接口
interface PaymentStrategy {
  pay(order: Order): Promise<PaymentResult>;
}

// 具体策略
class AlipayStrategy implements PaymentStrategy {
  constructor(private readonly alipayClient: AlipayClient) {}

  async pay(order: Order): Promise<PaymentResult> {
    return this.alipayClient.createPayment(order);
  }
}

class WechatPayStrategy implements PaymentStrategy {
  constructor(private readonly wechatClient: WechatClient) {}

  async pay(order: Order): Promise<PaymentResult> {
    return this.wechatClient.createPayment(order);
  }
}

// 策略上下文
class PaymentService {
  private strategies = new Map<string, PaymentStrategy>();

  registerStrategy(type: string, strategy: PaymentStrategy): void {
    this.strategies.set(type, strategy);
  }

  async pay(type: string, order: Order): Promise<PaymentResult> {
    const strategy = this.strategies.get(type);
    if (!strategy) {
      throw new Error(`不支持的支付方式: ${type}`);
    }
    return strategy.pay(order);
  }
}

// 使用
const paymentService = new PaymentService();
paymentService.registerStrategy('alipay', new AlipayStrategy(alipayClient));
paymentService.registerStrategy('wechat', new WechatPayStrategy(wechatClient));

const result = await paymentService.pay('alipay', order);
```

### 工厂模式

```typescript
// 产品接口
interface Notification {
  send(message: string, recipient: string): Promise<boolean>;
}

// 具体产品
class EmailNotification implements Notification {
  async send(message: string, recipient: string): Promise<boolean> {
    // 发送邮件
    return true;
  }
}

class SMSNotification implements Notification {
  async send(message: string, recipient: string): Promise<boolean> {
    // 发送短信
    return true;
  }
}

class PushNotification implements Notification {
  async send(message: string, recipient: string): Promise<boolean> {
    // 发送推送
    return true;
  }
}

// 工厂
class NotificationFactory {
  private static readonly notificationTypes: Record<string, new () => Notification> = {
    email: EmailNotification,
    sms: SMSNotification,
    push: PushNotification,
  };

  static create(type: string): Notification {
    const NotificationClass = this.notificationTypes[type];
    if (!NotificationClass) {
      throw new Error(`不支持的通知类型: ${type}`);
    }
    return new NotificationClass();
  }

  static register(type: string, notificationClass: new () => Notification): void {
    this.notificationTypes[type] = notificationClass;
  }
}

// 使用
const notification = NotificationFactory.create('email');
await notification.send('Hello', 'user@example.com');
```

### 装饰器模式

```typescript
// 方法装饰器：重试
function Retry(maxAttempts = 3, delay = 1000) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: Error;

      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error as Error;
          console.warn(`第 ${attempt} 次尝试失败: ${error}`);

          if (attempt < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }

      throw lastError!;
    };

    return descriptor;
  };
}

// 方法装饰器：计时
function Timer() {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const start = performance.now();
      try {
        return await originalMethod.apply(this, args);
      } finally {
        const duration = performance.now() - start;
        console.log(`${propertyKey} 执行耗时: ${duration.toFixed(2)}ms`);
      }
    };

    return descriptor;
  };
}

// 使用
class UserService {
  @Retry(3, 500)
  @Timer()
  async fetchUserFromRemote(id: number): Promise<User> {
    // 远程调用
  }
}
```

## 异步处理

### Promise 和 async/await

```typescript
// 并发请求
async function fetchUserData(userId: number): Promise<UserFullData> {
  const [user, orders, profile] = await Promise.all([
    userApi.getUser(userId),
    orderApi.getUserOrders(userId),
    profileApi.getUserProfile(userId),
  ]);

  return { user, orders, profile };
}

// 错误处理
async function safeApiCall<T>(
  promise: Promise<T>,
  defaultValue: T,
): Promise<T> {
  try {
    return await promise;
  } catch (error) {
    console.error('API 调用失败:', error);
    return defaultValue;
  }
}

// 并发控制
async function batchProcess<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  concurrency = 5,
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }

  return results;
}
```

### 队列处理

```typescript
import Bull from 'bull';

// 创建队列
const emailQueue = new Bull<{ to: string; subject: string; body: string }>(
  'email',
  {
    redis: {
      host: 'localhost',
      port: 6379,
    },
  },
);

// 添加任务
async function sendEmail(to: string, subject: string, body: string) {
  await emailQueue.add(
    { to, subject, body },
    {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 1000,
      },
    },
  );
}

// 处理任务
emailQueue.process(async (job) => {
  const { to, subject, body } = job.data;
  await emailService.send(to, subject, body);
  console.log(`邮件发送成功: ${to}`);
});

// 监听事件
emailQueue.on('completed', (job) => {
  console.log(`任务完成: ${job.id}`);
});

emailQueue.on('failed', (job, err) => {
  console.error(`任务失败: ${job.id}`, err);
});
```

## 测试实践

### 单元测试（Jest）

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ConflictException, NotFoundException } from '@nestjs/common';

import { UserService } from './user.service';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';

describe('UserService', () => {
  let service: UserService;
  let repository: jest.Mocked<Repository<User>>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UserService,
        {
          provide: getRepositoryToken(User),
          useValue: {
            findOne: jest.fn(),
            findAndCount: jest.fn(),
            create: jest.fn(),
            save: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<UserService>(UserService);
    repository = module.get(getRepositoryToken(User));
  });

  describe('create', () => {
    const createUserDto: CreateUserDto = {
      name: 'test',
      email: 'test@example.com',
      password: 'Password123',
    };

    it('应该成功创建用户', async () => {
      repository.findOne.mockResolvedValue(null);
      repository.create.mockReturnValue({ id: 1, ...createUserDto } as User);
      repository.save.mockResolvedValue({ id: 1, ...createUserDto } as User);

      const result = await service.create(createUserDto);

      expect(result).toBeDefined();
      expect(result.id).toBe(1);
      expect(result.name).toBe('test');
      expect(repository.save).toHaveBeenCalled();
    });

    it('邮箱已存在时应该抛出 ConflictException', async () => {
      repository.findOne.mockResolvedValue({ id: 1 } as User);

      await expect(service.create(createUserDto)).rejects.toThrow(
        ConflictException,
      );
    });
  });

  describe('findOne', () => {
    it('用户存在时应该返回用户', async () => {
      const user = { id: 1, name: 'test', email: 'test@example.com' } as User;
      repository.findOne.mockResolvedValue(user);

      const result = await service.findOne(1);

      expect(result.id).toBe(1);
      expect(result.name).toBe('test');
    });

    it('用户不存在时应该抛出 NotFoundException', async () => {
      repository.findOne.mockResolvedValue(null);

      await expect(service.findOne(999)).rejects.toThrow(NotFoundException);
    });
  });
});
```

### E2E 测试

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';

import { AppModule } from '../src/app.module';

describe('UserController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe());
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /users', () => {
    it('应该成功创建用户', () => {
      return request(app.getHttpServer())
        .post('/users')
        .send({
          name: 'test',
          email: 'test@example.com',
          password: 'Password123',
        })
        .expect(201)
        .expect((res) => {
          expect(res.body.name).toBe('test');
          expect(res.body.email).toBe('test@example.com');
        });
    });

    it('参数校验失败应该返回 400', () => {
      return request(app.getHttpServer())
        .post('/users')
        .send({
          name: 't', // 太短
          email: 'invalid-email',
          password: '123', // 太短
        })
        .expect(400);
    });
  });

  describe('GET /users/:id', () => {
    it('用户不存在应该返回 404', () => {
      return request(app.getHttpServer())
        .get('/users/999999')
        .expect(404);
    });
  });
});
```

### React 组件测试

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import { UserList } from './UserList';
import userReducer from '../slice';
import * as userApi from '../api';

jest.mock('../api');

describe('UserList', () => {
  const mockUsers = [
    { id: 1, name: '用户1', email: 'user1@example.com', status: 'active' },
    { id: 2, name: '用户2', email: 'user2@example.com', status: 'active' },
  ];

  let store: ReturnType<typeof configureStore>;

  beforeEach(() => {
    store = configureStore({
      reducer: { user: userReducer },
    });

    (userApi.getUsers as jest.Mock).mockResolvedValue({
      data: { items: mockUsers, total: 2 },
    });
  });

  it('应该渲染用户列表', async () => {
    render(
      <Provider store={store}>
        <UserList />
      </Provider>,
    );

    await waitFor(() => {
      expect(screen.getByText('用户1')).toBeInTheDocument();
      expect(screen.getByText('用户2')).toBeInTheDocument();
    });
  });

  it('点击用户应该触发 onUserSelect', async () => {
    const handleSelect = jest.fn();

    render(
      <Provider store={store}>
        <UserList onUserSelect={handleSelect} />
      </Provider>,
    );

    await waitFor(() => {
      expect(screen.getByText('用户1')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('用户1'));

    expect(handleSelect).toHaveBeenCalledWith(mockUsers[0]);
  });

  it('加载中应该显示 Loading', () => {
    (userApi.getUsers as jest.Mock).mockImplementation(
      () => new Promise(() => {}),
    );

    render(
      <Provider store={store}>
        <UserList />
      </Provider>,
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});
```

## 注意事项

1. **类型安全**：充分利用 TypeScript 类型系统，避免使用 `any`
2. **代码风格**：使用 ESLint + Prettier 保持代码风格一致
3. **模块化**：按功能模块组织代码，保持单一职责
4. **异常处理**：使用自定义异常类，统一异常处理
5. **测试覆盖**：核心业务逻辑必须有单元测试
6. **性能优化**：注意 React 组件重渲染，使用 useMemo/useCallback

