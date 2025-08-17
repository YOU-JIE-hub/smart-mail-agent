#!/usr/bin/env python3
# 檔案位置：tests/test_init_users_db.py
# 測試 init_db.py 中 init_users_db 功能的細部邏輯：建立 users / diff_log 資料表

import os
import sqlite3

import pytest
from init_db import init_users_db

DB_PATH = "data/users.db"


@pytest.fixture(autouse=True)
def cleanup_db():
    """每次測試前後刪除 users.db"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_users_table_schema():
    """驗證 users 表格建立與欄位是否正確"""
    init_users_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected = ["email", "name", "phone", "address"]
    for col in expected:
        assert col in columns


def test_diff_log_table_schema():
    """驗證 diff_log 表格建立與欄位是否正確"""
    init_users_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(diff_log)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()

    expected = ["id", "email", "欄位", "原值", "新值", "created_at"]
    for col in expected:
        assert col in columns


def test_repeat_init_users_db_does_not_fail():
    """連續初始化不應噴錯"""
    init_users_db()
    init_users_db()
    assert os.path.exists(DB_PATH)
