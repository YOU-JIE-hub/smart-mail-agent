from smart_mail_agent.spam.orchestrator_offline import SpamFilterOrchestratorOffline, Thresholds


def test_nested_empty_href_and_hidden_elements():
    html = '<a href=""> <span style="display:none">bait</span>點此</a>  文本'
    orch = SpamFilterOrchestratorOffline(
        thresholds=Thresholds(link_ratio_drop=0.40, link_ratio_review=0.20)
    )
    out = orch.decide("x", html)
    assert out["action"] in ("drop", "review")
    assert any(r.startswith("rule:link_ratio>=") for r in out.get("reasons", []))
