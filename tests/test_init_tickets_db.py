#!/usr/bin/env python3
# 檔案位置：tests/test_init_tickets_db.py
# 測試 init_db.py 中 init_tickets_db 功能是否能成功建立 tickets.db 與資料表欄位

import os
import sqlite3

import pytest
from init_db import init_tickets_db

DB_PATH = "data/tickets.db"


@pytest.fixture(autouse=True)
def cleanup_db():
    """測試前後刪除 tickets.db 避免污染"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_support_tickets_table_created():
    """驗證 support_tickets 表格存在且欄位齊全"""
    init_tickets_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(support_tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected = [
        "id",
        "subject",
        "content",
        "summary",
        "sender",
        "category",
        "confidence",
        "created_at",
        "updated_at",
        "status",
        "priority",
    ]
    for col in expected:
        assert col in columns


def test_repeat_init_tickets_db_does_not_fail():
    """重複執行不應失敗"""
    init_tickets_db()
    init_tickets_db()
    assert os.path.exists(DB_PATH)
