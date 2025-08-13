#!/usr/bin/env python3
from __future__ import annotations

from typing import Any, Dict

from src.utils.templater import render

SEVERITY_MAP = {
    "high": ["惡劣", "退款", "法律", "投訴到主管機關", "崩潰", "無法使用", "嚴重"],
    "med": ["很差", "非常失望", "體驗不好", "延遲", "卡頓"],
    "low": ["不滿", "不便", "希望改善", "小問題"],
}


def _severity(body: str) -> str:
    b = body or ""
    for key, words in SEVERITY_MAP.items():
        if any(w in b for w in words):
            return key
    return "low"


def handle(
    request: Dict[str, Any],
    *,
    request_id: str,
    dry_run: bool = False,
    simulate_failure: str | None = None,
) -> Dict[str, Any]:
    if simulate_failure == "template":
        raise RuntimeError("E_TEMPLATE_SIMULATED")
    body = request.get("body", "")
    sev = _severity(body)
    pri = {"high": "P1", "med": "P2", "low": "P3"}[sev]
    eta = {"high": "24h", "med": "48h", "low": "72h"}[sev]
    rendered = render(f"complaint_{sev}.j2", {"sender": request.get("sender"), "severity": sev})
    intent, subject = "complaint", "收到您的意見與協助處理"
    conf = float(request.get("confidence", -1.0))
    return {
        "ok": True,
        "action_name": intent,
        "subject": subject,
        "to": [request.get("sender")] if request.get("sender") else [],
        "cc": [],
        "body": rendered,
        "attachments": [],
        "meta": {"severity": sev, "priority": pri, "sla_eta": eta},
        "request_id": request_id,
        "intent": intent,
        "confidence": conf,
    }
