# scripts/test_smtp.py
# 測試是否能成功從 .env 寄出郵件（SSL）

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

user = os.getenv("SMTP_USER")
password = os.getenv("SMTP_PASS")
host = os.getenv("SMTP_HOST")
port = int(os.getenv("SMTP_PORT", 465))
sender = os.getenv("SMTP_FROM", user)
to = os.getenv("SMTP_USER")  # 寄給自己測試

msg = MIMEText("這是自動化測試信件，若你收到表示 SMTP 設定成功。", "plain", "utf-8")
msg["Subject"] = "【SMTP 測試信件】Smart-Mail-Agent"
msg["From"] = sender
msg["To"] = to

try:
    print(f"嘗試連線 SMTP：{host}:{port} ...")
    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.send_message(msg)
    print("✅ 測試成功：信件已寄出")
except Exception as e:
    print("❌ 測試失敗：", str(e))
# scripts/test_smtp.py
# 測試是否能成功從 .env 寄出郵件（SSL）

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

user = os.getenv("SMTP_USER")
password = os.getenv("SMTP_PASS")
host = os.getenv("SMTP_HOST")
port = int(os.getenv("SMTP_PORT", 465))
sender = os.getenv("SMTP_FROM", user)
to = os.getenv("SMTP_USER")  # 寄給自己測試

msg = MIMEText("這是自動化測試信件，若你收到表示 SMTP 設定成功。", "plain", "utf-8")
msg["Subject"] = "【SMTP 測試信件】Smart-Mail-Agent"
msg["From"] = sender
msg["To"] = to

try:
    print(f"嘗試連線 SMTP：{host}:{port} ...")
    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.send_message(msg)
    print("✅ 測試成功：信件已寄出")
except Exception as e:
    print("❌ 測試失敗：", str(e))
