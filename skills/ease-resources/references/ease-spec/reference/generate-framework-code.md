---
description: 基于设计文档生成框架代码骨架，仅包含类/接口/函数签名和实现步骤注释，不实现具体业务逻辑。支持 Java、Python、Go 三种语言。
handoffs: 
  - label: 生成任务列表
    agent: ease.tasks
    prompt: 基于框架代码生成任务列表
scripts:
   sh: scripts/bash/check-prerequisites.sh --json
   ps: scripts/powershell/check-prerequisites.ps1 -Json
skills: ease-spec
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前（如不为空），你必须考虑用户输入。

## 大纲

目标：基于详细设计文档生成可编译/运行的框架代码骨架，代码仅包含结构定义和实现步骤注释，供开发人员后续填充具体逻辑。

支持语言：**Java**、**Python**、**Go**

注意：此流程是 `/ease.design` 命令的必需阶段，在技术计划阶段之后、任务分解阶段之前执行。

## 执行步骤

### 1. 加载设计文档与识别语言

必需加载：
- `detail-design.md`：模块设计、数据结构、接口定义
- `arch-design.md`：架构约束、技术栈、模块边界
- `plan.md`：技术计划（含语言/框架信息）
- `/docs/system/01_SYSTEM_OVERVIEW.md`：系统技术栈
- `/memory/constitution.md`：项目宪章

**语言识别**：从 `plan.md` 或系统概览中提取项目主语言（Java/Python/Go）

### 2. 识别需生成的代码文件（按语言）

| 层级 | Java | Python | Go |
|------|------|--------|-----|
| 实体/模型 | Entity/DTO/VO 类 | dataclass/Pydantic Model | struct 定义 |
| 数据访问 | DAO 接口 + Impl + MyBatis XML | Repository 类 | repository 包 |
| 业务逻辑 | Service 接口 + Impl | Service 类 | service 包 |
| 接口层 | Controller 类 | FastAPI Router / Flask Blueprint | handler 包 |
| 配置 | @Configuration 类 | config.py / settings.py | config 包 |
| 入口 | Application 类 | main.py / app.py | main.go |

### 3. 生成框架代码

#### 3.1 生成原则

1. **仅生成骨架**：类/接口/函数签名完整，函数体为空或抛出 TODO 异常
2. **详细注释**：每个函数使用语言对应的文档注释说明实现步骤
3. **可编译/运行**：生成的代码必须语法正确
4. **符合规范**：遵循项目的代码规范和目录结构

#### 3.2 注释格式（按语言）

**Java：**
```java
/**
 * [方法功能简述]
 * 
 * 实现步骤：
 * 1. [步骤1描述]
 * 2. [步骤2描述]
 * 3. [步骤3描述]
 * 
 * 注意事项：
 * - [注意点1]
 * - [注意点2]
 * 
 * @param paramName [参数说明]
 * @return [返回值说明]
 * @throws ExceptionType [异常说明]
 * @see RelatedClass#relatedMethod
 */
public ReturnType methodName(ParamType param) {
    // TODO: 按上述步骤实现
    throw new UnsupportedOperationException("待实现");
}
```

**Python：**
```python
def method_name(self, param: ParamType) -> ReturnType:
    """
    [方法功能简述]
    
    实现步骤：
    1. [步骤1描述]
    2. [步骤2描述]
    3. [步骤3描述]
    
    注意事项：
    - [注意点1]
    - [注意点2]
    
    Args:
        param: [参数说明]
    
    Returns:
        [返回值说明]
    
    Raises:
        ExceptionType: [异常说明]
    
    See Also:
        RelatedClass.related_method
    """
    # TODO: 按上述步骤实现
    raise NotImplementedError("待实现")
```

