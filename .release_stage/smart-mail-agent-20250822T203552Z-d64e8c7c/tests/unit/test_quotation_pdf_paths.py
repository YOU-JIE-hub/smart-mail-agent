from __future__ import annotations
from pathlib import Path
from modules.quotation import generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

def test_generate_pdf_quote_newsig(tmp_path):
    p = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmp_path)
    assert Path(p).exists()

def test_generate_pdf_quote_oldsig_fallback(tmp_path, monkeypatch):
    # 舊簽名：write_pdf_or_txt(content, out_path)
    def oldsig(content, out_path):
        out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(content) if isinstance(content, list) else str(content)
        out.write_text(text, encoding="utf-8")
        return str(out)
    monkeypatch.setattr(pdf_safe, "write_pdf_or_txt", oldsig)
    p = generate_pdf_quote("ACME-OLD", [("Pro", 2, 50.0)], outdir=tmp_path)
    assert Path(p).exists()
