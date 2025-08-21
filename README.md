![coverage](badges/coverage.svg)
![CI](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg)
![type](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/typecheck.yml/badge.svg)
![tag](https://img.shields.io/github/v/tag/YOU-JIE-hub/smart-mail-agent?sort=semver)
![release](https://img.shields.io/github/v/release/YOU-JIE-hub/smart-mail-agent?include_prereleases)
![lint](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/lint.yml/badge.svg)
<p align="left">
  <a href="https://github.com/YOU-JIE-hub/smart-mail-agent/actions"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/YOU-JIE-hub/smart-mail-agent/tests.yml?branch=hardening/pro-release-20250821-060514&label=CI"></a>
  <a href="https://github.com/YOU-JIE-hub/smart-mail-agent/actions"><img alt="Lint" src="https://img.shields.io/github/actions/workflow/status/YOU-JIE-hub/smart-mail-agent/lint.yml?branch=hardening/pro-release-20250821-060514&label=lint"></a>
  <a href="https://github.com/YOU-JIE-hub/smart-mail-agent/actions"><img alt="Type Check" src="https://img.shields.io/github/actions/workflow/status/YOU-JIE-hub/smart-mail-agent/typecheck.yml?branch=hardening/pro-release-20250821-060514&label=type"></a>
  <a href="badges/coverage.svg"><img alt="Coverage" src="badges/coverage.svg"></a>
  <a href="https://github.com/YOU-JIE-hub/smart-mail-agent/releases"><img alt="Release" src="https://img.shields.io/github/v/tag/YOU-JIE-hub/smart-mail-agent?sort=semver&display_name=tag"></a>
</p>

## 使用說明（統一入口）

1. 建立與啟用虛擬環境：
   ```bash
   python3 -m venv .venv && . .venv/bin/activate
   pip install -r requirements.txt
   ```

2. 設定 `.env`（可參考 `.env.example`）：
   - NOTO_FONT_PATH、PDF_FONT_FALLBACK：中文 PDF 字型路徑（必要時自備字型檔放入 assets/fonts/）
   - SMTP_HOST、SMTP_PORT、SMTP_USER、SMTP_PASS、MAIL_FROM：SMTP 寄信設定
   - OUTPUT_DIR：輸出資料夾（PDF、附件）

3. 執行主流程：
   ```bash
   bin/smarun --help
   # 或
   python -m src.run_action_handler --help
   ```

## CI

已提供 `.github/workflows/ci.yml`，push/PR 會自動執行 pytest 與覆蓋率報告。
