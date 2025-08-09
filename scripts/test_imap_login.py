# scripts/test_imap_login.py
# 測試 Gmail IMAP 登入與資料夾列出功能

import imaplib
import os

from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")

print(f"嘗試登入 IMAP：{IMAP_HOST} / {IMAP_USER}")

try:
    with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
        imap.login(IMAP_USER, IMAP_PASS)
        print("成功登入 Gmail IMAP，以下是可用資料夾：\n")
        status, mailboxes = imap.list()
        if status == "OK":
            for box in mailboxes:
                print(box.decode())
except Exception as e:
    print(f"登入失敗：{e}")
