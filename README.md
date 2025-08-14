# Smart Mail Agent

![CI](https://img.shields.io/github/actions/workflow/status/YOU-JIE-hub/smart-mail-agent/ci.yml?branch=main) ![License](https://img.shields.io/badge/license-MIT-green)


單一命名空間 `smart_mail_agent`，保留並相容既有主流程（`python -m src.run_action_handler`）。
本倉庫已提供零互動一鍵腳本完成初始化、封裝與 CLI 安裝。

## CLI
- `sma`：等同 `python -m smart_mail_agent`（轉呼叫舊主流程）
- `sma-run`：顯式呼叫 `python -m src.run_action_handler`
- `sma-spamcheck --subject ... --content ... [--sender ...]`：垃圾信檢查包裝器

若需 PDF 中文字型，請放置 `assets/fonts/NotoSansTC-Regular.ttf` 或設定 `.env` 的 `FONT_PATH`。

## 一鍵操作（本地零互動）
```bash
make install && make build
```

## Docker
```bash
docker build -t smart-mail-agent:local .
docker run --rm smart-mail-agent:local
```

## 設定檔
- 預設會讀取 `.env` 與 `configs/default.yml`。
- 字型：放在 `assets/fonts/` 或設定 `FONT_PATH`。
