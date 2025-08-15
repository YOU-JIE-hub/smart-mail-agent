import argparse
import json
import os
import sys

# 加入 src 模組路徑
SRC_PATH = os.path.join(os.path.dirname(__file__), "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from spam.ml_spam_classifier import SpamBertClassifier
from spam.rule_filter import RuleBasedSpamFilter
from spam.spam_llm_filter import SpamLLMFilter
from utils.logger import logger

parser = argparse.ArgumentParser(description="三層 Spam 過濾流程")
parser.add_argument("--model", required=True, help="BERT 模型路徑")
parser.add_argument("--input", required=True, help="輸入郵件 JSON 檔案")
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
content = mail.get("content", "")
text = (subject + "\n" + content).strip()

logger.info("【Step 1】啟動 Rule-Based 過濾")
rule_filter = RuleBasedSpamFilter()
if rule_filter.is_spam(text):
    logger.info("結果：Rule-Based 判定為垃圾信")
    print("分類結果：垃圾信（Rule-Based）")
    sys.exit(0)

logger.info("【Step 2】啟動 BERT Spam 分類模型")
bert_clf = SpamBertClassifier(model_path)
bert_result = bert_clf.predict(subject, content)
if bert_result["label"].lower() == "spam":
    logger.info("結果：BERT 判定為垃圾信")
    print("分類結果：垃圾信（BERT 模型）")
    sys.exit(0)

logger.info("【Step 3】啟動 LLM 語意判斷")
llm_filter = SpamLLMFilter()
if llm_filter.is_suspicious(subject, content):
    logger.info("結果：LLM 判定為垃圾信")
    print("分類結果：垃圾信（LLM 分析）")
    sys.exit(0)

logger.info("所有層級判斷為正常信件")
print("分類結果：正常信件（非垃圾）")
