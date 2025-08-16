import json, subprocess, tempfile, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

def _run_cli(payload: dict, *flags: str):
    with tempfile.TemporaryDirectory() as td:
        inp = pathlib.Path(td) / "in.json"
        out = pathlib.Path(td) / "out.json"
        inp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        cmd = [
            sys.executable,
            str(ROOT / "src" / "run_action_handler.py"),
            "--input", str(inp),
            "--output", str(out),
            *flags,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0, (r.stdout, r.stderr)
        return json.loads(out.read_text(encoding="utf-8"))

def test_send_quote_simulate_failure_and_require_review():
    payload = {
        "predicted_label": "send_quote",
        "from": "Alice <a@trusted.example>",
        "subject": "大檔案請協助",
        "body": "如題，附件很大",
        "attachments": [{"filename": "big.bin", "size": 6 * 1024 * 1024}],
    }
    out = _run_cli(payload, "--dry-run", "--simulate-failure")
    assert out["action_name"] == "send_quote"
    assert any(a["filename"].endswith(".txt") for a in out["attachments"])

    m = out["meta"]
    assert m.get("require_review") is True
    assert m.get("dry_run") is True
    # 有些路徑不填 whitelisted；允許 None/True，但需有 cc 安全副本
    assert m.get("whitelisted") in (True, None)
    assert "support@company.example" in m.get("cc", [])

def test_complaint_p1_path():
    payload = {"predicted_label": "complaint", "subject": "系統宕機", "body": "嚴重 無法使用"}
    out = _run_cli(payload, "--dry-run")
    assert out["action_name"] == "complaint"
    m = out["meta"]
    assert m.get("priority") in ("P1", "p1")
    assert m.get("SLA_eta") in ("4h", "4H", "4小時")
