import importlib, inspect
from pathlib import Path

def _fill_for(sig, out_path):
    m = {
        "customer":"ACME", "company":"ACME", "recipient":"ACME",
        "package":"標準",
        "subject":"一般詢價",
        "content":"請提供報價", "body":"請提供報價", "message":"請提供報價",
        "output": str(out_path), "path": str(out_path), "outfile": str(out_path), "filepath": str(out_path),
    }
    kw = {}
    for name in sig.parameters:
        if name in m: kw[name] = m[name]
    return kw

def test_generate_pdf_quote_smoke(tmp_path, monkeypatch):
    q = importlib.import_module("modules.quotation")
    monkeypatch.chdir(tmp_path)
    assert hasattr(q, "generate_pdf_quote")
    sig = inspect.signature(q.generate_pdf_quote)
    out = tmp_path / "quote.pdf"
    kw = _fill_for(sig, out)
    res = q.generate_pdf_quote(**kw)

    candidates = [out]
    if isinstance(res, (str, Path)):
        candidates.append(Path(res))
    candidates.append(tmp_path / "quote_pdf.pdf")

    exists = [p for p in candidates if p.exists()]
    assert exists, f"no pdf produced among: {candidates}"
    assert exists[0].stat().st_size > 0
