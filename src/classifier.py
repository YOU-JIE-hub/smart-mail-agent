"""Compatibility shim for legacy tests:

    from classifier import IntentClassifier

Re-exports the modern implementation from smart_mail_agent.core.classifier.
"""

from smart_mail_agent.core.classifier import IntentClassifier  # noqa: F401

__all__ = ["IntentClassifier"]
