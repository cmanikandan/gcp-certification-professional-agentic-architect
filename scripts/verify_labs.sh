#!/usr/bin/env bash
# Verify that every lab honours the authoring contract:
#   - run_lab.sh and cleanup.sh exist and are executable
#   - the lab runs to completion offline, with no credentials
#   - cleanup is safe to run immediately afterwards
#
# This is what CI runs. If a lab needs a Google Cloud project to pass, that is a
# bug in the lab: the offline path is mandatory.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Make sure nothing accidentally takes the live path.
unset GOOGLE_APPLICATION_CREDENTIALS GOOGLE_API_KEY GEMINI_API_KEY || true

total=0
failed=0
failed_labs=()

for lab_dir in "$REPO_ROOT"/tracks/[0-9][0-9]_*/lab_[0-9][0-9]_*; do
  [[ -d "$lab_dir" ]] || continue
  lab_name="$(basename "$lab_dir")"
  total=$((total + 1))

  echo ""
  echo "──────────────────────────────────────────────────────────────────────"
  echo "  $lab_name"
  echo "──────────────────────────────────────────────────────────────────────"

  missing=0
  for script in run_lab.sh cleanup.sh; do
    if [[ ! -f "$lab_dir/$script" ]]; then
      echo "  MISSING  $script" >&2
      missing=1
    elif [[ ! -x "$lab_dir/$script" ]]; then
      echo "  NOT EXECUTABLE  $script  (run: chmod +x $lab_dir/$script)" >&2
      missing=1
    fi
  done

  if [[ $missing -eq 1 ]]; then
    failed=$((failed + 1))
    failed_labs+=("$lab_name (contract)")
    continue
  fi

  if ! "$lab_dir/run_lab.sh"; then
    echo "  FAILED  run_lab.sh" >&2
    failed=$((failed + 1))
    failed_labs+=("$lab_name (run)")
    continue
  fi

  if ! "$lab_dir/cleanup.sh"; then
    echo "  FAILED  cleanup.sh" >&2
    failed=$((failed + 1))
    failed_labs+=("$lab_name (cleanup)")
    continue
  fi

  echo "  OK"
done

echo ""
echo "======================================================================"
if [[ $failed -eq 0 ]]; then
  echo "  All $total labs passed the run and cleanup contract."
  echo "======================================================================"
  exit 0
fi

echo "  $((total - failed))/$total labs passed. Failures:"
for entry in "${failed_labs[@]}"; do
  echo "    - $entry"
done
echo "======================================================================"
exit 1
