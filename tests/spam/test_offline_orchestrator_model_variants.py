from smart_mail_agent.spam.orchestrator_offline import orchestrate


def r_false(_):
    return False


def r_true(_):
    return True


def test_model_none_is_ham():
    res = orchestrate("x", r_false, lambda s, c: None, model_threshold=0.6)
    assert res.is_spam is False and res.source in ("model", "fallback")


def test_model_string_spam():
    res = orchestrate("x", r_false, lambda s, c: "spam", model_threshold=0.6)
    assert res.is_spam is True and res.source == "model"


def test_model_score_only_borderline_equals_threshold():
    res = orchestrate("x", r_false, lambda s, c: 0.6, model_threshold=0.6)
    assert res.is_spam is True and res.is_borderline is True and res.source == "model"


def test_model_list_of_dict_best_score():
    def m(s, c):
        return [{"label": "ham", "score": 0.1}, {"label": "spam", "score": 0.91}]

    res = orchestrate("x", r_false, m, model_threshold=0.6)
    assert res.is_spam is True and res.source == "model" and res.action == "drop"


def test_model_list_of_dict_no_scores_uses_first_label():
    def m(s, c):
        return [{"label": "spam"}, {"label": "ham"}]

    res = orchestrate("x", r_false, m, model_threshold=0.6)
    assert res.is_spam is True and res.source == "model"
