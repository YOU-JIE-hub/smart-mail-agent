#!/usr/bin/env python3
# 檔案位置：scripts/dev_seed_emails_log.py
# 目的：離線環境灌入 emails_log.db 示範資料，方便 demo 與檢查報表

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path("data/emails_log.db")
DB.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute(
    """
CREATE TABLE IF NOT EXISTS emails_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    content TEXT,
    summary TEXT,
    predicted_label TEXT,
    confidence REAL,
    action TEXT,
    error TEXT,
    created_at TEXT
)
"""
)
conn.commit()

cur.execute("SELECT COUNT(1) FROM emails_log")
count = cur.fetchone()[0]
if count and count > 0:
    print(f"[seed] 略過：已有 {count} 筆紀錄")
else:
    now = datetime.utcnow().isoformat()
    rows = [
        ("我要報價", "請提供企業年約方案", "詢價需求", "業務接洽或報價", 0.92, "demo", "", now),
        ("忘記密碼", "請協助重設密碼", "會員登入問題", "請求技術支援", 0.88, "demo", "", now),
        ("功能建議", "建議新增 SSO", "產品回饋", "其他", 0.70, "demo", "", now),
    ]
    cur.executemany(
        "INSERT INTO emails_log(subject, content, summary, predicted_label, confidence, action, error, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    print(f"[seed] 已寫入 {len(rows)} 筆示範資料")
conn.close()
print("[ok] dev_seed_emails_log 完成")
