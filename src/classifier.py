from __future__ import annotations
import re
from typing import Any, Iterable

def _merge_text(subject: str | None, content: str | None, text: str | None) -> str:
    parts = [p for p in [subject, content, text] if p]
    return " ".join(parts).strip()

def _is_generic(s: str) -> bool:
    t = s.lower()
    return t in {"hi","hello"} or re.fullmatch(r"(hi|hello)[!. ]*", t or "") is not None

_RULES = [
    ("send_quote", [r"報價", r"\bquote\b", r"詢價", r"合作"]),
    ("refund", [r"退款", r"\brefund\b", r"退費"]),
    ("complaint", [r"抱怨|投訴|故障|宕機|無法使用"]),
]

def _apply_rules(subject: str, content: str, label: str, score: float) -> tuple[str,float]:
    s = f"{subject} {content}".lower()
    for new_label, pats in _RULES:
        for p in pats:
            if re.search(p, s, re.I):
                return new_label, max(score, 0.9)
    return label, score

class IntentClassifier:
    def __init__(self, model_path: str | None = None, pipeline_override: Any | None = None, **_: Any) -> None:
        self.pipe = pipeline_override
        self.model_path = model_path

    def _run_pipe(self, text: str) -> tuple[str,float]:
        if not self.pipe:
            # 簡易規則當作預設模型
            lbl, sc = "other", 0.51
            for new_label, pats in _RULES:
                if any(re.search(p, text, re.I) for p in pats):
                    return new_label, 0.95
            return lbl, sc
        out = self.pipe(text)
        # 支援 tuple、dict、list[dict]
        if isinstance(out, tuple) and len(out)>=2:
            return str(out[0]), float(out[1])
        if isinstance(out, dict):
            return str(out.get("label","other")), float(out.get("score",0.5))
        if isinstance(out, list) and out and isinstance(out[0], dict):
            return str(out[0].get("label","other")), float(out[0].get("score",0.5))
        return "other", 0.5

    # 支援：classify(subject, content) 或 classify(text) 或 classify(subject=..., content=...)
    def classify(self, *args: Any, **kwargs: Any) -> dict:
        subject = content = text = None
        if len(args) == 1:
            text = str(args[0])
        elif len(args) >= 2:
            subject = str(args[0]); content = str(args[1])
        subject = kwargs.get("subject", subject)
        content = kwargs.get("content", content)
        text = kwargs.get("text", text)
        merged = _merge_text(subject, content, text)

        label, score = self._run_pipe(merged)
        # 低信心 + 泛用招呼 → fallback
        if _is_generic(merged) and score < 0.6:
            label = "other"
        # 規則覆寫
        label, score = _apply_rules(subject or "", content or "", label, score)
        return {"label": label, "score": float(score)}
