# Change Worktree Contract

## Purpose

Every Ease change owns exactly one feature branch and one Git worktree. The
branch/worktree pair is established once, at the first write-capable flow entry,
and all later phases only discover, reuse, and verify it.

The authority is the Git registry returned by `git worktree list --porcelain`.
Directory naming conventions, `.claude/` folders, and the presence of a sibling
`.bare/` directory are not evidence that the current process is in the correct
worktree.

## Identity

| Item | Value |
|---|---|
| Change identity | `${CHANGE_ID}` (`NNN-kebab-case`) |
| Feature branch | `feature/${CHANGE_ID}` |
| Default base | `develop`, then `main`, then `master` |
| Worktree identity | Registered path for `refs/heads/feature/${CHANGE_ID}` |

BRD and TRD use the same branch rule. `TRACK` changes artifact paths, not Git
isolation semantics.

## Single entry point

```bash
references/ease-spec/scripts/bash/ensure-change-worktree.sh \
  --change-id "${CHANGE_ID}" \
  --policy "${WORKTREE_POLICY:-auto}"

# PowerShell
$WorktreePolicy = if ($env:WORKTREE_POLICY) { $env:WORKTREE_POLICY } else { "auto" }
references/ease-spec/scripts/powershell/ensure-change-worktree.ps1 `
  -ChangeId "${CHANGE_ID}" `
  -Policy $WorktreePolicy
```

The command emits one JSON object. Relevant statuses are:

| Status/error | Caller action |
|---|---|
| `reused-current` | Continue; environment admission passed |
| `created` / `attached` / `attached-remote` | Switch every subsequent tool call to `worktree_path`, invoke again, and require `reused-current` before writing |
| `existing-worktree` | Switch to `worktree_path`, invoke again, and require `reused-current` |
| `skipped` | Continue only because the user explicitly selected `off`; record the waiver in the flow summary |
| `dirty-working-tree` | Stop; commit or stash before isolation |
| `branch-conflict` | Stop; the current feature belongs to another change |
| Any other error | Stop and preserve the JSON evidence |

Changing a subprocess directory is not enough. Agents must set the working
directory of all subsequent filesystem and shell tools to the returned absolute
`worktree_path`.

## Policies

| Policy | Meaning |
|---|---|
| `auto` | Default. Create missing branch/worktree, otherwise discover and reuse it |
| `required` | Never create or redirect; current checkout must already be the target worktree |
| `reuse` | Never create; discover an existing target worktree or fail |
| `off` | Explicitly waive isolation; never create a branch or worktree |

The policy is selected once at the outermost command and passed unchanged across
Starter, Flow 1, Flow 2, and Flow 3. A nested phase must not silently downgrade
it. `off` is the only valid path without a feature worktree and must never be
inferred from missing tools or an unsupported platform.

## Write boundary

For a new change, determine `DOMAIN_ID`/`CHANGE_ID` without writing artifacts,
admit the worktree, switch to it, verify `reused-current`, and only then create
`context.json`, domain/TRD documents, `.eases/` artifacts, framework code, or
production code. This prevents uncommitted files in the stable checkout from
being stranded outside the new worktree.

`create-new-feature.sh` is an artifact lifecycle helper in the three-phase flow.
When `--feature-dir` is supplied it intentionally has no Git responsibility.

## Idempotency

- A second call for the same change must not create another branch or worktree.
- Flow 2 and Flow 3 must use the same `feature/${CHANGE_ID}` created by Flow 1.
- Resume must discover the registered worktree instead of deriving a directory.
- A different current `feature/*` branch is a conflict, never an invitation to
  create another branch.
