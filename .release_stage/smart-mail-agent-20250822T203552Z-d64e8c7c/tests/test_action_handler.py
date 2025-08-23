#!/usr/bin/env python3
# 檔案位置：tests/test_action_handler.py
# 測試用途：驗證六大分類動作決策、附件產出、離線不寄信。

from __future__ import annotations

import importlib
import os
from pathlib import Path

os.environ["OFFLINE"] = "1"
os.environ.setdefault("SMTP_FROM", "noreply@example.com")

ah = importlib.import_module("action_handler")

SAMPLE = {
    "subject": "測試主旨",
    "content": "測試內容",
    "sender": "user@example.com",
    "confidence": 0.9,
}


def _run(label: str):
    payload = dict(SAMPLE)
    payload["predicted_label"] = label
    return ah.handle(payload)


def test_support():
    r = _run("請求技術支援")
    assert r["ok"] is True and r["action_name"] == "reply_support"
    assert "[支援回覆]" in r["subject"]


def test_info_change():
    r = _run("申請修改資訊")
    assert r["ok"] is True and r["action_name"] == "apply_info_change"
    assert "[資料更新受理]" in r["subject"]


def test_faq():
    r = _run("詢問流程或規則")
    assert r["ok"] is True and r["action_name"] == "reply_faq"
    assert "[流程說明]" in r["subject"]


def test_apology():
    r = _run("投訴與抱怨")
    assert r["ok"] is True and r["action_name"] == "reply_apology"
    assert "[致歉回覆]" in r["subject"]


def test_quote_with_attachment():
    r = _run("業務接洽或報價")
    assert r["ok"] is True and r["action_name"] == "send_quote"
    assert "[報價]" in r["subject"]
    assert "attachments" in r and len(r["attachments"]) >= 1
    for p in r["attachments"]:
        assert Path(p).exists()


def test_other_fallback():
    r = _run("其他")
    assert r["ok"] is True and r["action_name"] == "reply_general"
    assert "[自動回覆]" in r["subject"]


def test_unknown_label_as_general():
    r = _run("未定義標籤")
    assert r["ok"] is True and r["action_name"] == "reply_general"
