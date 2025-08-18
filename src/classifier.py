from __future__ import annotations
import re
from typing import Any, Callable, Dict, List

RE_QUOTE = re.compile(r"(報價|詢價|報價單|報價需求|採購|合約|價格|quotation|quote)", re.IGNORECASE)
RE_FLOW  = re.compile(r"(FAQ|常見問題|流程|規則|退貨|保固|shipping|refund|return|warranty)", re.IGNORECASE)
RE_AFTER = re.compile(r"(售後|售後服務|客服|抱怨|投訴|維修|RMA|claim)", re.IGNORECASE)

def _coerce_preds(obj: Any) -> List[Dict[str, Any]]:
    if obj is None:
        return []
    if isinstance(obj, dict):
        d = {}
        if "label" in obj:
            d["label"] = obj["label"]
        if "score" in obj:
            d["score"] = float(obj["score"])
        if "confidence" in obj and "score" not in d:
            d["score"] = float(obj["confidence"])
        return [d] if d else []
    if isinstance(obj, tuple) and len(obj) >= 2:
        lab, sc = obj[0], obj[1]
        try:
            sc = float(sc)
        except Exception:
            sc = 0.0
        return [{"label": lab, "score": sc}]
    if isinstance(obj, list):
        out: List[Dict[str, Any]] = []
        for it in obj:
            out.extend(_coerce_preds(it))
        return out
    try:
        return _coerce_preds(list(obj))  # type: ignore
    except Exception:
        return []

class IntentClassifier:
    def __init__(self, model_path: str | None = None, *, pipeline_override: Callable | None = None, **kwargs: Any):
        self._pipe = pipeline_override
        self._use_shim = pipeline_override is not None

    def _fallback_label(self, subject: str, body: str) -> str:
        text = f"{subject} {body}"
        if RE_QUOTE.search(text):
            return "業務接洽或報價"
        if RE_AFTER.search(text):
            return "售後服務或抱怨"
        if RE_FLOW.search(text):
            return "詢問流程或規則"
        return "其他"

    def classify(self, subject: str = "", body: str = "", **kw: Any) -> Dict[str, Any]:
        if not body and "content" in kw:
            body = str(kw["content"] or "")
        if self._use_shim and callable(self._pipe):
            text = f"{subject}\n{body}"
            raw = self._pipe(text)
            preds = _coerce_preds(raw)
            top = preds[0] if preds else {"label": "other", "score": 0.0}
            score = float(top.get("score", 0.0) or 0.0)
            label = self._fallback_label(subject, body) if score < 0.8 else self._fallback_label(subject, body)
            return {"predicted_label": label, "label": label, "confidence": score, "reason": "shim"}
        label = self._fallback_label(subject, body)
        return {"predicted_label": label, "label": label, "confidence": 0.5, "reason": "fallback"}
