"""Compatibility shim for legacy imports:

from inference_classifier import classify_intent
"""

from smart_mail_agent.features.spam.inference_classifier import (  # noqa: F401
    classify_intent,
)

__all__ = ["classify_intent"]
