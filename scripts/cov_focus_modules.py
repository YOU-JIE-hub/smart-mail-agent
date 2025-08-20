from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# -- 新簽名（會嘗試寫 PDF）
p1 = generate_pdf_quote("ACME股份有限公司", [("Basic", 1, 100.0), ("加值", 2, 0.5)], outdir=tmpdir)
assert Path(p1).exists()

# -- 舊簽名 fallback（覆寫成兩參數簽名 → 走 TXT）
def oldsig(content, out_path):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(content) if isinstance(content, str) else "\n".join(content), encoding="utf-8")
    return str(out)
pdf_safe.write_pdf_or_txt = oldsig
p2 = generate_pdf_quote("測試公司", [], outdir=tmpdir)
assert Path(p2).exists()

# -- 企業整合：ERP/SSO
for s in ("需要 ERP 整合", "SSO 單點登入"):
    choose_package(subject=s, content="")
    choose_package(subject="", content=s)

# -- 進階自動化：workflow / 自動化
for t in ("workflow 自動化", "我們要做自動化流程"):
    choose_package(subject=t, content="")
    choose_package(subject="", content=t)

# -- needs_manual：≥ 5MB（多種寫法）
for mb in ("5MB", "5 MB", "005mb", "5.0MB", "6mb", "10 MB"):
    choose_package(subject="", content=f"附件 {mb}，請協助")

# -- 非 needs_manual 邊界：< 5MB
for mb in ("4.9MB", "4.99 MB", "4mb", "0mb"):
    choose_package(subject="", content=f"附件 {mb}")

# -- 關鍵字：附件很大 / 請協助
choose_package(subject="附件很大，請協助", content="")

# -- 預設/空字串路徑
for subj, body in (("一般詢價", "normal"), ("", ""), (None, None)):
    choose_package(subject=subj or "", content=body or "")
