#!/usr/bin/env python3
# 檔案位置：tools/repo_tidy.py
# 模組用途：補 shebang/檔頭、簡易檢查 emails_log 表名

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ["src", "utils", "scripts", "modules", "spam"]
HEADER_RE = re.compile(r"^#!/usr/bin/env python3\n# 檔案位置：.*\n# 模組用途：.*", re.M)


def list_py():
    files = []
    for d in TARGET_DIRS:
        p = ROOT / d
        if p.exists():
            files += list(p.rglob("*.py"))
    return files


def ensure_header(p: Path, dry: bool = False):
    rel = p.relative_to(ROOT).as_posix()
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if HEADER_RE.search(txt):
        return False
    header = f"#!/usr/bin/env python3\n# 檔案位置：{rel}\n# 模組用途：請補充此模組用途說明\n\n"
    if not dry:
        p.write_text(header + txt, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    changed = 0
    for p in list_py():
        changed += 1 if ensure_header(p, dry=args.check) else 0
    print(("[檢查]" if args.check else "[修正]") + f" 檔頭處理：{changed} 檔")


if __name__ == "__main__":
    main()
