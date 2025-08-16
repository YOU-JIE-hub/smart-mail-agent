#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output" / "matrix" / "matrix_summary.json"
OUT.parent.mkdir(parents=True, exist_ok=True)
payload = {
    "generated_at": int(time.time()),
    "engine": "shim-minimal",
<<<<<<< HEAD
    "cases": [{
        "id": "shim-sales-1",
        "action": "sales",
        "request": {"subject":"Hello from shim","content":"price/報價 詢問","meta":{"offline": True}},
        "result": {"ok": True, "label": "inquiry", "confidence": 0.9, "notes": "portfolio-clean shim"},
    }],
=======
    "cases": [
        {
            "id": "shim-sales-1",
            "action": "sales",
            "request": {
                "subject": "Hello from shim",
                "content": "price/報價 詢問",
                "meta": {"offline": True},
            },
            "result": {"ok": True, "label": "inquiry", "confidence": 0.9, "notes": "portfolio-clean shim"},
        }
    ],
>>>>>>> origin/main
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[shim] wrote non-empty {OUT} with {len(payload['cases'])} case(s)")
