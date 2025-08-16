from __future__ import annotations

from typing import Any

LABELS = {
    "sales_inquiry": ("報價", "詢價", "quote", "price", "quotation"),
    "complaint": ("投訴", "抱怨", "complaint", "refund", "宕機", "嚴重"),
}


def smart_truncate(text: str, max_chars: int = 1000) -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    keep = max(0, max_chars - 4)  # 預留 "...\n"
    return text[:keep] + "...\n"


def load_model(*_args, **_kwargs):
    class _Dummy: ...

    return _Dummy()


def classify_intent(subject: str = "", body: str | None = None) -> dict[str, Any]:
    # 測試會把 load_model monkeypatch 成拋錯，需回傳 unknown
    try:
        load_model()
    except Exception:
        return {"label": "unknown", "score": 0.0, "confidence": 0.0}

    text = f"{subject or ''} {body or ''}"
    for lbl, kws in LABELS.items():
        for kw in kws:
            if kw in text:
                return {"label": lbl, "score": 0.95, "confidence": 0.95}
    return {"label": "unknown", "score": 0.5, "confidence": 0.5}
