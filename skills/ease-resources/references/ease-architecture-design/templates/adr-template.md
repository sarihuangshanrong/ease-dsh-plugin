# ADR-[NNN]: [Decision Title]

## Metadata

| Field | Value |
|-------|-------|
| **Status** | Proposed / Accepted / Rejected / Deprecated / Superseded |
| **Date** | [YYYY-MM-DD] |
| **Decision ID** | ADR-[NNN] |
| **Supersedes** | [ADR-XXX, if applicable] |
| **Superseded by** | [ADR-XXX, if applicable] |
| **Trigger Source** | flow-2-design / architecture-review |
| **Approval** | [批准人、时间、批准记录路径；Accepted 必填] |
| **Realization** | unknown / not_observed / partial / realized / conflict（附快照） |
| **Change Refs** | [显式关联变更，不以 ADR 编号推断] |
| **Source Document** | [path to originating document] |

## Context

[Why is this decision needed? Technical/business background, driving forces, constraints.]

[Reference Constitution MUST principles if relevant.]

[Reference existing ADRs if relevant: ADR-XXX.]

## Options Comparison

At least 2 alternatives:

| Option | Pros | Cons | Notes |
|--------|------|------|-------|
| Option A: [name] | [...] | [...] | [...] |
| Option B: [name] | [...] | [...] | [...] |

## Decision

[What was decided and why.]

## Decision Basis

[What justified the choice: team consensus, POC results, benchmark data, architecture review findings, etc.]

## Risks and Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| [risk] | High/Medium/Low | [mitigation] |

## Rollback Strategy

[What to do if the decision proves wrong. Trigger conditions and steps.]

---

## Architecture Impact *(optional — fill when applicable)*

- **Impact Level**: L0 / L1 / L2 / L3
- **Dependency topology**: [change description]
- **Module boundaries**: [change description]
- **Data architecture**: [change description]
- **Interface contracts**: [change description]
- **Operations**: [change description]
- **NFR propagation**: [change description]
- **Affected Modules**: [list]

## Consistency Check *(optional — fill when applicable)*

| Check Item | Status | Notes |
|------------|--------|-------|
| [Existing ADR-XXX] | Consistent / Conflict | [explanation] |
| [Constitution principle] | Compliant / Exception | [explanation] |
| [Architecture standard] | Compliant / Exception | [explanation] |

## Quantified Evidence *(optional — fill when POC or benchmark data exists)*

| Metric | Actual Value | Target/Threshold | Source | Verdict |
|--------|-------------|------------------|--------|---------|
| [metric] | [value] | [threshold] | [VP-XXX-NNN or test name] | Pass/Fail |

## Implementation Evidence *(optional — filled by flow-3-implement)*

> This section is added during Phase 2 (Implementation) of two-phase recording.

- **Actual Implementation**: [how the decision was implemented in code]
- **Deviations from Design**: [any differences from the original design, and why]
- **Runtime Data**: [performance metrics, error rates, or other operational evidence]
- **Implementation Date**: [YYYY-MM-DD]

## Follow-up Actions *(optional — fill when applicable)*

| Action | Skill/Command | Notes |
|--------|--------------|-------|
| [action] | [ease-coding / flow-2-design / ...] | [notes] |

新 ADR 同时使用 `../references/decision-traceability.md` 中的 json adr 结构块，决策字段一旦 Accepted 只能通过替代 ADR 演进。
