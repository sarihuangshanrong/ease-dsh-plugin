# 测试案例设计（ease-test-case-design）

从用例文档和业务规则出发，应用黑盒测试设计技术，系统化生成结构化的测试案例集合文档。

> **定位**：这是一个"需求驱动"的测试设计技能，回答的是"测什么"而非"怎么测"。产出的测试案例文档是 ease-testing（代码级测试生成）和 TDD 流程的输入参考。

## Role Contract

- **主角色 — 测试分析师（Test Analyst / QA）**：从需求、用例和业务规则设计可追溯的黑盒测试案例，独立识别正常、边界和异常场景。
- **允许**：创建测试范围、测试条件、案例、数据建议、优先级和追溯矩阵；指出需求或设计的可测性缺口。
- **禁止**：生成或修改测试代码、修改生产代码、替实现选择技术方案，或把当前实现行为反向当成正确需求。
- **移交边界**：测试代码生成移交 `ease-testing`；实现缺陷移交 `ease-coding`；需求歧义返回 `ease-analysis`；架构可测性问题返回 `ease-architecture`。

## 概述

本技能将软件工程中成熟的黑盒测试设计技术（等价类划分、边界值分析、判定表、状态转换等）系统化应用于 DDD 用例文档，产出可追溯、有方法论依据的测试案例集合。

**核心价值**：
- 每个测试案例都有明确的需求来源（用例编号 + 规则编号）
- 每个测试案例都标注了所使用的测试设计技术及其选择理由
- 覆盖正常路径、异常路径、边界条件、跨用例场景

## 适用范围

### 适用场景

- flow-2-design 阶段，架构设计工件生成后、ease-spec 生命周期前（步骤 4.5）
- 需要基于需求文档独立设计测试方案，不依赖实现代码
- 需要向测试团队交付结构化的测试案例文档
- 需要对业务规则进行系统化的测试覆盖分析

### 不适用场景

- 已有实现代码需要生成测试代码 → 使用 `ease-testing` 技能
- 需要 TDD 红-绿-重构循环 → 使用 `test-driven-development` 技能
- 需要测试代码模板和 Mock 策略 → 使用 `ease-testing` 技能

### 与 ease-testing 的边界

| 维度 | ease-test-case-design (本技能) | ease-testing (现有技能) |
|------|-------------------------------|------------------------|
| 方法 | 黑盒（从需求推导） | 白盒（从代码推导） |
| 产出 | 测试案例文档 | 测试代码 |
| 时机 | Phase 2 步骤 4.5 | Phase 2 步骤 5.5.3 |
| 关注 | 测什么（What） | 怎么测（How） |
| 技术 | ECP/BVA/判定表/状态转换/场景 | MC/DC、AAA、Mock 策略、覆盖率 |

**关系**：本技能的产出 → 作为 ease-testing 生成测试代码的输入参考。

## 快速参考

| 步骤 | 关键动作 | 输出 | 参考文档 |
|------|---------|------|---------|
| 1. 需求解析 | 提取可测试需求点 | 可测性分析报告 | `references/test-design-techniques.md` |
| 2. 技术选型 | 按需求特征匹配测试技术 | 技术选型矩阵 | `references/test-design-techniques.md` (DDD 映射表) |
| 3. 案例生成 | 系统化推导测试案例 | 测试案例集 | `templates/test-case-document.md` |
| 4. 风险排序 | 评估失败可能性 × 业务影响 | 优先级排序 | `flows/design-test-cases.md` |
| 5. 质量校验 | 可追溯性 + 覆盖度检查 | 质量度量 | `flows/design-test-cases.md` |

### 测试技术速查（按需求特征选择）

| 需求特征 | 推荐技术 | 典型场景 |
|---------|---------|---------|
| 输入字段有取值范围 | 边界值分析 (BVA) | 年龄 18-65、金额 0.01-999999.99 |
| 输入字段有离散类别 | 等价类划分 (ECP) | 支付方式（信用卡/借记卡/电子钱包） |
| 业务规则含多条件组合 | 判定表测试 | 折扣规则（会员 AND 消费>100 AND 无欠款） |
| 实体有生命周期状态 | 状态转换测试 | 订单（创建→支付→发货→完成/取消） |
| 单个用例的完整功能 | 基于用例的测试 | 登录用例（成功/密码错误/账号锁定） |
| 跨多个用例的业务流程 | 基于场景的测试 | 下单→支付→发货→确认收货 |
| 多参数组合输入 | 配对/组合测试 | 搜索条件（价格范围 × 分类 × 排序 × 页码） |
| 需要确定测试优先级 | 风险驱动测试 | 核心支付流程 vs 边缘辅助功能 |

## 不可协商原则

