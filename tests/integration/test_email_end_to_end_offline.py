import json
import types

import pytest

from smart_mail_agent.spam import rules
from smart_mail_agent.spam.orchestrator_offline import orchestrate


def _rule_via_rules_mapping(email):
    # 用 mapping 介面，讓 orchestrator 能讀 'label'
    res = rules.label_email(email)
    return {"label": res["label"], "score": res.get("score", 0.0)}


def test_legit_mapping_basic():
    email = {
        "sender": "client@company.com",
        "subject": "請協助報價",
        "content": "請提供合約附件與付款條款",
        "attachments": [],
    }
    r = rules.label_email(email)  # mapping -> dict（normalized score）
    assert r["label"] in ("legit", "suspect")
    assert isinstance(r["scores"], dict) and "link_ratio" in r["scores"]


def test_obvious_spam_many_links():
    email = {
        "sender": "promo@xxx.top",
        "subject": "GET RICH QUICK!!!",
        "content": ("點此 http://a.io x " * 20) + "end",
        "attachments": [],
    }
    r = rules.label_email(email)
    assert r["label"] == "spam"
    assert r["score"] >= 0.60  # normalized


def test_suspicious_attachment_score_and_label():
    email = {
        "sender": "it@support.com",
        "subject": "Password reset",
        "content": "Please verify your login",
        "attachments": ["reset.js", "readme.txt"],
    }
    r = rules.label_email(email)
    assert r["label"] in ("suspect", "spam")
    assert r["score"] >= 0.45


def test_orchestrate_rule_shortcut_and_model_paths():
    # 規則直接命中 -> drop
    def rule_true(_):
        return True

    res = orchestrate("subj", rule_true, model=None, model_threshold=0.6)
    assert res.is_spam is True and res.source == "rule" and res.action == "drop"

    # 模型高分 spam -> drop
    def m_high(s, c):
        return ("spam", 0.91)

    res = orchestrate("x", lambda _: False, m_high, model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"

    # 模型等於門檻 -> review
    def m_eq(s, c):
        return ("spam", 0.6)

    res = orchestrate("x", lambda _: False, m_eq, model_threshold=0.6)
    assert res.is_spam is True and res.is_borderline is True and res.action == "review"

    # 模型 ham -> route
    def m_ham(s, c):
        return ("ham", 0.2)

    res = orchestrate("x", lambda _: False, m_ham, model_threshold=0.6)
    assert res.is_spam is False and res.action == "route_to_inbox"


def test_orchestrate_model_crash_fallback():
    def m_boom(_s, _c):
        raise RuntimeError("model boom")

    res = orchestrate("x", lambda _: False, m_boom, model_threshold=0.6)
    assert res.is_spam is False and res.source == "fallback"
    assert hasattr(res, "extra") and "model_error" in res.extra
