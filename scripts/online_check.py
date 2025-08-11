#!/usr/bin/env python3
# 檔案：scripts/online_check.py
# 目的：線上檢查（SMTP、IMAP），並寫入 emails_log.db 一筆 online-check 紀錄

from __future__ import annotations

import imaplib
import os
import smtplib
import sqlite3
import ssl
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

# 載入 .env（若有）
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

# 確保可匯入 src/*
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _write_log_to_db(
    subject: str,
    predicted_label: str,
    action: str,
    content: str = "",
    summary: str = "",
    confidence: float = 0.0,
    error: str = "",
) -> None:
    # 先試專案內工具；失敗才用 sqlite3
    try:
        from log_writer import log_to_db  # type: ignore

        log_to_db(
            subject=subject,
            content=content,
            summary=summary,
            predicted_label=predicted_label,
            confidence=confidence,
            action=action,
            error=error,
        )
        print("[OK] 以 log_writer.log_to_db 寫入 emails_log")
        return
    except Exception as e:
        print(f"[WARN] 導入 log_writer 失敗，改用 sqlite3：{e}")

    db_path = ROOT / "data" / "emails_log.db"  # noqa: F841
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
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
        conn.execute(
            """
INSERT INTO emails_log (subject, content, summary, predicted_label, confidence, action, error, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""",
            (
                subject,
                content,
                summary,
                predicted_label,
                float(confidence),
                action,
                error,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        print("[OK] 以 sqlite3 直接寫入 emails_log")
    finally:
        conn.close()


def require_env(keys: list[str]) -> list[str]:
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        print("[MISS] 未設定：", ", ".join(missing))
    else:
        print("[OK] 所有必要環境變數已設定")
    return missing


def test_smtp() -> bool:
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "465"))
    user = os.getenv("SMTP_USER", "")
    pwd = os.getenv("SMTP_PASS", "")
    sender = os.getenv("SMTP_FROM", user or "")
    to = os.getenv("REPLY_TO", user or "")

    print(f"[SMTP] host={host} port={port} user={user} to={to}")
    if not all([host, port, user, pwd, sender, to]):
        print("[SMTP] 參數不足，跳過")
        return False
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=20) as s:
            s.login(user, pwd)
            msg = MIMEText("Smart-Mail-Agent 線上檢查：這是一封測試信。")
            msg["Subject"] = "SMA Online Check - SMTP OK"
            msg["From"] = sender
            msg["To"] = to
            s.sendmail(sender, [to], msg.as_string())
        print("[OK] SMTP 寄信成功（請到信箱確認）")
        return True
    except Exception as e:
        print(f"[ERR] SMTP 測試失敗：{e}")
        return False


def test_imap() -> bool:
    host = os.getenv("IMAP_HOST", "")
    user = os.getenv("IMAP_USER", "")
    pwd = os.getenv("IMAP_PASS", "")
    folder = os.getenv("IMAP_FOLDER", "INBOX")
    print(f"[IMAP] host={host} folder={folder} user={user}")
    if not all([host, user, pwd]):
        print("[IMAP] 參數不足，跳過")
        return False
    try:
        with imaplib.IMAP4_SSL(host) as imap:
            imap.login(user, pwd)
            typ, _ = imap.select(folder, readonly=True)  # noqa: F841
            if typ != "OK":
                print("[IMAP] 選擇資料夾失敗，改用 INBOX")
                imap.select("INBOX", readonly=True)
            typ, data = imap.search(None, "ALL")
            if typ != "OK":
                print("[IMAP] 搜尋失敗")
                return False
            ids = data[0].split() if data and data[0] else []
            print(f"[OK] IMAP 連線成功，可見郵件數：{len(ids)}")
            return True
    except imaplib.IMAP4.error as e:
        print(f"[ERR] IMAP 認證失敗：{e}")
        return False
    except Exception as e:
        print(f"[ERR] IMAP 一般錯誤：{e}")
        return False


def main() -> int:
    # OFFLINE 模式：不打網路，寫一筆 skipped 記錄後成功結束
    import os

    if os.getenv("OFFLINE", "0") == "1":
        try:
            _write_log_to_db(
                subject="ONLINE CHECK",
                predicted_label="其他",
                action="online-check:skipped",
                content="OFFLINE=1",
                summary="線上環境檢查（跳過）",
                confidence=0.0,
                error="",
            )
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測，已寫入 emails_log")
        except Exception as _:  # noqa: F841
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測（未寫 DB）")
        return 0


def main() -> int:  # noqa: F811
    # OFFLINE 模式：不打網路，寫一筆 skipped 記錄後成功結束
    import os

    if os.getenv("OFFLINE", "0") == "1":
        try:
            _write_log_to_db(
                subject="ONLINE CHECK",
                predicted_label="其他",
                action="online-check:skipped",
                content="OFFLINE=1",
                summary="線上環境檢查（跳過）",
                confidence=0.0,
                error="",
            )
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測，已寫入 emails_log")
        except Exception as _:  # noqa: F841
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測（未寫 DB）")
        return 0


def main() -> int:  # noqa: F811
    # OFFLINE 模式：不打網路，寫一筆 skipped 記錄後成功結束
    import os

    if os.getenv("OFFLINE", "0") == "1":
        try:
            _write_log_to_db(
                subject="ONLINE CHECK",
                predicted_label="其他",
                action="online-check:skipped",
                content="OFFLINE=1",
                summary="線上環境檢查（跳過）",
                confidence=0.0,
                error="",
            )
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測，已寫入 emails_log")
        except Exception as _:  # noqa: F841
            print("[SKIP] OFFLINE=1：略過 SMTP/IMAP 實測（未寫 DB）")
        return 0


def main() -> int:  # noqa: F811
    # 必要環境檢查
    require_env(
        [
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_USER",
            "SMTP_PASS",
            "SMTP_FROM",
            "REPLY_TO",
            "IMAP_HOST",
            "IMAP_USER",
            "IMAP_PASS",
        ]
    )
    smtp_ok = test_smtp()  # noqa: F841
    imap_ok = test_imap()  # noqa: F841

    # 寫一筆 DB 記錄
    status = "ok" if (smtp_ok or imap_ok) else "fail"
    _write_log_to_db(
        subject="ONLINE CHECK",
        predicted_label="其他",
        action=f"online-check:{status}",
        content=f"smtp_ok={smtp_ok}, imap_ok={imap_ok}",
        summary="線上環境檢查",
        confidence=1.0 if (smtp_ok or imap_ok) else 0.0,
        error="" if (smtp_ok or imap_ok) else "smtp/imap 均失敗",
    )
    print("[DONE] Online 檢查完成。")
    return 0 if (smtp_ok or imap_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
