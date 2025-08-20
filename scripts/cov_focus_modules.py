from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# 新簽名（會走 PDF）
p1 = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmpdir)
assert Path(p1).exists()

# 舊簽名（觸發 except TypeError 或舊介面路徑）
def oldsig(content, out_path):
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content, list) else str(content)
    out.write_text(text, encoding="utf-8")
    return str(out)
pdf_safe.write_pdf_or_txt = oldsig
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# choose_package 的主要分支都打到
for subj, body in [
    ("需要 ERP 整合", ""),
    ("", "我們計畫導入 SSO 與 ERP"),
    ("Workflow 引擎", ""),
    ("", "workflow 自動化與表單審批"),
    ("附件很大，請協助", ""),
    ("", "附件 6MB，請處理"),
    ("", "有個 5MB 附件在內"),
    ("一般詢價", "想瞭解產品"),
]:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
