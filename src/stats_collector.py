<<<<<<< HEAD
# AUTO-GENERATED SHIM for backward-compat imports
from smart_mail_agent.observability.stats_collector import *  # noqa: F401,F403
=======
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__all__ = ["init_stats_db", "increment_counter", "main"]


def _get_db_path() -> Path:
    return Path(os.environ.get("SMA_STATS_DB", "data/stats.db")).resolve()


def init_stats_db() -> Path:
    db = _get_db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stats (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              label TEXT NOT NULL,
              elapsed REAL NOT NULL,
              created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    return db


def increment_counter(label: str, elapsed: float) -> int:
    db = init_stats_db()
    with sqlite3.connect(str(db)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stats (label, elapsed, created_at) VALUES (?, ?, ?)",
            (label or "", float(elapsed), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Stats collector CLI")
    p.add_argument("--init", action="store_true", help="初始化統計資料庫")
    p.add_argument("--label", default=None, help="事件標籤（與 --elapsed 同用代表插入一筆）")
    p.add_argument("--elapsed", type=float, default=None, help="事件耗時/數值")
    # 兼容舊旗標（不影響測試）
    p.add_argument("--insert", action="store_true", help="(兼容) 插入一筆")
    p.add_argument("--event", default=None, help="(兼容) 事件=label")
    p.add_argument("--count", type=float, default=None, help="(兼容) 數值=elapsed")
    return p


def main(argv: list[str] | None = None) -> int:
    import sys

    args = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    if args.init:
        init_stats_db()
        print("資料庫初始化完成")
        return 0
    if (args.label is not None and args.elapsed is not None) or args.insert:
        label = args.label if args.label is not None else (args.event or "")
        elapsed = args.elapsed if args.elapsed is not None else (args.count if args.count is not None else 0.0)
        increment_counter(label, float(elapsed))
        print("已新增統計紀錄")
        return 0
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
>>>>>>> origin/main
