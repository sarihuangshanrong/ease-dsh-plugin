## Task Management Standards (TodoWrite)

This skill uses **TodoWrite** to prevent skipped steps on large analyses.

### Rules

- Every task must have: `id`, `content`, `status`, `priority`.
- Only **one** task may be `in_progress` at any time.
- Mark a task `completed` immediately when done (do not batch).
- Report progress every 3–5 tasks, then continue (unless blocked).

### Allowed statuses

- `pending`
- `in_progress`
- `completed`
- `cancelled`

### When to pause and ask the user

- Required paths/files are missing and you need confirmation
- You find conflicting conventions and need a decision
- The scope materially changes
