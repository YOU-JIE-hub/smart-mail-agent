# scripts/gen_testdata_pipeline.py

import json
from pathlib import Path

SAVE_DIR = Path("data/testdata/pipeline")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

test_emails = [
    {
        "filename": "test_tech_support.json",
        "data": {
            "subject": "無法登入後台系統，請協助",
            "body": "您好，我使用 admin 帳號無法登入系統，顯示帳號已停用，請盡快協助處理。",
            "sender": "client@example.com",
            "predicted_label": "請求技術支援",
            "confidence": 0.98,
            "summary": "登入問題",
        },
    },
    {
        "filename": "test_info_change.json",
        "data": {
            "subject": "修改公司聯絡資料",
            "body": "新電話：02-8888-8888\n新地址：台中市西區台灣大道88號",
            "sender": "info@acme.com",
            "predicted_label": "申請修改資訊",
            "confidence": 0.93,
            "summary": "更新聯絡資訊",
        },
    },
    {
        "filename": "test_general_inquiry.json",
        "data": {
            "subject": "請問如何設定自動寄信？",
            "body": "想詢問貴公司平台是否支援自動排程寄信功能？有提供設定教學嗎？",
            "sender": "sam@client.com",
            "predicted_label": "詢問流程或規則",
            "confidence": 0.92,
            "summary": "自動排程寄信詢問",
        },
    },
    {
        "filename": "test_complaint.json",
        "data": {
            "subject": "對你們客服處理速度很不滿",
            "body": "之前送出的工單到現在還沒有人處理，請問還要等多久？太誇張了。",
            "sender": "angry@client.com",
            "predicted_label": "投訴與抱怨",
            "confidence": 0.88,
            "summary": "客服處理延遲",
        },
    },
    {
        "filename": "test_quotation.json",
        "data": {
            "subject": "報價需求：Smart-Mail 全功能方案",
            "body": "您好，我們對 Smart-Mail 系統感興趣，請提供 SME 適用的完整報價單。",
            "sender": "sales@demo.com",
            "predicted_label": "業務接洽或報價",
            "confidence": 0.95,
            "summary": "詢問 SME 方案報價",
        },
    },
    {
        "filename": "test_unknown.json",
        "data": {
            "subject": "Hello?",
            "body": "Hi just testing your service without any clear topic.",
            "sender": "test@random.com",
            "predicted_label": "其他",
            "confidence": 0.65,
            "summary": "無特定主題",
        },
    },
]

for mail in test_emails:
    path = SAVE_DIR / mail["filename"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mail["data"], f, ensure_ascii=False, indent=2)
    print(f"已建立：{path}")
