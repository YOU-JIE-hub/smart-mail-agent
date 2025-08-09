#!/usr/bin/env python3
# 檔案位置：scripts/init_users_db.py
# 模組用途：建立標準 SQLite users 資料表，含自動測試資料（可用於開發 / 展示）

import sqlite3
from pathlib import Path

from utils.logger import logger

DB_PATH = "data/users.db"
TABLE_NAME = "users"


def init_users_db():
    Path("data").mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    logger.info("初始化使用者資料表：%s", TABLE_NAME)

    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    cursor.execute(
        f"""
        CREATE TABLE {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT
        )
    """
    )

    test_data = [
        ("test@example.com", "測試用戶", "0912345678", "台北市信義區"),
        ("alice@trusted.org", "Alice Wang", "0933222111", "新北市板橋區"),
        ("bob@demo.com", "Bob Chen", "0988777666", "高雄市鼓山區"),
    ]

    cursor.executemany(
        f"""
        INSERT INTO {TABLE_NAME} (email, name, phone, address)
        VALUES (?, ?, ?, ?)
    """,
        test_data,
    )

    conn.commit()
    conn.close()
    logger.info("資料表初始化完成，已插入 %d 筆測試資料", len(test_data))


if __name__ == "__main__":
    init_users_db()
