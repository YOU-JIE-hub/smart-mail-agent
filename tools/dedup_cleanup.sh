#!/usr/bin/env bash
# 去重 + 瘦身 + 基本工具化（僅搬檔/刪產物，不改你的業務邏輯）
set +e
set -u

cd "$(dirname "$0")/.." || exit 1

STAMP="$(date +%Y%m%d-%H%M%S)"
BK="backup_dedup_${STAMP}"
mkdir -p "${BK}"

echo "=== [1/6] 備份可能要移除/替換的檔案 ==="
for p in \
  share_bundle \
  run_pipeline.sh \
  init_db.py \
  README.md
do
  if [ -e "$p" ]; then
    mkdir -p "${BK}/$(dirname "$p")"
    mv "$p" "${BK}/$p"
    echo "moved: $p -> ${BK}/$p"
  fi
done

echo "=== [2/6] 去重與清理（不動邏輯程式） ==="
# 2-1) 移除重複目錄
rm -rf share_bundle 2>/dev/null || true

# 2-2) 清理大檔/產物（單條加 || true，避免因不存在而中斷）
rm -f assets/fonts/*.ttf 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
rm -rf htmlcov .coverage* coverage.xml 2>/dev/null || true
rm -rf logs/* 2>/dev/null || true
rm -rf data/output/* 2>/dev/null || true
rm -f smart-mail-agent-*.tar.gz smart-mail-agent-*.tgz 2>/dev/null || true
# 用 find 刪 __pycache__，不會回非 0
find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null

echo "=== [3/6] 強化 .gitignore（避免之後又長肥檔） ==="
add_ignore() { grep -qxF "$1" .gitignore 2>/dev/null || echo "$1" >> .gitignore; }
add_ignore "# --- dedup cleanup ($(date)) ---"
add_ignore "share_bundle/"
add_ignore "assets/fonts/*.ttf"
add_ignore "logs/"
add_ignore "src/logs/"
add_ignore "*.log"
add_ignore "htmlcov/"
add_ignore ".coverage*"
add_ignore ".pytest_cache/"
add_ignore "data/output/"

echo "=== [4/6] 產生 Makefile 常用指令（可覆蓋） ==="
cat > Makefile <<'MAKE'
.PHONY: help install format lint test-offline clean-light clean-heavy tools-check-log tools-list-folders tools-online-check

help:
	@echo "make install        - 建 venv + 安裝開發套件"
	@echo "make format         - isort + black"
	@echo "make lint           - flake8（不擋）"
	@echo "make test-offline   - OFFLINE=1，僅 not online 測試"
	@echo "make clean-light    - 清快取/覆蓋/輸出（安全）"
	@echo "make clean-heavy    - 連 pip/hf 快取一起清（更省空間）"
	@echo "make tools-check-log     - 檢視最近 20 筆 emails_log"
	@echo "make tools-list-folders  - 列 IMAP 資料夾（OFFLINE=1 會 SKIP）"
	@echo "make tools-online-check  - 線上 smoke（需 SMTP/IMAP 環境）"

install:
	python -m venv .venv || true
	. .venv/bin/activate; \
	pip install -U pip; \
	pip install -r requirements.txt || true; \
	pip install -U pytest black isort flake8 python-dotenv

format:
	. .venv/bin/activate; python -m isort .; python -m black .

lint:
	. .venv/bin/activate; python -m flake8 || true

test-offline:
	. .venv/bin/activate; OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"

clean-light:
	rm -rf .pytest_cache || true
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage* coverage.xml logs/* data/output/* || true

clean-heavy: clean-light
	python -m pip cache purge || true
	rm -rf ~/.cache/pip ~/.cache/huggingface ~/.cache/torch || true

tools-check-log:
	. .venv/bin/activate; PYTHONPATH=src python scripts/check_email_log.py --limit 20

tools-list-folders:
	. .venv/bin/activate; PYTHONPATH=src python scripts/list_gmail_folders.py

tools-online-check:
	. .venv/bin/activate; PYTHONPATH=src python scripts/online_check.py
MAKE

echo "=== [5/6]（可選）離線自測：若系統有 pytest 就跑；不會中斷 ==="
if command -v python >/dev/null 2>&1; then
  [ -d .venv ] && . .venv/bin/activate
  export OFFLINE=1
  python -c "import pytest" >/dev/null 2>&1 && PYTHONPATH=src pytest -q -k "not online" || echo "(略過 pytest)"
fi

echo "=== [6/6] 完成；所有被動到的檔已備份在：${BK} ==="
