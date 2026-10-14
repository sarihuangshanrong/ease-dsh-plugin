# Ease Framework Code

## Overview

从用例/规则/设计文档生成"可编译骨架 + TODO 步骤 + 规则映射"，不写业务逻辑。支持通用多语言框架代码生成（Java/Go/Python/TypeScript）。

## Role Contract

- **主角色 — 框架代码工程师（Framework Code Engineer）**：把已经批准的用例、规则和技术设计机械化落成可编译骨架；结构决策仍由 `ease-architecture` 负责。
- **允许**：创建类、接口、签名、依赖注入声明、占位实现、TODO 与 UC/BR 映射，并验证骨架可编译。
- **禁止**：新增或猜测架构决策、事务边界、错误策略、数据一致性方案和业务规则；不得用 TODO 掩盖会改变结构的设计缺口。
- **输入门禁**：若缺失的信息会影响组件边界、接口契约、事务、错误模型或依赖方向，必须停止生成并移交 `ease-architecture`；设计补齐后才能继续。
- **实现边界**：不得写业务逻辑；详细实现移交 `ease-coding`，测试代码移交 `ease-testing`。

## When to Use

**Use this skill when:**

- 有 design/usecase/rules 文档，需要生成框架代码骨架（不包含业务逻辑）
- 需要输出可编译的代码结构，附带详细实现步骤 TODO 注释
- 需要将业务规则（BR-XXX）映射到代码注释中

**Do NOT use when:**

- 主要目标是直接交付可运行业务逻辑 → 使用 `ease-coding` / `ease-testing`
- 项目是 MumbleSDK 企业框架 → **必须优先调用 `mumblesdk` skill**（本 skill 作为通用规范参考）
- 主要目标是架构设计 → 使用 `ease-architecture`

## Quick Reference

| 你正在做什么 | 输入 | 输出 | 关键规则 |
|---|---|---|---|
| 生成通用框架代码骨架 | plan.md + detail-design.md + usecases/rules | 可编译的代码骨架 + TODO 注释 | 禁止业务逻辑、必须引用用例/规则 |
| MumbleSDK 框架代码生成 | 设计文档 + MumbleSDK 规范 | 严格符合企业规范的骨架 | **必须调用 `mumblesdk` skill** |
| 验证框架代码质量 | 生成的代码 | 验证结果 + 清单 | 使用 checklists/framework_verification_checklist.md |

## Core Rules (Non-negotiables)

1. **禁止业务逻辑**：只生成类/接口/函数签名，方法体只留 TODO 注释
2. **规则映射必须**：每个 TODO 必须引用对应的用例文档（UC-XXX）和规则文档（BR-XXX）
3. **输出可编译**：生成的代码必须语法正确，可被 IDE/编译器使用
4. **提供 manifest**：生成 `framework-code-manifest.md` 清单文件
5. **MumbleSDK 项目优先级**：检测到 MumbleSDK 时，必须先调用 `mumblesdk` skill

## 项目类型检测（必须首先执行）

### 2.1 语言识别（Glob 优先）

| 语言 | 特征文件（Glob） | 处理方式 |
|---|---|---|
| Java (MumbleSDK) | `pom.xml` 或 `build.gradle` + 含 `mumble-sdk` 依赖 | **必须调用 `mumblesdk` skill** |
| Java (通用) | `pom.xml` 或 `build.gradle` | 使用通用 Java 骨架规范 |
| Go | `go.mod` | 使用 Go 骨架规范 |
| Python | `requirements.txt` 或 `pyproject.toml` | 使用 Python 骨架规范 |
| TypeScript | `package.json` + `tsconfig.json` | 使用 TypeScript 骨架规范 |

### 2.2 MumbleSDK 检测规则

满足以下任一条件即为 MumbleSDK 项目：
- `pom.xml`/`build.gradle` 中包含 `mumble-sdk` 依赖
- 源码中检测到 `MumbleAbstractBaseController`、`AbstractSimpleDAO`、`@MumbleMessageService` 等特征

