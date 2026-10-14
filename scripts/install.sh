#!/usr/bin/env bash
# Copy the whole suite, including shared resources, to a skill discovery root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
case "${1:-project}" in
  project) DEST="${PWD}/.dsh/skills" ;;
  user) DEST="${HOME}/.dsh/skills" ;;
  *) echo "usage: $0 [project|user]" >&2; exit 1 ;;
esac
python3 "$ROOT/scripts/install.py" "$DEST"
echo "Skills installed. Colon commands additionally require the runtime overlay; see README.md."
