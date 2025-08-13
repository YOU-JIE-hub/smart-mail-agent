#!/usr/bin/env bash
set -Eeuo pipefail
python - <<'PY'
import json, pathlib
def show(p):
    p=pathlib.Path(p)
    if not p.exists(): return
    d=json.loads(p.read_text(encoding="utf-8"))
    name=p.name.replace('out_','').replace('.json','')
    print(f"=== {name} ===")
    print("action_name=", d.get("action_name"))
    print("subject=", d.get("subject"))
    print("meta=", d.get("meta"))
    print("attachments=", d.get("attachments"))
for name in ["out_sales.json","out_quote.json","out_overlimit.json","out_whitelist.json"]:
    show(f"data/output/{name}")
PY
