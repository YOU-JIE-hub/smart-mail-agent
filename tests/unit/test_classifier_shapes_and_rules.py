from __future__ import annotations
from classifier import IntentClassifier

def _pipe_dict(_):  # list[dict]
    return [{"label": "詢價", "score": 0.88}]

def _pipe_tuple(_):  # (label, score)
    return ("其他", 0.66)

def _pipe_full_dict(_):  # list[dict] with predicted_label/confidence
    return [{"predicted_label": "其他", "confidence": 0.12}]

def test_rule_override_keeps_model_confidence():
    clf = IntentClassifier(pipeline_override=_pipe_dict)
    r = clf.classify(subject="報價一下", content="")
    assert r["predicted_label"] == "業務接洽或報價"
    assert isinstance(r["confidence"], float)

def test_generic_low_confidence_fallback_preserves_score():
    clf = IntentClassifier(pipeline_override=_pipe_tuple)
    r = clf.classify("Hi", "Hello")
    assert r["predicted_label"] == "其他"
    assert r["confidence"] == 0.66

def test_non_generic_low_confidence_no_fallback():
    clf = IntentClassifier(pipeline_override=_pipe_full_dict)
    r = clf.classify("正常主旨", "內容不是 hello/hi")
    assert r["label"] == "其他"
    assert r["confidence"] == 0.12
