# Python Review Guidance

Trace router/view/consumer entry points through service, ORM, and external clients.

Check:

- missing runtime validation, optional-value handling, broad exception catches, lost causes, and cleanup;
- authorization, injection, unsafe deserialization, path handling, and sensitive logging;
- blocking work in async functions, cancellation loss, unbounded tasks, N+1 queries, and session lifetime;
- mutable defaults, global state, import-time side effects, and incorrect sync/async boundaries;
- type suppressions and tests that miss failure, rollback, and nondeterministic paths.

Formatting preferences and docstring counts are not defects unless project rules or concrete impact support them.
