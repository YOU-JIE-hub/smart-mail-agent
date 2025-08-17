# Smart Mail Agent

[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://YOU-JIE-hub.github.io/smart-mail-agent/) [![CI](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python](https://img.shields.io/badge/python-3.10%20|%203.11-blue)

[![CI](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Python](https://img.shields.io/badge/python-3.10%20|%203.11-blue)

面向企業展示的 AI + RPA 郵件自動化專案：結合 NLP/LLM 與流程自動化，離線可跑、CLI 一鍵驗證，涵蓋垃圾郵件過濾、意圖分類、動作路由（報價 PDF、FAQ 回覆、工單建立、銷售通知）、統計與日誌。

## 核心特性
- 垃圾郵件多層過濾（規則、ML、LLM）
- 意圖分類與路由：技術支援、資料修改、流程詢問、抱怨投訴、商務報價、其他
- 自動動作：產生 PDF、寄信回覆、紀錄與統計
- 觀測與日誌：統一結構化輸出
- CLI 友善：本地離線 Demo 與自動測試
- 工程化：pre-commit、pytest、CI、版本標籤

## 專案結構（重點目錄）
src/smart_mail_agent/ 下：
- actions/：行為集合（如銷售報價）
- cli/：CLI 進入點
- features/：高階功能（apply_diff、spam 等）
- ingestion/：資料庫初始化與郵件擷取
- routing/：路由與主流程
- spam/：spam 規則、模型與編排
- utils/：共用工具（logger、pdf、db_tools ...）
tests/：pytest 測試
.github/workflows/：CI 工作流

## 安裝與快速開始
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e .
pip install -U pytest pytest-cov pre-commit ruff black isort
pre-commit install
cp -n .env.example .env

## 環境變數（.env）
OFFLINE=1
LOG_LEVEL=INFO
SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS/SMTP_FROM/SMTP_TLS/SMTP_SSL
NOTO_FONT_PATH=assets/fonts/NotoSansTC-Regular.ttf
PDF_FONT_FALLBACK=1

## 常用 CLI
python -m smart_mail_agent.cli_spamcheck --subject "免費中獎" --body "恭喜獲得獎金"
OFFLINE=1 python -m smart_mail_agent.routing.run_action_handler --input data/sample/email.json

## 測試與品質
pytest -q
pre-commit run -a

## 授權
MIT License（見 LICENSE）
