    0 * * * * cd $HOME/projects/smart-mail-agent && . .venv/bin/activate && OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --tasks classify >> logs/cron.log 2>&1

# Smart Mail Agent

一個可離線驗證的 AI + RPA 郵件處理範例專案。

快速連結：
- [Architecture](architecture.md)
- [Cookbook](cookbook.md)
[![tests](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml)
![coverage](https://raw.githubusercontent.com/YOU-JIE-hub/smart-mail-agent/main/badges/coverage.svg?t=1755671581)



**離線展示：**
```bash
scripts/demo_offline.sh

## 使用說明（統一入口）

1. 建立與啟用虛擬環境：
   ```bash
   python3 -m venv .venv && . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 設定環境檔 `.env`（可參考 `.env.example`）：
   - NOTO_FONT_PATH、PDF_FONT_FALLBACK：中文 PDF 字型路徑
   - SMTP_HOST、SMTP_PORT、SMTP_USER、SMTP_PASS、MAIL_FROM：SMTP 寄信設定
   - OUTPUT_DIR：輸出資料夾（PDF、附件）

3. 執行主流程（單一入口）：
   ```bash
   bin/smarun --help
   # 或
   python -m src.run_action_handler --help
   ```

## CI

專案已提供 `.github/workflows/ci.yml`，push 或 PR 會自動跑 pytest 與覆蓋率報告。
