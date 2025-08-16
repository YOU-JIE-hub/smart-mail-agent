.PHONY: help lint test test-offline test-online cov-offline demo-send

help: ## 列出可用目標
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed -E 's/:.*?##/: /' | sort

lint: ## ruff 稽核（使用 .ruff.toml）
	ruff check .

test: test-offline ## 等同 test-offline

test-offline: ## 跑整包離線測試（不會連網）；CI 預設跑這個
	OFFLINE=1 PYTHONPATH=".:src" pytest -q

cov-offline: ## 產 XML 覆蓋率（離線）
	OFFLINE=1 PYTHONPATH=".:src" pytest -q --cov=src --cov-config=.coveragerc --cov-report=term-missing:skip-covered --cov-report=xml:reports/coverage-offline.xml --cov-fail-under=60

test-online: ## 線上寄信冒煙（需先 export SMTP_* / REPLY_TO；OFFLINE=0）
	OFFLINE=0 PYTHONPATH=".:src" pytest -q -rs --online tests/test_mailer_online.py -k test_smtp_live_send_ok

demo-send: ## 直接寄一封測試信（不透過 pytest）

tests-spam-and-flows: ## 僅跑本批 SPAM/分類/動作/錯誤情境測試
	OFFLINE=1 PYTHONPATH=.:src pytest -q -k "spam or inference_classifier_errors or online_send_paths" -rs
	OFFLINE=0 PYTHONPATH=".:src" python scripts/online_check.py


tests-spam-orchestrator: ## 只跑離線 Spam orchestrator 行為/錯誤測
	OFFLINE=1 PYTHONPATH=".:src" pytest -q -k "offline_orchestrator" -rs

tests-spam-and-flows: ## 跑本輪新增的 spam & flow 測試集合
	OFFLINE=1 PYTHONPATH=".:src" pytest -q -k "spam or inference_classifier_errors or online_send_paths" -rs
