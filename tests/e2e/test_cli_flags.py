# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


def _run_cli(inp, outp, *extra):
    env = os.environ.copy()
    env.setdefault("OFFLINE", "1")
    cmd = [
        sys.executable,
        "-m",
        "src.run_action_handler",
        "--input",
        str(inp),
        "--output",
        str(outp),
        *extra,
    ]
    subprocess.run(cmd, check=True, env=env)


def test_dry_run_flag(tmp_path):
    i = tmp_path / "in.json"
    o = tmp_path / "out.json"
    i.write_text(
        json.dumps(
            {
                "subject": "請問服務內容？",
                "from": "a@b.c",
                "body": "想要了解細節",
                "predicted_label": "reply_faq",
                "confidence": 0.9,
                "attachments": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _run_cli(i, o, "--dry-run")
    d = json.loads(o.read_text(encoding="utf-8"))
    assert d.get("action_name") == "reply_faq"
    assert d.get("dry_run") is True


def test_simulate_pdf_failure(tmp_path):
    i = tmp_path / "in.json"
    o = tmp_path / "out.json"
    i.write_text(
        json.dumps(
            {
                "subject": "請報價",
                "from": "a@b.c",
                "body": "我要報價",
                "predicted_label": "send_quote",
                "confidence": 0.9,
                "attachments": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _run_cli(i, o, "--simulate-failure", "pdf")
    d = json.loads(o.read_text(encoding="utf-8"))
    assert d.get("action_name") == "send_quote"
    assert (
        "simulated_pdf_failure" in "|".join(d.get("warnings", [])) or d.get("meta", {}).get("simulate_failure") == "pdf"
    )
