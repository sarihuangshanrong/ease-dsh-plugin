# Java Review Guidance

Trace Controller/consumer entry points through service and repository or external clients.

Check:

- nullability, boundary conditions, exception mapping, transaction scope, idempotency, and concurrency;
- authorization at the service boundary, injection, unsafe deserialization, and sensitive logging;
- N+1 queries, unbounded executors/retries, blocking calls, resource leaks, and oversized collections;
- equality/hash contracts, mutable shared state, proxy/annotation behavior, and reflection-sensitive changes;
- whether tests exercise business decisions and failure paths rather than framework wiring only.

Treat style, method length, Optional, Streams, Lombok, and design patterns as findings only when they cause a demonstrated maintenance or correctness impact.
