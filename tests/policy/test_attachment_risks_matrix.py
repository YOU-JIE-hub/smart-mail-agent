import json
import pathlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_cli(payload, *flags):
    with tempfile.TemporaryDirectory() as td:
        i = Path(td) / "in.json"
        o = Path(td) / "out.json"
        i.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(
            [
                sys.executable,
                str(ROOT / "src" / "run_action_handler.py"),
                "--input",
                str(i),
                "--output",
                str(o),
                *flags,
            ],
            text=True,
        )
        assert r.returncode == 0
        return json.loads(o.read_text(encoding="utf-8"))


def test_mime_edge_cases_matrix():
    payload = {
        "predicted_label": "reply_faq",
        "attachments": [
            {"filename": "safe.pdf", "mime": "application/pdf"},
            {"filename": "payroll.xlsm.exe", "mime": "application/x-msdownload"},
            {"filename": "R" * 200 + ".pdf", "mime": "application/pdf"},
            {"filename": "brief.pdf", "mime": "application/octet-stream"},
        ],
    }
    out = _run_cli(payload, "--dry-run")
    m = out.get("meta") or {}
    risks = m.get("risks") or []
    assert any("double_ext" in r for r in risks)
    assert any("long_name" in r for r in risks)
    assert any("mime_mismatch" in r for r in risks)
    assert m.get("require_review") is True
    # 需要安全副本
    assert "support@company.example" in (m.get("cc") or [])
