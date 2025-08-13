import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PY = sys.executable


def run_cli(payload: dict) -> dict:
    in_p = ROOT / "data/output/in_sales.json"
    out_p = ROOT / "data/output/out_sales.json"
    in_p.parent.mkdir(parents=True, exist_ok=True)
    in_p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    cmd = [PY, "-m", "src.run_action_handler", "--input", str(in_p), "--output", str(out_p)]
    env = dict(os.environ)
    env["OFFLINE"] = "1"
    subprocess.run(cmd, cwd=str(ROOT), check=True, env=env)
    return json.loads(out_p.read_text(encoding="utf-8"))


def test_sales_inquiry_generates_md_and_next_step():
    payload = {
        "subject": "合作報價與時程 2025-08-20",
        "from": "alice@biz.com",
        "body": "本公司偉大股份有限公司 需要 50 台 方案，預算 NTD 300,000，請於 2025/08/20 前回覆。",
        "predicted_label": "sales_inquiry",
        "confidence": 0.87,
        "attachments": [],
    }
    out = run_cli(payload)
    assert out["action_name"] == "sales_inquiry"
    names = [a["filename"] for a in out.get("attachments", [])]
    assert any(n.endswith(".md") and "needs_summary_" in n for n in names)
    assert out["meta"].get("next_step"), "meta.next_step 應存在"
