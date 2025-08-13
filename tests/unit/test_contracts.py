#!/usr/bin/env python3
from __future__ import annotations

from src.sma_types import normalize_request, normalize_result


def test_request_normalization_defaults():
    raw = {"subject": "s", "from": "a@b.com", "body": "x"}
    req = normalize_request(raw).dict(by_alias=True)
    assert req["confidence"] == -1.0
    assert req["predicted_label"] == ""


def test_result_normalization_prefix_and_fields():
    raw = {
        "action_name": "reply_faq",
        "subject": "退款流程說明",
        "body": "text",
        "request_id": "r",
        "intent": "reply_faq",
        "confidence": 0.5,
    }
    res = normalize_result(raw).dict()
    assert res["subject"].startswith("[自動回覆] ")
    assert res["ok"] is True
    assert "duration_ms" in res
