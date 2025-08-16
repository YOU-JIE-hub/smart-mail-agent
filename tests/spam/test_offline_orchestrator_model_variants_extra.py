import pytest

from smart_mail_agent.spam.orchestrator_offline import orchestrate


def r_false(_):
    return False


def test_model_tuple_score_first():
    res = orchestrate("x", r_false, lambda s, c: (0.7, "spam"), model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"


def test_model_tuple_label_first_unknown_label():
    res = orchestrate("x", r_false, lambda s, c: ("unknown", 0.7), model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"


def test_model_list_dict_mixed_scores():
    def m(s, c):
        return [{"label": "ham", "score": 0.2}, {"label": "spam", "score": 0.65}]

    res = orchestrate("x", r_false, m, model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"
