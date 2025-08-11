#!/usr/bin/env python3
# 檔案位置：src/run_action_handler.py
# 模組用途：CLI 入口，包裝 action_handler 的執行

from __future__ import annotations

import argparse
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description="執行 Action Handler CLI")
    parser.add_argument(
        "--input", type=str, default="data/output/classify_result.json", help="分類結果 JSON"
    )
    parser.add_argument(
        "--output", type=str, default="data/output/action_result.json", help="動作結果輸出 JSON"
    )
    args = parser.parse_args()

    cmd = ["python", "-m", "action_handler", "--input", args.input, "--output", args.output]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
