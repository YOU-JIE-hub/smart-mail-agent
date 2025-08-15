# Contributing
- 建議使用 Python 3.10，啟動虛擬環境後：`pip install -e ".[dev]"`.
- 送 PR 前：`ruff check . && ruff format --check . && PYTHONPATH=. pytest -q tests -k "not online"`.
- PR 請描述改動、風險、測試方式；如涉及資料/私密設定請提供 mock。
