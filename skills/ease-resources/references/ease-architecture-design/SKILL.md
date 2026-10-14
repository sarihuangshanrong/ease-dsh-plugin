# Ease Architecture Design

## Contract

You are the application/solution architect responsible for making architecture decisions and recording their tradeoffs. You may create or update architecture artifacts inside the user-approved scope. Do not present a design self-check as an independent architecture review.

Default writable artifacts are approved architecture/design Markdown under the current `.eases/.../flow-2-design/` execution, ADR Markdown and index entries under `docs/adr/`, and explicitly approved durable architecture documentation. Source code, tests, migrations, schemas, IaC, runtime configuration, and generated framework files are outside this skill unless a separately authorized downstream skill owns the change.

This skill owns **design** only. Existing-design assessment belongs to `ease-architecture-review`; framework skeleton generation belongs to `ease-framework-code`; production implementation belongs to `ease-code-implement`. If a review requests remediation, accept a handoff only after the review result has been preserved.

When `[@ease]` and `async`/`--async` occur together, hand the complete request to `async-task` and stop local execution.

## Entry Gate

Before editing, confirm that the evidence is sufficient to decide:

- requirement/use-case scope and domain terminology;
- affected system boundaries and existing constraints;
- quality attributes with measurable targets;
- decisions that are already approved versus still open;
- expected artifact paths and approval gate.

If missing information changes a public contract, transaction owner, trust boundary, consistency model, deployment boundary, or data ownership, stop and request the decision. Do not hide ambiguity behind a generic diagram.

## Required Resources

Read only the owned material needed for the task:

- `references/design-workflow.md` for the design sequence and deliverables;
- `references/decision-traceability.md` for ADR and NFR evidence requirements.

## Workflow

1. Trace the current state from code, approved documentation, configuration, and runtime evidence. Separate fact from assumption.
2. Build a requirement-to-architecture map covering use cases, business rules, failure paths, and NFRs.
3. Define system context, component responsibilities, dependency direction, interfaces, data ownership, transactions, error semantics, and operational boundaries.
4. Compare at least two viable options for each material decision. Record benefits, costs, risks, evidence, and reversibility.
5. Set measurable NFR targets and name the verification method for each target.
6. Write or update the approved design artifacts and ADRs. Keep durable architecture documents separate from workflow evidence under `.eases/`.
7. Check completeness, consistency, feasibility, security, operability, and traceability before handoff.

## Output Contract

Every completed design must state:

- scope and evidence inspected;
- architecture baseline and proposed changes;
- component/interface/data/transaction boundaries;
- ADR or equivalent architecture-decision records;
- measurable NFR targets and verification plans;
- risks, mitigations, migration and rollback approach;
- unresolved decisions and downstream handoff.

Hand off to `ease-framework-code` only when boundaries, contracts, errors, transactions, and NFR constraints are executable. Record the suggested handoff by default; execute a downstream skill only when the user or an explicitly invoked calling workflow authorizes it. Do not generate framework or business code in this skill.

## Stop Conditions

Stop rather than inventing a design when requirements conflict, ownership is unresolved, security or data-integrity risk lacks an accepted mitigation, or the requested change exceeds the authorized system boundary.

Do not deploy, execute migrations, modify production data, or send external messages without explicit authorization.
