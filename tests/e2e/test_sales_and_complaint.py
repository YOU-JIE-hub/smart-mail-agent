#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PY = sys.executable


def run_cli(inp: dict, workdir: Path) -> dict:
    in_p, out_p = workdir / "in.json", workdir / "out.json"
    in_p.write_text(json.dumps(inp, ensure_ascii=False), encoding="utf-8")
    env = os.environ.copy()
    env.setdefault("SMA_OFFLINE", "1")
    env.setdefault("SMA_DATA_DIR", str(workdir))
    cmd = [
        PY,
        "-m",
        "src.run_action_handler",
        "--input",
        str(in_p),
        "--output",
        str(out_p),
        "--dry-run",
    ]
    subprocess.run(cmd, check=True, env=env)
    return json.loads(out_p.read_text(encoding="utf-8"))


def test_e2e_sales_inquiry(tmp_path):
    res = run_cli(
        {
            "subject": "詢價",
            "from": "alice@partner.co",
            "body": "我們是XX股份有限公司，需要數量 50，預算 20000，期限 2025-09-01。",
            "predicted_label": "sales_inquiry",
            "confidence": 0.9,
        },
        tmp_path,
    )
    assert res["action_name"] == "sales_inquiry"
    assert res["subject"].startswith("[自動回覆] ")


def test_e2e_complaint_high(tmp_path):
    res = run_cli(
        {
            "subject": "嚴重投訴",
            "from": "bob@example.com",
            "body": "產品無法使用而且非常惡劣，要求退款，否則投訴到主管機關。",
            "predicted_label": "complaint",
            "confidence": 0.8,
        },
        tmp_path,
    )
    assert res["action_name"] == "complaint"
    assert res["meta"]["priority"] in {"P1", "P2", "P3"}
