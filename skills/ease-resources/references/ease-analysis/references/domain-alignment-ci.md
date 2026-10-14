# 领域对齐严格验收与 CI 契约

## 目标

二期验收是现有方法论的附加守门器，不改变原有阶段职责：

- BRD：Flow 1 分析 → Flow 2 设计 → Flow 3 实现。
- 纯技术 TRD：Flow 1 内置设计 → Flow 3 实现。
- Flow 1 BRD 仍禁止 API/DB Schema/技术架构和代码；Flow 2 仍只允许骨架；Flow 3 仍只执行 implement。
- 原测试覆盖率、TDD、架构门禁继续生效，领域门禁不能替代或降低它们。

## 四层验收

1. **结构契约**：Schema、ID、来源、DDR、阶段证据完整。
2. **行为契约**：真实 Git diff 能区分无关变更与领域实现变更。
3. **跨阶段契约**：业务语义变化回流 Flow 1，TRD Domain Impact Guard 正确放行/阻断。
4. **非回归契约**：`test-flow-p0-contracts.sh` 与一期/二期领域测试必须同时通过。

## 本地提交策略

本地 `/ease-tools:git-commit` 使用 `detect_domain_drift.py --policy warn`。它报告需要语义审查的领域实现变化，但不改变该命令“一键 commit + push”的既有授权语义。

## CI 阻断策略

CI 必须使用严格入口：

```bash
python3 references/ease-analysis/scripts/accept_domain_alignment.py \
  --repo-root . \
  --change "${CHANGE_ID}" \
  --domain "${DOMAIN_ID}" \
  --level ci \
  --base "${MERGE_BASE}" \
  --head HEAD \
  --semantic-review ".eases/${CHANGE_ID}/domain-semantic-review.json"
```

CI 固定使用 `--policy block`，以下情况失败：

- UC/BR/DDR/设计/实现证据不完整；
- 领域实现路径发生变化但缺少语义审查；
- 变更源码中的 `UC-*`/`BR-*` 标识未知，或对应文件未登记到实现证据；
- 审查范围与实际 Git diff 不一致；
- `aligned-domain-change` 没有同步领域文档；
- verdict 为 `semantic-drift`。

验收脚本只读，不生成、不更新、不修复任何业务或技术工件。

语义审查绑定已经存在的 base/head commit SHA，因此应在提交后生成，并作为流水线工作区或审批系统工件传给验收器；不要要求它进入被审查的同一个 commit，否则会形成无法满足的提交自引用。审查文件是否最终归档由项目治理决定，不影响本次只读裁决。

## 语义裁决

语义裁决只允许：

- `no-semantic-change`：重构、格式或实现替换，业务行为不变；必须给出测试或差异证据。
- `aligned-domain-change`：业务变化已回流 Flow 1，领域文档与基线出现在同一差异范围。
- `semantic-drift`：实现改变业务语义但领域事实未对齐，必须阻断并返回 Flow 1。

资金、权限、合规、状态机不变量等高风险变化必须设置 `risk_level=high`；不得仅由 Agent 自动判为 `no-semantic-change`，`human_approval` 为空时 CI 强制失败。
