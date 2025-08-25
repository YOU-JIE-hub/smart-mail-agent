from __future__ import annotations

from modules.spam import SpamFilterOrchestrator, score_spam


def run(subject: str, content: str, sender: str):
    sc = score_spam(subject, content, sender)
    return {
        "is_spam": float(sc["score"]) >= SpamFilterOrchestrator.THRESHOLD,
        "score": float(sc["score"]),
    }
