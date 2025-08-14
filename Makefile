.PHONY: venv install fmt lint test build clean hooks

venv:
	@[ -d .venv ] || python3 -m venv .venv

install: venv
	. .venv/bin/activate && python -m pip install -U pip
	@if [ -f requirements.txt ]; then . .venv/bin/activate && python -m pip install -e . -r requirements.txt; else . .venv/bin/activate && python -m pip install -e .; fi

fmt:
	. .venv/bin/activate && ruff --fix .
	. .venv/bin/activate && black .

lint:
	. .venv/bin/activate && ruff .

test:
	. .venv/bin/activate && pytest -q || true

build:
	. .venv/bin/activate && python -m pip install -U build
	. .venv/bin/activate && python -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info

hooks:
	. .venv/bin/activate && python -m pip install -U pre-commit
	. .venv/bin/activate && pre-commit install -f --install-hooks || true
