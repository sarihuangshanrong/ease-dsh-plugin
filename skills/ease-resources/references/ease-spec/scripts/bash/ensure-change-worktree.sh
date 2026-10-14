#!/usr/bin/env bash
set -euo pipefail

POLICY="auto"
CHANGE_ID=""
BASE_BRANCH=""
REPO_INPUT="."
WORKTREE_ROOT=""

usage() {
    cat <<'EOF'
Usage: ensure-change-worktree.sh --change-id <NNN-name> [options]

Create, discover, or verify the single Git worktree for an Ease change.

Options:
  --change-id <id>       Required Ease CHANGE_ID (for example 042-user-registration)
  --policy <policy>      auto (default), required, reuse, or off
  --base <branch>        Explicit base branch for a new feature branch
  --repo <path>          Repository/worktree to inspect (default: current directory)
  --worktree-root <path> Root for new worktrees
  --help                 Show this help

The command prints one JSON object. Callers must use worktree_path as the working
directory for all subsequent tools, then invoke this command again to verify the
reused-current state before writing artifacts.
EOF
}

emit_json() {
    local status="$1"
    local branch="$2"
    local worktree_path="$3"
    local base_branch="${4:-}"
    local isolation_status="active"
    [[ "$POLICY" == "off" ]] && isolation_status="waived"
    printf '{"status":"%s","policy":"%s","change_id":"%s","branch":"%s","worktree_path":"%s","base_branch":"%s","isolation_status":"%s"}\n' \
        "$status" "$POLICY" "$CHANGE_ID" "$branch" "$worktree_path" "$base_branch" "$isolation_status"
}

emit_error() {
    local error="$1"
    local message="$2"
    printf '{"error":"%s","policy":"%s","change_id":"%s","message":"%s"}\n' \
        "$error" "$POLICY" "$CHANGE_ID" "$message" >&2
}

resolve_ref() {
    local candidate="$1"
    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$candidate"; then
        printf '%s\n' "$candidate"
        return 0
    fi
    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$candidate"; then
        printf 'origin/%s\n' "$candidate"
        return 0
    fi
    return 1
}

select_base_ref() {
    local candidate
    if [[ -n "$BASE_BRANCH" ]]; then
        resolve_ref "$BASE_BRANCH" || {
            emit_error "base-branch-not-found" "Base branch '$BASE_BRANCH' does not exist locally or on origin"
            return 1
        }
        return 0
    fi

    for candidate in develop main master; do
        if resolve_ref "$candidate"; then
            return 0
        fi
    done

    emit_error "base-branch-not-found" "No develop, main, or master branch is available"
    return 1
}

