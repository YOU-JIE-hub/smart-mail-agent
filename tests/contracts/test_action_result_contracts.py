from __future__ import annotations

import json
from pathlib import Path

from smart_mail_agent.sma_types import ActionResult, AttachmentMeta

ALLOWED_ACTIONS = {
    "send_quote",
    "reply_faq",
    "reply_support",
    "reply_general",
    "reply_apology",
    "sales",
    "apply_info_change",
}
ALLOWED_CODES = {"OK", "INPUT_INVALID", "EXTERNAL_FAIL", "INTERNAL_ERROR"}


def test_contracts_matrix_schema(_ensure_matrix):
    root = Path(__file__).resolve().parents[2]
    data = json.loads(
        (root / "data" / "output" / "matrix" / "matrix_summary.json").read_text(
            encoding="utf-8"
        )
    )
    cases = data.get("cases", [])
    assert cases, "矩陣沒有案例"

    for c in cases:
        assert c.get("action") in ALLOWED_ACTIONS
        payload = {
            "action": c["action"],
            "ok": bool(c.get("ok", True)),
            "code": c.get("code", "OK"),
            "message": c.get("message", ""),
            "output": c.get("output"),
            "attachments": [
                (
                    AttachmentMeta(path=a, exists=True).model_dump()
                    if isinstance(a, str)
                    else a
                )
                for a in (c.get("attachments") or [])
            ],
            "request_id": c.get("request_id"),
            "spent_ms": c.get("spent_ms"),
        }
        ar = ActionResult(**payload)
        assert ar.code in ALLOWED_CODES
        for att in ar.attachments:
            p = Path(att.path)
            if not p.is_absolute():
                p = root / att.path
            assert p.exists(), f"附件不存在：{att.path}"