**Go：**
```go
// MethodName [方法功能简述]
//
// 实现步骤：
// 1. [步骤1描述]
// 2. [步骤2描述]
// 3. [步骤3描述]
//
// 注意事项：
// - [注意点1]
// - [注意点2]
//
// Parameters:
//   - param: [参数说明]
//
// Returns:
//   - ReturnType: [返回值说明]
//   - error: [错误说明]
//
// See: RelatedStruct.RelatedMethod
func (s *ServiceStruct) MethodName(ctx context.Context, param ParamType) (ReturnType, error) {
    // TODO: 按上述步骤实现
    return nil, errors.New("待实现")
}
```

#### 3.3 空实现策略（按语言）

| 返回类型 | Java | Python | Go |
|----------|------|--------|-----|
| 无返回 | 空方法体或 TODO 注释 | `pass` 或 TODO 注释 | 空函数体 |
| 对象 | `return null;` 或抛异常 | `raise NotImplementedError` | `return nil, errors.New("待实现")` |
| 基本类型 | 返回默认值（0, false） | 返回默认值（0, False） | 返回零值 |
| 集合 | `Collections.emptyList()` | `return []` | `return nil, nil` |
| 强制实现 | `throw new UnsupportedOperationException` | `raise NotImplementedError` | `return nil, errors.New("待实现")` |

### 4. 生成清单文件

创建 `framework-code-manifest.md`：

```markdown
# 框架代码清单

**生成时间**：[DATE]
**项目语言**：[Java/Python/Go]
**来源设计**：detail-design.md

## 文件列表

| 序号 | 文件路径 | 类型 | 说明 | 待实现函数数 |
|------|----------|------|------|--------------|
| 1    | [路径] | 实体类 | [说明] | 0 |
| 2    | [路径] | Repository | [说明] | 5 |
| 3    | [路径] | Service | [说明] | 8 |

## 待实现函数汇总

### [文件名]
- [ ] `functionName(params)` - [功能描述]
- [ ] `anotherFunction(params)` - [功能描述]
...
```

### 5. 输出目录结构（按语言）

**Java：**
```
.eases/[编号]-[功能名]/flow-2-design/framework-code/
├── framework-code-manifest.md
├── src/main/java/[package]/
│   ├── entity/
│   ├── dao/
│   ├── service/
│   ├── controller/
│   └── config/
├── src/main/resources/
│   ├── mapper/
│   └── application.properties
└── sql/
    └── init.sql
```

**Python：**
```
.eases/[编号]-[功能名]/flow-2-design/framework-code/
├── framework-code-manifest.md
├── [project_name]/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── [entity].py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── [repo].py
│   ├── services/
│   │   ├── __init__.py
│   │   └── [service].py
│   ├── api/
│   │   ├── __init__.py
│   │   └── [router].py
│   ├── config.py
│   └── main.py
├── requirements.txt
└── sql/
    └── init.sql
```

**Go：**
```
.eases/[编号]-[功能名]/flow-2-design/framework-code/
├── framework-code-manifest.md
├── cmd/
│   └── main.go
├── internal/
│   ├── model/
│   │   └── [entity].go
│   ├── repository/
│   │   └── [repo].go
│   ├── service/
│   │   └── [service].go
│   ├── handler/
│   │   └── [handler].go
│   └── config/
│       └── config.go
├── go.mod
├── go.sum
└── sql/
    └── init.sql
```

### 6. 校验

- 所有代码文件语法正确（可编译/运行）
- 每个待实现函数都有实现步骤注释
- 清单文件完整列出所有待实现函数
- 文件路径与设计文档中的模块划分一致
- 遵循语言对应的命名规范（Java驼峰、Python下划线、Go驼峰）

## 行为规则

- 不实现任何业务逻辑，仅生成骨架
- 注释要具体到可指导实现，不能太笼统
- 遵循项目现有的代码风格和命名规范
- 若设计文档信息不足，在注释中标注 `[设计待补充]`
- 根据识别的语言选择对应的目录结构和代码风格

## 上下文

{ARGS}
