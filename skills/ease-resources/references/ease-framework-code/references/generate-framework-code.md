# 通用框架代码生成指南

本文档描述如何在设计阶段生成通用框架代码骨架，支持多种编程语言（Java、Python、Go等）。框架代码仅包含结构骨架和实现步骤注释，不实现具体业务逻辑。

## 执行条件

- **输入**：
  - `plan.md`（技术计划，含技术栈/语言信息）
  - `detail-design.md`（详细设计）
  - `/docs/system/`（系统知识）
  - **用例文档**：`docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md`（提取用例流程和规则引用）
  - **规则文档**：`docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md`（提取业务规则详情）

- **项目类型处理**：
  - 若 `PROJECT_TYPE=mumble-sdk`：**优先调用** `mumblesdk` skill，遵循 MumbleSDK 框架规范
  - 若 `PROJECT_TYPE=java`：使用通用 Java 框架代码生成规范
  - 其他语言：按对应语言的框架代码生成指南

## 语言检测

从以下来源识别项目语言：
1. `plan.md` 中的技术栈信息
2. `/docs/system/01_SYSTEM_OVERVIEW.md` 中的技术栈描述
3. 项目根目录的特征文件：
   - Java: `pom.xml` 或 `build.gradle`
   - Python: `requirements.txt` 或 `pyproject.toml`
   - Go: `go.mod`
   - TypeScript: `package.json` + `tsconfig.json`

## 生成原则

1. **仅生成骨架**：类/接口/函数签名，不实现具体业务逻辑
2. **详细注释**：在函数体内使用注释说明实现步骤
3. **规则映射**：**必须**从用例文档（`usecase.md`）和规则文档（`rules.md`）中提取业务规则，并在代码注释中明确标注规则 ID（BR-XXX）
4. **规则判断**：在实现步骤中明确标注需要应用的业务规则判断点
5. **符合规范**：遵循 `/docs/system/` 中的代码规范
6. **可编译/运行**：生成的代码必须语法正确

## 按语言生成框架代码内容

| 层级      | Java                   | Python                   | Go            |
| --------- | ---------------------- | ------------------------ | ------------- |
| 实体/模型 | Entity/DTO/VO 类       | dataclass/Pydantic Model | struct 定义   |
| 数据访问  | DAO 接口 + MyBatis XML | Repository 类            | repository 包 |
| 业务逻辑  | Service 接口与实现     | Service 类               | service 包    |
| 接口层    | Controller 类          | FastAPI/Flask Router     | handler 包    |
| 配置      | @Configuration 类      | config.py / settings.py  | config 包     |
| 入口      | Application 类         | main.py / app.py         | main.go       |

## 注释格式规范

### Java 注释格式

```java
/**
 * TODO: [功能描述]
 *
 * 用例引用：UC-XXX（用例名称）
 * 用例文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
 * 规则文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md
 *
 * 实现步骤：
 * 1. [步骤1描述]
 *    - 应用规则：BR-XXX（规则名称）
 * 2. [步骤2描述]
 *    - 应用规则：BR-XXX（规则名称）
 *
 * 业务规则映射：
 * - BR-XXX: [规则描述]
 * - BR-XXX: [规则描述]
 *
 * @see 相关类#相关方法
 * @see docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
 * @see docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md
 */
public ReturnType methodName(ParamType param) {
    // TODO: 步骤1 - [步骤描述]（应用 BR-XXX）
    // BR-XXX: [规则具体说明]

    // TODO: 步骤2 - [步骤描述]（应用 BR-XXX）
    // BR-XXX: [规则具体说明]

    throw new UnsupportedOperationException("待实现");
}
```

### Python 注释格式

```python
def method_name(self, param: ParamType) -> ReturnType:
    """
    TODO: [功能描述]

    用例引用：UC-XXX（用例名称）
    用例文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
    规则文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md

    实现步骤：
    1. [步骤1描述]
       - 应用规则：BR-XXX（规则名称）
    2. [步骤2描述]
       - 应用规则：BR-XXX（规则名称）

    业务规则映射：
    - BR-XXX: [规则描述]
    - BR-XXX: [规则描述]

    See Also:
        相关类.相关方法
        docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
        docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md
    """
    # TODO: 步骤1 - [步骤描述]（应用 BR-XXX）
    # BR-XXX: [规则具体说明]

    # TODO: 步骤2 - [步骤描述]（应用 BR-XXX）
    # BR-XXX: [规则具体说明]

    raise NotImplementedError("待实现")
```

