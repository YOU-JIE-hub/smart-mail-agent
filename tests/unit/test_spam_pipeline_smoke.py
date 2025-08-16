import importlib, sys, pytest
sys.path.insert(0, "src")
pl = importlib.import_module("smart_mail_agent.spam.pipeline")

def test_orchestrate_rules_only_if_present(monkeypatch):
    orchestrate = getattr(pl, "orchestrate", None)
    if orchestrate is None:
        pytest.skip("orchestrate not implemented")
    class DummyModel:
        def predict_proba(self, X): return [[0.1, 0.9] for _ in X]
    # 若模組有 load_model，就替換掉避免依賴外部資源
    if hasattr(pl, "load_model"):
        monkeypatch.setattr(pl, "load_model", lambda: DummyModel())
    res = orchestrate(["你中獎了！點此領獎"], rules_only=True)
    assert isinstance(res, dict)
    assert "verdict" in res
