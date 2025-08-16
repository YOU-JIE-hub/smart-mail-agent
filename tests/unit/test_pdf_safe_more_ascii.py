from pathlib import Path

from smart_mail_agent.utils import pdf_safe as ps


def test_ascii_escape_and_multiline_pdf(tmp_path):
    s = "a(b)c)中文\\ 雙字節"
    e = ps._escape_pdf_text(s)
    assert "\\(" in e and "\\)" in e and "\\\\" in e
    assert all(32 <= ord(ch) <= 126 for ch in e)

    out = tmp_path / "multi.pdf"
    p = ps._write_minimal_pdf(["Hello", "World"], out)
    assert isinstance(p, Path) and p.exists()
    head = p.read_bytes()[:5]
    assert head == b"%PDF-"
