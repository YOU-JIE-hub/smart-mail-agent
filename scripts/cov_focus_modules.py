from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe
tmpdir = Path(tempfile.mkdtemp())
p1 = generate_pdf_quote("ACME",[("Basic",1,100.0)],outdir=tmpdir); assert Path(p1).exists()
def oldsig(content, out_path):
    out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content); return str(out_path)
pdf_safe.write_pdf_or_txt = oldsig
p2 = generate_pdf_quote("ACME2",[("Pro",2,50.0)],outdir=tmpdir); assert Path(p2).exists()
for subj,body in [("需要 ERP 整合",""),("","workflow 自動化"),("附件很大，請協助",""),("一般詢價","內容")]:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r,dict) and "package" in r and "needs_manual" in r
