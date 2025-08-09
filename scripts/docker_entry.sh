#!/usr/bin/env bash
set -euo pipefail

# OFFLINE=1 時，跳過外部抓取（例如 HF 下載）
export OFFLINE=${OFFLINE:-1}
export PYTHONPATH=src

echo "[entry] OFFLINE=$OFFLINE"
python init_db.py
python scripts/run_all.py || true
python scripts/check_email_log.py || true