find_worktree_for_branch() {
    local branch_ref="refs/heads/$1"
    git -C "$REPO_ROOT" worktree list --porcelain | awk -v target="$branch_ref" '
        /^worktree / { path = substr($0, 10) }
        /^branch / && substr($0, 8) == target { print path; exit }
    '
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --change-id)
            [[ $# -ge 2 ]] || { emit_error "invalid-arguments" "--change-id requires a value"; exit 2; }
            CHANGE_ID="$2"
            shift 2
            ;;
        --policy)
            [[ $# -ge 2 ]] || { emit_error "invalid-arguments" "--policy requires a value"; exit 2; }
            POLICY="$2"
            shift 2
            ;;
        --base)
            [[ $# -ge 2 ]] || { emit_error "invalid-arguments" "--base requires a value"; exit 2; }
            BASE_BRANCH="$2"
            shift 2
            ;;
        --repo)
            [[ $# -ge 2 ]] || { emit_error "invalid-arguments" "--repo requires a value"; exit 2; }
            REPO_INPUT="$2"
            shift 2
            ;;
        --worktree-root)
            [[ $# -ge 2 ]] || { emit_error "invalid-arguments" "--worktree-root requires a value"; exit 2; }
            WORKTREE_ROOT="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            emit_error "invalid-arguments" "Unknown argument: $1"
            exit 2
            ;;
    esac
done

case "$POLICY" in
    auto|required|reuse|off) ;;
    *)
        emit_error "invalid-policy" "Policy must be auto, required, reuse, or off"
        exit 2
        ;;
esac

if [[ ! "$CHANGE_ID" =~ ^[0-9]{3}-[a-z0-9][a-z0-9-]*$ ]]; then
    emit_error "invalid-change-id" "CHANGE_ID must match NNN-kebab-case"
    exit 2
fi

if ! REPO_ROOT="$(git -C "$REPO_INPUT" rev-parse --show-toplevel 2>/dev/null)"; then
    emit_error "not-a-git-repository" "The requested path is not inside a Git worktree"
    exit 2
fi

TARGET_BRANCH="feature/$CHANGE_ID"
CURRENT_BRANCH="$(git -C "$REPO_ROOT" branch --show-current)"
[[ -n "$CURRENT_BRANCH" ]] || CURRENT_BRANCH="DETACHED"
CURRENT_PATH="$REPO_ROOT"

if [[ "$POLICY" == "off" ]]; then
    emit_json "skipped" "$CURRENT_BRANCH" "$CURRENT_PATH"
    exit 0
fi

if [[ "$CURRENT_BRANCH" == "$TARGET_BRANCH" ]]; then
    emit_json "reused-current" "$TARGET_BRANCH" "$CURRENT_PATH"
    exit 0
fi

if [[ "$POLICY" == "required" ]]; then
    emit_error "target-worktree-required" "Current branch '$CURRENT_BRANCH' is not '$TARGET_BRANCH'"
    exit 3
fi

if [[ "$CURRENT_BRANCH" == feature/* ]]; then
    emit_error "branch-conflict" "Current feature branch '$CURRENT_BRANCH' does not match '$TARGET_BRANCH'"
    exit 3
fi

EXISTING_WORKTREE="$(find_worktree_for_branch "$TARGET_BRANCH")"
if [[ -n "$EXISTING_WORKTREE" ]]; then
    emit_json "existing-worktree" "$TARGET_BRANCH" "$EXISTING_WORKTREE"
    exit 0
fi

if [[ "$POLICY" == "reuse" ]]; then
    emit_error "worktree-not-found" "No worktree is registered for '$TARGET_BRANCH'"
    exit 3
fi

if [[ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
    emit_error "dirty-working-tree" "Commit or stash current changes before creating '$TARGET_BRANCH'"
    exit 3
fi

if [[ -z "$WORKTREE_ROOT" ]]; then
    WORKTREE_ROOT="$(dirname "$REPO_ROOT")/.ease-worktrees/$(basename "$REPO_ROOT")"
elif [[ "$WORKTREE_ROOT" != /* ]]; then
    WORKTREE_ROOT="$(cd "$(dirname "$WORKTREE_ROOT")" 2>/dev/null && pwd)/$(basename "$WORKTREE_ROOT")"
fi

TARGET_PATH="$WORKTREE_ROOT/feature/$CHANGE_ID"
mkdir -p "$(dirname "$TARGET_PATH")"

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
    git -C "$REPO_ROOT" worktree add "$TARGET_PATH" "$TARGET_BRANCH" >/dev/null
    emit_json "attached" "$TARGET_BRANCH" "$TARGET_PATH"
    exit 0
fi

if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/remotes/origin/$TARGET_BRANCH"; then
    git -C "$REPO_ROOT" worktree add --track -b "$TARGET_BRANCH" "$TARGET_PATH" "origin/$TARGET_BRANCH" >/dev/null
    emit_json "attached-remote" "$TARGET_BRANCH" "$TARGET_PATH" "origin/$TARGET_BRANCH"
    exit 0
fi

BASE_REF="$(select_base_ref)"
git -C "$REPO_ROOT" worktree add -b "$TARGET_BRANCH" "$TARGET_PATH" "$BASE_REF" >/dev/null
emit_json "created" "$TARGET_BRANCH" "$TARGET_PATH" "$BASE_REF"
