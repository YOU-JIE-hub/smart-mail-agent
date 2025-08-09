# tests/test_apply_diff.py
# 單元測試模組：apply_diff.py
# 測試目標：update_user_info() 函式，能正確比對使用者資料異動並更新 DB + diff_log

import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from modules.apply_diff import update_user_info

TEST_DB = "tests/mock_users.db"


@pytest.fixture(scope="module", autouse=True)
def setup_mock_db():
    Path("tests").mkdir(exist_ok=True)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # 建立使用者資料表與 diff_log
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            phone TEXT,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS diff_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            欄位 TEXT,
            原值 TEXT,
            新值 TEXT,
            created_at TEXT
        );
    """
    )

    cursor.execute(
        """
        INSERT OR REPLACE INTO users (email, phone, address)
        VALUES ('user@example.com', '0912345678', '台北市信義區')
    """
    )

    conn.commit()
    conn.close()
    yield
    Path(TEST_DB).unlink(missing_ok=True)


def test_update_with_changes():
    content = "電話: 0987654321\n地址: 新北市板橋區"
    result = update_user_info("user@example.com", content, db_path=TEST_DB)
    assert result["status"] == "updated"
    assert "phone" in result["changes"]
    assert "address" in result["changes"]


def test_update_with_no_change():
    content = "電話: 0987654321\n地址: 新北市板橋區"
    result = update_user_info("user@example.com", content, db_path=TEST_DB)
    assert result["status"] == "no_change"


def test_update_partial_change():
    # 僅變更地址
    content = "地址: 桃園市中壢區"
    result = update_user_info("user@example.com", content, db_path=TEST_DB)
    assert result["status"] == "updated"
    assert "address" in result["changes"]


def test_empty_content():
    result = update_user_info("user@example.com", "", db_path=TEST_DB)
    assert result["status"] == "no_change"


def test_user_not_found():
    content = "電話: 0911111111\n地址: 新北市中和區"
    result = update_user_info("notfound@example.com", content, db_path=TEST_DB)
    assert result["status"] == "not_found"
