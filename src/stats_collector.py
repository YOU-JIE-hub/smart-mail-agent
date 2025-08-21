from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/stats.db")


def init_stats_db(path: Optional[Path] = None) -> None:
    p = path or DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT, elapsed REAL, ts DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        conn.commit()


def insert_stat(label: str, elapsed: float, path: Optional[Path] = None) -> None:
    p = path or DB_PATH
    with sqlite3.connect(p) as conn:
        conn.execute("INSERT INTO stats(label, elapsed) VALUES(?, ?)", (label, float(elapsed)))
        conn.commit()


# 舊名相容
def increment_counter(label: str, elapsed: float) -> None:
    if not DB_PATH.exists():
        init_stats_db()
    insert_stat(label, elapsed)


def main(argv=None) -> int:
    import sys

    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true")
    p.add_argument("--label")
    p.add_argument("--elapsed", type=float)
    args = p.parse_args(argv)

    if args.init:
        init_stats_db()
        print("資料庫初始化完成")
        return 0

    if args.label is not None and args.elapsed is not None:
        if not DB_PATH.exists():
            init_stats_db()
        insert_stat(args.label, args.elapsed)
        print("已新增統計紀錄")
        return 0

    p.print_usage(sys.stdout)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
