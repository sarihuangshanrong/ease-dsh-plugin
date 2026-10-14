# Go Review Guidance

Trace handler/RPC entry points through service, repository, and outbound I/O.

Check:

- ignored errors, lost `%w` causes, context loss, partial writes, and cleanup after iteration;
- goroutine leaks, send/close ownership, races, deadlocks, and unbounded fan-out;
- authorization, path and command handling, SQL construction, and sensitive logs;
- transaction lifetime, query count, allocations on hot paths, and missing timeouts;
- exported API compatibility and tests for error identity, cancellation, and concurrent behavior.

Do not report interface extraction, channel changes, or goroutine introduction as improvements without a concrete need and evidence.
