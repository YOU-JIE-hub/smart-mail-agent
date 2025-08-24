.PHONY: setup lint test ocr-demo nlp-demo dist
setup:
	python -m pip install -U pip
	pip install -e ".[ocr,llm,dev]"
	pre-commit install || true
lint:
	ruff check --fix src tests_smoke || true
	black src tests_smoke
	isort src tests_smoke
test:
	pytest -q
ocr-demo:
	ai-rpa --input-path samples/ocr_tra.png --tasks ocr,nlp,actions --output data/output/ocr_report.json
	@echo "→ data/output/ocr_report.json"
nlp-demo:
	ai-rpa --input-path samples/nlp_demo.txt --tasks nlp,actions --output data/output/report.json
	@echo "→ data/output/report.json"
dist:
	python -m build || true
