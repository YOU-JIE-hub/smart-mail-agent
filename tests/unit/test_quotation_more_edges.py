from __future__ import annotations
from pathlib import Path
from modules.quotation import choose_package, generate_pdf_quote

def test_filename_sanitized_and_created(tmp_path):
    # 不合法字元都會被清理，且實際有產物
    p = generate_pdf_quote("A?C/ME* 公司", [("Basic", 1, 1.0)], outdir=tmp_path)
    name = Path(p).name
    assert Path(p).exists()
    for ch in "?*/\\":
        assert ch not in name

def test_choose_package_variations_and_default():
    cases = [
        ("ERP 整合與 workflow", ""),     # 同時出現關鍵字（取規則優先序）
        ("", "附件 5 mb"),               # 單位大小寫
        ("", "附件5MB"),                 # 無空白
        ("", "附件 6 MB"),               # >5MB
        ("", ""),                        # 完全無訊息 → 標準且不需人工
    ]
    for subj, content in cases:
        r = choose_package(subject=subj, content=content)
        assert isinstance(r, dict) and "package" in r and "needs_manual" in r
    r0 = choose_package(subject="", content="")
    assert r0["package"] == "標準" and r0["needs_manual"] is False
