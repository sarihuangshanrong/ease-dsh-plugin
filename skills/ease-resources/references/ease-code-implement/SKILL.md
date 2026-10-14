# Ease Code Implement

## Contract

Modify production behavior only from confirmed requirements, design, acceptance criteria, or a diagnosed defect. An evidence-backed temporary mitigation with confirmed behavior and acceptance criteria is also a valid input; the complete root cause need not be known. Do not invent scope or make new system-level architecture decisions.

Before editing:

1. Confirm the expected behavior and acceptance evidence.
2. For BRD work already in the Ease lifecycle, require Flow 2 design artifacts. TRD work may consume the design embedded in Flow 1.
3. Establish the relevant test or regression point and use `test-driven-development` for behavior changes.
4. Detect the language and framework using `references/project-type-detection.md`, then read one matching reference for each language boundary actually changed.

If the task is review-only, use `ease-code-review`. If external behavior must remain unchanged, use `ease-code-refactor`. Send architecture gaps to `ease-architecture`, test-only work to `ease-testing`, and apply `mumblesdk` constraints before implementation in MumbleSDK projects.

## Production Mitigation Handoff

When called by `ease-production-bugfix`, require the recovery goal, evidence explaining why the action should work, bounded scope, accepted behavior changes, acceptance checks, and reversal point. Record remaining root-cause uncertainty; unknown complete root cause alone does not block this confirmed mitigation. Missing action evidence or unknown impact still requires investigation. Keep code-change TDD and high-integrity constraints; do not expand the mitigation into permanent redesign. Report a verified patch separately from production recovery, which needs production observation evidence.

For production mitigation, preserve the caller's impact-based acceptance matrix: demonstrate both the original failure is addressed and affected normal behavior remains correct. Cover applicable shared callers, boundaries, compatibility, concurrency and side effects. Return baseline and final-candidate evidence separately; missing checks or new/unexplained failures block a verified handoff. Never weaken assertions or suppress tests to obtain a pass. Preserve any caller-selected E2E scenarios and return their per-scenario results with current build/configuration evidence and real/mock boundaries; unit tests cannot substitute for required E2E, and skipped or blocked scenarios do not pass. The caller owns release and production-observation gates.

## Language References

| Target | Required reference |
|---|---|
| Java | `references/java.md` |
| Go | `references/go.md` |
| Python | `references/python.md` |
| TypeScript/JavaScript | `references/typescript.md` |

For mixed-language changes, process one language boundary at a time and record the interfaces between them. For unsupported languages or configuration/schema formats, follow project-local conventions and explicitly record the missing specialized guidance.

## Workflow

1. Trace the affected entry point through core logic to external dependencies.
2. Record scope, error behavior, security constraints, and rollback or regression points.
3. Write and run the smallest failing test for the changed behavior.
4. Implement only enough production code to satisfy the current behavior.
5. Refactor only while tests remain green. Delegate to `ease-code-refactor` when cleanup becomes a separate goal, crosses modules, or touches public contracts, transaction ownership, persistence meaning, or message ordering; system-boundary changes require `ease-architecture`.
6. Run diagnostics, targeted tests, relevant regression tests, formatter, and linter.
7. Summarize evidence in the task response with `templates/implementation-summary.md`. Create a file only when the user or calling workflow explicitly requires an artifact path.

Stop when the design is contradictory, the change exceeds the confirmed scope, a new or unresolved security/data-integrity risk falls outside the confirmed defect and mitigation, or three consecutive attempts fail for the same unexplained reason and require `systematic-debugging`.

For money movement, inventory, identity, or other high-integrity state changes, confirm the identity key and scope, concurrent atomicity, transaction boundary, retry/acknowledgement semantics, failure recovery, and existing-data handling before implementation. A check-then-write sequence without an atomic guarantee is not sufficient evidence of idempotency.

## Verification

- Type, syntax, and import diagnostics are clean.
- Changed behavior has executable tests and the relevant regression suite passes.
- Errors are actionable and failure paths are observable.
- Security and performance claims are supported by evidence.
- No type escape such as `any`, ignore directives, or unchecked casts was introduced merely to pass validation.
- No deployment, production data repair, migration execution, external message, or repository-wide rewrite occurs unless the user explicitly authorized that operation.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Coding before expected behavior is fixed | Return to requirements/design or diagnose the defect first |
| Expanding architecture while implementing | Stop and hand off to `ease-architecture` |
| Optimizing without a baseline | Measure first and retain a rollback strategy |
| Treating tests as optional follow-up | Use `test-driven-development` before production changes |
