from pathlib import Path
import importlib
pdfs = importlib.import_module("smart_mail_agent.utils.pdf_safe")

def test_write_pdf_or_txt_pdf(tmp_path):
    p = pdfs.write_pdf_or_txt(["Hi","There"], tmp_path, "報價 單")
    assert Path(p).exists() and Path(p).suffix in (".pdf",".txt")

def test_write_pdf_or_txt_txt_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(pdfs, "_write_minimal_pdf", lambda lines, path: (_ for _ in ()).throw(RuntimeError("x")))
    p = pdfs.write_pdf_or_txt(["A"], tmp_path, "quote")
    assert Path(p).exists() and Path(p).suffix==".txt"
