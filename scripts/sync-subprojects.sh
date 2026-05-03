#!/usr/bin/env bash
# Sync subprojects from solo-leveling monorepo to external local repos.
# Run from the solo-leveling repo root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

declare -A MAP=(
  ["subprojects/dashboard"]="/Users/macmini/Documents/projects/dashboard"
  ["subprojects/wedding-invitation"]="/Users/macmini/Documents/projects/wedding-invitation"
  ["subprojects/koperasi-landing"]="/Users/macmini/Documents/projects/koperasi"
)

for src in "${!MAP[@]}"; do
  dst="${MAP[$src]}"
  src_path="$REPO_ROOT/$src"

  if [ ! -d "$src_path" ]; then
    echo "SKIP: $src_path does not exist"
    continue
  fi

  if [ ! -d "$dst" ]; then
    echo "SKIP: $dst does not exist"
    continue
  fi

  echo "SYNC: $src -> $dst"
  rsync -av --exclude='.git' --delete "$src_path/" "$dst/"

done

echo "Done. Review changes in each target repo before committing."
