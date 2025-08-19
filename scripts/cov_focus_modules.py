from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# 新簽名（write_pdf_or_txt(content, outdir, basename)）
p1 = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmpdir)
assert Path(p1).exists()

# 舊簽名（write_pdf_or_txt(content, out_path)）走 except TypeError 分支
def oldsig(content, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return str(out_path)
pdf_safe.write_pdf_or_txt = oldsig
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# choose_package 的各分支
cases = [
    ("需要 ERP 整合", ""),
    ("", "workflow 自動化"),
    ("附件很大，請協助", ""),
    ("", "附件 6MB，請處理"),
    ("一般詢價", "內容"),
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