1. **可追溯性 ≥90%**：每个测试案例必须关联用例编号（UC-XXX）和规则编号（BR-XXX）
2. **方法论标注**：每个测试案例必须标注使用的测试设计技术及选择理由
3. **Given-When-Then 格式**：所有测试案例使用统一的 Given-When-Then 结构描述
4. **正负路径兼顾**：每个需求点至少覆盖一个正常路径和一个异常路径
5. **风险优先排序**：所有案例必须标注风险等级和执行优先级
6. **接口覆盖率 100%**：`api-interface-report.md` §1.2 中每个**新增/修改/涉及**接口都必须有标准合格 testcase（分层标准见 `flows/design-test-cases.md` Step 3.3）

## 核心工作流

详细流程参见 `flows/design-test-cases.md`。

```
需求解析 → 技术选型 → 案例生成 → 风险排序 → 质量校验
   │           │           │           │           │
   ▼           ▼           ▼           ▼           ▼
 可测性      技术选型    测试案例    P1/P2/P3    质量度量
 分析报告     矩阵        文档       排序        统计
```

## 常见错误

| 错误 | 症状 | 修正 |
|------|------|------|
| 只覆盖正常路径 | 异常案例占比 < 30% | 对每个正常路径设计对应的异常路径 |
| 测试案例无法追溯到需求 | 案例中缺少 UC-XXX/BR-XXX 引用 | 回到用例文档，重新建立映射 |
| 过度使用单一技术 | 90%+ 案例使用同一技术 | 按需求特征选择不同技术，至少使用 2 种 |
| 测试数据不具体 | 测试步骤中缺少具体输入值 | 使用 BVA/ECP 推导出具体边界值和代表值 |
| 忽略跨用例场景 | 缺少端到端场景案例 | 梳理用例之间的依赖关系，设计跨用例场景 |
| 抄需求文档当测试案例 | 测试步骤就是需求描述的复述 | 将需求转化为可执行的 Given-When-Then |

## 长期 TC 接入（新任务）

执行前读取 `ease-test-case-design/references/durable-test-assets.md`（相对 `references/`）。领域 TC 保存在 `docs/domains/${DOMAIN_ID}/testcases/`，跨域/架构 TC 在 `docs/qa/testcases/`；不创建 docs/testing。任务只保存 test-selection 和执行证据。

新任务优先读取 BRD `flow-2-design/test-cases/test-selection.json` 或 TRD `flow-1-analyze-trd/validation/test-selection.json`，按 path/revision/hash 加载长期 TC；存在但无效不得回退。下文 `test-case-document.md` 对新任务仅指从所选 TC 生成的只读可读投影，旧任务无 selection 时才兼容旧权威案例文件。接口报告与测试方法必须引用同一集合，不能重新从代码推导并丢弃它。


## 输入与输出

### 输入

| 输入来源 | 路径 | 用途 |
|---------|------|------|
| 用例文档 | `docs/domains/[编号]/usecases/[subdomain]/usecase.md` | 提取测试场景 |
| 规则文档 | `docs/domains/[编号]/usecases/[subdomain]/rules.md` | 提取业务规则和约束 |
| 架构设计 | `.eases/[编号]/flow-2-design/architecture/arch-design.md` | 组件边界、接口契约 |
| 详细设计 | `.eases/[编号]/flow-2-design/detail/detail-design.md` | 数据结构、接口实现细节 |
| 系统知识 | `/docs/system/` | 技术栈、模块、数据模型 |
| 接口文档报告（可选） | `.eases/[编号]/flow-2-design/architecture/api-interface-report.md` | 权威接口清单（§1.2）交叉核对来源 |
| 项目宪章 | `/memory/constitution.md` | MUST 原则 |

### 输出

| 输出 | 路径 |
|------|------|
| 长期测试案例 | `docs/domains/${DOMAIN_ID}/testcases/` 或 `docs/qa/testcases/` |
| 本次案例选择 | `.eases/${CHANGE_ID}/flow-2-design/test-cases/test-selection.json` |
| 兼容可读投影 | `.eases/${CHANGE_ID}/flow-2-design/test-cases/test-case-document.md`（只读派生） |

## 参见

- **测试设计技术参考**: `references/test-design-techniques.md` — 8 种黑盒测试技术的详细说明、操作步骤和 DDD 映射
- **测试案例文档模板**: `templates/test-case-document.md` — 标准化的测试案例文档结构
- **测试案例设计流程**: `flows/design-test-cases.md` — 5 步详细流程指南
- **ease-testing 技能**: `references/ease-testing/SKILL.md` — 代码级测试生成（白盒）
- **TDD 技能**: `references/test-driven-development/SKILL.md` — 红-绿-重构循环

## 版本历史

### v1.0.0

- 初版：定义 8 种黑盒测试技术的系统化应用流程
- 创建测试案例文档模板和追溯矩阵标准
- 集成到 flow-2-design 步骤 4.5
