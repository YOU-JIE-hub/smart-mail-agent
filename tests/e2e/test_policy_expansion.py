import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PY = sys.executable


def run_cli(payload: dict, name: str) -> dict:
    in_p = ROOT / f"data/output/in_{name}.json"
    out_p = ROOT / f"data/output/out_{name}.json"
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


def test_attachments_over_limit_requires_review():
    payload = {
        "subject": "一般詢問",
        "from": "user@somewhere.com",
        "body": "附件很多請協助查看。",
        "predicted_label": "reply_faq",
        "confidence": 0.9,
        "attachments": [{"filename": "a.bin", "size": 6 * 1024 * 1024}],
    }
    out = run_cli(payload, "overlimit")
    assert out["meta"].get("require_review") is True


def test_sender_domain_whitelist_flag():
    payload = {
        "subject": "一般詢問",
        "from": "alice@trusted.example",
        "body": "這是白名單寄件者。",
        "predicted_label": "reply_faq",
        "confidence": 0.9,
        "attachments": [],
    }
    out = run_cli(payload, "whitelist")
    assert out["meta"].get("whitelisted") is True
