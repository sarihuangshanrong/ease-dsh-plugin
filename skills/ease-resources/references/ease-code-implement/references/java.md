# Java Implementation Guidance

## Boundaries

- Follow the existing package and Controller/Service/Repository boundaries; do not introduce a new layer during implementation.
- Validate transport input at the boundary and enforce business invariants in the domain/service layer.
- Keep transactions around the smallest consistent business operation; do not include remote calls unless the design requires it.
- Preserve exception causes and map internal failures to stable external error contracts.

## Data and Concurrency

- Use parameterized persistence APIs and inspect generated query count for collection access.
- Make nullability explicit; do not use `Optional` for entity fields or serialization merely for style.
- Define idempotency and locking semantics before modifying shared state.
- Bound executors, queues, retries, and timeouts; propagate cancellation and tracing context.

## Verification

- Run the project formatter, compiler, static analysis, targeted tests, and affected module tests.
- Test transaction rollback, authorization, boundary values, and concurrent/idempotent paths when applicable.
- Avoid Lombok or Stream rewrites unless they match the existing project and improve the concrete change.
