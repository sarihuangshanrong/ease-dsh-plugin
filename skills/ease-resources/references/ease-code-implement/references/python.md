# Python Implementation Guidance

## Boundaries

- Follow existing module, service, router/view, and persistence boundaries.
- Use type annotations at public boundaries and model optionality explicitly; do not silence errors with broad `Any` or ignores.
- Validate untrusted data before domain use and keep framework exceptions out of domain code.
- Preserve exception causes with `raise ... from ...`; catch only errors the current layer can handle.

## Data and Async

- Scope sessions and transactions explicitly and avoid lazy-loading surprises outside their lifetime.
- Do not perform blocking I/O in an async path; propagate cancellation and use bounded concurrency.
- Inject clocks, randomness, and external clients when behavior must be deterministic.

## Verification

- Run the configured formatter, type checker, linter, targeted tests, and affected suite.
- Cover validation, authorization, transaction rollback, async cancellation, and boundary values when relevant.
