import src.inference_classifier as ic


def test_smart_truncate_marks_ellipsis():
    text = "A" * 3000
    out = ic.smart_truncate(text, max_chars=1000)
    assert "...\n" in out and len(out) < len(text)


def test_classify_intent_returns_unknown_when_model_fail(monkeypatch):
    monkeypatch.setattr(
        ic, "load_model", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail"))
    )
    ret = ic.classify_intent("s", "b")
    assert ret["label"] in ("unknown", "UNK") and ret["confidence"] == 0.0
