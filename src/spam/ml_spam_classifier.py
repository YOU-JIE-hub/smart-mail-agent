from __future__ import annotations
import importlib as _im

_mod = _im.import_module("smart_mail_agent.spam.ml_spam_classifier")
# 只導出對方顯式 API，如未定義 __all__ 則不污染命名空間
__all__ = getattr(_mod, "__all__", [])
for _k in __all__:
    globals()[_k] = getattr(_mod, _k)
del _im, _mod
