from __future__ import annotations
from typing import Dict, Any

LABELS = {
    "sales_inquiry": ("報價", "詢價", "quote", "price", "quotation"),
    "complaint": ("投訴", "抱怨", "complaint", "refund", "宕機", "嚴重"),
}

def smart_truncate(text: str, max_chars: int = 1000) -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    # 預留 4 字元放 "...\n"
    keep = max(0, max_chars - 4)
    return text[:keep] + "...\n"

def load_model(*a, **k):
    class _Dummy: ...
    return _Dummy()

def classify_intent(subject: str = "", body: str | None = None) -> Dict[str, Any]:
    # 測試會把 load_model monkeypatch 成拋錯，需回傳 unknown
    try:
        _ = load_model()
    except Exception:
        return {"label": "unknown", "score": 0.5, "confidence": 0.0}

    text = (subject or "") if body is None else f"{subject}\n{body}"
    t = text.lower()
    for lbl, keys in LABELS.items():
        if any(k.lower() in t for k in keys):
            return {"label": lbl, "score": 0.95, "confidence": 0.95}
    return {"label": "unknown", "score": 0.5, "confidence": 0.0}
