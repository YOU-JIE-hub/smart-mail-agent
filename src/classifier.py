from __future__ import annotations
from typing import Any, Callable, Optional

def _normalize_result(res: Any) -> dict:
    """把 pipeline/底層輸出正規化成 {predicted_label, score}。"""
    try:
        # 1) 已是 dict
        if isinstance(res, dict):
            if 'predicted_label' in res:
                return res
            label = res.get('label') or res.get('intent') or res.get('category')
            score = res.get('score') or res.get('confidence') or res.get('prob') or res.get('probability')
            if label is not None:
                try:
                    score = float(score) if score is not None else 1.0
                except Exception:
                    score = 1.0
                return {'predicted_label': str(label), 'score': score}
            return {'predicted_label': 'unknown', 'score': 0.0}
        # 2) list/tuple
        if isinstance(res, (list, tuple)):
            if not res:
                return {'predicted_label': 'unknown', 'score': 0.0}
            first = res[0]
            # [(label, score)], 或 [label, score]
            if isinstance(first, (list, tuple)) and first:
                label = first[0]
                sc = 1.0
                if len(first) > 1:
                    try:
                        sc = float(first[1])
                    except Exception:
                        sc = 1.0
                return {'predicted_label': str(label), 'score': sc}
            # [{'label': ..., 'score': ...}]
            if isinstance(first, dict):
                return _normalize_result(first)
            # ['label']
            if isinstance(first, str):
                return {'predicted_label': first, 'score': 1.0}
            return {'predicted_label': 'unknown', 'score': 0.0}
        # 3) 直接是字串
        if isinstance(res, str):
            return {'predicted_label': res, 'score': 1.0}
    except Exception:
        pass
    return {'predicted_label': 'unknown', 'score': 0.0}


# 嘗試載入正式實作；有些版本只有函式沒有類別
try:
    from smart_mail_agent.inference_classifier import IntentClassifier as _RealIC  # type: ignore
except Exception:
    _RealIC = None

try:
    from smart_mail_agent.inference_classifier import classify_intent as _base_classify  # type: ignore
except Exception:
    _base_classify = None

def _safe_call_base(subject: str, content: str, sender: Optional[str] = None) -> dict:
    """呼叫底層 classify_intent，忽略多餘參數與簽名差異。"""
    if _base_classify is None:
        text = f"{subject or ''} {content or ''}".strip()
        return {"intent": "none" if not text else "unknown", "score": 0.0}
    try:
        return _base_classify(subject, content, sender)  # type: ignore[misc]
    except TypeError:
        return _base_classify(subject, content)  # type: ignore[misc]

def classify_intent(subject: str, content: str, sender: Optional[str] = None, **_: Any) -> dict:
    """頂層函式 shim：吞掉未知 kwargs。"""
    return _safe_call_base(subject, content, sender)

if _RealIC is None:
    class IntentClassifier:
        """兼容用分類器：
        - 接受任意 kwargs（如 model_path, pipeline_override），不往下傳。
        - 若提供 pipeline_override 可呼叫，分類時優先使用它。
        - 否則委派到底層 classify_intent。
        """
        def __init__(self, **kwargs: Any):
            self.kwargs = dict(kwargs)
            self._override: Optional[Callable[..., dict]] = self.kwargs.get("pipeline_override")

        def classify(self, subject: str, content: str, sender: Optional[str] = None, **kwargs: Any) -> dict:
            merged = {**self.kwargs, **kwargs}
            override = merged.get("pipeline_override")
            if callable(override):
                try:
                    return _normalize_result(override(subject, content, sender))
                except TypeError:
                    return _normalize_result(override(subject, content))
            return _safe_call_base(subject, content, sender)

        def predict(self, subject: str, content: str, sender: Optional[str] = None, **kwargs: Any) -> dict:
            return self.classify(subject, content, sender, **kwargs)

        def __call__(self, subject: str, content: str, sender: Optional[str] = None, **kwargs: Any) -> dict:
            return self.classify(subject, content, sender, **kwargs)
else:
    # 有正式類別就直接導出；上面的 classify_intent 仍保有寬鬆行為
    IntentClassifier = _RealIC  # type: ignore[misc]
