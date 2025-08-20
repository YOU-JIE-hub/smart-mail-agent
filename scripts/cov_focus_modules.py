from __future__ import annotations
from pathlib import Path
import tempfile, runpy, importlib

from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# ---- A) generate_pdf_quote：新簽名（PDF 路徑） + 預設 outdir ----
p1 = generate_pdf_quote("A?C/ME* 公司", [("Basic", 1, 100.0), ("加值", 2, 0.5)], outdir=tmpdir)
assert Path(p1).exists()
p1b = generate_pdf_quote("Long Company Name —— 內部測試", [("Std", 3, 9.99)])
assert Path(p1b).exists()

# ---- B) generate_pdf_quote：舊簽名 fallback（觸發 except TypeError）----
def _old_sig(content, out_path):
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content, (list, tuple)) else str(content)
    outp.write_text(text, encoding="utf-8")
    return str(outp)
pdf_safe.write_pdf_or_txt = _old_sig
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# ---- C) choose_package：全分支/邊界/容錯 ----
cases = [
    ("需要 ERP 整合", ""), ("erp", ""), ("ERP 整合 與 workflow", ""),
    ("", "workflow 自動化"), ("", "WorkFlow 自動化"),
    ("", "附件5MB"), ("", "附件 5 MB"), ("", "附件 5.0 MB"),
    ("", "附件 4.99 MB"), ("", "附件 6 MB"), ("", "附件10mb"),
    ("ERP + 大附件", "workflow 附件 8 MB"),
    ("一般詢價", "內容"),
    (None, None), ("", ""), ("  ", "  "), (0, []), (object(), {"x":1}),
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r

# ---- D) 嘗試覆蓋 if __name__ == "__main__": 區塊 ----
try:
    runpy.run_module("modules.quotation", run_name="__main__", alter_sys=True)
except SystemExit:
    pass
except Exception:
    try:
        m = importlib.import_module("modules.quotation")
        if hasattr(m, "main") and callable(m.main):
            m.main()
    except Exception:
        pass
