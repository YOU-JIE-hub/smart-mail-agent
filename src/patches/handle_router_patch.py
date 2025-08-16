from __future__ import annotations
import importlib

def _normalize(label: str) -> str:
    m = {"sales": "sales_inquiry", "complain": "complaint"}
    l = (label or "").strip().lower()
    return m.get(l, l or "unknown")

def _get_orig():
    try:
        return importlib.import_module("smart_mail_agent.patches.handle_router_patch")
    except Exception:
        return None

def handle(request: dict) -> dict:
    orig = _get_orig()
    if orig and hasattr(orig, "handle"):
        return orig.handle(request)
    action = _normalize(request.get("predicted_label") or request.get("action") or "")
    if action == "unknown":
        return {"action": "reply_general", "subject": "[自動回覆] 我們已收到您的郵件"}
    return {"action": action}
