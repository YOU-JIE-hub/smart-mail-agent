from __future__ import annotations
from pathlib import Path
import tempfile, importlib, runpy, sys, pathlib
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())
q = importlib.import_module("modules.quotation")

# A) 新簽名
p1 = Path(q.generate_pdf_quote("A?C/ME* 公司", [("Basic",1,100.0),("加值",2,0.5)], outdir=tmpdir)); assert p1.exists()

# B) 舊簽名（兩參數）→ except TypeError
def _oldsig(content, out_path):
    outp = Path(out_path); outp.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content,(list,tuple)) else str(content)
    outp.write_text(text, encoding="utf-8"); return str(outp)
pdf_safe.write_pdf_or_txt = _oldsig
p2 = Path(q.generate_pdf_quote("ACME2",[("Pro",2,50.0)], outdir=tmpdir)); assert p2.exists()

# C) default outdir（Path.home → tmpdir）
try:
    orig_home = pathlib.Path.home
    pathlib.Path.home = lambda: tmpdir  # type: ignore
    p3 = Path(q.generate_pdf_quote("DefaultOut", [("Std",1,9.9)])); assert p3.exists()
finally:
    try: pathlib.Path.home = orig_home  # type: ignore
    except Exception: pass

# D) choose_package：所有路徑 + 容錯
for subj, body in [("需要 ERP 整合",""),("","workflow 自動化"),("附件很大，請協助",""),("一般詢價","內容"),(None,None),("","")]:
    r = q.choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r

# E) __main__ 入口，以新簽名 stub，避免寫 PDF
def _stub(content, outdir, basename):
    p = Path(outdir) / (basename + ".txt")
    Path(outdir).mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content,(list,tuple)) else str(content)
    p.write_text(text, encoding="utf-8"); return str(p)
pdf_safe.write_pdf_or_txt = _stub

for argv in (["modules.quotation"], ["modules.quotation","ACME","Basic=1x100"]):
    sys.modules.pop("modules.quotation", None)
    bak = sys.argv[:]
    try:
        sys.argv = argv[:]
        try:
            runpy.run_module("modules.quotation", run_name="__main__", alter_sys=True)
        except SystemExit:
            pass
    finally:
        sys.argv = bak
