# Go Implementation Guidance

## Boundaries

- Preserve package ownership and keep handlers responsible for transport conversion rather than business rules.
- Accept `context.Context` at request-scoped boundaries and propagate cancellation to I/O.
- Wrap errors with actionable context while keeping machine-testable causes through `%w` or typed errors.
- Keep interfaces consumer-owned and introduce them only where multiple behavior-compatible implementations or test seams are required.

## Data and Concurrency

- Close resources, check iterator errors, and make transaction ownership explicit.
- Bound goroutines and channels; every goroutine needs a termination path and ownership model.
- Protect shared state with synchronization or confinement and verify with the race detector where practical.

## Verification

- Run `gofmt`, `go vet`, targeted tests, affected package tests, and `go test -race` for concurrency changes.
- Use table-driven tests for meaningful behavioral partitions, not for mechanically combining unrelated cases.
