from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple

_ZH = {
    "send_quote": "業務接洽或報價",
    "reply_faq": "詢問流程或規則",
    "complaint": "售後服務或抱怨",
    "other": "其他",
    "unknown": "其他",
}


def _to_label_score(x: Any) -> Tuple[str, float]:
    if isinstance(x, tuple) and len(x) >= 2:
        return str(x[0]), float(x[1])
    if isinstance(x, dict):
        lbl = x.get("label") or x.get("predicted_label") or "other"
        scr = x.get("score", 0.0)
        return str(lbl), float(scr)
    return "other", 0.0


def _is_generic_greeting(subject: str, content: str) -> bool:
    s = f"{subject} {content}".lower()
    return any(k in s for k in ["hi", "hello", "哈囉", "您好"])


@dataclass
class IntentClassifier:
    model_path: str | None = None
    pipeline_override: Callable[[str], Any] | None = None

    def __post_init__(self) -> None:
        if self.pipeline_override is None:
            self.pipeline_override = lambda text: {"label": "other", "score": 0.0}

    def _apply_rules(self, subject: str, content: str, raw_label: str, score: float) -> Tuple[str, float]:
        text = subject + " " + content
        if any(k in text for k in ["報價", "報 價", "报价", "quote"]):
            return "send_quote", score
        return raw_label, score

    def classify(self, subject: str, content: str) -> Dict[str, Any]:
        raw = self.pipeline_override(f"{subject}\n{content}")
        raw_label, score = _to_label_score(raw)

        is_generic = _is_generic_greeting(subject, content)
        ruled_label, score = self._apply_rules(subject, content, raw_label, score)

        if is_generic and score < 0.5:
            final_en = "other"
        else:
            final_en = ruled_label or "other"

        final_zh = _ZH.get(final_en, "其他")
        return {
            "predicted_label": final_zh,
            "label": final_zh,
            "raw_label": raw_label,
            "score": float(score),
        }
