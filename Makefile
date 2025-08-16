.PHONY: help lint test test-offline test-online cov-offline demo-send

help: ## 列出可用目標
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed -E 's/:.*?##/: /' | sort

lint: ## ruff 稽核（使用 .ruff.toml）
	ruff check .

test: test-offline ## 等同 test-offline

test-offline: ## 跑整包離線測試（不會連網）；CI 預設跑這個
	OFFLINE=1 PYTHONPATH=".:src" pytest -q

cov-offline: ## 產 XML 覆蓋率（離線）
	OFFLINE=1 PYTHONPATH=".:src" pytest -q --cov=src --cov-report=term-missing:skip-covered --cov-report=xml:reports/coverage-offline.xml

test-online: ## 線上寄信冒煙（需先 export SMTP_* / REPLY_TO；OFFLINE=0）
	OFFLINE=0 PYTHONPATH=".:src" pytest -q -rs --online tests/test_mailer_online.py -k test_smtp_live_send_ok

demo-send: ## 直接寄一封測試信（不透過 pytest）
	OFFLINE=0 PYTHONPATH=".:src" python scripts/online_check.py
