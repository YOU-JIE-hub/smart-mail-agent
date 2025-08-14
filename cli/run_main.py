import argparse
import json
import os
import sys

SRC_PATH = os.path.join(os.path.dirname(__file__), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from classifier import IntentClassifier
from spam.spam_filter_orchestrator import SpamFilterOrchestrator
from utils.logger import logger

parser = argparse.ArgumentParser(description="郵件處理主流程")
parser.add_argument("--spam_model", required=True, help="BERT spam 模型路徑")
parser.add_argument("--intent_model", required=True, help="六分類模型路徑")
parser.add_argument("--input", required=True, help="輸入信件 JSON 檔案")
parser.add_argument("--output", required=True, help="輸出結果 JSON 檔案")
args = parser.parse_args()

# 絕對路徑轉換
input_path = os.path.abspath(args.input)
output_path = os.path.abspath(args.output)
spam_model_path = os.path.abspath(args.spam_model)
intent_model_path = os.path.abspath(args.intent_model)

# 載入信件內容
with open(input_path, encoding="utf-8") as f:
    mail = json.load(f)
subject = mail.get("subject", "")
content = mail.get("content", "")

# 垃圾信三層過濾
spam_orchestrator = SpamFilterOrchestrator(model_path=spam_model_path)
spam_result = spam_orchestrator.is_legit(subject, content)

if not spam_result["allow"]:
    final = {
        "label": "垃圾信",
        "stage": spam_result["stage"],
        "subject": subject,
        "content": content,
    }
else:
    clf = IntentClassifier(model_path=intent_model_path)
    intent_result = clf.classify(subject, content)
    final = intent_result

# 輸出結果
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

logger.info("已完成主流程處理，輸出至 %s", output_path)
print(json.dumps(final, ensure_ascii=False, indent=2))
