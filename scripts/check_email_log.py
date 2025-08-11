#!/usr/bin/env python3
# 檔案位置：scripts/check_email_log.py
# 模組用途：檢查 emails_log.db 最新紀錄與統計（自動遷移、適配欄位/表名）

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path("data/emails_log.db")
CANDIDATE_TABLES = ["emails_log", "email_logs"]  # 兼容舊名


def ensure_migrated():
    # 若遷移腳本存在，先跑一次，避免欄位缺失
    mig = Path("tools/db_migrate_emails_log.py")
    if mig.exists():
        import subprocess
        import sys

        subprocess.run([sys.executable, str(mig)], check=False)


def find_table(conn) -> str:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names = {r[0] for r in cur.fetchall()}
    for t in CANDIDATE_TABLES:
        if t in names:
            return t
    raise RuntimeError("找不到 emails_log / email_logs 資料表")


def list_columns(conn, table: str):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def fetch_latest(limit=20):
    if not DB_PATH.exists():
        print(f"[錯誤] 找不到 DB：{DB_PATH}")
        return []
    try:
        conn = sqlite3.connect(str(DB_PATH))
        table = find_table(conn)
        cols = list_columns(conn, table)

        # 想查哪些欄位 → 以實際存在為準動態組合
        want = ["id", "subject", "predicted_label", "action", "error", "created_at"]
        select_cols = [c for c in want if c in cols]
        if not select_cols:
            select_cols = [cols[0]]  # 至少要有 1 欄避免語法錯誤

        sql = f"SELECT {', '.join(select_cols)} FROM {table} ORDER BY id DESC LIMIT ?"
        cur = conn.execute(sql, (limit,))
        rows = cur.fetchall()
        conn.close()
        return select_cols, rows
    except Exception as e:
        print("[錯誤] 資料讀取失敗：", e)
        return [], []


def show_stats():
    if not DB_PATH.exists():
        print("[錯誤] DB 不存在")
        return
    try:
        conn = sqlite3.connect(str(DB_PATH))
        table = find_table(conn)
        cols = set(list_columns(conn, table))
        total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        spam = 0
        if "predicted_label" in cols:
            spam = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE LOWER(predicted_label)='spam'"
            ).fetchone()[0]
        errors = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE COALESCE(error,'')<>''"
        ).fetchone()[0]
        print("信件處理統計報告")
        print(f"- 總筆數：{total}")
        print(f"- 被過濾為 Spam：{spam}")
        print(f"- 發生錯誤：{errors}")
        conn.close()
    except Exception as e:
        print("[錯誤] 統計失敗：", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    ensure_migrated()
    print("最新信件處理紀錄 (最近 20 筆)：\n")
    headers, rows = fetch_latest(args.limit)
    if not rows:
        print("無任何 log 記錄，請確認主流程有正確寫入 emails_log.db")
    else:
        # 簡單表格輸出（不引入其他套件）
        widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
        fmt = " | ".join("{:<" + str(w) + "}" for w in widths)
        print(fmt.format(*headers))
        print("-+-".join("-" * w for w in widths))
        for r in rows:
            print(fmt.format(*[str(x) for x in r]))
    print()
    show_stats()


if __name__ == "__main__":
    main()
