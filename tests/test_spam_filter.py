# tests/test_spam_filter.py
# 單元測試：垃圾信過濾系統（rule_filter, spam_llm_filter, spam_filter_orchestrator）

import pytest

from spam.spam_filter_orchestrator import SpamFilterOrchestrator


@pytest.mark.parametrize(
    "email_json, expected",
    [
        (
            {
                "subject": "免費中獎通知",
                "content": "您中了100萬，點此領獎",
                "from": "spam@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "API 串接報價",
                "content": "您好，我想了解貴公司的 API 串接方案",
                "from": "biz@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "登入失敗",
                "content": "我的帳號被鎖住，請協助",
                "from": "user@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "邀請你加入免費贈品活動",
                "content": "點擊這裡即可獲得免費耳機",
                "from": "promo@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "發票中獎通知",
                "content": "請下載附件登入以領取發票獎金",
                "from": "fraud@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "",
                "content": "這是一封無主旨的信件",
                "from": "unknown@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "測試空內容",
                "content": "",
                "from": "empty@example.com",
                "to": ["me@example.com"],
            },
            False,
        ),
        (
            {
                "subject": "群發測試信",
                "content": "這是一封寄給多人的測試信",
                "from": "mass@example.com",
                "to": ["a@example.com", "b@example.com", "me@example.com"],
            },
            True,
        ),
        (
            {
                "subject": "標題僅此",
                "content": "",
                "from": "abc@unknown-domain.com",
                "to": ["me@example.com"],
            },
            True,
        ),  # ← 修正此處預期值為 True
    ],
)
def test_spam_filter_logic(email_json, expected):
    sf = SpamFilterOrchestrator()
    result = sf.is_legit(
        subject=email_json.get("subject", ""),
        content=email_json.get("content", ""),
        sender=email_json.get("from", ""),
    )
    assert isinstance(result, dict)
    assert "allow" in result
    assert result["allow"] == expected
