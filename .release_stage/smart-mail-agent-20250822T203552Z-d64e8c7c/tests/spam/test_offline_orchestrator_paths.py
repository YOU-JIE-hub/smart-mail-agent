from __future__ import annotations

from smart_mail_agent.spam.orchestrator_offline import orchestrate


def r_true(_):
    return True


def r_false(_):
    return False


def m_spam_high(_):
    return {"label": "SPAM", "score": 0.95}


def m_spam_eq_thr(_):
    return {"label": "SPAM", "score": 0.6}


def m_spam_low(_):
    return ("SPAM", 0.4)


def m_ham(_):
    return [{"label": "HAM", "score": 0.99}]


def m_broken(_):
    raise RuntimeError("model boom")


def test_TT_rule_shortcuts_to_spam():
    res = orchestrate("x", r_true, m_ham, model_threshold=0.6)
    assert res.is_spam is True and res.source == "rule" and res.action == "drop"


def test_FT_model_decides_spam_high():
    res = orchestrate("x", r_false, m_spam_high, model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"


def test_FT_model_borderline_equals_threshold():
    res = orchestrate("x", r_false, m_spam_eq_thr, model_threshold=0.6)
    assert res.is_spam is True and res.is_borderline is True and res.action == "review"


def test_FF_model_not_spam_low_score():
    res = orchestrate("x", r_false, m_spam_low, model_threshold=0.6)
    assert res.is_spam is False and res.action == "route_to_inbox"


def test_FF_model_says_ham():
    res = orchestrate("x", r_false, m_ham, model_threshold=0.6)
    assert res.is_spam is False and res.action == "route_to_inbox"


def test_Ffallback_model_crash_falls_back_to_rule():
    res = orchestrate("x", r_false, m_broken, model_threshold=0.6)
    assert res.is_spam is False and res.source == "fallback"
    assert "model_error" in res.extra
