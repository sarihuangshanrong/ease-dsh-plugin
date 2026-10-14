# 内置场景架构模板维护指南

> **适用**: 维护 `ease-arch-documentation` 技能内置的场景架构模板库。模板仅供 Agent 在 `flow-2-design` 阶段参考使用，**不会生成到用户项目中**。

## 概述

场景架构模板库存放在 skill 内置目录中：

```
references/ease-arch-documentation/references/scenario-templates/
├── README.md                 # 模板索引
├── transaction-template.md   # 交易类
├── query-template.md         # 查询类
├── workflow-template.md      # 流程类
├── messaging-template.md     # 消息类
├── sync-template.md          # 数据同步类
├── auth-template.md          # 认证类
├── file-template.md          # 文件处理类
├── realtime-template.md      # 实时类
└── generic-template.md       # 通用类（兜底，必须存在）
```

`/ease:flow-2-design` 在步骤 3.5（场景识别与模板匹配）中**直接从此内置路径加载**模板，不会在用户项目的 `docs/system/` 下生成任何模板文件。

## 模板加载路径

```
flow-2-design Step 3.5.2:
  1. 场景识别引擎确定 SCENARIO_TYPE
  2. 从内置路径加载: references/scenario-templates/${SCENARIO_TYPE}-template.md
  3. 如果目标模板不存在，回退到 generic-template.md
```

## 新增/修改内置模板流程

当需要新增场景类型或修改现有模板时：

1. **在 `scenario-templates/` 目录下创建或修改 `{scenario_id}-template.md`**
2. **遵循模板标准结构**（参考 `scenario-template-writing-guide.md`）：
   - 模板元数据（场景类型、适用用例、版本）
   - 架构模式推荐
   - 技术栈推荐
   - 组件清单（含必需性标注）
   - 数据流设计（Mermaid 序列图）
   - 接口契约模板
   - 安全考虑
   - 性能优化
   - 可观测性
   - 测试策略
   - 定制化参数
3. **更新 `scenario-templates/README.md`** 索引
4. **更新 `scenario-classification.md`** 中的场景关键词库和识别规则

## 质量校验

- 每个模板文件必须包含完整的 10 个标准章节
- `generic-template.md` 必须始终存在（兜底方案）
- 模板中的推荐不应绑定特定项目，保持通用性
