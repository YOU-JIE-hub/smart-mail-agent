import argparse
import json
import os
import sys

# 加入 src 模組目錄，支援根目錄執行 CLI
SRC_PATH = os.path.join(os.path.dirname(__file__), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from utils.logger import logger

from spam.spam_llm_filter import SpamLLMFilter

parser = argparse.ArgumentParser(description="執行 LLM 詐騙語意辨識")
parser.add_argument("--input", required=True, help="輸入郵件 JSON 檔案")
args = parser.parse_args()

input_path = os.path.abspath(args.input)
if not os.path.isfile(input_path):
    raise FileNotFoundError(f"找不到輸入檔案：{input_path}")

with open(input_path, encoding="utf-8") as f:
    mail = json.load(f)

subject = mail.get("subject", "")
content = mail.get("content", "")

filt = SpamLLMFilter()
result = filt.is_suspicious(subject, content)

logger.info("LLM 判定：%s", "詐騙可疑" if result else "內容安全")
print("詐騙可疑" if result else "內容安全")