**MumbleSDK 项目必须调用 `mumblesdk` skill**，本 skill 的通用规范仅作为参考。

## Language Guidance

### 通用骨架生成（非 MumbleSDK）

详见：`references/generate-framework-code.md`

- **Java**: Entity/DTO/Service/Controller 类 + MyBatis 映射
- **Python**: dataclass/Pydantic Model + Service + FastAPI Router
- **Go**: struct + repository + service + handler
- **TypeScript**: Interface + Service + Router

### MumbleSDK 企业框架

详见：`references/mumblesdk/`（目录结构、包规范、配置格式、质量门槛等）

## 占位策略（统一原则）

1. **优先保证可编译**：否则骨架无法被 IDE/CI 使用
2. **占位必须显式"未实现"**：避免产生"看似可用"的默认值导致误用
3. **禁止业务逻辑/条件分支**：除非是为了让代码可编译的最小结构

| 返回类型 | Java | Python | Go |
|---|---|---|---|
| 无返回 | 空方法体 | `pass` | 空函数体 |
| 对象 | `throw new UnsupportedOperationException("待实现")` | `raise NotImplementedError("待实现")` | `return nil, errors.New("待实现")` |
| 基本类型 | 返回默认值（0/false/null） | 返回默认值 | 返回零值 |
| 集合 | `Collections.emptyList()` | `return []` | `return nil, nil` |

## 输出与验证

### 输出目录

```
.eases/[编号]-[功能名]/flow-2-design/framework-code/
├── framework-code-manifest.md           # 框架代码清单
├── src/main/java/...                    # Java 源码骨架
├── app/...                              # Python/Go 源码骨架
└── ...
```

### framework-code-manifest.md 格式

```markdown
# 框架代码清单

## 生成信息
- 生成时间: [时间]
- 项目语言: [语言]
- 用例来源: docs/domains/.../usecase.md
- 规则来源: docs/domains/.../rules.md

## 生成文件列表

| 文件路径 | 文件类型 | 说明 | 关联用例 |
|----------|----------|------|----------|
| [路径] | [类型] | [说明] | UC-XXX |

## 业务规则映射

| 规则ID | 规则描述 | 映射文件 | 映射位置 |
|--------|----------|----------|----------|
| BR-XXX | [描述] | [文件] | [位置] |
```

### 质量验证

详见：`checklists/framework_verification_checklist.md`

生成后逐项核验：
- [ ] 所有文件语法正确，可编译/运行
- [ ] 每个方法都有详细的 TODO 注释
- [ ] 所有业务规则（BR-XXX）都在注释中明确标注
- [ ] 空实现策略符合语言规范

## Common Mistakes

| 错误 | 症状 | 修复 |
|---|---|---|
| 在骨架代码中写业务逻辑 | 违背"骨架"目标，后续难以区分已实现/未实现 | 方法体只留 TODO 注释，禁止实际逻辑 |
| 方法体留空但返回值处理不当 | 编译失败 | 使用标准占位异常/默认值 |
| TODO 不引用用例/规则文档 | 实现时找不到依据 | 必须标注 `UC-XXX` 和 `BR-XXX` 及文档路径 |
| MumbleSDK 项目未调用 mumblesdk | 生成不符合企业规范的代码 | 检测到 MumbleSDK 特征，强制先调用对应 skill |
| 占位异常使用非标准类（如 `NotImplementedException` in Java） | 复制粘贴后无法编译 | 使用 JDK 标准异常 `UnsupportedOperationException` |

## See Also

- **通用框架代码生成详情**：`references/generate-framework-code.md`
- **框架代码验证清单**：`checklists/framework_verification_checklist.md`
- **MumbleSDK 企业框架规范**：`references/mumblesdk/SKILL.md`
- **架构设计规范（与 ease-architecture 边界）**：`../ease-architecture/SKILL.md`
