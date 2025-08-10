# test_imap_connect.py
import imaplib
import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("IMAP_HOST")
user = os.getenv("IMAP_USER")
pwd = os.getenv("IMAP_PASS")

print("Connecting to", host)
imap = imaplib.IMAP4_SSL(host)
imap.login(user, pwd)
imap.logout()
print("Success")
