.PHONY: help ensure-venv install format lint test-offline-venv fix-classifier fix-quotation clean-light clean-heavy

help:
	@echo "make ensure-venv          - 建 venv（如無）並升級 pip"
	@echo "make install              - 安裝開發套件"
	@echo "make format               - isort + black"
	@echo "make lint                 - flake8（需全過）"
	@echo "make test-offline-venv    - 自動啟 venv + OFFLINE 測試"
	@echo "make fix-classifier       - 修 transformers.from_pretrained 參數順序"
	@echo "make fix-quotation        - 修 quotation（專業優先、dict 回傳、PDF fallback）"
	@echo "make clean-light          - 清 cache/覆蓋/輸出"
	@echo "make clean-heavy          - 連 pip/hf 快取一起清"

ensure-venv:
	@test -d .venv || python -m venv .venv
	@. .venv/bin/activate; pip -q install -U pip

install: ensure-venv
	@. .venv/bin/activate; \
	  pip install -r requirements.txt || true; \
	  pip install -U pytest black isort flake8 python-dotenv

format:
	. .venv/bin/activate; python -m isort .; python -m black .

lint:
	. .venv/bin/activate; python -m flake8

test-offline-venv: ensure-venv
	. .venv/bin/activate; OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"

fix-classifier: ensure-venv
	. .venv/bin/activate; \
	  python tools/fix_from_pretrained_order_v3.py; \
	  PYTHONPATH=src pytest -q -k "not online"

fix-quotation: ensure-venv
	. .venv/bin/activate; \
	  PYTHONPATH=src pytest -q -k "not online"

clean-light:
	rm -rf .pytest_cache **/__pycache__ htmlcov .coverage* coverage.xml logs/* data/output/* || true

clean-heavy: clean-light
	python -m pip cache purge || true
	rm -rf ~/.cache/pip ~/.cache/huggingface ~/.cache/torch || true
