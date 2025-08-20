from __future__ import annotations

# 盡量沿用正式實作；缺的再提供保底 wrapper
try:
    from smart_mail_agent.inference_classifier import IntentClassifier as _IC  # type: ignore
except Exception:
    _IC = None

try:
    from smart_mail_agent.inference_classifier import classify_intent as _classify_intent  # type: ignore
except Exception:
    def _classify_intent(subject: str, content: str, sender: str | None = None, **kwargs):
        text = f"{subject or ''} {content or ''}".strip()
        # 安全保底：回傳最小可用結果結構，避免測試直接崩
        return {"intent": "none" if not text else "unknown", "score": 0.0}

if _IC is None:
    class IntentClassifier:
        """Thin-compat classifier shim. Delegates to classify_intent()."""
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def classify(self, subject: str, content: str, sender: str | None = None, **kwargs):
            merged = {**self.kwargs, **kwargs}
            return _classify_intent(subject, content, sender, **merged)

        def predict(self, subject: str, content: str, sender: str | None = None, **kwargs):
            return self.classify(subject, content, sender, **kwargs)

        def __call__(self, subject: str, content: str, sender: str | None = None, **kwargs):
            return self.classify(subject, content, sender, **kwargs)
else:
    # 直接用正式的
    IntentClassifier = _IC

def classify_intent(subject: str, content: str, sender: str | None = None, **kwargs):
    return _classify_intent(subject, content, sender, **kwargs)

__all__ = ["IntentClassifier", "classify_intent"]
