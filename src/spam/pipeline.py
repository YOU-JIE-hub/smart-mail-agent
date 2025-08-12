from __future__ import annotations

from typing import Any, Dict, List

from .rules import label_email, load_rules


def analyze(email: Dict[str, Any]) -> Dict[str, Any]:
    sender = email.get("sender", "") or ""
    subject = email.get("subject", "") or ""
    content = email.get("content", "") or ""
    attachments = email.get("attachments") or []
    label, score, reasons = label_email(sender, subject, content, attachments)
    return {"label": label, "score": int(score), "reasons": list(reasons), "subject": subject}
