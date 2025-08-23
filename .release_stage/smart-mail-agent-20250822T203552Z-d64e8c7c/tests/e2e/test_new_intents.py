from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


def _run_cli(inp, outp):
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
    ]
    subprocess.run(cmd, check=True, env=env)


def test_sales_inquiry(tmp_path):
    i = tmp_path / "in.json"
    o = tmp_path / "out.json"
    i.write_text(
        json.dumps(
            {
                "subject": "合作洽談",
                "from": "boss@example.com",
                "body": "想談合作與規格",
                "predicted_label": "sales_inquiry",
                "confidence": 0.9,
                "attachments": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _run_cli(i, o)
    d = json.loads(o.read_text(encoding="utf-8"))
    a = d.get("action_name") or d.get("action")
    assert a == "sales_inquiry"
    assert (d.get("subject") or "").startswith("[自動回覆]")
    assert pathlib.Path("data/leads/leads.csv").exists()


def test_complaint(tmp_path):
    i = tmp_path / "in.json"
    o = tmp_path / "out.json"
    i.write_text(
        json.dumps(
            {
                "subject": "我要投訴",
                "from": "user@example.com",
                "body": "服務很差！退貨退款！",
                "predicted_label": "complaint",
                "confidence": 0.95,
                "attachments": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    _run_cli(i, o)
    d = json.loads(o.read_text(encoding="utf-8"))
    a = d.get("action_name") or d.get("action")
    assert a == "complaint"
    assert (d.get("subject") or "").startswith("[自動回覆]")
    assert pathlib.Path("data/complaints/log.csv").exists()
