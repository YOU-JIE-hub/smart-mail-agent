from __future__ import annotations

# Re-export the canonical spam orchestrator API with explicit imports (no star import)
from smart_mail_agent.spam.spam_filter_orchestrator import (
    SpamFilterOrchestrator,
    score_spam,
)

__all__ = ["SpamFilterOrchestrator", "score_spam"]
