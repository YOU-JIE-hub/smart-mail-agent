from __future__ import annotations

from src.spam.pipeline import analyze


def test_ham_is_legit():
    r = analyze(
        {
            "sender": "client@company.com",
            "subject": "請協助報價",
            "content": "請提供合約附件與付款條款",
            "attachments": [],
        }
    )
    assert r["label"] in ("legit", "suspect")
    assert r["score"] < 0.50


def test_obvious_spam():
    r = analyze(
        {
            "sender": "promo@xxx.top",
            "subject": "GET RICH QUICK!!!",
            "content": "Free crypto giveaway: https://x.xyz/win?token=1",
            "attachments": [],
        }
    )
    assert r["label"] == "spam"
    assert r["score"] >= 0.60


def test_suspicious_attachment():
    r = analyze(
        {
            "sender": "it@support.com",
            "subject": "Password reset",
            "content": "Please verify your login",
            "attachments": ["reset.js"],
        }
    )
    assert r["label"] in ("suspect", "spam")
    assert r["score"] >= 0.45
