#!/usr/bin/env python3
# 檔案位置：tools/project_catalog.py
# 模組用途：掃描專案並產生 PROJECT_STATUS.md

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "PROJECT_STATUS.md"

ENTRY = re.compile(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]')
ARG = re.compile(r"argparse\.ArgumentParser")
DDL = re.compile(r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.I)


def list_py():
    return [p for p in ROOT.rglob("*.py") if ".venv" not in str(p)]


def main():
    files = list_py()
    entries = [str(p.relative_to(ROOT)) for p in files if ENTRY.search(p.read_text(encoding="utf-8", errors="ignore"))]
    clis = [str(p.relative_to(ROOT)) for p in files if ARG.search(p.read_text(encoding="utf-8", errors="ignore"))]
    tables = defaultdict(set)
    for p in files:
        for m in DDL.finditer(p.read_text(encoding="utf-8", errors="ignore")):
            tables[m.group(1)].add(str(p.relative_to(ROOT)))
    md = []
    md.append("# PROJECT STATUS\n")
    md.append("## Entries\n")
    md += [f"- {e}" for e in sorted(entries)]
    md.append("\n## CLI-capable modules\n")
    md += [f"- {e}" for e in sorted(clis)]
    md.append("\n## Detected DB tables\n")
    for t, locs in sorted({k: sorted(v) for k, v in tables.items()}.items()):
        md.append(f"- **{t}**: {', '.join(locs)}")
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
