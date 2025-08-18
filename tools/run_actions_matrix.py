#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output" / "matrix"
OUT.mkdir(parents=True, exist_ok=True)
msum = OUT / "matrix_summary.json"

# 產生最小合法輸出，供測試讀取（離線安全）
payload = {
    "version": 1,
    "generated_at": os.environ.get("GITHUB_SHA") or "local",
    "total_cases": 0,
    "buckets": [],         # 預留欄位，讓 schema/讀取不爆
}
msum.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
print(f"[matrix] wrote {msum}")
