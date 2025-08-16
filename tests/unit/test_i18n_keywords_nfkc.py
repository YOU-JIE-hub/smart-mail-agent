from smart_mail_agent.spam.orchestrator_offline import SpamFilterOrchestratorOffline


def test_fullwidth_english_and_emoji_detected():
    orch = SpamFilterOrchestratorOffline()
    out = orch.decide("ＦＲＥＥ 🎁", "請點此")
    assert out["action"] == "drop" and out["source"] == "keyword"
