#!/usr/bin/env python3
# 檔案位置: src/stats_collector.py
# 模組用途: 統計事件收集（觀測）最小可用實作與 CLI。
# 測試對齊:
#   - 函式: init_stats_db()、increment_counter(label: str, elapsed: float)
#   - DB: 表名 'stats'，欄位 'label' (TEXT)、'elapsed' (REAL)、'created_at' (TEXT)
#   - CLI:
#       python3 src/stats_collector.py --init
#           -> stdout 必須含「資料庫初始化完成」
#       python3 src/stats_collector.py --label 投訴 --elapsed 0.56
#           -> stdout 必須含「已新增統計紀錄」

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__all__ = ["init_stats_db", "increment_counter", "main"]


def _get_db_path() -> Path:
    """
    讀取統計資料庫路徑。
    優先使用環境變數 SMA_STATS_DB；未設定時落到 data/stats.db。
    """
    return Path(os.environ.get("SMA_STATS_DB", "data/stats.db")).resolve()


def init_stats_db() -> Path:
    """
    初始化統計資料庫與資料表 'stats'。
    回傳:
        Path: 實際的資料庫檔案路徑
    """
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                elapsed REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    return db_path


def increment_counter(label: str, elapsed: float) -> int:
    """
    新增一筆事件計數到 'stats'。
    參數:
        label (str): 事件標籤
        elapsed (float): 耗時/數值（REAL）
    回傳:
        int: 新增資料列的 row id
    """
    db_path = init_stats_db()
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stats (label, elapsed, created_at) VALUES (?, ?, ?)",
            (label or "", float(elapsed), created_at),
        )
        conn.commit()
        return int(cur.lastrowid)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Stats collector CLI")
    p.add_argument("--init", action="store_true", help="初始化統計資料庫")
    # 依照測試期望使用 --label / --elapsed
    p.add_argument("--label", default=None, help="事件標籤（與 --elapsed 同用代表插入一筆）")
    p.add_argument("--elapsed", type=float, default=None, help="事件耗時（REAL）")
    # 兼容舊旗標（非測試必要）：--insert / --event / --count
    p.add_argument("--insert", action="store_true", help="兼容舊旗標：插入一筆")
    p.add_argument("--event", default=None, help="兼容舊旗標：事件名稱=label")
    p.add_argument("--count", type=float, default=None, help="兼容舊旗標：數值=elapsed")
    return p


def main(argv: list[str] | None = None) -> int:
    """
    CLI 入口。不委派外部模組，直接調用本地 API 確保測試穩定。
    回傳:
        int: 程式結束碼
    """
    import sys

    args = _build_parser().parse_args(sys.argv[1:] if argv is None else argv)

    # 初始化路徑/資料表
    if args.init:
        init_stats_db()
        print("資料庫初始化完成")
        return 0

    # 插入一筆（符合測試：--label/--elapsed）
    if (args.label is not None and args.elapsed is not None) or args.insert:
        label = args.label if args.label is not None else (args.event or "")
        elapsed = args.elapsed if args.elapsed is not None else (args.count if args.count is not None else 0.0)
        increment_counter(label, float(elapsed))
        print("已新增統計紀錄")
        return 0

    # 無旗標時僅確認 CLI 可執行
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
