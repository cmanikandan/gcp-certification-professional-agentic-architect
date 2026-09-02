#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# This default teardown is intentionally local and idempotent. The offline lab
# provisions no cloud resources. Any optional live resources must be deleted
# with the exact commands and identifiers documented in this module's README.
find "$LAB_DIR" -type d -name __pycache__ -prune -exec rm -rf -- {} +
if [[ -d "$LAB_DIR/.pytest_cache" ]]; then
  rm -rf -- "$LAB_DIR/.pytest_cache"
fi
find "$LAB_DIR" -maxdepth 2 -type f \( -name '*.log' -o -name '*.tmp' -o -name '*.cache' \) -delete

echo "Cleanup complete for 04_optimizing_agent_behavior; no default lab cloud resources exist."
