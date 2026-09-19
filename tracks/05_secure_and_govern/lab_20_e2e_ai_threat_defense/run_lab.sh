#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$LAB_DIR/../../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="${PYTHON_FALLBACK:-python3}"

cd "$REPO_ROOT"
export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"

echo "Running lab: $(basename "$LAB_DIR")"
"$PYTHON_BIN" "$LAB_DIR/lab.py" "$@"

echo
echo "Running lab tests"
"$PYTHON_BIN" -m pytest "$LAB_DIR/tests" -q

echo
echo "Done. Run $LAB_DIR/cleanup.sh when finished."
