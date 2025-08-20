from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# 新簽名：帶怪字元公司名 → 觸發檔名清理 + PDF 路徑
p1 = generate_pdf_quote("A?C/ME* 公司", [("Basic", 1, 100.0)], outdir=tmpdir)
assert Path(p1).exists()

# 舊簽名：改寫成 old-style API 以走 except TypeError 分支 → 走 TXT 後援
def _oldsig(content, out_path):
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(content) if isinstance(content, (list, tuple)) else str(content), encoding="utf-8")
    return str(outp)
pdf_safe.write_pdf_or_txt = _oldsig
p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p2).exists()

# choose_package：把所有分支都踩過（大小寫 / 無空白 / 複合關鍵字 / 預設）
cases = [
    ("需要 ERP 整合", ""),           # 企業整合
    ("erp", ""),                    # 大小寫 & 短詞
    ("", "workflow 自動化"),        # 進階自動化
    ("", "WorkFlow 自動化"),        # 大小寫變體
    ("", "附件5MB"),                # 無空白，臨界值
    ("", "附件 6 MB"),              # 超過 5MB → 需要人工
    ("ERP 整合 與 workflow", ""),    # 複合關鍵字（測試優先序）
    ("一般詢價", "內容"),           # 預設標準
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
