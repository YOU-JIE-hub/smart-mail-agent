import json, sys
from pathlib import Path
import importlib
run = importlib.import_module("smart_mail_agent.routing.run_action_handler")

def test_risk_helpers():
    # 副檔名與 MIME 檢查
    att = {"filename":"report.xlsm.exe", "mime":"application/pdf", "size":6*1024*1024}
    rs = run._attachment_risks(att)
    assert "attach:double_ext" in rs and "attach:too_large" in rs
    # MIME 不符
    att2 = {"filename":"a.pdf", "mime":"text/plain", "size":10}
    assert "attach:mime_mismatch" in run._attachment_risks(att2)

def test_cli_stdin_and_flags(tmp_path, monkeypatch, capsys):
    payload = {"predicted_label":"send_quote","subject":"x","body":"y","attachments":[{"filename":"a.pdf","mime":"application/pdf","size":10}]}
    # 走 stdin 讀取
    monkeypatch.setattr(sys, "stdin", type("S",(),{"read":lambda self=None: json.dumps(payload)})())
    argv = ["--dry-run","--simulate-failure","--out",str(tmp_path/"o.json")]
    rc = run.main(argv)
    assert rc==0
    outp = tmp_path/"o.json"
    assert outp.exists()
    data = json.loads(outp.read_text(encoding="utf-8"))
    assert data["meta"]["dry_run"] and data["meta"]["require_review"]
