#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
TEMP_DIR="$ROOT/.share_tmp"
OUT_DIR="$ROOT/share_bundle"
ARCHIVE="$ROOT/smart-mail-agent-full-$(date +%F-%H%M).tar.gz"

echo "[1/5] 準備目錄"
rm -rf "$TEMP_DIR" "$OUT_DIR" "$ARCHIVE"
mkdir -p "$OUT_DIR"

echo "[2/5] 複製專案（排除 .git / .venv / __pycache__ / tmp / logs/*.log / *.pkl）"
# 若有 rsync 用 rsync；沒有就用 tar 解決
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude ".git" \
    --exclude ".venv" \
    --exclude "__pycache__" \
    --exclude "tmp" \
    --exclude "logs/*.log" \
    --exclude "*.pkl" \
    ./ "$OUT_DIR/"
else
  mkdir -p "$TEMP_DIR"
  tar -cf "$TEMP_DIR/src.tar" \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="tmp" \
    --exclude="logs/*.log" \
    --exclude="*.pkl" \
    .
  tar -xf "$TEMP_DIR/src.tar" -C "$OUT_DIR"
fi

echo "[3/5] 處理 .env（自動遮蔽祕密；若沒有就略過）"
if [ -f "$ROOT/.env" ]; then
  sed -E 's/(OPENAI_API_KEY|SMTP_PASS|IMAP_PASS|GH_TOKEN)=.*/\1=***REDACTED***/' "$ROOT/.env" > "$OUT_DIR/.env"
fi

echo "[4/5] 打包壓縮"
tar -czf "$ARCHIVE" -C "$OUT_DIR/.." "$(basename "$OUT_DIR")"

echo "[5/5] 完成"
echo "==> 產生：$ARCHIVE"
echo "提示：直接把這個 .tar.gz 檔拖到聊天室上傳即可"
