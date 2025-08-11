#!/bin/bash

# 進入腳本所在目錄
cd "$(dirname "$0")"

# 檢查 logs 目錄
mkdir -p logs

# 檢查虛擬環境存在
if [ ! -f ".venv/bin/activate" ]; then
  echo "[Pipeline] 找不到 .venv 虛擬環境，請先建立" >> logs/pipeline.log
  exit 1
fi

# 啟動虛擬環境
source .venv/bin/activate

# 記錄開始時間
echo "[Pipeline] 啟動 $(date "+%F %T")" >> logs/pipeline.log

# 執行主流程
python pipeline/main.py >> logs/pipeline.log 2>&1
EXIT_CODE=$?

# 記錄結束狀態
if [ $EXIT_CODE -eq 0 ]; then
  echo "[Pipeline] 成功結束 $(date "+%F %T")" >> logs/pipeline.log
else
  echo "[Pipeline] 執行失敗（代碼 $EXIT_CODE）於 $(date "+%F %T")" >> logs/pipeline.log
fi
