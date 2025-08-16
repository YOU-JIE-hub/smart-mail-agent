from __future__ import annotations

import importlib
import types

import pytest

# 我們用 "smart_mail_agent.spam.spam_filter_orchestrator" 若存在；否則用 rule_filter 做簡化測
spam_orch = None
rule_filter = None
try:
    spam_orch = importlib.import_module("smart_mail_agent.spam.spam_filter_orchestrator")
except Exception:
    pass
try:
    rule_filter = importlib.import_module("smart_mail_agent.spam.rule_filter")
except Exception:
    pass

if not (spam_orch or rule_filter):
    pytest.skip("No offline spam orchestrator available", allow_module_level=True)


def _mk_stub_model(label: str, score: float = 0.9):
    class Stub:
        def predict(self, text: str):
            return {"label": label, "score": score}

    return Stub()


def _mk_stub_rules(spam: bool):
    mod = types.SimpleNamespace()
    mod.contains_keywords = lambda s: spam
    mod.link_ratio = lambda s: 0.9 if spam else 0.0
    return mod


@pytest.mark.parametrize(
    "rule_says_spam, model_says_spam",
    [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ],
)
def test_rule_model_tiebreak(monkeypatch, rule_says_spam, model_says_spam):
    text = "任意內容"
    if spam_orch and hasattr(spam_orch, "decide"):
        # 預期 decide(text, rules, model) -> ("SPAM"/"HAM", score_like)
        monkeypatch.setitem(spam_orch.__dict__, "rules", _mk_stub_rules(rule_says_spam))
        stub_model = _mk_stub_model("SPAM" if model_says_spam else "HAM", 0.91)
        label, conf = spam_orch.decide(text, rules=spam_orch.rules, model=stub_model)
        assert label in {"SPAM", "HAM"}
        assert isinstance(conf, (int, float))
        # 若兩者一致 → 必須一致
        if rule_says_spam == model_says_spam:
            expect = "SPAM" if rule_says_spam else "HAM"
            assert label == expect
    elif rule_filter and hasattr(rule_filter, "decide"):  # 簡化路徑
        stub_rules = _mk_stub_rules(rule_says_spam)
        stub_model = _mk_stub_model("SPAM" if model_says_spam else "HAM", 0.91)
        label, conf = rule_filter.decide(text, rules=stub_rules, model=stub_model)
        assert label in {"SPAM", "HAM"}
        assert isinstance(conf, (int, float))
