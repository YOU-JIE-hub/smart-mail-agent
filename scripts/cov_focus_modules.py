from __future__ import annotations
from pathlib import Path
import tempfile
from modules.quotation import choose_package, generate_pdf_quote
import smart_mail_agent.utils.pdf_safe as pdf_safe

tmpdir = Path(tempfile.mkdtemp())

# --- 新簽名（PDF）: 觸發檔名清理 & 非 ASCII ---
p_pdf = generate_pdf_quote("A?C/ME* 公司", [("Basic", 1, 100.0), ("加值", 2, 0.5)], outdir=tmpdir)
assert Path(p_pdf).exists()

# --- 舊簽名（TXT fallback）: 觸發 except TypeError ---
def _oldsig(content, out_path):
    outp = Path(out_path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(content) if isinstance(content, (list, tuple)) else str(content)
    outp.write_text(text, encoding="utf-8")
    return str(outp)
pdf_safe.write_pdf_or_txt = _oldsig
p_txt = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmpdir)
assert Path(p_txt).exists()

# --- choose_package：踩滿關鍵分支/優先序/大小寫/臨界 ---
cases = [
    ("需要 ERP 整合", ""),            # ERP → 企業整合
    ("erp", ""),                     # 小寫
    ("", "workflow 自動化"),         # workflow → 進階自動化
    ("", "WorkFlow 自動化"),         # 大小寫變體
    ("", "附件5MB"),                 # 無空白臨界
    ("", "附件 6 MB"),               # 超過 → 需要人工
    ("ERP 整合 與 workflow", ""),     # 複合關鍵字（測優先序覆蓋）
    ("一般詢價", "內容"),            # 預設標準
    (None, None),                    # None 安全處理
    ("附件很大，請協助", ""),        # 明確需要人工
]
for subj, body in cases:
    r = choose_package(subject=subj, content=body)
    assert isinstance(r, dict) and "package" in r and "needs_manual" in r
