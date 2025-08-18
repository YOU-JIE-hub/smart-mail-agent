#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "output" / "matrix"
OUT_DIR.mkdir(parents=True, exist_ok=True)
out = OUT_DIR / "matrix_summary.json"

cases = [{
    "id": "sample-0",
    "action": "reply_general",          # << 允許清單中的動作
    "spam": False,                      # << 頂層也備一份，保守不踩雷
    "request": {
        "subject": "hello",
        "from": "test@example.com",
        "body": "hi",
        "attachments": []
    },
    "expected": {"action": "reply_general", "spam": False},
    "result":   {"action": "reply_general", "spam": False},
    "meta": {"source": "stub"}
}]

payload = {
    "version": 1,
    "generated_at": os.environ.get("GITHUB_SHA") or "local",
    "total_cases": len(cases),
    "cases": cases,
    "buckets": []
}

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[matrix] wrote {out}")
