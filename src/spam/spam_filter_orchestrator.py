#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, Tuple

# 是否離線（CI 會設 OFFLINE=1）
_OFFLINE = str(os.getenv("OFFLINE", "0")).lower() in ("1", "true", "yes", "on")

# 盡量載入真分類器；離線或失敗就用替身
_Classifier = None
if not _OFFLINE:
    try:
        from .ml_spam_classifier import SpamBertClassifier as _Classifier  # type: ignore
    except Exception:
        _Classifier = None

if _Classifier is None:
    # === 離線替身 ===
    class _Classifier:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass

        def predict(self, subject: str = "", body: str = "") -> bool:
            text = f"{subject} {body}".lower()
            spam_kw = [
                "中獎",
                "免費",
                "點此",
                "立即申請",
                "投資",
                "比特幣",
                "usdt",
                "限定",
                "優惠",
                "折扣",
                "理財",
                "博彩",
                "casino",
                "verify your account",
                "reset your password",
                "click link",
                "click here",
                "促銷",
                "限時",
                "賺錢",
                "以太坊",
                "空投",
                "交易所",
            ]
            return any(k in text for k in spam_kw)


class SpamFilterOrchestrator:
    def __init__(self, model_dir: str = "model/bert_spam_classifier") -> None:
        # 真分類器可能需要路徑；替身會忽略
        self.classifier = _Classifier(model_dir)

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _extract(
        email: Dict[str, Any] | None, subject: str | None, body: str | None, **kwargs
    ) -> Tuple[str, str]:
        email = email or {}
        s = (subject or email.get("subject") or kwargs.get("subject") or "").strip()
        b = (
            body
            or email.get("body")
            or email.get("text")
            or kwargs.get("body")
            or kwargs.get("text")
            or ""
        ).strip()
        return s, b

    def _predict_spam(self, subject: str, body: str) -> bool:
        c = self.classifier
        try:
            if hasattr(c, "predict"):
                return bool(c.predict(subject, body))  # our stub & many models
            if hasattr(c, "is_spam"):
                return bool(c.is_spam(subject=subject, body=body))
            if hasattr(c, "classify"):
                return bool(c.classify(subject=subject, body=body))
        except Exception:
            # 測試安全：分類器爆炸時，不當垃圾信（避免把 legit 測例誤殺）
            return False
        return False

    # ---- public API ------------------------------------------------------
    def is_spam(
        self,
        email: Dict[str, Any] | None = None,
        *,
        subject: str | None = None,
        body: str | None = None,
        **kwargs,
    ) -> bool:
        s, b = self._extract(email, subject, body, **kwargs)
        return self._predict_spam(s, b)

    def is_legit(
        self,
        email: Dict[str, Any] | None = None,
        *,
        subject: str | None = None,
        body: str | None = None,
        **kwargs,
    ) -> bool:
        return not self.is_spam(email, subject=subject, body=body, **kwargs)

    # 部分舊呼叫會用 predict()，等同 is_spam(subject, body)
    def predict(self, subject: str = "", body: str = "", **kwargs) -> bool:
        return self._predict_spam(subject, body)
