#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any, Dict

from src.utils.templater import render

RE_COMPANY = re.compile(
    r"(公司|corporation|corp|有限公司|股份有限公司|Co\.|Inc\.)[:：]?\s*([A-Za-z0-9\u4e00-\u9fff\-\._ ]+)"
)
RE_QTY = re.compile(r"(數量|quantity|qty)[:：]?\s*(\d+)")
RE_BUDGET = re.compile(r"(預算|budget)[:：]?\s*([0-9,\.]+)")
RE_DEADLINE = re.compile(r"(期限|截止|deadline)[:：]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9/]{5,10})")


def _extract(body: str) -> Dict[str, str]:
    b = body or ""

    def _m(r):
        m = r.search(b)
        return m.group(m.lastindex or 1) if m else ""

    words = re.findall(r"[A-Za-z\u4e00-\u9fff]{2,}", b)
    return {
        "company": _m(RE_COMPANY),
        "quantity": _m(RE_QTY),
        "budget": _m(RE_BUDGET),
        "deadline": _m(RE_DEADLINE),
        "keywords": ", ".join(sorted(set(w for w in words if len(w) >= 2))[:10]),
    }


def _write_needs_md(out_dir: Path, fields: Dict[str, str]) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"needs-summary-{ts}.md"
    path.write_text(render("needs_summary.md.j2", {"fields": fields}), encoding="utf-8")
    return str(path)


def handle(
    request: Dict[str, Any],
    *,
    request_id: str,
    dry_run: bool = False,
    simulate_failure: str | None = None,
) -> Dict[str, Any]:
    if simulate_failure == "template":
        raise RuntimeError("E_TEMPLATE_SIMULATED")
    subject, intent = "商務詢問初步回覆", "sales_inquiry"
    confidence = float(request.get("confidence", -1.0))
    fields = _extract(request.get("body", ""))
    out_dir = Path(os.getenv("SMA_DATA_DIR", "data")) / "output"
    attachment_path = "" if dry_run else _write_needs_md(out_dir, fields)
    body = render("sales_inquiry_reply.j2", {"fields": fields, "sender": request.get("sender")})
    return {
        "ok": True,
        "action_name": intent,
        "subject": subject,
        "to": [request.get("sender")] if request.get("sender") else [],
        "cc": [],
        "body": body,
        "attachments": ([attachment_path] if attachment_path else []),
        "meta": {"next_step": "業務將於 1 個工作日內聯繫確認需求細節", "confidence": confidence},
        "request_id": request_id,
        "intent": intent,
        "confidence": confidence,
    }
