#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict

from src.policy_engine import apply_policy
from src.sma_types import normalize_request, normalize_result

try:
    from src.actions.sales_inquiry import handle as handle_sales_inquiry
except Exception:

    def handle_sales_inquiry(req: Dict[str, Any], **kw) -> Dict[str, Any]:
        return {
            "action_name": "sales_inquiry",
            "subject": "商務詢問初步回覆",
            "body": "暫無模板（降級）",
            **kw,
        }


try:
    from src.actions.complaint import handle as handle_complaint
except Exception:

    def handle_complaint(req: Dict[str, Any], **kw) -> Dict[str, Any]:
        return {
            "action_name": "complaint",
            "subject": "已收到您的意見",
            "body": "暫無模板（降級）",
            **kw,
        }


def _read_json(p: str) -> Dict[str, Any]:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _write_json(p: str, obj: Dict[str, Any]) -> None:
    path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def process(
    req_obj: Dict[str, Any], *, dry_run: bool = False, simulate_failure: str | None = None
) -> Dict[str, Any]:
    t0 = time.time()
    request_id = str(uuid.uuid4())
    req = normalize_request(req_obj).dict(by_alias=True)
    intent = (req.get("predicted_label") or "").strip().lower()
    if intent == "sales_inquiry":
        raw = handle_sales_inquiry(
            req, request_id=request_id, dry_run=dry_run, simulate_failure=simulate_failure
        )
    elif intent == "complaint":
        raw = handle_complaint(
            req, request_id=request_id, dry_run=dry_run, simulate_failure=simulate_failure
        )
    elif intent == "reply_faq":
        raw = {
            "action_name": "reply_faq",
            "subject": "常見問題回覆",
            "body": "FAQ 占位回覆（離線示範）",
            "request_id": request_id,
            "intent": "reply_faq",
            "confidence": float(req.get("confidence", -1.0)),
        }
    elif intent == "send_quote":
        raw = {
            "action_name": "send_quote",
            "subject": "報價單",
            "body": "報價流程由既有模組處理（此輪不動）",
            "request_id": request_id,
            "intent": "send_quote",
            "confidence": float(req.get("confidence", -1.0)),
        }
    else:
        raw = {
            "action_name": "reply_general",
            "subject": "已收到您的來信",
            "body": "感謝您的來信，我們將儘速回覆。",
            "request_id": request_id,
            "intent": "reply_general",
            "confidence": float(req.get("confidence", -1.0)),
        }
    policy_file = os.getenv("SMA_POLICY_FILE", os.getenv("POLICY_FILE", "configs/policy.yaml"))
    raw = apply_policy(raw, req, policy_file)
    res = normalize_result(raw).dict()
    res["dry_run"] = dry_run
    if simulate_failure:
        res.setdefault("meta", {})
        res["meta"]["simulate_failure"] = simulate_failure
        res.setdefault("warnings", []).append(f"simulated_{simulate_failure}_failure")
    res["duration_ms"] = int((time.time() - t0) * 1000)
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Smart Mail Agent - Action Handler")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--simulate-failure", choices=["pdf", "smtp", "db", "template"])
    args = ap.parse_args(argv)
    obj = _read_json(args.input)
    result = process(obj, dry_run=args.dry_run, simulate_failure=args.simulate_failure)
    _write_json(args.output, result)
    print(f"已輸出：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
