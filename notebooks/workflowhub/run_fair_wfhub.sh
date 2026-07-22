#!/bin/bash
# Fetch FAIR evaluations from WorkflowHub and generate the UpSet plot.
#
# Usage:
#   ./run_fair_wfhub.sh [--limit N] [--output PREFIX]
#
# Options:
#   --limit N       Only process the first N workflows (default: all)
#   --output PREFIX Base name for CSV and plot files (default: wfhub-fc_evals)
#
# Examples:
#   ./run_fair_wfhub.sh
#   ./run_fair_wfhub.sh --limit 100 --output wfhub-fc_evals-test

set -euo pipefail

LIMIT=""
OUTPUT="wfhub-fc_evals"

while [[ $# -gt 0 ]]; do
    case $1 in
        --limit)  LIMIT="$2";  shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

CSV="${OUTPUT}.csv"
FETCH_ARGS="--output ${CSV}"
[ -n "$LIMIT" ] && FETCH_ARGS="${FETCH_ARGS} --limit ${LIMIT}"

echo "=== Step 1: FAIR assessment ==="
# --no-capture-output: without it, `conda run` buffers the subprocess's
# stdout/stderr and only flushes it once the process exits, so the progress
# bar and logs would appear all at once instead of updating live
conda run --no-capture-output -n visu python fetch_wfhub_fair_evals.py ${FETCH_ARGS}

echo ""
echo "=== Step 2: UpSet plot ==="
conda run --no-capture-output -n visu python upset_plot.py --input "${CSV}" --output "${OUTPUT}"

echo ""
echo "Done. Results: ${CSV}, ${OUTPUT}.pdf, ${OUTPUT}.png"
