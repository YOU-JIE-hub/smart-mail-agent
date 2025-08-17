#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from utils.logger import logger

# 檔案位置：src/stats_collector.py
# 模組用途：記錄分類執行次數與處理耗時，儲存至 SQLite（供統計分析或儀表板視覺化）


# === 統一路徑設定 ===
DB_PATH = Path("data/stats.db")


def init_stats_db() -> None:
    """
    初始化 stats.db 資料表（若尚未建立）

    欄位:
        - id: 自動流水編號
        - label: 類別名稱（如：投訴與抱怨）
        - elapsed: 分類耗時（秒）
        - created_at: 建立時間（UTC）
    """
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                elapsed REAL,
                created_at TEXT
            )
        """
        )
        conn.commit()
        conn.close()
        logger.info("[STATS] stats.db 初始化完成")
    except Exception as e:
        logger.error(f"[STATS] 初始化資料庫失敗：{e}")


def increment_counter(label: str, elapsed: float) -> None:
    """
    新增一筆分類統計紀錄

    參數:
        label (str): 分類結果（如：業務接洽）
        elapsed (float): 執行耗時（秒）
    """
    try:
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO stats (label, elapsed, created_at)
            VALUES (?, ?, ?)
        """,
            (label, elapsed, now),
        )
        conn.commit()
        conn.close()
        logger.debug(f"[STATS] 統計記錄成功：{label}（{elapsed:.3f}s）")
    except Exception as e:
        logger.warning(f"[STATS] 寫入失敗：{e}")


def main():
    """
    CLI 執行模式：支援初始化與測試寫入
    """
    parser = argparse.ArgumentParser(description="統計資料管理工具")
    parser.add_argument("--init", action="store_true", help="初始化 stats.db")
    parser.add_argument("--label", type=str, help="分類標籤名稱")
    parser.add_argument("--elapsed", type=float, help="處理耗時（秒）")

    args = parser.parse_args()

    if args.init:
        init_stats_db()
        print("資料庫初始化完成")
    elif args.label and args.elapsed is not None:
        increment_counter(args.label, args.elapsed)
        print(f"已新增統計紀錄：{args.label}，耗時 {args.elapsed:.3f} 秒")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
