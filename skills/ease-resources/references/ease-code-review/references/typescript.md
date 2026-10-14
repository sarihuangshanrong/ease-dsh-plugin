# TypeScript Review Guidance

Trace HTTP/event/UI entry points through application state, persistence, and outbound calls.

Check:

- runtime validation gaps hidden by static types, non-exhaustive states, rejected promises, and cleanup;
- authorization, XSS, injection, unsafe HTML, secret exposure, and trust-boundary confusion;
- unbounded concurrency, missing timeouts/cancellation, duplicate effects, render loops, and N+1 requests;
- `any`, unsafe casts, non-null assertions, stale closures, mutable shared state, and type/runtime divergence;
- tests for malformed input, failure paths, state transitions, effects, and asynchronous ordering.

Do not recommend memoization, state libraries, queues, or async parallelism without profiling or behavior evidence.
