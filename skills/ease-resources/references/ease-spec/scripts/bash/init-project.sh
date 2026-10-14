#!/usr/bin/env bash
# Initialize Spec Kit project from latest GitHub release assets
# Equivalent to 'specify init' (non-interactive), driven by JSON args
# Requires: curl, jq, unzip (or Python 3 fallback for zip extraction), git (optional)

set -euo pipefail

# ----------------------------
# Helpers
# ----------------------------

log() { printf "%s\n" "$*" >&2; }
info() { log "INFO: $*"; }
warn() { log "WARNING: $*"; }
err() { log "ERROR: $*"; }

has_cmd() { command -v "$1" >/dev/null 2>&1; }

OS_DEFAULT_SCRIPT() {
  if [[ "${OS:-}" == "Windows_NT" ]] || [[ "${OSTYPE:-}" == "msys" ]] || [[ "${OSTYPE:-}" == "cygwin" ]]; then
    echo "ps"
  else
    echo "sh"
  fi
}

# Deep merge two JSON files using jq (best-effort)
# - If jq missing, or files unreadable, falls back to copy new over existing
merge_json_files() {
  local existing_file="$1"
  local new_file="$2"
  local out_file="$3"

  if ! has_cmd jq; then
    warn "jq not found; copying new settings.json over existing"
    cp -f "$new_file" "$out_file"
    return 0
  fi

  # Deep merge function in jq
  # Source approach: recursively merge objects; arrays replaced by new
  local jq_script='
    def deepmerge(a;b):
      if (a|type) == "object" and (b|type) == "object" then
        reduce (b|to_entries[]) as $item (
          a;
          .[$item.key] = (
            if .[$item.key] == null then
              $item.value
            else
              deepmerge(.[$item.key]; $item.value)
            end
          )
        )
      else
        b
      end;
    deepmerge(.[0]; .[1])
  '

  if ! jq -e . "$existing_file" >/dev/null 2>&1; then
    warn "Existing settings.json invalid JSON; copying new"
    cp -f "$new_file" "$out_file"
    return 0
  fi

  if ! jq -e . "$new_file" >/dev/null 2>&1; then
    warn "New settings.json invalid JSON; keeping existing"
    cp -f "$existing_file" "$out_file"
    return 0
  fi

  local merge_tmp
  merge_tmp="${EASE_TMP_DIR:?EASE_TMP_DIR must be set before merging settings.json}/settings-merge.$$.tmp"
  jq -s "$jq_script" "$existing_file" "$new_file" >"$merge_tmp" && mv "$merge_tmp" "$out_file"
}

# Extract zip to destination directory
extract_zip() {
  local zip_path="$1"
  local dest_dir="$2"

  mkdir -p "$dest_dir"

  if has_cmd unzip; then
    unzip -q "$zip_path" -d "$dest_dir"
    return 0
  fi

  if has_cmd python3; then
    python3 - <<'PYCODE'
import sys, zipfile, os
zip_path = sys.argv[1]
dest_dir = sys.argv[2]
with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(dest_dir)
PYCODE
    return 0
  fi

  err "Neither unzip nor python3 available to extract zip"
  return 1
}

# Ensure *.sh under .specify/scripts are executable (shebang-aware best-effort)
ensure_posix_exec_bits() {
  local project_path="$1"
  local scripts_root="$project_path/.specify/scripts"
  [[ -d "$scripts_root" ]] || return 0

  local updated=0
  while IFS= read -r -d '' script; do
    if head -c 2 "$script" | grep -q "^#\!"; then
      chmod +x "$script" || true
      updated=$((updated+1))
    fi
  done < <(find "$scripts_root" -type f -name "*.sh" -print0)
  if [[ "$updated" -gt 0 ]]; then
    info "Updated execute permissions on $updated script(s)"
  fi
}

is_git_repo() {
  local path="$1"
  git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1
}

