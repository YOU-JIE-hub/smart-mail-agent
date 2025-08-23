from pathlib import Path
import importlib, time
mod = importlib.import_module("smart_mail_agent.features.sales.quotation")

def test_choose_package():
    assert mod.choose_package("我要報價","")["package"] in ("基礎","專業","企業")
    assert mod.choose_package("","我想退款")["package"] in ("基礎","專業","企業")
    r = mod.choose_package("","噪音文字")
    assert "package" in r and "needs_manual" in r

def test_generate_pdf_quote(tmp_path):
    p = mod.generate_pdf_quote("專業","客戶X", out_dir=str(tmp_path))
    assert Path(p).exists() and Path(p).suffix==".pdf"
