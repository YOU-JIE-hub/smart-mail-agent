#!/usr/bin/env python3
# 檔案位置：cli/run_generate_spam_testcases.py
# 模組用途：自動生成完整垃圾信過濾測試資料（涵蓋 rule / ml / llm / whitelist / 合法 / 錯誤）

import json
import os
from pathlib import Path

OUTPUT_DIR = "data/testdata/spam"

testcases = {
    "spam_rule.json": {
        "subject": "限時優惠送你",
        "content": "裸聊加 LINE，投資機會免費賺錢",
        "sender": "hacker@spamlink.net",
    },
    "spam_ml_high.json": {
        "subject": "快速致富 100% 成功！",
        "content": "點擊投資回報 10 倍，立即註冊！",
        "sender": "promo@unknown.com",
    },
    "spam_ml_low_llm_spam.json": {
        "subject": "Hi，有個計畫想和你聊聊",
        "content": "可以跟你談談金融合作嗎？會有收益保證。",
        "sender": "unclear@softpush.co",
    },
    "nonspam_whitelist.json": {
        "subject": "系統維護完成通知",
        "content": "您的帳戶維護已完成，歡迎使用。",
        "sender": "admin@trusted.org",
    },
    "nonspam_legit.json": {
        "subject": "詢問合約內容與付款時間",
        "content": "請問 8 月的合約是否已匯款？附件已寄出。",
        "sender": "client@business.com",
    },
    "edge_ml_unknown.json": {
        "subject": "!!##!!",
        "content": ".....",
        "sender": "undefined@empty.ai",
    },
}


def main():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    for filename, data in testcases.items():
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[完成] 已建立測資：{path}")


if __name__ == "__main__":
    main()
