#!/usr/bin/env python3
# 檔案位置: tests/spam/test_offline_orchestrator_e2e.py
# 測試用途: 以最短路徑驗證 orchestrator 的 drop/review/route 決策

from __future__ import annotations

from smart_mail_agent.spam.orchestrator_offline import (
    SpamFilterOrchestratorOffline,
    Thresholds,
)


def test_e2e_drop_by_keyword():
    orch = SpamFilterOrchestratorOffline()
    out = orch.decide("免費贈品", "恭喜中獎，點此連結")
    assert out["action"] == "drop"
    assert "rule:keyword" in out["reasons"]


def test_e2e_drop_or_review_by_link_ratio():
    orch = SpamFilterOrchestratorOffline(
        thresholds=Thresholds(link_ratio_drop=0.50, link_ratio_review=0.30)
    )
    html_body = (
        '<a href="#">免費</a> <a href="#">中獎</a> <a href="#">點此連結</a> 很少文字'
    )
    out = orch.decide("一般通知", html_body)
    assert out["action"] in ("drop", "review")
    assert any(r.startswith("rule:link_ratio>=") for r in out["reasons"])


def test_e2e_route_normal_mail():
    orch = SpamFilterOrchestratorOffline()
    out = orch.decide("API 串接報價需求", "您好，我們想瞭解企業版報價與 SLA。")
    assert out["action"] == "route"
    assert out["scores"]["link_ratio"] == 0.0
