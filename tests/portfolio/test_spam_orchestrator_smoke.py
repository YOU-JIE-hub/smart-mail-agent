import importlib
m = importlib.import_module("smart_mail_agent.spam.spam_filter_orchestrator")
def test_orchestrator_has_public_symbol():
    names = ("main", "orchestrate", "SpamFilterOrchestrator")
    assert any(hasattr(m, n) for n in names)
