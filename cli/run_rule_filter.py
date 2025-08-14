#!/usr/bin/env python3
# 檔案位置：cli/run_rule_filter.py
# 模組用途：使用 CLI 執行 Rule-Based spam 判斷

import argparse
import json

from spam.rule_filter import RuleBasedSpamFilter


def run(json_path: str):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    subject = data.get("subject", "")
    content = data.get("content", "")
    full_text = f"{subject}\n{content}".strip()

    clf = RuleBasedSpamFilter()
    result = clf.is_spam(full_text)

    print("[結果] 是否為垃圾信：", "是" if result else "否")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用 Rule-Based 方法檢測垃圾郵件")
    parser.add_argument("--json", required=True, help="輸入 JSON 路徑，需含 subject 與 content 欄位")
    args = parser.parse_args()
    run(args.json)
