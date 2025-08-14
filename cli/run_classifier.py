import argparse
import json
import os
import sys

# 加入 src 模組路徑
SRC_PATH = os.path.join(os.path.dirname(__file__), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from classifier import IntentClassifier
from utils.logger import logger

parser = argparse.ArgumentParser(description="六分類意圖分類模型推論器")
parser.add_argument("--model", required=True, help="模型資料夾路徑")
parser.add_argument("--input", required=True, help="輸入 JSON 郵件檔案（需含 subject / content）")
args = parser.parse_args()

model_path = os.path.abspath(args.model)
input_path = os.path.abspath(args.input)

if not os.path.isdir(model_path):
    raise FileNotFoundError(f"模型路徑不存在：{model_path}")
if not os.path.isfile(input_path):
    raise FileNotFoundError(f"找不到輸入檔案：{input_path}")

with open(input_path, encoding="utf-8") as f:
    mail = json.load(f)

subject = mail.get("subject", "")
content = mail.get("content", mail.get("body", ""))

clf = IntentClassifier(model_path)
result = clf.classify(subject, content)

logger.info("分類結果：%s", json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2))
