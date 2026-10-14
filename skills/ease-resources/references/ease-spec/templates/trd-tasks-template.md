---
description: "用于 TRD 实施的技术工作包清单模板"
---

# 技术实施任务：[TRD NAME]

**权威输入**：`TRD.md`、`artifacts/solution-design.md`

**风险级别**：`Lite | Standard | Strict`
**状态职责**：Flow 1 创建未完成任务 `[ ]`；Flow 3 实施后就地标记 `[X]`。

## 格式

```text
- [ ] T001 [P?] [BASELINE|IMPLEMENT|COMPAT|VERIFY|ROLLOUT|ROLLBACK] 动作；文件/命令；完成证据
```

- `[P]`：可与相邻任务并行，且不修改同一文件。
- 分类标签必须准确反映技术工作包，不使用 `US1` 等业务用户故事标签。
- 每个任务必须包含实际文件路径或可执行命令，以及可判断的完成证据。
- 不适用的阶段直接删除；不得为了填满模板制造任务。

## 基线（Baseline）

- [ ] T001 [BASELINE] 记录变更前基线、复现方式与观测证据：[命令/指标/文件]

## 实施（Implementation）

- [ ] T002 [IMPLEMENT] 按 `solution-design.md` 修改 [文件路径]；完成证据：[测试或差异]

## 兼容与迁移（Compatibility / Migration，按需）

- [ ] T003 [COMPAT] 验证 API、数据、配置或依赖兼容性：[命令/证据]

## 验证（Verification）

- [ ] T004 [VERIFY] 先建立失败测试或失败基线，再完成实现验证：[测试命令]
- [ ] T005 [VERIFY] 验证 TRD 成功指标与非功能目标：[指标采集方式]

## 发布与观测（Rollout，按需）

- [ ] T006 [ROLLOUT] 执行灰度/发布并观察 [指标]；放量条件：[阈值]

## 回滚（Rollback）

- [ ] T007 [ROLLBACK] 验证回滚步骤可执行；触发条件：[阈值]；回滚命令：[命令]

## 依赖与完成定义

- 基线任务先于实施任务。
- 兼容/迁移任务必须在发布前完成。
- 验证失败或超过回滚阈值时停止推进。
- 所有目标任务完成且证据可复查后，Flow 3 才可将对应任务标记为 `[X]`。
