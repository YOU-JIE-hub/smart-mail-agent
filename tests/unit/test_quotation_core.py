from __future__ import annotations
from pathlib import Path
import pathlib
import smart_mail_agent.utils.pdf_safe as pdf_safe
from modules.quotation import choose_package, generate_pdf_quote

def test_generate_pdf_quote_new_old_and_default(tmp_path):
    # 新簽名（PDF or TXT 均可）
    p1 = Path(generate_pdf_quote("ACME* 公司", [("Basic",1,100.0),("加值",2,0.5)], outdir=tmp_path))
    assert p1.exists() and p1.suffix in {".pdf", ".txt"}

    # 舊簽名（兩參數）：觸發 except TypeError 分支；不強制副檔名
    def _oldsig(content, out_path):
        outp = Path(out_path); outp.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(content) if isinstance(content,(list,tuple)) else str(content)
        outp.write_text(text, encoding="utf-8"); return str(outp)
    pdf_safe.write_pdf_or_txt = _oldsig
    p2 = Path(generate_pdf_quote("ACME2",[("Pro",2,50.0)], outdir=tmp_path))
    assert p2.exists()

    # default outdir：不給 outdir，走 Path.home 分支（覆蓋 basename 清理/預設輸出夾）
    orig_home = pathlib.Path.home
    try:
        pathlib.Path.home = lambda: tmp_path  # type: ignore
        p3 = Path(generate_pdf_quote("Default/Out? Co.", [("Std",1,9.9)]))
        assert p3.exists()
    finally:
        try: pathlib.Path.home = orig_home  # type: ignore
        except Exception: pass

def test_choose_package_all_paths():
    cases = [
        ("需要 ERP 整合", ""),                 # -> 企業整合
        ("", "workflow 自動化"),               # -> 進階自動化
        ("附件很大，請協助", ""),               # -> needs_manual True
        ("一般詢價", "內容"),                  # -> 標準
        (None, None),                         # 容錯
        ("", ""),                             # 容錯
    ]
    seen = {"企業整合": False, "進階自動化": False, "標準": False, "needs_manual": False}
    for subj, body in cases:
        r = choose_package(subject=subj, content=body)
        assert isinstance(r, dict) and "package" in r and "needs_manual" in r
        seen[r["package"]] = True
        if r.get("needs_manual"): seen["needs_manual"] = True
    assert all(seen.values())
