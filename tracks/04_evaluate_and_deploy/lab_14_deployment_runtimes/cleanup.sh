#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

find "$LAB_DIR" -type d -name __pycache__ -prune -exec rm -rf -- {} +
rm -rf -- "$LAB_DIR/.pytest_cache"
find "$LAB_DIR" -maxdepth 2 -type f \
  \( -name '*.log' -o -name '*.tmp' -o -name '*.session.json' \) -delete

echo "Local cleanup complete for $(basename "$LAB_DIR")."
echo "The offline lab provisions no cloud resources."
echo "If you ran --live, see section 9 of this lab's README for teardown."
