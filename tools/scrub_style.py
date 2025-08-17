from __future__ import annotations

import re
import sys
from pathlib import Path

AIISH = (
    r"(chatgpt|copilot|llm|large\s+language\s+model|ai\s*助手|ai\s*產生|由\s*ai\s*生成|"
    r"魔法|神器|小幫手|神級|一鍵|智慧助理)"
)
EMOJI = r"[\U0001F000-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF]"
DECOR = r"^[\s#]*([=~\-\*_]{4,}|[★☆•▶♦◆●◉■□]+)\s*$"

AIISH_RE = re.compile(AIISH, re.I)
EMOJI_RE = re.compile(EMOJI)
DECOR_RE = re.compile(DECOR)
TRAILING_WS = re.compile(r"[ \t]+$", re.M)


def scrub_text(txt: str) -> str:
    # 去 emoji
    txt = EMOJI_RE.sub("", txt)
    # 去裝飾性分隔線/圖案行
    lines = []
    for ln in txt.splitlines():
        if DECOR_RE.match(ln):
            continue
        # 刪掉太 AI 味的註解行或模組級 docstring 標語
        if ln.lstrip().startswith("#") and AIISH_RE.search(ln):
            continue
        lines.append(ln)
    txt = "\n".join(lines)
    # 收尾空白
    txt = TRAILING_WS.sub("", txt)
    return txt


def ensure_future_annotations(txt: str) -> str:
    # 已經有就不重複
    if "from __future__ import annotations" in txt:
        return txt
    # 插在 shebang / encoding 之後，或檔頭
    lines = txt.splitlines()
    ins = 0
    while ins < len(lines) and (lines[ins].startswith("#!") or lines[ins].startswith("# -*-")):
        ins += 1
    lines.insert(ins, "from __future__ import annotations")
    return "\n".join(lines)


def process_file(p: Path) -> bool:
    old = p.read_text(encoding="utf-8", errors="ignore")
    new = scrub_text(old)
    new = ensure_future_annotations(new)
    if new != old:
        p.write_text(new, encoding="utf-8")
        return True
    return False


def main(paths: list[str]) -> None:
    changed = 0
    for base in paths:
        for p in Path(base).rglob("*.py"):
            # 跳過第三方/產物
            if any(
                seg in p.parts
                for seg in (
                    ".venv",
                    "venv",
                    "__pycache__",
                    "site-packages",
                    "_vendored",
                    "vendored",
                    "bundled",
                )
            ):
                continue
            if process_file(p):
                changed += 1
    print(f"[scrub] files changed: {changed}")


if __name__ == "__main__":
    mains = sys.argv[1:] or [
        "src/smart_mail_agent/core",
        "src/smart_mail_agent/features",
        "src/smart_mail_agent/spam",
    ]
    main(mains)
