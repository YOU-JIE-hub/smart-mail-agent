from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

LABEL_ZH = {
    "other": "其他",
    "quote": "業務接洽或報價",
    "sales": "業務接洽或報價",
    "refund": "詢問流程或規則",
    "process": "詢問流程或規則",
    "support": "售後服務或抱怨",
}


def _norm_pipe(out: Any) -> Tuple[str, float, Dict[str, Any]]:
    """接受多種形狀：str | (label,score) | dict"""
    if isinstance(out, str):
        return out, 0.0, {"raw_label": out, "score": 0.0}
    if isinstance(out, tuple) and len(out) >= 2:
        return str(out[0]), float(out[1]), {"raw": out}
    if isinstance(out, dict):
        label = out.get("label") or out.get("raw_label") or "other"
        score = float(out.get("score") or 0.0)
        return str(label), score, out
    return "other", 0.0, {"raw": out}


def _rule_override(subject: str, content: str) -> str | None:
    s = (subject or "") + " " + (content or "")
    if any(k in s for k in ("報價", "詢價", "合作")):
        return "業務接洽或報價"
    if any(k in s for k in ("售後", "抱怨", "投訴")):
        return "售後服務或抱怨"
    if any(k in s for k in ("流程", "退費", "退款")):
        return "詢問流程或規則"
    return None


def _is_generic(subject: str, content: str) -> bool:
    s = (subject or "").lower() + " " + (content or "").lower()
    return any(x in s for x in ("hi", "hello", "您好", "哈囉"))


class IntentClassifier:
    def __init__(self, model_path: str = "", pipeline_override: Callable[..., Any] | None = None):
        self.model_path = model_path
        self._pipe = pipeline_override

    def classify(self, subject: str = "", content: str = "") -> Dict[str, Any]:
        # 模型輸出正規化
        raw_label, score, extra = _norm_pipe(self._pipe() if callable(self._pipe) else {"label": "other", "score": 0.0})
        # 先把英文/代碼映射到中文
        label_zh = LABEL_ZH.get(
            raw_label,
            raw_label if raw_label in ("其他", "售後服務或抱怨", "業務接洽或報價", "詢問流程或規則") else "其他",
        )
        # 規則覆寫（保留原 score）
        rule = _rule_override(subject, content)
        predicted = rule or label_zh
        # generic + 低信心 -> 其他（保留分數）
        if _is_generic(subject, content) and score < 0.5:
            predicted = "其他"
        return {
            "label": label_zh,
            "predicted_label": predicted,
            "raw_label": raw_label,
            "confidence": float(score),
            **({"extra": extra} if extra else {}),
        }
