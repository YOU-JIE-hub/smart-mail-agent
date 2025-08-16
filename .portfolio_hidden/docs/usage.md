# Quickstart

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"

# CLI
sma --help
sma-run --help
sma-spamcheck --help

# 測試（離線）
PYTHONPATH=. pytest -q tests -k "not online"
