#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_DEFAULT = "data/quotes.db"
TABLE = "quotes"


def ensure_db_exists(db_path: str = DB_DEFAULT) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as c:
        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            package TEXT NOT NULL,
            pdf_path TEXT,
            created_at TEXT NOT NULL)"""
        )
        c.commit()


def log_quote(
    *, client_name: str, package: str, pdf_path: Optional[str], db_path: str = DB_DEFAULT
) -> int:
    ensure_db_exists(db_path)
    with sqlite3.connect(db_path) as c:
        cur = c.cursor()
        cur.execute(
            f"INSERT INTO {TABLE}(client_name,package,pdf_path,created_at) VALUES(?,?,?,?)",
            (client_name, package, pdf_path, datetime.now().isoformat(timespec="seconds")),
        )
        c.commit()
        return int(cur.lastrowid)


__all__ = ["ensure_db_exists", "log_quote"]
