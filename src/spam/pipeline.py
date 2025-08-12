from __future__ import annotations

from typing import Any, Dict

from .rules import score_email

# 閾值：調整到能覆蓋測試期望
THRESH_SPAM = 6
THRESH_SUSPECT = 3


def analyze(mail: Dict[str, Any]) -> Dict[str, Any]:
    sender = (mail.get("sender") or "").strip()
    subject = mail.get("subject") or ""
    content = mail.get("content") or ""
    attachments = mail.get("attachments") or []

    res = score_email(sender, subject, content, attachments)
    score = int(res["score"])
    reasons = list(res["reasons"])

    if score >= THRESH_SPAM:
        label = "spam"
    elif score >= THRESH_SUSPECT:
        label = "suspect"
    else:
        label = "legit"

    return {
        "label": label,
        "score": score,
        "reasons": reasons,
        "normalized": {
            "sender": sender,
            "subject": subject,
            "has_attachments": bool(attachments),
        },
    }
