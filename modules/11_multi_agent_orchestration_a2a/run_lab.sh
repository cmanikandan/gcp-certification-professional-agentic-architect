#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$LAB_DIR/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_FALLBACK:-python3}"
fi

echo "Running demo: 11_multi_agent_orchestration_a2a"
"$PYTHON_BIN" "$LAB_DIR/multi_agent_system.py"
echo "Running module tests"
"$PYTHON_BIN" -m pytest "$LAB_DIR/tests" -q
echo "Lab complete. Run $LAB_DIR/cleanup.sh when finished."
