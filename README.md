<!-- BADGES START -->
[![Build](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/build.yml/badge.svg)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/build.yml) [![Tests](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml) ![coverage](assets/badges/coverage.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
<!-- BADGES END -->
[![tests](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

# Smart Mail Agent

最小可演示的郵件自動化專案（離線可驗證）。已整理結構、提供 CLI 與離線測試，適合面試展示。

## 結構
- `src/smart_mail_agent/`：核心與功能模組（routing / features / observability / spam）
- `src/`：向後相容 shims
- `tests/`：單元與離線測試
- `.github/workflows/tests.yml`：CI（main / showcase / hardening）

## 安裝與測試（離線）
1. 建立虛擬環境並安裝：
   - `python -m venv .venv && . .venv/bin/activate`
   - `python -m pip install -U pip`
   - `pip install -e . || pip install -r requirements.txt`
2. 執行離線測試：
   - `OFFLINE=1 PYTHONPATH=".:src" pytest -q tests -k "not online" --timeout=60 --timeout-method=thread`

## CLI
- 初始化統計資料庫（stdout: 資料庫初始化完成）  
  `python src/stats_collector.py --init`
- 新增統計（stdout: 已新增統計紀錄）  
  `python src/stats_collector.py --label 投訴 --elapsed 0.56`

## PDF 中文字型
- 將 `NotoSansTC-Regular.ttf` 放在 `assets/fonts/`  
- 或在 `.env` 設：`FONT_TTC_PATH=assets/fonts/NotoSansTC-Regular.ttf`
