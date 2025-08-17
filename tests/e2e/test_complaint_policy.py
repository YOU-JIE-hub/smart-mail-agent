import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PY = sys.executable


def run_cli(payload: dict) -> dict:
    in_p = ROOT / "data/output/in_c.json"
    out_p = ROOT / "data/output/out_c.json"
    in_p.parent.mkdir(parents=True, exist_ok=True)
    in_p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    cmd = [
        PY,
        "-m",
        "src.run_action_handler",
        "--input",
        str(in_p),
        "--output",
        str(out_p),
    ]
    env = dict(os.environ)
    env["OFFLINE"] = "1"
    subprocess.run(cmd, cwd=str(ROOT), check=True, env=env)
    return json.loads(out_p.read_text(encoding="utf-8"))


def test_complaint_high_triggers_p1_and_cc():
    payload = {
        "subject": "系統當機導致客戶無法使用",
        "from": "user@example.com",
        "body": "目前服務 down，影響交易，請立即處理。",
        "predicted_label": "complaint",
        "confidence": 0.92,
        "attachments": [],
    }
    out = run_cli(payload)
    assert out["action_name"] == "complaint"
    assert out["meta"]["priority"] == "P1"
    assert out["meta"]["SLA_eta"] == "4h"
    cc = (out["meta"].get("cc") or []) if isinstance(out["meta"], dict) else []
    assert any(c in cc for c in ["qa@company.example", "ops@company.example"])
    assert out["meta"].get("next_step")
