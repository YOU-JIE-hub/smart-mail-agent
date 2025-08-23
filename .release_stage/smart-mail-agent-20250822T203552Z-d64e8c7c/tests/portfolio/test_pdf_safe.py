import smart_mail_agent.smart_mail_agent.utils.pdf_safe as ps


def test_escape_pdf_text_escapes_parens_and_non_ascii():
    s = "a(b)c)中文\\"
    e = ps._escape_pdf_text(s)
    assert "\\(" in e and "\\)" in e and "\\\\" in e
    assert all(32 <= ord(ch) <= 126 for ch in e)


def test_write_minimal_pdf_generates_valid_header(tmp_path):
    out = tmp_path / "x.pdf"
    p = ps._write_minimal_pdf(["Hello", "World"], out)
    data = p.read_bytes()
    assert data.startswith(b"%PDF-1.") and len(data) > 100
