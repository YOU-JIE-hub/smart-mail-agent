#!/usr/bin/env python3
"""tools/apply_mailer_online_tests_v1.py
建立「線上寄信」整合測試與 Makefile 目標：
- tests/test_mailer_online.py：呼叫 scripts/online_check.py，斷言寄信成功訊息
- pytest.ini：加入 pytest -m online 的標記說明
- Makefile：新增 smtp-test-online 目標
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"[ok] write {p}")


# 1) 建立線上寄信測試
write(
    ROOT / "tests" / "test_mailer_online.py",
    """#!/usr/bin/env python3
# tests/test_mailer_online.py
# 在 ON-LINE 環境下，實際寄一封測試信到 REPLY_TO，驗證 SMTP 是否可用。
from __future__ import annotations
import os
import pathlib
import subprocess
import sys
import pytest

pytestmark = pytest.mark.online

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

def _skip_if_no_env() -> None:
    required = ["SMTP_USER", "SMTP_PASS", "SMTP_HOST", "SMTP_PORT", "REPLY_TO"]
    missing = [k for k in required if not os.getenv(k)]
    if os.getenv("OFFLINE", "0") == "1" or missing:
        pytest.skip(f"缺少環境變數或 OFFLINE=1，略過線上寄信測試。missing={missing}")

def test_smtp_live_send_ok() -> None:
    _skip_if_no_env()
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "online_check.py")],
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, f"online_check.py 退出碼非 0：\\n{proc.stderr or proc.stdout}"
    assert "SMTP 寄信成功" in proc.stdout, f"未偵測到 SMTP 成功訊息：\\n{proc.stdout}"
""",
)

# 2) 確保 pytest.ini 有 online 標記
pytest_ini = ROOT / "pytest.ini"
if pytest_ini.exists():
    txt = pytest_ini.read_text(encoding="utf-8")
    if "online:" not in txt:
        if "markers" not in txt:
            txt = txt.rstrip() + "\nmarkers =\n    online: tests that hit real SMTP/IMAP\n"
        else:
            txt = re.sub(
                r"(markers\s*=\s*)([^\n]*?)\n",
                r"\\1\\2\n    online: tests that hit real SMTP/IMAP\n",
                txt,
                flags=re.IGNORECASE,
            )
        pytest_ini.write_text(txt, encoding="utf-8")
        print("[ok] update pytest.ini markers")
else:
    write(pytest_ini, "[pytest]\nmarkers =\n    online: tests that hit real SMTP/IMAP\n")

# 3) Makefile 增加 smtp-test-online 目標
mk = ROOT / "Makefile"
target = (
    "\n.PHONY: smtp-test-online\n"
    "smtp-test-online:\n"
    "\tOFFLINE=0 PYTHONPATH=src .venv/bin/pytest -q -m online -k mailer_online -s\n"
)
if mk.exists():
    t = mk.read_text(encoding="utf-8")
    if "smtp-test-online:" not in t:
        mk.write_text(t + target, encoding="utf-8")
        print("[ok] append Makefile target: smtp-test-online")
else:
    write(mk, target)

print("\n[done] apply_mailer_online_tests_v1 completed.")
