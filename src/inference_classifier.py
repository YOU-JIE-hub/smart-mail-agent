from __future__ import annotations
from typing import Any, Dict
from smart_mail_agent.classifier import classify_intent as _classify_intent

def classify_intent(subject: str | None, content: str | None) -> Dict[str, Any]:
    return _classify_intent(subject, content)
