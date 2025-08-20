from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# ---- A) generate_pdf_quote：新簽名（PDF 路徑） + 預設 outdir ----
p1 = generate_pdf_quote("A?C/ME* 公司", [("Basic", 1, 100.0), ("加值", 2, 0.5)], outdir=tmpdir)
assert Path(p1).exists()
# 不給 outdir，走預設輸出邏輯
p1b = generate_pdf_quote("Long Company Name —— 內部測試", [("Std", 3, 9.99)])
assert Path(p1b).exists()

# ---- B) generate_pdf_quote：舊簽名 fallback（TypeError 觸發） ----
def old_sig(content, out_path):
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content, (list, tuple)) else str(content)
    outp.write_text(text, encoding="utf-8")
    return str(outp)

pdf_safe.write_pdf_or_txt = old_sig  # 置換進舊簽名
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# ---- C) choose_package：關鍵分支/邊界/大小寫/空白/預設 ----
cases = [
    # ERP（大小寫、複合）
    ("需要 ERP 整合", ""), ("erp", ""), ("ERP 整合 與 workflow", ""),
    # workflow（大小寫）
    ("", "workflow 自動化"), ("", "WorkFlow 自動化"),
    # 附件大小：各種寫法/臨界
    ("", "附件5MB"), ("", "附件 5 MB"), ("", "附件 5.0 MB"),
    ("", "附件 4.99 MB"),  # 低於門檻
    ("", "附件 6 MB"),     # 高於門檻
    ("", "附件10mb"),      # 小寫 mb
    # 兩者命中 & 應有穩定返回
    ("ERP + 大附件", "workflow 附件 8 MB"),
    # 預設
    ("一般詢價", "內容"),
    # None/非字串/空白
    (None, None),
    ("", ""),
    ("  ", "  "),
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
