from __future__ import annotations
import sqlite3, sys
from pathlib import Path

_DB = Path("stats.db")

def init_stats_db(db_path: str | None = None) -> None:
    p = Path(db_path) if db_path else _DB
    con = sqlite3.connect(p)
    try:
        con.execute("CREATE TABLE IF NOT EXISTS stats (name TEXT PRIMARY KEY, count INTEGER NOT NULL)")
        con.commit()
    finally:
        con.close()
    print("資料庫初始化完成")

def increment_counter(name: str, db_path: str | None = None) -> None:
    p = Path(db_path) if db_path else _DB
    con = sqlite3.connect(p)
    try:
        cur = con.execute("SELECT count FROM stats WHERE name=?", (name,))
        row = cur.fetchone()
        if row:
            con.execute("UPDATE stats SET count=count+1 WHERE name=?", (name,))
        else:
            con.execute("INSERT INTO stats(name,count) VALUES(?,1)", (name,))
        con.commit()
    finally:
        con.close()
    print("已更新", name)

if __name__ == "__main__":
    if "--init" in sys.argv:
        init_stats_db()
    elif "--insert" in sys.argv:
        try:
            name = sys.argv[sys.argv.index("--insert")+1]
        except Exception:
            name = "default"
        increment_counter(name)
