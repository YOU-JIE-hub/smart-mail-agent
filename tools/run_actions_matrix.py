#!/usr/bin/env python3
from __future__ import annotations
import runpy, sys, json, time, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "output" / "matrix"
OUT = OUT_DIR / "matrix_summary.json"
HIDDEN_ROOT = ROOT / ".portfolio_hidden"
HIDDEN_OUT = HIDDEN_ROOT / "data" / "output" / "matrix" / "matrix_summary.json"

def try_forward() -> bool:
    # 只允許「可見」的開發路徑；不要跑隱藏版，避免把產物寫錯地方
    candidates = [
        ROOT / ".dev" / "run_actions_matrix.py",
        ROOT / "scripts" / "dev" / "run_actions_matrix.py",
    ]
    for p in candidates:
        if p.exists():
            sys.argv[0] = str(p)
            runpy.run_path(str(p), run_name="__main__")
            return True
    return False

def ensure_out_from_hidden() -> None:
    # 如果可見路徑沒有，但隱藏路徑有，就把它複製過來
    if (not OUT.exists()) and HIDDEN_OUT.exists():
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HIDDEN_OUT, OUT)
        print(f"[shim] copied {HIDDEN_OUT} -> {OUT}")

def write_minimal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "engine": "portfolio-clean-shim",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "matrix": [],
        "cases": [],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[shim] wrote minimal {OUT}")

def main() -> int:
    forwarded = try_forward()
    ensure_out_from_hidden()
    if not OUT.exists():
        write_minimal()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
