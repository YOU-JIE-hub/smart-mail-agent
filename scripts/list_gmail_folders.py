# scripts/list_gmail_folders.py
import imaplib
import os

from dotenv import load_dotenv

load_dotenv()
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")

with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
    imap.login(IMAP_USER, IMAP_PASS)
    typ, mailboxes = imap.list()
    print("\nGmail 可用資料夾：\n")
    for box in mailboxes:
        print(box.decode())
