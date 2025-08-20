from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# 新簽名路徑（pdf）
p1 = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmpdir)
assert Path(p1).exists()

# 舊簽名路徑（txt fallback）
def _oldsig(content, out_path):
    out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    return str(out_path)
pdf_safe.write_pdf_or_txt = _oldsig
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# choose_package 四條分支都打到
cases = [
    ("需要 ERP 整合", ""),            # 企業整合
    ("", "workflow 自動化"),           # 進階自動化
    ("附件很大，請協助", ""),          # needs_manual
    ("一般詢價", "內容"),              # 標準
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
