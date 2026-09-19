#!/usr/bin/env bash
# Run the whole test suite: the repo-wide guards, then every lab's own tests.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "======================================================================"
echo "  Repo guards — authoring contract and stale-fact checks"
echo "======================================================================"
python3 -m pytest tests/ -v

echo ""
echo "======================================================================"
echo "  Lab tests — all 20 labs"
echo "======================================================================"
python3 -m pytest tracks/ -v --durations=10

echo ""
echo "======================================================================"
echo "  All test suites passed."
echo "======================================================================"
