from pathlib import Path
from modules.quotation import generate_pdf_quote

def test_generate_pdf_quote_both_signatures(tmp_path, monkeypatch):
    # 先用實作簽名（新版或舊版其一）
    p1 = generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmp_path)
    assert Path(p1).exists()

    # 再把 pdf_safe 換成「只支援舊簽名」的函式，打到 except TypeError 分支
    import smart_mail_agent.utils.pdf_safe as pdf_safe
    def oldsig(content, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content)
        return str(out_path)
    monkeypatch.setattr(pdf_safe, "write_pdf_or_txt", oldsig)

    p2 = generate_pdf_quote("ACME2", [("Pro", 2, 50.0)], outdir=tmp_path)
    assert Path(p2).exists()
