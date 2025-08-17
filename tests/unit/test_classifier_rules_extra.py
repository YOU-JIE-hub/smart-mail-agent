from __future__ import annotations

import pytest
from classifier import IntentClassifier


def _pipe_quote(_):  # 模型其實回「其他」，但規則會覆蓋成「業務接洽或報價」
    return [{"label": "其他", "score": 0.77}]


def _pipe_normal(_):
    return [{"label": "售後服務或抱怨", "score": 0.8}]


def test_rule_quote_overrides_label():
    clf = IntentClassifier(pipeline_override=_pipe_quote)
    res = clf.classify(subject="想詢問報價與合作", content="")
    assert res["predicted_label"] == "業務接洽或報價"
    assert res["confidence"] == pytest.approx(0.77, rel=1e-6)


def test_no_fallback_when_not_generic():
    clf = IntentClassifier(pipeline_override=_pipe_normal)
    res = clf.classify(subject="售後服務問題：序號 ABC", content="請協助")
    assert res["predicted_label"] == "售後服務或抱怨"
    assert res["confidence"] == pytest.approx(0.8, rel=1e-6)
