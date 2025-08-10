#!/usr/bin/env python3
from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

# 是否離線（CI 可設 OFFLINE=1）
_OFFLINE = str(os.getenv("OFFLINE", "0")).lower() in ("1", "true", "yes", "on")

# 嘗試載入真分類器；離線或失敗就用替身
_Classifier = None  # type: ignore
if not _OFFLINE:
    try:
        from .ml_spam_classifier import SpamBertClassifier as _Classifier  # type: ignore
    except Exception:
        _Classifier = None  # 失敗時走替身

if _Classifier is None:
    # === 離線替身（零依賴）===
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
    """統一對外 API：
    - analyze(...) -> dict
    - is_spam(...) -> dict
    - is_legit(...) -> dict
    - predict(subject, body) -> dict  （為相容舊呼叫）
    """

    def __init__(self, model_dir: str = "model/bert_spam_classifier") -> None:
        self._engine_name = "stub" if _Classifier is None else "bert"
        # 真分類器可能需要路徑；替身會忽略
        try:
            self.classifier = _Classifier(model_dir)  # type: ignore
        except Exception:
            # 就算不是 OFFLINE，也要能回退到替身
            self._engine_name = "stub"
            self.classifier = _Classifier()  # type: ignore

    # ------------------ helpers ------------------
    @staticmethod
    def _extract(
        email: Optional[Dict[str, Any]], subject: Optional[str], body: Optional[str], **kwargs
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

    def _predict_spam(self, subject: str, body: str) -> Tuple[bool, str, Optional[float], str]:
        """回傳：(is_spam, reason, score, engine)"""
        c = self.classifier
        score: Optional[float] = None
        try:
            # 常見介面：predict(subject, body) -> bool
            if hasattr(c, "predict"):
                is_spam = bool(c.predict(subject, body))  # type: ignore[arg-type]
                return is_spam, "model_predict", score, self._engine_name
            # 其他可能的介面
            if hasattr(c, "is_spam"):
                is_spam = bool(c.is_spam(subject=subject, body=body))  # type: ignore[call-arg]
                return is_spam, "model_is_spam", score, self._engine_name
            if hasattr(c, "classify"):
                is_spam = bool(c.classify(subject=subject, body=body))  # type: ignore[call-arg]
                return is_spam, "model_classify", score, self._engine_name
        except Exception:
            # 任何模型錯誤都退回啟發式，避免測試被模型波及
            pass

        # 最終保底：簡單啟發式
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
        is_spam = any(k in text for k in spam_kw)
        return is_spam, "heuristic_fallback", None, "stub"

    # ------------------ public API ------------------
    def analyze(
        self,
        email: Optional[Dict[str, Any]] = None,
        *,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        s, b = self._extract(email, subject, body, **kwargs)
        is_spam, reason, score, engine = self._predict_spam(s, b)
        return {
            "subject": s,
            "body_snippet": b[:160],
            "is_spam": is_spam,
            "is_legit": (not is_spam),
            "score": score,
            "engine": engine,
            "reason": reason,
        }

    def is_spam(
        self,
        email: Optional[Dict[str, Any]] = None,
        *,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        return self.analyze(email, subject=subject, body=body, **kwargs)

    def is_legit(
        self,
        email: Optional[Dict[str, Any]] = None,
        *,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        return self.analyze(email, subject=subject, body=body, **kwargs)

    # 舊版相容：一些呼叫會用 predict()，這裡也回傳 dict
    def predict(self, subject: str = "", body: str = "", **kwargs) -> Dict[str, Any]:
        return self.analyze(None, subject=subject, body=body, **kwargs)
