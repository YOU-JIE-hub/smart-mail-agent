#!/usr/bin/env python3
# 檔案位置：modules/quote_logger.py
# 模組用途：報價記錄落庫（SQLite）
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_DEFAULT = "data/quotes.db"
TABLE = "quotes"


def ensure_db_exists(db_path: str = DB_DEFAULT) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer TEXT NOT NULL,
                package  TEXT NOT NULL,
                total    REAL NOT NULL,
                file_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def log_quote(
    db_path: str,
    customer: str,
    package: str,
    total: float,
    file_path: Optional[str] = None,
) -> int:
    """
    寫入一筆報價記錄，回傳 row id
    """
    ensure_db_exists(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {TABLE} (customer, package, total, file_path, created_at) VALUES (?,?,?,?,?)",
            (
                customer,
                package,
                float(total),
                file_path,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


__all__ = ["ensure_db_exists", "log_quote"]
