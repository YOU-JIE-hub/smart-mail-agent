#!/usr/bin/env python3
# 檔案位置：tests/test_init_emails_log_db.py
# 測試 init_db.py 中 init_emails_log_db 功能是否能正確建立 emails_log.db 與表格欄位

import os
import sqlite3

import pytest
from init_db import init_emails_log_db

DB_PATH = "data/emails_log.db"


@pytest.fixture(autouse=True)
def cleanup_db():
    """測試前後清除資料庫檔案，避免交叉污染"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_emails_log_table_created():
    """驗證 emails_log 表格建立成功且欄位齊全"""
    init_emails_log_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(emails_log)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected = [
        "id",
        "subject",
        "content",
        "summary",
        "predicted_label",
        "confidence",
        "action",
        "error",
        "created_at",
    ]
    for col in expected:
        assert col in columns


def test_repeat_init_emails_log_db_does_not_fail():
    """重複初始化不應失敗"""
    init_emails_log_db()
    init_emails_log_db()
    assert os.path.exists(DB_PATH)
