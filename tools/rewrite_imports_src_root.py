from __future__ import annotations

import re
import sys
from pathlib import Path

# 需要處理的根目錄（有就掃，沒有就跳過）
TARGETS = ["src", "tests", "scripts", "reports"]

# 基本規則：大多數 src.* → smart_mail_agent.*
BULK_RULES = [
    (r"\bfrom\s+src\.modules\b", "from smart_mail_agent.features"),
    (r"\bimport\s+src\.modules\b", "import smart_mail_agent.features"),
    (r"\bfrom\s+src\.utils\b", "from smart_mail_agent.utils"),
    (r"\bimport\s+src\.utils\b", "import smart_mail_agent.utils"),
    (r"\bfrom\s+src\.spam\b", "from smart_mail_agent.spam"),
    (r"\bimport\s+src\.spam\b", "import smart_mail_agent.spam"),
    (r"\bfrom\s+src\b", "from smart_mail_agent"),
    (r"\bimport\s+src\b", "import smart_mail_agent"),
]

# 常見舊→新 精確對應（優先於 BULK_RULES）
EXACT_RULES = [
    (r"\bfrom\s+src\s+import\s+classifier\b", "from smart_mail_agent import classifier"),
    (r"\bfrom\s+src\s+import\s+policy_engine\b", "from smart_mail_agent import policy_engine"),
    (r"\bfrom\s+src\s+import\s+sma_types\b", "from smart_mail_agent import sma_types"),
    (r"\bfrom\s+src\s+import\s+email_processor\b", "from smart_mail_agent import email_processor"),
    (
        r"\bfrom\s+src\s+import\s+support_ticket\b",
        "from smart_mail_agent.features.support import support_ticket",
    ),
    (r"\bfrom\s+src\.support_ticket\b", "from smart_mail_agent.features.support.support_ticket"),
    (r"\bfrom\s+src\.action_handler\b", "from smart_mail_agent.routing.action_handler"),
    (r"\bimport\s+src\.action_handler\b", "import smart_mail_agent.routing.action_handler"),
    (r"\bfrom\s+src\.run_action_handler\b", "from smart_mail_agent.routing.run_action_handler"),
    (r"\bimport\s+src\.run_action_handler\b", "import smart_mail_agent.routing.run_action_handler"),
    (r"\bfrom\s+src\.log_writer\b", "from smart_mail_agent.utils.log_writer"),
    (r"\bimport\s+src\.log_writer\b", "import smart_mail_agent.utils.log_writer"),
    (r"\bfrom\s+src\.stats_collector\b", "from smart_mail_agent.observability.stats_collector"),
    (r"\bimport\s+src\.stats_collector\b", "import smart_mail_agent.observability.stats_collector"),
]

SKIP_PARTS = {
    ".venv",
    "venv",
    "__pycache__",
    "site-packages",
    "_vendored",
    "vendored",
    "bundled",
    "node_modules",
    ".portfolio_hidden",
    "src_lowcov",
}


def rewrite_text(txt: str) -> str:
    out = txt
    # 先跑精確規則
    for pat, rep in EXACT_RULES:
        out = re.sub(pat, rep, out)
    # 再跑一般規則
    for pat, rep in BULK_RULES:
        out = re.sub(pat, rep, out)
    return out


def should_touch(p: Path) -> bool:
    if p.suffix != ".py":
        return False
    parts = set(p.parts)
    if SKIP_PARTS & parts:
        return False
    # 不處理新樹
    if "smart_mail_agent" in p.parts and p.parts[
        p.parts.index("smart_mail_agent") - 1 : p.parts.index("smart_mail_agent")
    ] == ["src"]:
        # 仍然允許改 tests 中的任何檔，但 smart_mail_agent 內部一般不會引用 src.*
        pass
    return True


def main() -> None:
    changed = 0
    scanned = 0
    for base in TARGETS:
        root = Path(base)
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            if not should_touch(p):
                continue
            old = p.read_text(encoding="utf-8", errors="ignore")
            new = rewrite_text(old)
            scanned += 1
            if new != old:
                p.write_text(new, encoding="utf-8")
                changed += 1
    print(f"[rewrite_imports] scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
