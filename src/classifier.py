from __future__ import annotations
class IntentClassifier:
    def __init__(self, *a, **k): ...
    def predict(self, text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["quote", "報價", "詢價"]): return "sales_inquiry"
        if any(k in t for k in ["complaint", "投訴", "抱怨"]): return "complaint"
        return "unknown"
