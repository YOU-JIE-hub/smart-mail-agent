from __future__ import annotations
import argparse
import sqlite3
from pathlib import Path
from time import time
from typing import Optional

_DB = Path("data/stats.db")

def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def init_stats_db(db_path: Optional[str | Path] = None) -> Path:
    p = Path(db_path) if db_path else _DB
    _ensure_dir(p)
    with sqlite3.connect(p) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS stats (ts INTEGER, label TEXT, elapsed REAL)")
    print("資料庫初始化完成")
    return p

def increment_counter(label: str, elapsed: float, db_path: Optional[str | Path] = None) -> None:
    p = Path(db_path) if db_path else _DB
    _ensure_dir(p)
    with sqlite3.connect(p) as conn:
        conn.execute(
            "INSERT INTO stats (ts, label, elapsed) VALUES (?, ?, ?)",
            (int(time()), str(label), float(elapsed)),
        )
    print("已新增統計紀錄")

def _cli() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--label")
    ap.add_argument("--elapsed")
    args = ap.parse_args()

    if args.init:
        init_stats_db()
        return
    if args.label is not None and args.elapsed is not None:
        increment_counter(args.label, float(args.elapsed))
        return
    ap.print_help()

if __name__ == "__main__":
    _cli()
