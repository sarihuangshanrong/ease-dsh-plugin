# Decision Traceability

## ADR minimum fields

For each material decision record:

- ID and status: proposed, accepted, superseded, or deprecated.
- Context: business goal, constraints, current-state evidence.
- Options: at least two viable choices, including keeping the current design when relevant.
- Decision: selected option and explicit rationale.
- Consequences: benefits, costs, operational burden, security and data risks.
- Verification: metric, test, POC, review, or operational signal.
- Reversal: migration and rollback path, including compatibility constraints.
- Trace links: use cases, business rules, affected contracts, and follow-up work.

## NFR evidence

| Attribute | Target example | Required verification |
|---|---|---|
| Performance | peak QPS and p99 latency | load profile and acceptance threshold |
| Availability | SLO and recovery objective | failure injection or recovery exercise |
| Security | trust boundary and control | threat review and control evidence |
| Consistency | invariant and consistency model | concurrency/failure-path test |
| Observability | service-level signals | dashboard, alert, and trace acceptance |
| Cost | capacity or budget ceiling | forecast and measured unit cost |

Words such as “high performance” or “high availability” are not decisions until paired with a target and verification method.

## 批准状态与实现状态（当前契约）

Accepted 仅表示有批准记录，不表示代码已实现。已有批准无需重复确认。Flow 3 不得因实现了 Proposed 建议自动授予 Accepted。落实状态另记 realized/partial/conflict/not_observed/unknown，并绑定快照和验证证据。关联通过 change_refs、scope 和契约，不根据 ADR 编号推断需求。

新 ADR 在正文中添加一个 `json adr` 结构块，字段见下方；正文与结构块含义必须一致。已 Accepted 的 decision/rationale/scope/constraints 不改写；创建新 ADR 并 supersedes，旧状态改为 Superseded。实施证据另追加，不改变决策。

```json adr
{
  "id": "ADR-001",
  "status": "Accepted",
  "scope": ["src/order"],
  "change_refs": ["001-order-change"],
  "approval": {"by": "<approver>", "at": "<ISO8601>", "source": "<approval-record.md>"},
  "decision": "<approved choice>",
  "rationale": "<approved reason>",
  "constraints": [{"id": "ADR-001-C001", "text": "<verifiable constraint>", "scope": ["src/order"], "effective": true}],
  "supersedes": []
}
```

约束 effective 表示当前是否生效；延后生效的决策在批准时明确计划，调整生效语义通过新的批准记录/替代 ADR。未生效约束可以 not_observed，不能被误当成本次违规。旧 ADR 无结构块时保留历史并报告证据缺口，不能自动猜测批准信息。
