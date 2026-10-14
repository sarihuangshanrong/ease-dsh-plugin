# Ease System Bootstrap

## Overview

Bootstrap a greenfield system once, before ordinary BRD/TRD delivery begins. Keep approved target intent separate from architecture observed in code so an empty repository never needs fabricated `docs/system/` evidence.

## Contract

- This skill owns system inception orchestration, not recurring feature delivery.
- Drafts and gate evidence stay under `.eases/bootstrap/${BOOTSTRAP_ID}/`.
- Only approved target architecture is promoted to `docs/architecture/target/`.
- `docs/system/` remains owned by `ease-arch-documentation` and may be created only after code, configuration, IaC, tests, or runtime evidence exists.
- Architecture decisions belong to `ease-architecture-design`; skeleton generation belongs to `ease-framework-code`; source implementation belongs to `ease-code-implement` with `test-driven-development`.
- Do not merge Bootstrap into a BRD/TRD `CHANGE_ID`, weaken their gates, or describe target intent as implemented fact.

## Entry Gate

Run `scripts/resolve-architecture-baseline.sh --root <project-root>`.

| State | Action |
|---|---|
| `empty` | Bootstrap is required. |
| `target_only` | Resume the matching Bootstrap or begin normal feature delivery from the approved target. |
| `observed_missing` | Generate an observed baseline with `ease-arch-documentation`; do not bootstrap over existing code. |
| `observed_only` | Use the existing brownfield flow. |
| `hybrid` | Use observed facts as the current state and target documents as constraints. |

## Workflow

Read `references/bootstrap-contract.md` and execute B0 through B4. `--design-only` stops after the B2 consumer gate. Every material architecture decision requires alternatives, measurable NFRs, verification, and reversal guidance.

After B4, hand ordinary business requirements to `/ease:starter`; do not keep using Bootstrap as a feature workflow.

## Stop Conditions

Stop when product scope cannot identify a system boundary, a public contract or ownership decision remains unresolved, target documents are not approved, or the walking skeleton would require business behavior. Existing code without an observed baseline routes to `/ease:arch-docs`, not Bootstrap.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Create empty `docs/system/` files to satisfy Flow 2 | Create approved target documents, then generate observed docs from code after B3. |
| Treat the whole product as one giant feature | Bootstrap the foundation once; deliver capabilities through normal BRD/TRD changes. |
| Generate microservices from directory guesses | Decide deployable boundaries through architecture evidence and ADRs. |
| Put business logic in the walking skeleton | Limit B3 to build, runtime, configuration, health, observability, test, and delivery seams. |
