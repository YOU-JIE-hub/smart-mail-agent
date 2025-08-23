from __future__ import annotations

from smart_mail_agent.spam.orchestrator_offline import orchestrate


def rule_dict_true(_):
    return {"is_spam": True}


def rule_dict_false(_):
    return {"is_spam": False}


def model_tuple(_):
    return ("SPAM", 0.7)


def model_list_of_dict(_):
    return [{"label": "SPAM", "score": 0.65}]


def model_weird(_):
    return {"label": "???", "score": 0.9}


def test_rule_accepts_dict_shape():
    res = orchestrate("x", rule_dict_true, model_weird, model_threshold=0.6)
    assert res.is_spam and res.source == "rule"


def test_model_tuple_shape_accepted():
    res = orchestrate("x", rule_dict_false, model_tuple, model_threshold=0.6)
    assert res.is_spam and res.source == "model"


def test_model_list_of_dict_shape_accepted():
    res = orchestrate("x", rule_dict_false, model_list_of_dict, model_threshold=0.6)
    assert res.is_spam and res.source == "model"
