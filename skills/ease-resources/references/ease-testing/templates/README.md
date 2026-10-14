# 测试模板使用说明

本目录包含各种编程语言的服务类测试模板，用于生成标准化的单元测试代码。

## 模板概览

| 模板文件 | 语言 | 测试框架 | 用途 |
|----------|------|----------|------|
| `java-service-test.template` | Java | JUnit 5 + Mockito | Service 层测试 |
| `go-service-test.template` | Go | testing + testify | 结构体方法测试 |
| `python-service-test.template` | Python | pytest + mock | 服务类测试 |
| `typescript-service-test.template` | TypeScript | Jest | 服务类测试 |

## 模板语法

所有模板使用 **Mustache** 语法：

| 语法 | 说明 | 示例 |
|------|------|------|
| `{{variable}}` | 变量替换 | `{{class_name}}` → `UserService` |
| `{{#section}}...{{/section}}` | 条件/循环块 | 遍历依赖列表 |
| `{{^section}}...{{/section}}` | 反向条件块 | 非 void 方法时显示返回值 |
| `{{{raw}}}` | 不转义的原始输出 | 代码块内容 |
| `{{#last}}...{{/last}}` | 最后一项标记 | 控制逗号分隔 |

## 变量定义

### 通用变量

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `class_name` | string | 被测类名 | `UserService` |
| `instance_name` | string | 实例变量名 | `userService` |
| `package_name` | string | 包名/模块名 | `com.example.service` |
| `file_path` | string | 源文件路径 | `user/user.service` |

### 依赖相关变量

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `dependencies` | array | 依赖列表 | - |
| `dependencies.type` | string | 依赖类型 | `UserRepository` |
| `dependencies.name` | string | 依赖名称 | `userRepository` |
| `dependencies.last` | boolean | 是否最后一项 | 控制逗号 |
| `has_mock_dependencies` | boolean | 是否有需要 Mock 的依赖 | - |

### 方法相关变量

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `methods` | array | 方法列表 | - |
| `method_name` | string | 方法名 | `createUser` |
| `scenario` | string | 测试场景（驼峰） | `ValidData` |
| `scenario_description` | string | 场景描述 | `create user with valid data` |
| `expected_result` | string | 期望结果（驼峰） | `ReturnsUser` |
| `is_void` | boolean | 是否 void 方法 | - |
| `is_async` | boolean | 是否异步方法 | - |
| `return_type` | string | 返回类型 | `User` |

### 参数相关变量

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `params` | array | 参数列表 | - |
| `param_name` | string | 参数名 | `userDto` |
| `param_type` | string | 参数类型 | `UserDto` |
| `param_value` | string | 参数值 | `new UserDto(...)` |

### 测试代码块变量

| 变量名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `setup` | string | Given 阶段代码 | Mock 设置代码 |
| `assertions` | array | 断言语句列表 | - |
| `assertion` | string | 单个断言语句 | `assertThat(result.getName()).isEqualTo("John")` |
| `verifications` | array | 验证语句列表 | - |
| `verification` | string | 单个验证语句 | `verify(repo).save(argThat(u -> u.getName().equals("John")))` |

## 使用示例

### 输入数据结构

```json
{
  "package_name": "com.example.service",
  "class_name": "UserService",
  "instance_name": "userService",
  "dependencies": [
    { "type": "UserRepository", "name": "userRepository", "last": false },
    { "type": "EmailService", "name": "emailService", "last": true }
  ],
  "methods": [
    {
      "method_name": "createUser",
      "scenario": "ValidData",
      "expected_result": "ReturnsUser",
      "is_void": false,
      "return_type": "User",
      "params": [
        { "param_name": "userDto", "param_type": "UserDto", "last": true }
      ],
      "setup": "UserDto userDto = new UserDto(\"John\", \"john@example.com\");\nwhen(userRepository.save(any())).thenReturn(new User(1L, \"John\"));",
      "assertions": [
        { "assertion": "assertThat(result.getId()).isEqualTo(1L);" },
        { "assertion": "assertThat(result.getName()).isEqualTo(\"John\");" }
      ],
      "verifications": [
        { "verification": "verify(userRepository).save(argThat(u -> u.getName().equals(\"John\") && u.getEmail().equals(\"john@example.com\")));" }
      ]
    }
  ]
}
```

### 生成的 Java 测试代码

```java
package com.example.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    private UserService userService;

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @BeforeEach
    void setUp() {
        userService = new UserService(userRepository, emailService);
    }

    @Test
    void createUser_ValidData_ReturnsUser() {
        // Given
        UserDto userDto = new UserDto("John", "john@example.com");
        when(userRepository.save(any())).thenReturn(new User(1L, "John"));

        // When
        User result = userService.createUser(userDto);

        // Then
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("John");

        verify(userRepository).save(argThat(u -> u.getName().equals("John") && u.getEmail().equals("john@example.com")));
    }
}
```

## 各语言模板特点

### Java 模板
- 使用 `@ExtendWith(MockitoExtension.class)` 自动初始化 Mock
- 支持 `@Mock` 注解声明依赖
- 使用 AssertJ 流式断言

### Go 模板
- 支持表驱动测试 (`table_driven_tests`)
- 自动生成 Mock 结构体定义
- 使用 testify/assert 断言

### Python 模板
- 使用 `setup_method` 初始化
- 支持 `@pytest.mark.parametrize` 参数化测试
- 支持异步测试 (`is_async`)

### TypeScript 模板
- 使用 `beforeEach`/`afterEach` 管理生命周期
- 支持 `jest.Mocked<T>` 类型安全 Mock
- 支持 `test.each` 参数化测试

## 最佳实践

1. **保持模板简洁**: 只包含必要的结构框架
2. **遵循语言规范**: 使用各语言的惯用测试模式
3. **易于扩展**: 预留扩展点（如参数化测试、异常测试）
4. **保持一致性**: 所有模板遵循相同的 AAA 模式

## 模板维护指南

更新模板时：
1. 确保修改符合对应语言的测试最佳实践
2. 更新本 README 中的变量说明
3. 验证示例代码可正确生成
4. 同步更新 `references/testing-*.md` 中的相关示例