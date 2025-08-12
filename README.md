# Smart Mail Agent

可離線運行的郵件處理/自動化專案：
- 意圖分類（離線 stub；可切換 Hugging Face / OpenAI）
- 垃圾信/白名單 Orchestrator（規則 + 動作）
- 報價單 PDF（缺字型自動回退 Helvetica）
- CLI：python -m src.run_action_handler
- 離線測試全綠

## 快速開始
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"
```

## 執行 CLI
```bash
PYTHONPATH=src python -m src.run_action_handler --help
```

## 品質檢查
```bash
python -m isort .
python -m black .
python -m flake8
```


## 下載區（可直接交付）
[![Download](https://img.shields.io/github/v/release/YOU-JIE-hub/smart-mail-agent?display_name=tag&sort=semver)](https://github.com/YOU-JIE-hub/smart-mail-agent/releases/latest)

- 最新離線 Demo 報告（HTML）：`reports/offline_demo_report.html`
- 一鍵展示 ZIP（Release 資產）：到 **Releases → 最新版本** 下載。
