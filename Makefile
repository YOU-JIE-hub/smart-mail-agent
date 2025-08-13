.PHONY: setup test-offline demo-quote demo-faq demo-other e2e pack

setup:
	python -m pip install -U pip
	pip install -r requirements.txt

test-offline:
	OFFLINE=1 PYTHONPATH=src pytest -q -k "(not online)"

demo-quote:
	mkdir -p data/output
	printf '%s' '{"subject":"please send quote","from":"alice@example.com","body":"need quotation","predicted_label":"send_quote","confidence":0.95,"attachments":[]}' > data/output/in.json
	OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --input data/output/in.json --output data/output/out.json
	@echo '---'; cat data/output/out.json

demo-faq:
	mkdir -p data/output
	printf '%s' '{"subject":"退貨流程？","from":"carol@example.com","body":"想了解退貨與退款流程","predicted_label":"reply_faq","confidence":0.90,"attachments":[]}' > data/output/in_faq.json
	OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --input data/output/in_faq.json --output data/output/out_faq.json
	@echo '---'; cat data/output/out_faq.json

demo-other:
	mkdir -p data/output
	printf '%s' '{"subject":"免費中獎","from":"x@spam.com","body":"點此領獎","predicted_label":"other","confidence":0.51,"attachments":[]}' > data/output/in_other.json
	OFFLINE=1 PYTHONPATH=src python -m src.run_action_handler --input data/output/in_other.json --output data/output/out_other.json
	@echo '---'; cat data/output/out_other.json

e2e:
	OFFLINE=1 PYTHONPATH=src pytest -q tests/e2e -k "label_routing_offline or cli_scripts or new_intents or cli_flags"

pack:
	git tag -a v0.2.0-interview-pro -m "Observability + env unify + CLI help + Makefile"
	git push origin v0.2.0-interview-pro
