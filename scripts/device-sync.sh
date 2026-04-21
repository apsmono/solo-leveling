#!/usr/bin/env bash
set -euo pipefail

# One-command helper for cross-device continuity.
# Usage:
#   ./scripts/device-sync.sh switch-out
#   ./scripts/device-sync.sh switch-in
#   ./scripts/device-sync.sh bootstrap-prompt

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-help}"

read_targets() {
  cat <<'EOF'
1) README.md
2) AI_CONTEXT.md
3) AGENTS.md
4) docs/ai-working-notes.md
5) docs/ai-knowledge/continuation-plan.md
EOF
}

bootstrap_prompt() {
  cat <<'EOF'
Continue as Monitor AI for this repo.
Assume strict continuity mode.
Read and obey:
- README.md
- AI_CONTEXT.md
- AGENTS.md
- docs/ai-working-notes.md
- docs/ai-knowledge/continuation-plan.md

Then return only:
1) current task state
2) next 3 executable actions
3) risks/blockers
4) first command you will run
EOF
}

case "$MODE" in
  switch-out)
    echo "== Device Switch-Out Checklist =="
    echo "Repository: $ROOT_DIR"
    echo
    echo "[1/5] Timestamp"
    date "+%Y-%m-%d %H-%M-%S"
    echo
    echo "[2/5] Git state"
    git fetch --all --prune
    git status -sb
    echo
    echo "[3/5] Required before leaving device"
    echo "- Commit and push your intended changes."
    echo "- Update docs/ai-working-notes.md with done/in-progress/next/blockers."
    echo "- Update AI_CONTEXT.md only if priorities changed."
    echo "- Update CHANGELOG.md for notable changes."
    echo
    echo "[4/5] Quick reminder"
    echo "Run on next device: ./scripts/device-sync.sh switch-in"
    echo
    echo "[5/5] Startup prompt for next device"
    bootstrap_prompt
    ;;

  switch-in)
    echo "== Device Switch-In =="
    echo "Repository: $ROOT_DIR"
    echo
    echo "[1/4] Git sync"
    git fetch --all --prune
    if [[ -z "$(git status --porcelain)" ]]; then
      git pull --ff-only
    else
      echo "Working tree has local changes; skipped auto-pull."
      echo "Review with: git status -sb"
    fi
    git status -sb
    echo
    echo "[2/4] Read in this exact order"
    read_targets
    echo
    echo "[3/4] Startup prompt"
    bootstrap_prompt
    echo
    echo "[4/4] Ready"
    echo "Paste the prompt above into Copilot Chat on this device."
    ;;

  bootstrap-prompt)
    bootstrap_prompt
    ;;

  help|--help|-h|*)
    cat <<'EOF'
Cross-device continuity helper

Usage:
  ./scripts/device-sync.sh switch-out       # Finish current device session
  ./scripts/device-sync.sh switch-in        # Start on other device
  ./scripts/device-sync.sh bootstrap-prompt # Print startup prompt only
EOF
    ;;
esac
