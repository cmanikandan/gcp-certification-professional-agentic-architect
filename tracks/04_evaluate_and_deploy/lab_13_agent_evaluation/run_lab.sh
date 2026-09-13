#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$LAB_DIR/../../.." && pwd)"
# Prefer, in order: an activated virtualenv, the repo's .venv, the development
# .venv-adk, then whatever python3 is on PATH.
if [[ -n "${PYTHON_BIN:-}" ]]; then
  :
elif [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
  PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv/bin/python"
elif [[ -x "$REPO_ROOT/.venv-adk/bin/python" ]]; then
  PYTHON_BIN="$REPO_ROOT/.venv-adk/bin/python"
else
  PYTHON_BIN="python3"
fi

cd "$REPO_ROOT"
export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"

echo "Running lab: $(basename "$LAB_DIR")"
"$PYTHON_BIN" "$LAB_DIR/lab.py" "$@"

if [[ " ${@:-} " =~ " --live " ]]; then
    # Run the adk eval CLI command
    echo "Running adk eval command..."
    "$REPO_ROOT/.venv-adk/bin/adk" eval "$LAB_DIR/agent.py" "$LAB_DIR/.evalset.json" --config_file_path "$LAB_DIR/config.json"
fi

echo
echo "Running lab tests"
"$PYTHON_BIN" -m pytest "$LAB_DIR/tests" -q

echo
echo "Done. Run $LAB_DIR/cleanup.sh when finished."
