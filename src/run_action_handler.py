#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict

# --- logging import（支援 src.utils.* 與 utils.* 兩種路徑） ---
try:
    from src.utils.jsonlog import log_event
except Exception:
    try:
        from utils.jsonlog import log_event  # 備援（你專案根的 proxy）
    except Exception:
        log_event = None  # 若真的連載入都失敗，後面會走防呆路徑


# -----------------------------
# helpers
# -----------------------------
def _read_json(p: str) -> Dict[str, Any]:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(p: str, obj: Dict[str, Any]) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _action_name_from(obj: Dict[str, Any]) -> str:
    label = (obj.get("predicted_label") or "").lower()
    if "sales" in label:
        return "handle_sales_inquiry"
    if "complaint" in label:
        return "handle_complaint"
    return "handle_message"


# -----------------------------
# core
# -----------------------------
def process(
    obj: Dict[str, Any], *, dry_run: bool = False, simulate_failure: bool = False
) -> Dict[str, Any]:
    t0 = time.time()
    warnings = []

    if simulate_failure:
        ok, code = False, "SIM_FAIL"
        warnings.append("simulated_failure")
    else:
        ok, code = True, "OK"

    result: Dict[str, Any] = {
        "ok": ok,
        "code": code,
        "dry_run": bool(dry_run),
        "action_name": _action_name_from(obj),
        "request_id": obj.get("request_id") or str(uuid.uuid4()),
        "intent": obj.get("predicted_label"),
        "confidence": obj.get("confidence"),
        "duration_ms": None,  # 寫完再補
        "warnings": warnings,
        "logged_path": None,  # 等下記錄成功後填入
        "output": {"status": "noop"},  # 保留一個固定欄位，避免下游爆型別
    }

    # 假裝做點事…
    time.sleep(0.01)

    result["duration_ms"] = int((time.time() - t0) * 1000)
    return result


# -----------------------------
# cli
# -----------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--simulate-failure", action="store_true")
    args = ap.parse_args(argv)

    obj = _read_json(args.input)
    result = process(obj, dry_run=args.dry_run, simulate_failure=args.simulate_failure)

    # 先嘗試寫 JSONL 日誌；成功則回填 logged_path，失敗才加 warnings
    try:
        if log_event is None:
            raise RuntimeError("log_event not available")
        logged_path = log_event(result, obj)
        if logged_path:
            result["logged_path"] = logged_path
        else:
            result.setdefault("warnings", []).append("log_write_failed")
    except Exception:
        result.setdefault("warnings", []).append("log_write_failed")

    # 最後輸出結果 JSON（不再覆蓋 logged_path 與 warnings）
    _write_json(args.output, result)
    print(f"已輸出：{args.output}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
