#!/usr/bin/env python3
from __future__ import annotations

import os

# 是否離線（CI 會設 OFFLINE=1）
_OFFLINE = str(os.getenv("OFFLINE", "0")).lower() in ("1", "true", "yes", "on")

# 先嘗試載入真正的分類器；離線或失敗時就用替身
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
        # 真 classifier 可能會用到 model_dir；替身會忽略
        self.classifier = _Classifier(model_dir)

    def is_spam(self, email: dict) -> bool:
        subject = (email.get("subject") or "").strip()
        body = (email.get("body") or email.get("text") or "").strip()
        return bool(self.classifier.predict(subject, body))

    # 兼容可能的呼叫方式
    def predict(self, subject: str = "", body: str = "") -> bool:
        return bool(self.classifier.predict(subject, body))
