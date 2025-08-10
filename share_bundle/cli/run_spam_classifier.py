#!/usr/bin/env python3
# 檔案位置：cli/run_spam_classifier.py
# 用途：透過 CLI 執行 SpamBertClassifier 並分類指定信件 JSON

import argparse
import json
import sys

from spam.ml_spam_classifier import SpamBertClassifier
from utils.logger import logger


def run(args):
    clf = SpamBertClassifier(args.model)

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"無法讀取 JSON 檔案：{e}")
        sys.exit(1)

    subject = data.get("subject", "").strip()
    content = data.get("content")

    # 統一格式欄位檢查
    if content is None:
        # 若使用者填寫了舊欄位名，主動提示
        if "body" in data:
            logger.error("請將欄位 'body' 改為 'content'。系統統一使用 'content' 表示信件內容。")
        elif "text" in data:
            logger.error("請將欄位 'text' 改為 'content'。系統統一使用 'content' 表示信件內容。")
        else:
            logger.error("JSON 資料缺少必要欄位 'content'")
        sys.exit(1)

    result = clf.predict(subject=subject, content=content.strip())
    print(f"分類結果：{result['label']} (信心值：{result['confidence']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BERT Spam 分類器 CLI 測試")
    parser.add_argument(
        "--json", required=True, help="輸入 JSON 檔案路徑，需包含 subject 與 content 欄位"
    )
    parser.add_argument("--model", required=True, help="模型目錄路徑")
    args = parser.parse_args()
    run(args)
