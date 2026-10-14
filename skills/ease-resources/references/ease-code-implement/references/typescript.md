# TypeScript Implementation Guidance

## Boundaries

- Keep transport, application, domain, and persistence responsibilities aligned with the existing project.
- Validate runtime input at trust boundaries; TypeScript types do not validate JSON, forms, environment variables, or database data.
- Prefer discriminated unions and exhaustive checks for stateful behavior.
- Do not introduce `any`, unsafe casts, or suppression directives merely to satisfy the compiler.

## Async and State

- Await or deliberately own every promise; define cancellation, timeout, retry, and error propagation semantics.
- Keep React render logic pure, clean up effects, and avoid copying derived state.
- Bound queues and parallel work; protect idempotency when retries can repeat side effects.

## Verification

- Run formatting, linting, `tsc --noEmit`, targeted tests, and affected integration/component tests.
- Cover malformed runtime input, rejected promises, authorization, state transitions, and cleanup paths where applicable.
