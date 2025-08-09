#!/usr/bin/env python3
# 檔案位置：tests/test_init_processed_mails_db.py
# 測試 init_db.py 中 init_processed_mails_db 功能是否正確建立資料庫與表格

import os
import sqlite3

import pytest

from init_db import init_processed_mails_db

DB_PATH = "data/db/processed_mails.db"


@pytest.fixture(autouse=True)
def cleanup_db():
    """測試前後清除 processed_mails.db，避免污染"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_processed_mails_table_created():
    """驗證 processed_mails 表格建立成功且欄位正確"""
    init_processed_mails_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(processed_mails)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected = ["uid", "subject", "sender"]
    for col in expected:
        assert col in columns


def test_repeat_init_processed_mails_db_does_not_fail():
    """重複執行初始化不應報錯"""
    init_processed_mails_db()
    init_processed_mails_db()
    assert os.path.exists(DB_PATH)
