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
                    return override(subject, content, sender)
                except TypeError:
                    return override(subject, content)
            return _safe_call_base(subject, content, sender)

        def predict(self, subject: str, content: str, sender: Optional[str] = None, **kwargs: Any) -> dict:
            return self.classify(subject, content, sender, **kwargs)

        def __call__(self, subject: str, content: str, sender: Optional[str] = None, **kwargs: Any) -> dict:
            return self.classify(subject, content, sender, **kwargs)
else:
    # 有正式類別就直接導出；上面的 classify_intent 仍保有寬鬆行為
    IntentClassifier = _RealIC  # type: ignore[misc]
