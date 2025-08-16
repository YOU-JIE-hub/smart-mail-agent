#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["init_stats_db", "increment_counter", "main"]

def _db_path() -> Path:
    return Path(os.environ.get("SMA_STATS_DB", "data/stats.db"))

def init_stats_db() -> Path:
    p = _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stats(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              label TEXT NOT NULL,
              elapsed REAL DEFAULT 0,
              created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    return p

def increment_counter(label: str, elapsed: float = 0.0) -> None:
    p = init_stats_db()
    with sqlite3.connect(p) as conn:
        conn.execute(
            "INSERT INTO stats(label,elapsed,created_at) VALUES (?,?,?)",
            (label, float(elapsed), datetime.now(timezone.utc).isoformat())
        )
        conn.commit()

def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true", help="initialize database")
    ap.add_argument("--label", "--event", dest="label", help="label to insert")
    ap.add_argument("--elapsed", "--count", dest="elapsed", type=float, default=0.0)
    args = ap.parse_args(argv)
    if args.__dict__.get("init"):
        init_stats_db()
        print("資料庫初始化完成")
        return 0
    if args.label:
        increment_counter(args.label, args.elapsed)
        print("已新增統計紀錄")
        return 0
    ap.print_help()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
