.PHONY: unit e2e all
unit:
\t. .venv/bin/activate && pytest -q
e2e:
\t. .venv/bin/activate && pytest tests/e2e -m online -q
all:
\t. .venv/bin/activate && pytest tests/unit tests/contracts -q && \
\tpytest tests/e2e -m online -q