init_git_repo() {
  local project_path="$1"
  if ! has_cmd git; then
    warn "git not found; skipping repository initialization"
    return 0
  fi
  if is_git_repo "$project_path"; then
    info "Existing git repository detected; skipping init"
    return 0
  fi

  ( cd "$project_path" && \
    git init && \
    git add . && \
    git commit -m "Initial commit from Specify template" >/dev/null 2>&1 || true )
  info "Initialized git repository"
}

flatten_if_nested() {
  local path="$1"
  # If path has exactly one top-level directory, move its contents up
  shopt -s dotglob
  local items=("$path"/*)
  shopt -u dotglob
  local count="${#items[@]}"
  if [[ "$count" -eq 1 ]] && [[ -d "${items[0]}" ]]; then
    local nested="${items[0]}"
    local tmp="${path}_tmp_move"
    mv "$nested" "$tmp"
    rm -rf "$path"
    mkdir -p "$path"
    shopt -s dotglob
    mv "$tmp"/* "$path"/
    shopt -u dotglob
    rmdir "$tmp" 2>/dev/null || true
    info "Flattened nested directory structure"
  fi
}

merge_into_current_dir() {
  local src_dir="$1"
  local dest_dir="$2"

  shopt -s dotglob
  for item in "$src_dir"/*; do
    local name="$(basename "$item")"
    local dest_path="$dest_dir/$name"
    if [[ -d "$item" ]]; then
      mkdir -p "$dest_path"
      # Copy/mirror files
      while IFS= read -r -d '' sub; do
        local rel="${sub#"$item"/}"
        local dest_file="$dest_path/$rel"
        mkdir -p "$(dirname "$dest_file")"
        if [[ "$(basename "$dest_file")" == "settings.json" && "$(basename "$(dirname "$dest_file")")" == ".vscode" ]]; then
          # Merge VSCode settings.json
          if [[ -f "$dest_file" ]]; then
            merge_json_files "$dest_file" "$sub" "$dest_file"
          else
            cp -f "$sub" "$dest_file"
          fi
        else
          cp -f "$sub" "$dest_file"
        fi
      done < <(find "$item" -type f -print0)
    else
      if [[ "$name" == "settings.json" && "$(basename "$(dirname "$dest_path")")" == ".vscode" ]]; then
        if [[ -f "$dest_path" ]]; then
          merge_json_files "$dest_path" "$item" "$dest_path"
        else
          mkdir -p "$(dirname "$dest_path")"
          cp -f "$item" "$dest_path"
        fi
      else
        cp -f "$item" "$dest_path"
      fi
    fi
  done
  shopt -u dotglob
}

# ----------------------------
# Args parsing
# ----------------------------

JSON_INPUT=""
if [[ "${1:-}" == "--json" && -n "${2:-}" ]]; then
  JSON_INPUT="$2"
  shift 2
elif [[ -n "${1:-}" ]]; then
  JSON_INPUT="$1"
  shift 1
fi

PROJECT=""
AI=""
SCRIPT_KIND=""
NO_GIT="false"
FORCE="false"
GITHUB_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"

# Try parse JSON via jq; fallback heuristics
if [[ -n "$JSON_INPUT" ]] && has_cmd jq && echo "$JSON_INPUT" | jq -e . >/dev/null 2>&1; then
  PROJECT=$(echo "$JSON_INPUT" | jq -r '.project // empty')
  AI=$(echo "$JSON_INPUT" | jq -r '.ai // empty')
  SCRIPT_KIND=$(echo "$JSON_INPUT" | jq -r '.script // empty')
  NO_GIT=$(echo "$JSON_INPUT" | jq -r '.no_git // false')
  FORCE=$(echo "$JSON_INPUT" | jq -r '.force // false')
  tk=$(echo "$JSON_INPUT" | jq -r '.github_token // empty')
  if [[ -n "$tk" ]]; then GITHUB_TOKEN="$tk"; fi
else
  # Heuristic: treat input as single 'project' value if not JSON-like
  if [[ -n "$JSON_INPUT" && "$JSON_INPUT" != *"{"* ]]; then
    PROJECT="$JSON_INPUT"
  fi
fi

# Defaults
if [[ -z "$PROJECT" ]]; then
  err "Missing 'project' parameter. Provide JSON: {\"project\":\"my-app\",\"ai\":\"copilot\"}"
  exit 1
fi
if [[ -z "$AI" ]]; then
  AI="copilot"
fi
if [[ -z "$SCRIPT_KIND" ]]; then
  SCRIPT_KIND="$(OS_DEFAULT_SCRIPT)"
fi

# Validate AI option (aligned with AGENT_CONFIG keys)
VALID_AIS=("copilot" "claude" "gemini" "cursor-agent" "qwen" "opencode" "codex" "windsurf" "kilocode" "auggie" "codebuddy" "roo" "amp" "shai" "q" "bob")
is_valid_ai="false"
for a in "${VALID_AIS[@]}"; do
  if [[ "$AI" == "$a" ]]; then is_valid_ai="true"; break; fi
done
if [[ "$is_valid_ai" != "true" ]]; then
  err "Invalid 'ai' value: $AI. Choose from: ${VALID_AIS[*]}"
  exit 1
fi

if [[ "$SCRIPT_KIND" != "sh" && "$SCRIPT_KIND" != "ps" ]]; then
  err "Invalid 'script' value: $SCRIPT_KIND. Choose 'sh' or 'ps'"
  exit 1
fi

# Determine target path and mode
HERE="false"
TARGET_DIR=""
if [[ "$PROJECT" == "." ]]; then
  HERE="true"
  TARGET_DIR="$(pwd)"
else
  HERE="false"
  TARGET_DIR="$(pwd)/$PROJECT"
  if [[ -e "$TARGET_DIR" ]]; then
    err "Target directory already exists: $TARGET_DIR"
    exit 1
  fi
fi

# ----------------------------
# Fetch latest release and download asset
# ----------------------------

API_URL="https://api.github.com/repos/github/spec-kit/releases/latest"
AUTH_HEADER=()
if [[ -n "$GITHUB_TOKEN" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer $GITHUB_TOKEN")
fi

info "Fetching latest release information..."
RELEASE_JSON="$(curl -fsSL "${AUTH_HEADER[@]}" "$API_URL")" || {
  err "Failed to fetch release info from GitHub"
  exit 1
}

if ! has_cmd jq; then
  err "jq is required to parse release JSON. Please install jq."
  exit 1
fi

# Find matching asset: name contains "spec-kit-template-{AI}-{SCRIPT_KIND}" and ends with .zip
pattern="spec-kit-template-${AI}-${SCRIPT_KIND}"
ASSET=$(echo "$RELEASE_JSON" | jq -c --arg pat "$pattern" '.assets[] | select((.name|contains($pat)) and (.name|endswith(".zip"))) | .')
if [[ -z "$ASSET" ]]; then
  err "No matching release asset found for pattern '$pattern'"
  echo "Available assets:" >&2
  echo "$RELEASE_JSON" | jq -r '.assets[].name'
  exit 1
fi

FILENAME="$(echo "$ASSET" | jq -r '.name')"
DOWNLOAD_URL="$(echo "$ASSET" | jq -r '.browser_download_url')"
SIZE_BYTES="$(echo "$ASSET" | jq -r '.size')"

info "Found template: $FILENAME ($SIZE_BYTES bytes)"

# Ease 临时产物契约（stage-contract §2.7）：初始化临时目录唯一合法位置
RUN_ID="$(date +%Y%m%d%H%M%S)-$$"
EASE_TMP_DIR="$TARGET_DIR/.eases/.tmp/${RUN_ID}/init-project"
mkdir -p "$EASE_TMP_DIR"
TMPDIR="$EASE_TMP_DIR"
ZIP_PATH="$TMPDIR/$FILENAME"

info "Downloading asset..."
curl -fsSL "${AUTH_HEADER[@]}" -L "$DOWNLOAD_URL" -o "$ZIP_PATH" || {
  err "Failed to download asset"
  rm -rf "$EASE_TMP_DIR"
  # HERE=false 时 TARGET_DIR 由本脚本首次创建，下载失败应清掉空骨架，避免残留
  if [[ "$HERE" == "false" ]]; then
    rm -rf "$TARGET_DIR/.eases"
    rmdir "$TARGET_DIR" 2>/dev/null || true
  fi
  exit 1
}

# ----------------------------
# Extract and place files
# ----------------------------

if [[ "$HERE" == "false" ]]; then
  mkdir -p "$TARGET_DIR"
  extract_zip "$ZIP_PATH" "$TARGET_DIR"
  flatten_if_nested "$TARGET_DIR"
else
  # Extract to temp and merge into current directory
  EXTRACT_DIR="$TMPDIR/extracted"
  mkdir -p "$EXTRACT_DIR"
  extract_zip "$ZIP_PATH" "$EXTRACT_DIR"

  # Detect single nested directory
  shopt -s dotglob
  items=("$EXTRACT_DIR"/*)
  shopt -u dotglob
  SRC_DIR="$EXTRACT_DIR"
  if [[ "${#items[@]}" -eq 1 ]] && [[ -d "${items[0]}" ]]; then
    SRC_DIR="${items[0]}"
  fi

  if [[ "${FORCE}" != "true" ]]; then
    warn "Merging template into non-empty directory may overwrite files. Use force=true to suppress this notice."
  fi
  merge_into_current_dir "$SRC_DIR" "$TARGET_DIR"
fi

# Cleanup contract temp dir (covers zip + extracted tree)
rm -rf "$EASE_TMP_DIR"

# ----------------------------
# POSIX exec bits
# ----------------------------

if [[ "$(OS_DEFAULT_SCRIPT)" == "sh" ]]; then
  ensure_posix_exec_bits "$TARGET_DIR"
fi

# ----------------------------
# Initialize git (optional)
# ----------------------------

if [[ "$NO_GIT" != "true" ]]; then
  init_git_repo "$TARGET_DIR" || true
else
  info "Skipping git initialization (--no_git=true)"
fi

# ----------------------------
# Final & next steps
# ----------------------------

# Agent folder security notice
case "$AI" in
  copilot) agent_folder=".github/";;
  claude) agent_folder=".claude/";;
  gemini) agent_folder=".gemini/";;
  cursor-agent) agent_folder=".cursor/";;
  qwen) agent_folder=".qwen/";;
  opencode) agent_folder=".opencode/";;
  codex) agent_folder=".codex/";;
  windsurf) agent_folder=".windsurf/";;
  kilocode) agent_folder=".kilocode/";;
  auggie) agent_folder=".augment/";;
  codebuddy) agent_folder=".codebuddy/";;
  roo) agent_folder=".roo/";;
  amp) agent_folder=".agents/";;
  shai) agent_folder=".shai/";;
  q) agent_folder=".amazonq/";;
  bob) agent_folder=".bob/";;
  *) agent_folder="";;
esac

echo
echo "==============================================="
echo "Project ready."
echo "Target: $TARGET_DIR"
echo "AI Assistant: $AI"
echo "Script Type: $SCRIPT_KIND"
echo "==============================================="
echo

if [[ -n "$agent_folder" ]]; then
  echo "Security notice: Consider adding '$agent_folder' (or parts of it) to .gitignore to avoid committing credentials."
  echo
fi

step=1
if [[ "$HERE" == "false" ]]; then
  echo "$step. cd \"$TARGET_DIR\""
  step=$((step+1))
else
  echo "$step. Already in project directory"
  step=$((step+1))
fi
echo "$step. Start using slash commands:"
echo "   - /ease.constitution"
echo "   - /ease.specify"
echo "   - /ease.plan"
echo "   - /ease.tasks"
echo "   - /ease.implement"

# Success
exit 0
