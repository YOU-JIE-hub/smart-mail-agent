import json
import pathlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_cli(payload: dict, *flags: str):
    with tempfile.TemporaryDirectory() as td:
        inp = pathlib.Path(td) / "in.json"
        out = pathlib.Path(td) / "out.json"
        inp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        cmd = [
            sys.executable,
            str(ROOT / "src" / "run_action_handler.py"),
            "--input",
            str(inp),
            "--output",
            str(out),
            *flags,
        ]
        cp = subprocess.run(cmd, text=True)
        assert cp.returncode == 0
        return json.loads(out.read_text(encoding="utf-8"))


def test_double_ext_and_long_name_and_mime_mismatch_trigger_review():
    payload = {
        "predicted_label": "reply_faq",
        "from": "a@b.c",
        "subject": "測試",
        "body": "附件測試",
        "attachments": [
            {"filename": "invoice.pdf.exe", "mime": "application/x-msdownload"},
            {"filename": "A" * 130 + ".pdf", "mime": "application/pdf"},
            {
                "filename": "report.pdf",
                "mime": "application/octet-stream",
            },  # 與副檔名推測不符
        ],
    }
    out = _run_cli(payload, "--dry-run")
    m = out.get("meta") or {}
    assert m.get("require_review") is True
    risks = m.get("risks") or []
    assert any("attach:double_ext" in r for r in risks)
    assert any("attach:long_name" in r for r in risks)
    assert any("attach:mime_mismatch" in r for r in risks)
    cc = m.get("cc") or []
    assert "support@company.example" in cc
