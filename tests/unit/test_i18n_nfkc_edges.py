from smart_mail_agent.spam.orchestrator_offline import SpamFilterOrchestratorOffline


def test_mixed_scripts_with_zwsp():
    s = "F\u200bR\u200bE\u200bE"  # FREE with zero-width spaces
    out = SpamFilterOrchestratorOffline().decide(s, "請點此")
    # 沒有連結比優勢、關鍵字中間夾 ZWSP，合理結果是 route；若之後加了 ZWSP 清除，可能會 drop。
    assert out["action"] in ("route", "drop")
