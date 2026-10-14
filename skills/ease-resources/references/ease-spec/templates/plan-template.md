# 实施计划： [FEATURE]

**分支**：`[###-feature-name]` | **日期**： [DATE] | **规范**： [link]
**输入**：来自 `.eases/[###-feature-name]/[command]/spec.md` 的功能规范

**说明**：此模板参考 reference/create-technical-plan.md 中的流程填充。

## 摘要

[从功能规范中提取：主要需求 + 来自研究的技术路径]

## 技术背景

<!--
  需执行的操作：请将本节内容替换为项目的技术细节。
  此处结构仅作建议，用于引导迭代过程。
-->

**语言/版本**： [例如：Python 3.11、Swift 5.9、Rust 1.75 或 待澄清]  
**主要依赖**： [例如：FastAPI、UIKit、LLVM 或 待澄清]  
**存储**： [如适用，例如：PostgreSQL、CoreData、文件 或 N/A]  
**测试**： [例如：pytest、XCTest、cargo test 或 待澄清]  
**目标平台**： [例如：Linux 服务器、iOS 15+、WASM 或 待澄清]  
**项目类型**： [single/web/mobile - 决定源码结构]  
**性能目标**： [与领域相关，例如：1000 req/s、10k lines/sec、60 fps 或 待澄清]  
**约束条件**： [与领域相关，例如：p95 <200ms、内存 <100MB、离线能力 或 待澄清]  
**规模/范围**： [与领域相关，例如：1 万用户、100 万行代码、50 个界面 或 待澄清]

## 宪章检查

*关卡：必须在第 0 阶段研究前通过。第 1 阶段设计后复查。*

[基于宪章文件确定的关卡]

## 项目结构

### 文档（本功能）

```text
.eases/[###-feature]/
├── [command]/
│   ├── plan.md          # 本文件（/ease:flow-2-design 命令输出到 flow-2-design/plan.md）
│   ├── research.md      # 第 0 阶段输出
│   ├── data-model.md    # 第 1 阶段输出
│   ├── quickstart.md    # 第 1 阶段输出
│   ├── tasks.md         # 第 2 阶段输出（/ease:flow-2-design 命令输出）
│   └── checklists/      # 质量检查清单
├── contracts/           # 契约定义（共享）
└── framework-code/      # 框架代码骨架（共享）
```

### 源码（仓库根目录）
<!--
  需执行的操作：请将下方占位树替换为本功能的具体布局。
  删除未使用的选项，并将选定结构扩展为真实路径（如 apps/admin、packages/something）。
  交付的计划不得包含“选项”标签。
-->

```text
# [若未使用请删除] 选项 1：单项目（默认）
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [若未使用请删除] 选项 2：Web 应用（检测到 “frontend” + “backend” 时）
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [若未使用请删除] 选项 3：移动端 + API（检测到 “iOS/Android” 时）
api/
└── [同上方 backend 结构]

ios/ 或 android/
└── [平台特定结构：功能模块、UI 流程、平台测试]
```

**结构决策**： [记录所选结构，并引用上面捕获的真实目录]

## 复杂度记录

> 仅当宪章检查存在需解释的违规项时填写

| 违规项 | 原因 | 更简单方案被拒绝的理由 |
|--------|------|------------------------|
| [例如：第 4 个项目] | [当前需要] | [为何 3 个项目不足] |
| [例如：仓储模式] | [具体问题] | [为何直接 DB 访问不足] |
