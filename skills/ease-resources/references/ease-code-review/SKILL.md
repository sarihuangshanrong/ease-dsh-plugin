# Ease Code Review

## Contract

Perform evidence-backed, read-only review. Do not modify the reviewed production code, tests, configuration, or generated artifacts. Concrete patch examples may be included in the report, but they are proposals rather than applied changes.

Before reviewing:

1. Confirm the review target and intended behavior.
2. Detect the language using `references/project-type-detection.md`, then read exactly one matching language reference.
3. Trace at least one complete path from entry point through core logic to an external dependency or observable result.

If the user requests review and repair, first finish and preserve the review report in the current task context. Then emit the handoff payload below and return control to the orchestrating Agent, which may invoke `ease-code-refactor` for behavior-preserving changes or `ease-code-implement` for behavior changes. Do not switch authority inside this skill. Do not create a report file unless the user explicitly requests an artifact and the orchestrator performs that separately authorized write.

## Fan-out assessment

直接调用本 Skill 或通过 Command 调用时，在确认范围和基线后、实质审查前执行一次轻量评估，无需经过 ease-agent，也不要求用户选择模式或另建规划文件。优先处理既有异步路由；本地 fan out 不触发云端提交。

仅当至少两个工作包边界明确、输入已就绪、互不依赖未完成结果，且节省时间预计超过分派与汇总成本时，使用当前宿主可用的 subagent 能力。小任务、强耦合任务、用户要求串行、工具不可用或并发额度不足时串行完成；不得绕过宿主权限获取并发能力。

- 分派前指定目标、共同基线（含纳入审查的未提交内容）、必要规范、范围、依赖、验收条件及输出格式。通常从 2–3 个工作包开始，受宿主实际额度约束；不要复制无关上下文。
- 子任务继承本 Skill 的只读契约与工具限制；禁止借助子代理修改代码、测试、配置或报告文件。只使用可遵守这些限制的子代理，否则串行执行。
- 已收到明确工作包的子任务直接执行，不再次 fan out；Command 不重复分派同一工作包。主执行者并行处理跨边界检查和未分派维度。
- 每个子任务返回 `scope`、`baseline`、`status: complete | partial | blocked`、符合 Finding Standard 的 `findings`、`evidence` 和 `uncovered`，无发现也说明实际覆盖范围；不要求额外文件。

### 代码审查拆分策略

多模块且边界清晰时按模块拆分，每包覆盖全部适用审查维度；单模块复杂时按正确性与异常、安全与权限、性能与资源等维度分组。选择一种主要拆分轴，不展开“模块 × 维度”组合。可读性、可测试性、可维护性、命令要求的注释覆盖率和坏味道检查也须分配给子任务或主执行者，不能因 fan out 遗漏。

### Fan-in

收齐结果后，主执行者核对同一基线与范围覆盖，回查关键证据，按根因和触发路径去重，统一严重程度并保留跨模块调用链结论。基线变化时重审受影响范围，不拼接不同版本的发现。

子任务失败或返回 partial/blocked 时，可由主执行者接手或将失败包拆小后重试，仍须补齐原定范围；独立工作可继续，但依赖该结果的结论不得推进。未补齐覆盖前显式报告未完成范围，不输出 `review_status: complete`，不宣称全部通过。审查与修复仍分步骤移交。

## Language References

| Target | Required reference |
|---|---|
| Java | `references/java.md` |
| Go | `references/go.md` |
| Python | `references/python.md` |
| TypeScript/JavaScript | `references/typescript.md` |

## Workflow

1. Establish scope and collect project conventions, then perform Fan-out assessment before the following review work.
2. Trace real data and control flow rather than reviewing isolated snippets only.
3. Check correctness, error handling, security, performance, readability, testability, and maintainability.
4. Exclude generated, vendored, or irrelevant code and distinguish evidence from inference.
5. Rank only actionable findings by impact and confidence.
6. Write the result with `templates/code-review-report.md`.

## Severity

| Level | Meaning |
|---|---|
| Critical | Exploitable security issue, data loss/corruption, or broad production outage on a realistic path |
| High | Incorrect authorization or business result, serious availability impact, or likely regression on a normal path |
| Medium | Bounded correctness, performance, testability, or maintenance impact with a credible trigger |
| Low | Localized improvement supported by project rules or measurable impact |

Severity alone never grants write authority.
Unless the user defines another threshold, natural-language “严重问题” means Critical or High findings.

## Finding Standard

Every finding must contain:

- precise file and location;
- triggering input or execution path;
- observed or logically demonstrated impact;
- supporting evidence and confidence;
- a bounded remediation and its trade-off.

Do not fabricate a minimum number of findings. Report no issue when evidence does not support one.

## Handoff Payload

For incomplete coverage, return `review_status: partial | blocked` with `uncovered` and the evidence needed; do not emit the complete handoff or start repair.

For review-and-repair requests, finish the complete review with a payload in the task response:

```yaml
review_status: complete
review_scope: <files and call paths>
findings: [<stable finding IDs>]
recommended_capability: ease-code-implement | ease-code-refactor | none
authorization_source: <explicit user request or none>
```

The next Skill starts a separate execution step and maps its changes and verification evidence back to the stable finding IDs.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Editing while reviewing | Preserve the report, then hand off to a write-capable skill |
| Reporting style preferences as defects | Tie findings to project rules or measurable impact |
| Suggesting cache/thread/async without evidence | Provide baseline and bottleneck evidence first |
| Reviewing only the changed line | Trace callers, state changes, and external dependencies |
