from __future__ import annotations

from typing import Any, Dict, List

from .rules import load_rules


class SpamFilterOrchestrator:
    def __init__(self):
        self.rules = load_rules()

    def score(self, subject: str, content: str, sender: str) -> (float, List[str]):
        text = f"{subject} {content}".lower()
        reasons = []
        if any(k.lower() in text for k in self.rules["spam_terms"]):
            reasons.append("zh_keywords")
        return (0.75 if reasons else 0.0), reasons

    def is_legit(
        self, *, subject: str = "", content: str = "", sender: str = "", threshold: float = 0.5, explain: bool = False
    ) -> Dict[str, Any]:
        sc, reasons = self.score(subject, content, sender)
        is_spam = sc >= float(threshold)
        out = {
            "is_spam": is_spam,
            "score": sc,
            "threshold": float(threshold),
            "reasons": reasons,
            "allow": (not is_spam),
        }
        if explain:
            out["explain"] = reasons[:]
        return out
