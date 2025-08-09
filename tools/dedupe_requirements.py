#!/usr/bin/env python3
# 檔案位置：tools/dedupe_requirements.py
# 模組用途：requirements.txt 去重與排序，輸出 requirements.cleaned.txt

import re
from pathlib import Path

IN = Path("requirements.txt")
OUT = Path("requirements.cleaned.txt")


def main():
    if not IN.exists():
        print("找不到 requirements.txt")
        return
    lines = [line.strip() for line in IN.read_text(encoding="utf-8").splitlines()]
    pkgs = {}
    for line in lines:
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<>=!~ ]", line, 1)[0].lower()
        # 保留最後一次宣告
        pkgs[name] = line
    cleaned = sorted(pkgs.values(), key=lambda s: s.lower())
    OUT.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
    print(f"已輸出：{OUT}")


if __name__ == "__main__":
    main()
