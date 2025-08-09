# scripts/send_test_emails.py
# 自動產生自然語氣測資信件並使用 SMTP 發送給 Smart-Mail-Agent 測試接收端
# 適用於 GitHub 公開專案，所有敏感設定皆讀自 .env

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path  # noqa: F401
from time import sleep

from dotenv import load_dotenv

# === 環境變數載入 (.env) ===
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")  # 寄件人帳號（登入用）
SMTP_PASS = os.getenv("SMTP_PASS")  # 應用程式密碼
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)  # 顯示寄件人
SMTP_TO = os.getenv("SMTP_TO")  # 接收測試信的信箱
REPLY_TO = os.getenv("REPLY_TO", SMTP_FROM)  # 可選回覆地址

# === 測資信件清單（自然語句、多分類、多情境） ===
test_emails = [
    {
        "subject": "關於你們服務的系統錯誤與支援請求",
        "body": (
            "您好，\n\n"
            "我昨天在使用你們的自動排程功能時，遇到系統錯誤，畫面會突然跳出 '未知錯誤'。\n"
            "我試過重開瀏覽器、清除快取也無效。想請問有可能是我帳號設定有誤嗎？\n\n"
            "希望能協助處理，謝謝。\n\n--\nMichael / IT Manager"
        ),
    },
    {
        "subject": "請協助修改公司登記資訊（電話與地址）",
        "body": (
            "您好，我們公司近期搬遷與換電話，以下是最新資訊，麻煩協助更新：\n"
            "新地址：台北市中正區重慶南路一段122號\n"
            "新電話：02-2345-6789\n"
            "帳號應為：info@abc-corp.com\n\n"
            "感謝！\nHelen Lin / 行政部"
        ),
    },
    {
        "subject": "想詢問你們產品續約與計費方式",
        "body": (
            "Hi Smart-Mail 團隊，\n\n"
            "我們團隊目前有 10 位使用者，接下來可能會擴充至 20 人，\n"
            "想了解你們的授權方式、續約流程與可能的企業折扣方案。\n\n"
            "如有簡報或產品白皮書也歡迎一併提供，謝謝！\n\n"
            "Best regards,\nSean / 資訊採購"
        ),
    },
    {
        "subject": "最近真的有點不滿你們客服處理方式",
        "body": (
            "你們好：\n\n"
            "上週我們已經回覆 ticket 並多次追蹤，但至今沒人主動聯繫。\n"
            "當初承諾三個工作天內會回覆，結果已經過了一週。\n\n"
            "我們非常重視這次問題處理，希望這封信能儘速引起重視。\n\n"
            "客戶代碼：AC-3382\n--\nRoger / 營運管理"
        ),
    },
    {
        "subject": "請提供自動郵件機器人報價方案",
        "body": (
            "您好：\n\n"
            "我們正在評估 AI 郵件處理機器人作為接下來的行銷支援工具。\n"
            "主要需求包含：\n- 支援 API 串接\n- 多信箱整合\n- 內部部署選項\n\n"
            "請提供報價單與功能差異表，謝謝。\n\nDavid / Marketing Dept."
        ),
    },
    {
        "subject": "hi",
        "body": (
            "Just wanted to say hi.\n\n"
            "No urgent matter. Just testing how this email system handles generic non-business emails."
        ),
    },
    {
        "subject": "LINE@:abcd-1234 載點：http://spam.me/free",
        "body": (
            "點這裡免費拿樣品：http://spammer.vip/linebot\n"
            "新產品試用申請已開放，填完立即領好禮！\n"
            "免費試用、限時優惠、立即點擊！"
        ),
    },
    {"subject": "", "body": ""},
    {
        "subject": "點擊下方連結立即獲得免費好禮與優惠資訊！",
        "body": (
            "我們精選了十個專屬連結供您領取限量優惠：\n"
            + "\n".join([f"{i+1}. https://click.spam{i+1}.com/deal" for i in range(10)])
            + "\n\n立即點選上方任一連結，即可參加抽獎與獲得折價券！"
        ),
    },
    {
        "subject": "有關 Smart-Mail-Agent 的完整導入需求與環境說明",
        "body": (
            (
                "您好，我們正在積極評估導入 Smart-Mail-Agent，以下是詳細需求：\n"
                "1. 多信箱整合需求\n"
                "2. LLM 彈性支援\n"
                "3. 自動副本轉寄設計\n"
                "4. systemd 與 crontab 相容性\n"
                "5. PDF 報價樣板自定義功能\n"
                "6. 自動統計與每日報表寄送...\n\n"
            )
            * 5
        ),
    },
]


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = SMTP_TO
    msg["Subject"] = subject or "(No Subject)"
    msg["Reply-To"] = REPLY_TO
    msg.attach(MIMEText(body or "(Empty Content)", "plain", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        print(f"已寄出：{subject}")
        sleep(2)


if __name__ == "__main__":
    for mail in test_emails:
        send_email(mail["subject"], mail["body"])
