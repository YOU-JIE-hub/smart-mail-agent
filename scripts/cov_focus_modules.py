from __future__ import annotations
from pathlib import Path
import tempfile, runpy, sys
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# 新簽名（顯式 outdir）
p1 = Path(generate_pdf_quote("ACME* 公司", [("Basic", 1, 100.0)], outdir=tmpdir))
assert p1.exists()

# 舊簽名 fallback（兩參數介面）
def _oldsig(content, out_path):
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content, (list, tuple)) else str(content)
    outp.write_text(text, encoding="utf-8")
    return str(outp)
pdf_safe.write_pdf_or_txt = _oldsig
p2 = Path(generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir))
assert p2.exists()

# 預設 outdir（不傳 outdir）
p3 = Path(generate_pdf_quote("Long —— 測試", [("Std", 1, 9.9)]))
assert p3.exists()

# choose_package 全分支 + 容錯
for subj, body in [
    ("需要 ERP 整合", ""),
    ("", "workflow 自動化"),
    ("附件很大，請協助", ""),
    ("一般詢價", "內容"),
    (None, None),
]:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r

# __main__ 入口
for argv in (["modules.quotation"], ["modules.quotation", "ACME", "Basic=1x100"]):
    try:
        bak = sys.argv[:]
        sys.argv = argv[:]
        runpy.run_module("modules.quotation", run_name="__main__", alter_sys=True)
    except SystemExit:
        pass
    finally:
        sys.argv = bak
