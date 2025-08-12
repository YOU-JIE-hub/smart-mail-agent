PYTHON?=.venv/bin/python
OFFLINE?=1
export OFFLINE
export PYTHONPATH=src

.PHONY: test-offline matrix report open-report demo clean-attachments

test-offline:
	$(PYTHON) -m pytest -q -k "not online"

matrix:
	$(PYTHON) tools/run_actions_matrix.py

report:
	$(PYTHON) tools/generate_offline_report.py

open-report:
	@if command -v wslview >/dev/null 2>&1; then wslview reports/offline_demo_report.html; \
	elif command -v xdg-open >/dev/null 2>&1; then xdg-open reports/offline_demo_report.html >/dev/null 2>&1 & \
	else echo "Open reports/offline_demo_report.html in your browser."; fi

demo: matrix report open-report

clean-attachments:
	@find data/output -maxdepth 1 -type f -name "attachment_*.txt" -print -delete | sed 's/^/removed: /' || true

PYTHON?=.venv/bin/python
export OFFLINE=1
export PYTHONPATH=src

.PHONY: qa lint format demo
qa:
	- black --check --diff . || true
	- isort --check-only . || true
	$(PYTHON) -m pytest -q -k 'not online'

lint:
	- black . || true
	- isort . || true

demo:
	$(PYTHON) -m cli.sma demo


PYTHON?=.venv/bin/python
export OFFLINE=1
export PYTHONPATH=src

.PHONY: contracts security sbom
contracts:
	$(PYTHON) -m pytest -q tests/contracts

security:
	@echo "[SEC] bandit 扫描（忽略 tests、data、.venv）"
	- bandit -q -r -x tests,data,.venv .
	@echo "[SEC] detect-secrets 扫描（若未安装会略过）"
	- detect-secrets scan --all-files --exclude-files '.*(\.venv|\.git|data|artifacts|reports|archive).*' || true

sbom:
	@echo "[SBOM] 產生 CycloneDX SBOM (sbom.json)"
	- python -m pip install -U cyclonedx-bom >/dev/null 2>&1 || true
	- cyclonedx-py --format json --outfile sbom.json || cyclonedx-bom -e -o sbom.json || true
