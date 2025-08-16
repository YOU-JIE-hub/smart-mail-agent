from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

RE_QUOTE = re.compile(r"(報價|詢價|報價單|quote|quotation|洽詢|合作|採購|價格|price)", re.I)


def _is_generic(text: str) -> bool:
    t = (text or "").strip().lower()
    return len(t) < 3 or t in {"hi", "hello", "test", "hey", "？", "?"}


class IntentClassifier:
    def __init__(
        self, model_path: str | None = None, pipeline_override: Callable[[str], Any] | None = None
    ):
        self.model_path = model_path or ""
        self.pipeline: Callable[[str], Any] = pipeline_override or (lambda txt: ("其他", 0.0))

    def _normalize_ret(self, ret: Any) -> tuple[str, float]:
        # 常見：list[dict] / (label, score)
        if isinstance(ret, list | tuple) and ret:
            head = ret[0]
            tail = ret[1] if len(ret) > 1 else None
            if isinstance(head, dict):
                lab = (
                    head.get("predicted_label") or head.get("label") or head.get("class") or "其他"
                )
                conf = head.get(
                    "confidence",
                    head.get("score", tail if isinstance(tail, int | float) else 0.0),
                )
                try:
                    conf = float(conf)
                except Exception:
                    conf = 0.0
                return str(lab), conf
            # 一般 (label, score)
            lab = str(head)
            try:
                conf = float(tail) if tail is not None else 1.0
            except Exception:
                conf = 0.0
            return lab, conf

        # dict
        if isinstance(ret, dict):
            lab = ret.get("predicted_label") or ret.get("label") or ret.get("class") or "其他"
            conf = ret.get("confidence", ret.get("score", 0.0))
            try:
                conf = float(conf)
            except Exception:
                conf = 0.0
            return str(lab), conf

        # 純字串
        if isinstance(ret, str):
            return ret, 1.0

        return "其他", 0.0

    def classify(self, subject: str = "", content: str = "") -> dict[str, float | str]:
        text = f"{(subject or '').strip()} {(content or '').strip()}".strip()

        # 先跑一次模型拿分數（之後不論規則或 fallback 都沿用這個分數）
        model_label, model_conf = self._normalize_ret(self.pipeline(text))
        conf = float(model_conf)

        # 規則優先：報價/洽詢等關鍵字
        if RE_QUOTE.search(subject or "") or RE_QUOTE.search(content or ""):
            lab = "業務接洽或報價"
            return {"predicted_label": lab, "confidence": conf, "label": lab, "score": conf}

        # 一般情況
        lab = model_label
        # generic + 低信心 → 改為「其他」，但 confidence 不變
        if _is_generic(subject) and _is_generic(content) and conf < 0.5:
            lab = "其他"

        return {"predicted_label": lab, "confidence": conf, "label": lab, "score": conf}
