# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(payload: dict, tmpdir: Path) -> dict:
    i = tmpdir / "in.json"
    o = tmpdir / "out.json"
    i.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    env = os.environ.copy()
    env["OFFLINE"] = "1"
    env["PYTHONPATH"] = str(Path("src").resolve())
    cmd = [sys.executable, "-m", "src.run_action_handler", "--input", str(i), "--output", str(o)]
    subprocess.run(cmd, check=True, env=env)
    return json.loads(o.read_text(encoding="utf-8"))


def test_label_send_quote(tmp_path: Path):
    out = _run_cli(
        {
            "subject": "報價",
            "from": "a@b.c",
            "body": "請報價",
            "predicted_label": "send_quote",
            "confidence": 0.9,
            "attachments": [],
        },
        tmp_path,
    )
    action = out.get("action_name") or out.get("action")
    assert action == "send_quote"


def test_label_reply_faq(tmp_path: Path):
    out = _run_cli(
        {
            "subject": "FAQ",
            "from": "a@b.c",
            "body": "退貨流程?",
            "predicted_label": "reply_faq",
            "confidence": 0.9,
            "attachments": [],
        },
        tmp_path,
    )
    action = out.get("action_name") or out.get("action")
    assert action == "reply_faq"
    subj = out.get("subject") or ""
    assert subj.startswith("[自動回覆] ")


def test_label_other_to_reply_general(tmp_path: Path):
    out = _run_cli(
        {
            "subject": "其他",
            "from": "a@b.c",
            "body": "Hi",
            "predicted_label": "other",
            "confidence": 0.5,
            "attachments": [],
        },
        tmp_path,
    )
    action = out.get("action_name") or out.get("action")
    assert action == "reply_general"
