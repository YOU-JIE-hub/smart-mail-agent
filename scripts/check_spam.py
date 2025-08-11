#!/usr/bin/env python3
# 檔案位置：scripts/check_spam.py
# 模組用途：離線/本地快速檢查垃圾信判斷，輸入主旨/內容/寄件者，輸出統一結構 JSON

from __future__ import annotations

import argparse
import json
import logging
from typing import Any, Dict

# 日誌風格
LOGGER_NAME = "SPAM"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [" + LOGGER_NAME + "] %(message)s",
)
logger = logging.getLogger(LOGGER_NAME)


def analyze_once(subject: str, content: str, sender: str) -> Dict[str, Any]:
    """
    呼叫離線替身總管進行分析。
    參數:
        subject: 郵件主旨
        content: 郵件內容
        sender: 寄件者郵件
    回傳:
        dict: 包含 engine/is_spam/is_legit/allow/body_snippet 的統一結構
    """
    from spam.spam_filter_orchestrator import SpamFilterOrchestrator  # 延遲載入

    sf = SpamFilterOrchestrator()
    result = sf.analyze(subject=subject, content=content, sender=sender)
    # 補充輸入欄位，方便檢視
    result["input"] = {"subject": subject, "content": content, "sender": sender}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="本地垃圾信檢查（離線）")
    parser.add_argument("--subject", required=False, default="", help="郵件主旨")
    parser.add_argument("--content", required=False, default="", help="郵件內容")
    parser.add_argument("--sender", required=False, default="unknown@example.com", help="寄件者")
    parser.add_argument(
        "--input-json", help="從 JSON 檔讀取輸入（ keys: subject, content, sender ）"
    )
    parser.add_argument("--output", default="", help="輸出結果 JSON 檔路徑（預設印到 stdout）")
    args = parser.parse_args()

    if args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        subject = data.get("subject", "")
        content = data.get("content", "")
        sender = data.get("sender", "unknown@example.com")
    else:
        subject, content, sender = args.subject, args.content, args.sender

    result = analyze_once(subject, content, sender)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info("結果已輸出：%s", args.output)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
