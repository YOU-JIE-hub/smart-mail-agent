[![coverage](https://img.shields.io/codecov/c/github/YOU-JIE-hub/smart-mail-agent?logo=codecov)](https://app.codecov.io/gh/YOU-JIE-hub/smart-mail-agent)
![Build](https://github.com/YOU-JIE-hub/smart-mail-agent/actions/workflows/tests.yml/badge.svg) ![Coverage](https://codecov.io/gh/YOU-JIE-hub/smart-mail-agent/branch/main/graph/badge.svg)
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

---

### Quickstart

```bash
# 1) 安裝
python -m pip install -U pip
python -m pip install -e ".[dev]"

# 2) CLI
sma --help
sma-run --help
sma-spamcheck --help

# 3) 測試（離線）
PYTHONPATH=. pytest -q tests -k "not online"
'

## Project structure

```text
.
├─ src/smart_mail_agent/        # 主程式（單一命名空間）
├─ tests/                       # 測試（CI 預設跑離線集）
├─ docs/                        # MkDocs 文件（gh-pages 自動部署）
├─ scripts/bin/                 # CLI/工具腳本（可執行）
├─ configs/                     # 設定與範例
├─ .github/                     # Actions / Issue & PR 模板
├─ pyproject.toml               # 打包/依賴/工具設定
├─ mkdocs.yml                   # 文件設定
├─ README.md LICENSE            # 說明與授權
├─ tools/run_actions_matrix.py  # 測試相容 shim
└─ (de-emphasized)
   ├─ .dev/                     # 只給開發者用的腳本與輔助工具
   └─ .archive/                 # 歷史資產（legacy、封包、備份）
```

> **Portfolio clean branch**：僅保留核心 src / tests / configs / scripts / tools。
> 其他開發資產已移到 `.portfolio_hidden/`（完整版本請看 `main` 分支）。

