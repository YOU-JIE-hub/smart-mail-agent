#!/usr/bin/env python3
# 檔案位置：tools/db_migrate_emails_log.py
# 模組用途：將舊表 email_logs 併入 emails_log，補欄位並避免 UNIQUE 衝突

import sqlite3
from pathlib import Path

DB_PATH = Path("data/emails_log.db")
FINAL = "emails_log"
LEGACY = "email_logs"

REQUIRED = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
    ("subject", "TEXT"),
    ("content", "TEXT"),
    ("summary", "TEXT"),
    ("predicted_label", "TEXT"),
    ("confidence", "REAL"),
    ("action", "TEXT"),
    ("error", "TEXT"),
    ("created_at", "TEXT"),
]


def list_tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def cols_of(conn, table):
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]


def ensure_final(conn):
    cols = ", ".join([f"{n} {t}" for n, t in REQUIRED])
    conn.execute(f"CREATE TABLE IF NOT EXISTS {FINAL} ({cols})")
    conn.commit()


def align_columns(conn, table):
    existing = set(cols_of(conn, table))
    for name, typ in REQUIRED:
        if name not in existing:
            print(f"[migrate] {table} 新增欄位：{name} {typ}")
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {typ}")
            conn.commit()


def migrate():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        ensure_final(conn)
        tables = list_tables(conn)

        if LEGACY in tables and FINAL not in tables:
            print("[migrate] 將 email_logs 更名為 emails_log")
            conn.execute(f"ALTER TABLE {LEGACY} RENAME TO {FINAL}")
            conn.commit()
            align_columns(conn, FINAL)
        elif LEGACY in tables and FINAL in tables:
            # 將舊表資料搬到新表（排除 id，避免 UNIQUE 衝突）
            align_columns(conn, LEGACY)
            align_columns(conn, FINAL)
            legacy_cols = cols_of(conn, LEGACY)
            final_cols = cols_of(conn, FINAL)
            common = [c for c in legacy_cols if c in final_cols and c != "id"]
            if common:
                cols_csv = ", ".join(common)
                print(f"[migrate] 合併資料：{LEGACY} → {FINAL}（欄位：{cols_csv}；不搬 id）")
                conn.execute(f"INSERT INTO {FINAL} ({cols_csv}) SELECT {cols_csv} FROM {LEGACY}")
                conn.commit()
            # 移除舊表避免之後重複合併
            conn.execute(f"DROP TABLE {LEGACY}")
            conn.commit()

        align_columns(conn, FINAL)
        print("[migrate] 完成。現有欄位：", cols_of(conn, FINAL))
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
