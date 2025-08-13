# -*- coding: utf-8 -*-
from __future__ import annotations

from policy_engine import apply_policies


def test_policy_require_review_on_low_conf():
    req = {"predicted_label": "reply_faq", "confidence": 0.2, "subject": "FAQ?", "from": "u@x"}
    res = {"ok": True, "action_name": "reply_faq", "subject": "[自動回覆] FAQ"}
    out = apply_policies(req, res)
    assert out.get("meta", {}).get("require_review") is True
    assert "review@company.com" in (out.get("cc") or [])
