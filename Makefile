.PHONY: venv install lint fmt test typecheck ci all

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate; \
	pip install -U pip; \
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi; \
	pip install ruff mypy pytest pytest-cov pytest-timeout pre-commit

lint:
	. .venv/bin/activate; ruff check .

fmt:
	. .venv/bin/activate; ruff format .

typecheck:
	. .venv/bin/activate; mypy .

test:
	. .venv/bin/activate; \
	PYTHONNOUSERSITE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OFFLINE=1 PYTHONPATH=".:src" \
	pytest -q -p pytest_timeout -p pytest_cov --cov --cov-branch --cov-report=term-missing:skip-covered

ci: lint typecheck test

all: install fmt lint typecheck test
