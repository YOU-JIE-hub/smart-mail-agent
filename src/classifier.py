from __future__ import annotations
from typing import Any, Callable, Optional

# 嘗試載入正式實作；有些版本只有函式沒有類別
try:
    from smart_mail_agent.inference_classifier import IntentClassifier as _RealIC  # type: ignore
except Exception:
    _RealIC = None

try:
    from smart_mail_agent.inference_classifier import classify_intent as _base_classify  # type: ignore
except Exception:
    _base_classify = None


def _normalize_result(res: Any) -> dict:
    """把 pipeline/底層輸出正規化成 {predicted_label, score, confidence}。"""
    try:
        # 1) 已是 dict
        if isinstance(res, dict):
            out = dict(res)
            # 推導 label/score
            label = (
                out.get("predicted_label")
                or out.get("label")
                or out.get("intent")
                or out.get("category")
            )
            score = (
                out.get("score")
                or out.get("confidence")
                or out.get("prob")
                or out.get("probability")
            )
            if label is None:
                return {"predicted_label": "unknown", "score": 0.0, "confidence": 0.0}
            try:
                score_f = float(score) if score is not None else 1.0
            except Exception:
                score_f = 1.0
            out["predicted_label"] = str(label)
            out["score"] = score_f
            out["confidence"] = out.get("confidence", score_f)
            return out

        # 2) list/tuple
        if isinstance(res, (list, tuple)):
            if not res:
                return {"predicted_label": "unknown", "score": 0.0, "confidence": 0.0}
            first = res[0]
            # [(label, score)] 或 [label, score]
            if isinstance(first, (list, tuple)) and first:
                label = first[0]
                try:
                    sc = float(first[1]) if len(first) > 1 else 1.0
                except Exception:
                    sc = 1.0
                return {"predicted_label": str(label), "score": sc, "confidence": sc}
            # [{'label':..., 'score':...}]
            if isinstance(first, dict):
                return _normalize_result(first)
            # ['label']
            if isinstance(first, str):
                return {"predicted_label": first, "score": 1.0, "confidence": 1.0}
            return {"predicted_label": "unknown", "score": 0.0, "confidence": 0.0}

        # 3) 直接是字串
        if isinstance(res, str):
            return {"predicted_label": res, "score": 1.0, "confidence": 1.0}
    except Exception:
        pass
    return {"predicted_label": "unknown", "score": 0.0, "confidence": 0.0}


def _safe_call_base(subject: str, content: str, sender: Optional[str] = None) -> dict:
    """呼叫底層 classify_intent，忽略多餘參數與簽名差異，並做正規化。"""
    if _base_classify is None:
        text = f"{subject or ''} {content or ''}".strip()
        return {"predicted_label": "none" if not text else "unknown", "score": 0.0, "confidence": 0.0}
    try:
        return _normalize_result(_base_classify(subject, content, sender))  # type: ignore[misc]
    except TypeError:
        return _normalize_result(_base_classify(subject, content))  # type: ignore[misc]


def classify_intent(subject: str, content: str, sender: Optional[str] = None, **_: Any) -> dict:
    """頂層函式 shim：吞掉未知 kwargs，並回傳正規化結構。"""
    return _safe_call_base(subject, content, sender)


if _RealIC is None:
    class IntentClassifier:
        """兼容用分類器：
        - 接受任意 kwargs（如 model_path, pipeline_override），不往下傳。
        - 若提供 pipeline_override 可呼叫，分類時優先使用它。
        - 否則委派到底層 classify_intent。
        """
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def classify(self, subject: str, content: str, sender: Optional[str] = None, **kwargs):
            merged = {**self.kwargs, **kwargs}
            override = merged.get("pipeline_override")
            if callable(override):
                try:
                    return _normalize_result(override(subject, content, sender))
                except TypeError:
                    return _normalize_result(override(subject, content))
            return _safe_call_base(subject, content, sender)

        # 兼容別名
        def predict(self, subject: str, content: str, sender: Optional[str] = None, **kwargs):
            return self.classify(subject, content, sender, **kwargs)

        def __call__(self, subject: str, content: str, sender: Optional[str] = None, **kwargs):
            return self.classify(subject, content, sender, **kwargs)
else:
    # 直接使用正式類別
    IntentClassifier = _RealIC  # type: ignore
