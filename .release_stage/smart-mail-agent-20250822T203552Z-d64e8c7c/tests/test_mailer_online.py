#!/usr/bin/env python3
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
    assert (
        proc.returncode == 0
    ), f"online_check.py 退出碼非 0：\n{proc.stderr or proc.stdout}"
    assert "SMTP 寄信成功" in proc.stdout, f"未偵測到 SMTP 成功訊息：\n{proc.stdout}"
