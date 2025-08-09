#!/bin/bash

cd "$(dirname "$0")/.."
source .venv/bin/activate

echo "[CronJob] 啟動 Smart-Mail-Agent pipeline"
python pipeline/main.py >> logs/cron_pipeline.log 2>&1
