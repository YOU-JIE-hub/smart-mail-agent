SHELL := /usr/bin/env bash

.PHONY: setup format lint test e2e demo-all show-summary build clean

setup: ; bash scripts/setup_env.sh
format: ; isort . && black .
lint: ; isort --check-only . && black --check . && flake8
test: ; OFFLINE=1 PYTHONPATH=src pytest -q
e2e: test
demo-all: ; ./bin/smarun
show-summary: ; tools/show_summary.sh
build: ; python -m build && tar -czf smart-mail-agent-$(shell date +%Y%m%d).tar.gz --exclude='.git' --exclude='.venv' --exclude='dist' --exclude='build' .
clean: ; rm -rf .pytest_cache .mypy_cache dist build *.egg-info && find . -name '__pycache__' -type d -exec rm -rf {} +
