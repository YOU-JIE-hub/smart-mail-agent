from __future__ import annotations

import importlib
from collections.abc import Callable


def _normalize(label: str) -> str:
    mapping = {"sales": "sales_inquiry", "complain": "complaint"}
    norm = (label or "").strip().lower()
    return mapping.get(norm, norm or "unknown")


def _get_orig() -> Callable[[str], object] | None:
    # 測試會 monkeypatch 這個函式成 None 以強迫 fallback
    return importlib.import_module


def handle(request: dict) -> dict:
    action = _normalize(request.get("predicted_label") or request.get("action") or "")
    importer = _get_orig()
    if importer:
        try:
            mod = importer(f"smart_mail_agent.actions.{action}")
            handler = getattr(mod, "handle", None)
            if callable(handler):
                return handler(request)
        except Exception:
            pass
    if action == "unknown":
        return {"action": "reply_general", "subject": "[自動回覆] 我們已收到您的郵件"}
    return {"action": action}
