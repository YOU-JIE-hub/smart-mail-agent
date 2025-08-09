# ===== Smart-Mail-Agent: Clean Makefile (auto-regenerated) =====
SHELL := /bin/bash
VENV  := .venv
PY    := $(VENV)/bin/python
PIP   := $(VENV)/bin/pip
OFFLINE ?= 1

.PHONY: venv fmt lint type test all smtp-test-online

venv:
	@test -d $(VENV) || python -m venv $(VENV)
	@. $(VENV)/bin/activate && pip install -U pip
	@. $(VENV)/bin/activate && pip install -r requirements.txt

fmt: venv
	@. $(VENV)/bin/activate && isort .
	@. $(VENV)/bin/activate && black .

lint: venv
	@. $(VENV)/bin/activate && flake8 --config .flake8 .
	@. $(VENV)/bin/activate && mypy --exclude '(^|/)(\.venv|data|build|dist)/' src || true

type: venv
	@. $(VENV)/bin/activate && mypy --exclude '(^|/)(\.venv|data|build|dist)/' src

test: venv
	@OFFLINE=$(OFFLINE) PYTHONPATH=src $(VENV)/bin/pytest -q

smtp-test-online: venv
	@OFFLINE=0 PYTHONPATH=src $(VENV)/bin/pytest -q -m online -k mailer_online -s

all: fmt lint test

# 引入 CI 子檔（包含 gh-login / gh-secrets / ci-smtp / ci-watch）
-include tools/ci.mk
