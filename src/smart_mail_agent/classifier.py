from __future__ import annotations
from typing import Any, Dict, Iterable, List, Tuple

def _contains_any(text: str, needles: Iterable[str]) -> bool:
    t = text.lower()
    return any(n.lower() in t for n in needles)

_LABELS = {
    "complaint": ("售後服務或抱怨", "complaint"),
    "policy":    ("詢問流程或規則", "policy"),
    "sales":     ("詢問流程或規則", "sales_inquiry"),
    "other":     ("其他", "other"),
}

_KW_COMPLAINT = ["抱怨","投訴","客訴","不滿","壞了","故障","退貨","退款","保固","維修"]
_KW_POLICY = ["流程","規則","政策","policy","rules","如何申請","怎麼申請","SOP"]
_KW_QUOTE_SALES = ["報價","價格","quote","quotation","price","pricing","費率"]

def _make_result(kind: str, score: float) -> Dict[str, Any]:
    label_zh, raw = _LABELS.get(kind, _LABELS["other"])
    return {"label": label_zh, "predicted_label": label_zh, "raw_label": raw, "score": float(score), "confidence": float(score)}

def classify_intent(subject: str | None, content: str | None) -> Dict[str, Any]:
    s = (subject or "").strip(); c = (content or "").strip(); text = f"{s}\n{c}".strip()
    if not text: return _make_result("other", 0.40)
    if _contains_any(text, _KW_COMPLAINT): return _make_result("complaint", 0.96)
    if _contains_any(text, _KW_QUOTE_SALES): return _make_result("sales", 0.93)
    if _contains_any(text, _KW_POLICY): return _make_result("policy", 0.92)
    return _make_result("other", 0.40)
