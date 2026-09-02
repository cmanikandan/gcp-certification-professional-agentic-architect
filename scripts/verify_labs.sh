#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for module_dir in "$REPO_ROOT"/modules/[0-9][0-9]_*; do
  [[ -x "$module_dir/run_lab.sh" ]] || {
    echo "Missing executable run_lab.sh: $module_dir" >&2
    exit 1
  }
  [[ -x "$module_dir/cleanup.sh" ]] || {
    echo "Missing executable cleanup.sh: $module_dir" >&2
    exit 1
  }
  "$module_dir/run_lab.sh"
  "$module_dir/cleanup.sh"
done

echo "All module run and cleanup contracts passed."
