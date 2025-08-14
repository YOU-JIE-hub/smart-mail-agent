# pipeline/main1.py

import argparse
import email
import imaplib
import json
import os
import sqlite3
import sys
from email.header import decode_header
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("src"))
from email_processor import main as process_email_main
from utils.logger import logger

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
SAVE_DIR = Path("data/testdata/inbox/")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = "data/db/processed_mails.db"


def init_db():
    Path("data/db").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_mails (
            uid TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT
        )
    """
    )
    conn.commit()
    conn.close()
    logger.info("processed_mails.db 初始化完成")


def decode_mime_header(header_bytes):
    decoded_parts = decode_header(header_bytes)
    return "".join(part.decode(encoding or "utf-8") if isinstance(part, bytes) else part for part, encoding in decoded_parts)


def uid_already_processed(uid: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM processed_mails WHERE uid=?", (uid,))
    result = cur.fetchone()
    conn.close()
    return result is not None


def save_processed_uid(uid: str, subject: str, sender: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO processed_mails (uid, subject, sender) VALUES (?, ?, ?)",
        (uid, subject, sender),
    )
    conn.commit()
    conn.close()


def fetch_emails(limit: int = 100, force: bool = False):
    with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
        logger.info(f"[IMAP] 連線中：{IMAP_HOST}")
        imap.login(IMAP_USER, IMAP_PASS)

        # 中文 Gmail 的「所有郵件」對應資料夾
        status, _ = imap.select('"[Gmail]/&UWiQ6JD1TvY-"')
        if status != "OK":
            logger.error("[IMAP] 無法選擇 [Gmail]/所有郵件")
            return []

        status, data = imap.uid("search", None, "ALL")
        if status != "OK":
            logger.error("[IMAP] 搜尋信件失敗")
            return []

        uid_list = data[0].split()[-limit:]
        emails = []

        for uid_bytes in uid_list:
            uid = uid_bytes.decode()
            if not force and uid_already_processed(uid):
                logger.info(f"[IMAP] 跳過已處理：UID={uid}")
                continue

            status, msg_data = imap.uid("fetch", uid_bytes, "(RFC822)")
            if status != "OK":
                logger.warning(f"[IMAP] 下載失敗：UID={uid}")
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = decode_mime_header(msg.get("Subject", ""))
            sender = decode_mime_header(msg.get("From", ""))
            content = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset() or "utf-8"
                        content = part.get_payload(decode=True).decode(charset, errors="ignore")
                        break
            else:
                charset = msg.get_content_charset() or "utf-8"
                content = msg.get_payload(decode=True).decode(charset, errors="ignore")

            email_json = {
                "subject": subject.strip(),
                "content": content.strip(),
                "sender": sender.strip(),
            }

            json_path = SAVE_DIR / f"mail_{uid}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(email_json, f, ensure_ascii=False, indent=2)

            save_processed_uid(uid, subject, sender)
            emails.append(str(json_path))

        return emails


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100, help="最多擷取多少封")
    parser.add_argument("--force", action="store_true", help="是否強制重抓已處理信")
    args = parser.parse_args()

    init_db()
    logger.info("開始抓取郵件")
    paths = fetch_emails(limit=args.limit, force=args.force)
    logger.info(f"共擷取 {len(paths)} 封信件")

    total = len(paths)
    success = 0
    failed = 0
    spam_blocked = 0

    for path in paths:
        logger.info(f"處理中：{path}")
        sys.argv = ["main", "--input", path]
        try:
            process_email_main()
            logger.info(f"處理完成：{path}")
            with open(path, encoding="utf-8") as f:
                mail = json.load(f)
            if "報價" in mail.get("subject", ""):
                spam_blocked += 1
            else:
                success += 1
        except Exception as e:
            logger.error(f"處理失敗：{e}")
            failed += 1

    print("\n信件處理統計報告")
    print(f"- 總共擷取：{total} 封")
    print(f"- 處理成功：{success} 封")
    print(f"- 處理失敗：{failed} 封")
    print(f"- 被過濾為 Spam：{spam_blocked} 封")


if __name__ == "__main__":
    run()
