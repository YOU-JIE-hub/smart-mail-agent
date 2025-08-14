#!/usr/bin/env bash
set -Eeuo pipefail
. .venv/bin/activate 2>/dev/null || true
export PYTHONPATH=src:${PYTHONPATH:-}
export OFFLINE=${OFFLINE:-1}
bin/smarun
tools/show_summary.sh
