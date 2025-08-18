.PHONY: init fmt lint test type cov docs serve build release

init:
\tpython -m pip install -U pip
\tpip install -e .[dev]
\tpre-commit install

fmt:
\tblack .
\tisort .

lint:
\truff check .
\tblack --check .
\tisort --check-only .

type:
\tmypy src || true

test:
\tOFFLINE=1 PYTHONPATH=".:src" pytest -q

cov:
\tOFFLINE=1 PYTHONPATH=".:src" pytest --cov=smart_mail_agent --cov-report=term-missing

docs:
\tmkdocs build

serve:
\tmkdocs serve -a 127.0.0.1:8000

build:
\tpython -m build

release:
\tgit tag $$(python -c "import tomllib,sys;print('v'+tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
\tgit push --tags
