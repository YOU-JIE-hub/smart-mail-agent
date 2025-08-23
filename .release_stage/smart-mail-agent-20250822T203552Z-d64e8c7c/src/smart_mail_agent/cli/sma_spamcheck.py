from __future__ import annotations
from smart_mail_agent.spam.spam_filter_orchestrator import SpamFilterOrchestrator
def run(subject: str, content: str, sender: str):
    return SpamFilterOrchestrator().is_legit(subject, content, sender)
