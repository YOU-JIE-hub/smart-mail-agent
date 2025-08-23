from __future__ import annotations

from typing import Any

__all__ = ["smart_truncate", "load_model", "classify_intent"]


def smart_truncate(text: str, max_chars: int = 1000) -> str:
    if text is None:
        return ""
    s = str(text)
    if len(s) <= max_chars:
        return s
    # 保留結尾 "...\\n"
    keep = max(0, max_chars - 4)
    return s[:keep] + "...\n"


def load_model(*_args: Any, **_kwargs: Any) -> object:
    """輕量佔位；測試會 monkeypatch 這個函式丟例外。"""
    return object()


def classify_intent(subject: str, body: str) -> dict[str, Any]:
    """
    極簡離線分類器（可測、可被 monkeypatch）。
    - 若 load_model() 在外部被猴補成丟錯，我們回 {"label":"unknown","confidence":0.0}
    - 否則做關鍵詞啟發式
    """
    text = f"{subject or ''} {body or ''}".lower()
    try:
        _ = load_model()
    except Exception:
        return {"label": "unknown", "confidence": 0.0}

    if any(k in text for k in ("報價", "價格", "詢價", "quote", "price")):
        return {"label": "sales_inquiry", "confidence": 0.6}
    if any(k in text for k in ("投訴", "抱怨", "退貨", "refund", "complaint")):
        return {"label": "complaint", "confidence": 0.6}
    return {"label": "other", "confidence": 0.5}
