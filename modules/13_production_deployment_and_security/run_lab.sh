#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$LAB_DIR/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_FALLBACK:-python3}"
fi

echo "Running demo: 13_production_deployment_and_security"
"$PYTHON_BIN" "$LAB_DIR/security_guardrails.py"
echo "Running module tests"
"$PYTHON_BIN" -m pytest "$LAB_DIR/tests" -q
echo "Lab complete. Run $LAB_DIR/cleanup.sh when finished."