### Go 注释格式

```go
// MethodName TODO: [功能描述]
//
// 用例引用：UC-XXX（用例名称）
// 用例文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
// 规则文档：docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md
//
// 实现步骤：
// 1. [步骤1描述]
//    - 应用规则：BR-XXX（规则名称）
// 2. [步骤2描述]
//    - 应用规则：BR-XXX（规则名称）
//
// 业务规则映射：
// - BR-XXX: [规则描述]
// - BR-XXX: [规则描述]
//
// See Also:
//     相关包.相关函数
//     docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
//     docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md
func MethodName(param ParamType) (ReturnType, error) {
    // TODO: 步骤1 - [步骤描述]（应用 BR-XXX）
    // BR-XXX: [规则具体说明]

    // TODO: 步骤2 - [步骤描述]（应用 BR-XXX）
    // BR-XXX: [规则具体说明]

    return nil, errors.New("待实现")
}
```

## 空实现策略

| 返回类型 | Java                        | Python                        | Go                                   |
| -------- | --------------------------- | ----------------------------- | ------------------------------------ |
| 无返回   | 空方法体                    | `pass`                      | 空函数体                             |
| 对象     | `return null` 或抛异常    | `raise NotImplementedError` | `return nil, errors.New("待实现")` |
| 基本类型 | 返回默认值                  | 返回默认值                    | 返回零值                             |
| 集合     | `Collections.emptyList()` | `return []`                 | `return nil, nil`                  |

## 输出目录结构

生成的框架代码应放置在以下目录：

```
.eases/[编号]-[功能名]/flow-2-design/framework-code/
├── framework-code-manifest.md           # 框架代码清单
├── src/main/java/...                    # Java 源码骨架
├── src/main/resources/...               # 配置文件骨架
├── app/...                              # Python/Go 等源码骨架
└── ...
```

## 框架代码清单 (framework-code-manifest.md)

框架代码清单应包含以下信息：

```markdown
# 框架代码清单

## 生成信息
- 生成时间: [时间]
- 项目语言: [语言]
- 用例来源: docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/usecase.md
- 规则来源: docs/domains/[编号]-[module_name]/usecases/[编号]-[subdomain]/rules.md

## 生成文件列表

| 文件路径 | 文件类型 | 说明 | 关联用例 |
|----------|----------|------|----------|
| [路径] | [类型] | [说明] | UC-XXX |

## 业务规则映射

| 规则ID | 规则描述 | 映射文件 | 映射位置 |
|--------|----------|----------|----------|
| BR-XXX | [描述] | [文件] | [位置] |

## 待实现方法统计

- 总方法数: [数量]
- 已添加TODO注释的方法数: [数量]
- 需要实现的业务规则数: [数量]
```

## 质量检查清单

生成框架代码后，应检查以下事项：

- [ ] 所有文件语法正确，可编译/运行
- [ ] 每个方法都有详细的TODO注释
- [ ] 所有业务规则（BR-XXX）都在注释中明确标注
- [ ] 代码结构符合项目规范
- [ ] 导入/依赖关系正确
- [ ] 空实现策略符合语言规范

## 与增量开发的区别

| 方面 | 全新开发（框架代码） | 增量开发（代码注释） |
|------|---------------------|---------------------|
| 目标 | 生成全新的代码骨架 | 在现有代码中添加TODO注释 |
| 输出 | 新文件 | 修改现有文件 |
| 位置 | `.eases/[编号]-[功能名]/flow-2-design/framework-code/` | 实际项目代码目录 |
| 清单 | `framework-code-manifest.md` | `code-annotation-manifest.md` |
| 后续 | 按框架代码实现TODO | 按代码注释实现TODO |
