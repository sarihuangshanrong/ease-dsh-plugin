# Architecture Design Workflow

## Evidence order

Inspect the narrowest authoritative sources first: approved use cases and rules, existing architecture decisions, public contracts, code and configuration, then operational evidence. Label inferred behavior and unresolved contradictions.

## Design sequence

1. State scope, stakeholders, constraints, and excluded concerns.
2. Describe the as-is system context and the change pressure.
3. Map use cases and failure paths to components and responsibilities.
4. Define dependency direction, interfaces, data ownership, transactions, consistency, idempotency, and error semantics.
5. Define deployment, scaling, security, observability, recovery, and cost boundaries.
6. Compare viable options and record material decisions.
7. Plan migration, compatibility, rollout, rollback, and verification.

## Minimum deliverables

- Context and component views appropriate to the decision.
- Contract and data-flow descriptions with ownership.
- Decision records for irreversible or costly choices.
- NFR targets with test or measurement methods.
- Risk register and an explicit list of open decisions.

Diagrams support decisions; they do not replace precise contracts or evidence.
