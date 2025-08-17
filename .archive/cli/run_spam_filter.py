#!/usr/bin/env python3
# 檔案位置：cli/run_spam_filter.py
# 模組用途：針對單筆或整批 JSON 測資執行 spam 判斷流程

import argparse
import json
from pathlib import Path

from spam.spam_filter_orchestrator import SpamFilterOrchestrator


def run_single(json_path: str, model_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    subject = data.get("subject", "")
    content = data.get("content", "") or data.get("body", "")
    sender = data.get("sender", "")

    clf = SpamFilterOrchestrator(model_path)
    result = clf.is_legit(subject, content, sender)

    print(f"\n[測資檔案] {json_path}")
    print(f"[主旨] {subject}")
    print(f"[寄件者] {sender}")
    print(
        f"[判斷結果] 許可: {result['allow']} | 階段: {result['stage']} | 理由: {result['reason']}\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Spam 判斷 CLI 工具")
    parser.add_argument("--json", required=True, help="單筆 JSON 檔案路徑，或目錄以跑整批")
    parser.add_argument("--model", default="model/bert_spam_classifier", help="ML 模型路徑")
    args = parser.parse_args()

    if Path(args.json).is_file():
        run_single(args.json, args.model)
    elif Path(args.json).is_dir():
        for file in sorted(Path(args.json).glob("*.json")):
            run_single(str(file), args.model)
    else:
        print("請指定有效的測資檔路徑或資料夾")


if __name__ == "__main__":
    main()
