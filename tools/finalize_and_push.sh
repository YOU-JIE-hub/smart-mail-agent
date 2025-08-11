#!/usr/bin/env bash
set -euo pipefail

# 0) 進入 repo 根目錄
cd "$(dirname "$0")/.." || exit 1

echo "==> 1) 檢查/建立 venv & 升級 pip"
test -d .venv || python -m venv .venv
. .venv/bin/activate
python -m pip -q install -U pip

echo "==> 2) 安裝必要套件（含 dev）"
pip -q install -r requirements.txt || true
pip -q install -U pytest black isort flake8 python-dotenv

echo "==> 3) 統一格式 & Lint（不通過就中止）"
python -m isort .
python -m black .
python -m flake8

echo "==> 4) 跑離線測試（與 CI 同步集合）"
export OFFLINE=1
PYTHONPATH=src pytest -q -k "not online"

echo "==> 5) 自動 commit & push（若有變更）"
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  git commit -m "chore: format+lint; offline tests green (finalize_and_push)"
  git push
else
  echo "沒有需要提交的變更，跳過 commit/push"
fi

echo "==> 完成 ✅"
