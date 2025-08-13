PYTHON ?= python
RUN    ?= PYTHONPATH=src $(PYTHON) -m src.run_action_handler

.PHONY: demo-sales demo-quote-fail demo-overlimit demo-whitelist demo-all show-summary

demo-sales:
	@mkdir -p data/output
	@printf '%s' '{"subject":"合作報價與時程 2025-08-20","from":"alice@biz.com","body":"偉大股份有限公司 需要 50 台，預算 NTD 300,000，請於 2025/08/20 前回覆。","predicted_label":"sales_inquiry","confidence":0.87,"attachments":[]}' > data/output/in_sales.json
	@$(RUN) --input data/output/in_sales.json --output data/output/out_sales.json
	@echo "已輸出：data/output/out_sales.json"

demo-quote-fail:
	@mkdir -p data/output
	@printf '%s' '{"subject":"請報價","from":"a@b.c","body":"我要報價","predicted_label":"send_quote","confidence":0.9,"attachments":[]}' > data/output/in_quote.json
	@$(RUN) --input data/output/in_quote.json --output data/output/out_quote.json --simulate-failure pdf || $(RUN) --input data/output/in_quote.json --output data/output/out_quote.json --simulate-failure
	@echo "已輸出：data/output/out_quote.json"

demo-overlimit:
	@mkdir -p data/output
	@printf '%s' '{"subject":"一般詢問","from":"user@somewhere.com","body":"附件很多請協助查看。","predicted_label":"reply_faq","confidence":0.9,"attachments":[{"filename":"big.bin","size":6291456}]}' > data/output/in_overlimit.json
	@$(RUN) --input data/output/in_overlimit.json --output data/output/out_overlimit.json
	@echo "已輸出：data/output/out_overlimit.json"

demo-whitelist:
	@mkdir -p data/output
	@printf '%s' '{"subject":"一般詢問","from":"alice@trusted.example","body":"這是白名單寄件者。","predicted_label":"reply_faq","confidence":0.9,"attachments":[]}' > data/output/in_whitelist.json
	@$(RUN) --input data/output/in_whitelist.json --output data/output/out_whitelist.json
	@echo "已輸出：data/output/out_whitelist.json"

demo-all: demo-sales demo-quote-fail demo-overlimit demo-whitelist

show-summary:
	@tools/show_summary.sh
