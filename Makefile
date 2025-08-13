PY ?= python
PIP ?= $(PY) -m pip
PKG_DIR ?= src
.DEFAULT_GOAL := help
help: ; @echo "Targets: install | fmt | lint | test-offline | e2e-offline | demo-quote | check-env | clean"
install: ; $(PIP) install -U pip ; $(PIP) install -r requirements.txt
fmt: ; $(PY) -m isort . ; $(PY) -m black .
lint: ; $(PY) -m flake8
test-offline: ; OFFLINE=1 PYTHONPATH=$(PKG_DIR) $(PY) -m pytest -q -k "not online"
e2e-offline: ; OFFLINE=1 PYTHONPATH=$(PKG_DIR) $(PY) -m pytest -q -k "not online or e2e"
demo-quote:
	mkdir -p data/output
	printf '%s\n' '{"subject":"please send quote","from":"alice@example.com","body":"need quotation","predicted_label":"send_quote","confidence":0.95,"attachments":[]}' > data/output/in.json
	OFFLINE=1 PYTHONPATH=$(PKG_DIR) $(PY) -m src.run_action_handler --input data/output/in.json --output data/output/out.json
	cat data/output/out.json || true
check-env: ; PYTHONPATH=$(PKG_DIR) $(PY) -m tools.check_env
clean:
	rm -rf .pytest_cache .mypy_cache build dist *.egg-info
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
.PHONY: help install fmt lint test-offline e2e-offline demo-quote check-env clean
