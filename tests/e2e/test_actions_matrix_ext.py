from pathlib import Path


def _h(payload):
    from action_handler import handle

    return handle(payload)


def test_happy_paths():
    cases = [
        ("業務接洽或報價", "send_quote"),
        ("請求技術支援", "reply_support"),
        ("申請修改資訊", "apply_info_change"),
        ("詢問流程或規則", "reply_faq"),
        ("投訴與抱怨", "reply_apology"),
        ("其他", "reply_general"),
    ]
    for label, expect in cases:
        res = _h(
            {
                "predicted_label": label,
                "subject": "S",
                "content": "C",
                "sender": "a@b.com",
            }
        )
        assert res.get("action") == expect
        if expect == "send_quote":
            atts = res.get("attachments") or []
            assert len(atts) >= 1
            p = Path(atts[0])
            assert p.exists() and p.stat().st_size > 0


def test_edge_cases():
    res = _h(
        {
            "predicted_label": "未定義分類",
            "subject": "?",
            "content": "?",
            "sender": "x@b.com",
        }
    )
    assert res.get("action") == "reply_general"

    res = _h({"predicted_label": "其他", "subject": "no sender", "content": "hello"})
    assert res.get("action") == "reply_general"

    res = _h(
        {
            "predicted_label": "請求技術支援",
            "subject": "",
            "content": "錯誤代碼 123",
            "sender": "n@b.com",
        }
    )
    assert res.get("action") == "reply_support"

    res = _h(
        {
            "predicted_label": "詢問流程或規則",
            "subject": "流程",
            "content": "",
            "sender": "n@b.com",
        }
    )
    assert res.get("action") == "reply_faq"

    res = _h(
        {
            "predicted_label": "申請修改資訊",
            "subject": "更新",
            "content": "您好",
            "sender": "z@b.com",
        }
    )
    assert res.get("action") == "apply_info_change"
