from __future__ import annotations
import importlib
from typing import Callable, Optional

def _normalize(label: str) -> str:
    m = {"sales": "sales_inquiry", "complain": "complaint"}
    l = (label or "").strip().lower()
    return m.get(l, l or "unknown")

def _get_orig() -> Optional[Callable[[str], object]]:
    # 測試會 monkeypatch 這個函式成 None 以強迫 fallback
    return importlib.import_module

def handle(request: dict) -> dict:
    action = _normalize(request.get("predicted_label") or request.get("action") or "")
    importer = _get_orig()
    if importer:
        try:
            mod = importer(f"smart_mail_agent.actions.{action}")
            h = getattr(mod, "handle", None)
            if callable(h):
                return h(request)
        except Exception:
            pass
    # fallback：一般回覆
    if action == "unknown":
        return {"action": "reply_general", "subject": "[自動回覆] 我們已收到您的郵件"}
    return {"action": action}
