#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob
OUT_DIR="data/output"
files=("$OUT_DIR"/out_*.json)
[ ${#files[@]} -eq 0 ] && echo "未找到輸出於 ${OUT_DIR}" >&2 && exit 1
for f in "${files[@]}"; do
  echo "==== $(basename "$f") ===="
  if command -v jq >/dev/null 2>&1; then
    jq '{action, label:.predicted_label, confidence, dry_run, meta, logged_path}' "$f" 2>/dev/null || cat "$f"
  else
    head -n 80 "$f"
  fi
done
