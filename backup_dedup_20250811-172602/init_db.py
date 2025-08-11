#!/usr/bin/env python3
# 檔案位置：init_db.py
# 模組用途：建立 emails_log / users+diff_log / processed_mails / support_tickets 四個資料庫

import os
import sqlite3
from pathlib import Path


def _ensure_dir(p: str) -> None:
    Path(os.path.dirname(p) or ".").mkdir(parents=True, exist_ok=True)


def init_emails_log_db(db_path: str = "data/emails_log.db") -> None:
    _ensure_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS emails_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                content TEXT,
                summary TEXT,
                predicted_label TEXT,
                confidence REAL,
                action TEXT,
                error TEXT,
                created_at TEXT
            )
        """
        )
        conn.commit()


def init_users_db(db_path: str = "data/users.db") -> None:
    _ensure_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute(
            """
            CREATE TABLE users (
                email TEXT PRIMARY KEY,
                name TEXT,
                phone TEXT,
                address TEXT
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS diff_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                欄位 TEXT,
                原值 TEXT,
                新值 TEXT,
                created_at TEXT
            )
        """
        )
        conn.commit()


def init_processed_mails_db(db_path: str = "data/db/processed_mails.db") -> None:
    _ensure_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_mails (
                uid TEXT PRIMARY KEY,
                subject TEXT,
                sender TEXT
            )
        """
        )
        conn.commit()


def init_tickets_db(db_path: str = "data/tickets.db") -> None:
    _ensure_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                content TEXT,
                summary TEXT,
                sender TEXT,
                category TEXT,
                confidence REAL,
                created_at TEXT,
                updated_at TEXT,
                status TEXT,
                priority TEXT
            )
        """
        )
        conn.commit()


if __name__ == "__main__":
    init_emails_log_db()
    init_users_db()
    init_processed_mails_db()
    init_tickets_db()
    print("OK: 初始化完成")
