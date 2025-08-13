PY ?= python
PIP ?= pip
PKGS ?= src tests
OFFLINE ?= 1

.PHONY: help fmt lint e2e demo-quote demo-complaint

help:
@echo "make fmt # isort + black"
@echo "make lint # flake8"
@echo "make e2e # 離線 E2E 測試"
@echo "make demo-quote # 報價動作示例（一行執行）"
@echo "make demo-complaint # 投訴動作示例（一行執行）"

fmt:
$(PY) -m isort .
$(PY) -m black .

lint:
$(PY) -m flake8

e2e:
OFFLINE=$(OFFLINE) PYTHONPATH=src $(PY) -m pytest -q -k "not online or e2e"

demo-quote:
mkdir -p data/output ;
printf '{"subject":"please send quote","from":"alice@example.com","body":"need quotation","predicted_label":"send_quote","confidence":0.95,"attachments":[]}\n' > data/output/in.json ;
OFFLINE=$(OFFLINE) PYTHONPATH=src $(PY) -m src.run_action_handler --input data/output/in.json --output data/output/out.json ;
cat data/output/out.json

demo-complaint:
mkdir -p data/output ;
printf '{"subject":"服務體驗不佳","from":"bob@example.com","body":"等候過久且態度不佳，要求協助。","predicted_label":"complaint","confidence":0.88,"attachments":[]}\n' > data/output/in.json ;
OFFLINE=$(OFFLINE) PYTHONPATH=src $(PY) -m src.run_action_handler --input data/output/in.json --output data/output/out.json ;
cat data/output/out.json
