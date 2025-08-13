#!/usr/bin/env python3
from __future__ import annotations

from src.policy_engine import apply_policies, apply_policy


def test_low_confidence_review(tmp_path):
    p = tmp_path / "policy.yaml"
    p.write_text(
        "low_confidence_review:\n  threshold: 0.6\n  cc: ['rev@example.com']\n", encoding="utf-8"
    )
    req = {"predicted_label": "reply_faq", "confidence": 0.5, "attachments": []}
    out = apply_policy({"action_name": "reply_faq", "meta": {}, "cc": []}, req, str(p))
    assert out["meta"]["require_review"] is True
    assert "rev@example.com" in out["cc"]


def test_apply_policies_alias(tmp_path):
    p = tmp_path / "policy.yaml"
    p.write_text("{}", encoding="utf-8")
    req = {"attachments": []}
    out = apply_policies({"action_name": "reply_general", "meta": {}, "cc": []}, req, str(p))
    assert out["action_name"] == "reply_general"
