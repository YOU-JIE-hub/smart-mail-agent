from __future__ import annotations
from pathlib import Path
import runpy
import sys
import smart_mail_agent.utils.pdf_safe as pdf_safe

def test_cli_main_runs(tmp_path):
    # 以新簽名 stub，避免 PDF 依賴與亂寫檔
    def _stub(content, outdir, basename):
        p = Path(outdir) / (basename + ".txt")
        Path(outdir).mkdir(parents=True, exist_ok=True)
        text = "\n".join(content) if isinstance(content,(list,tuple)) else str(content)
        p.write_text(text, encoding="utf-8"); return str(p)
    pdf_safe.write_pdf_or_txt = _stub

    for argv in (["modules.quotation"], ["modules.quotation","ACME","Basic=1x100"]):
        sys.modules.pop("modules.quotation", None)
        bak = sys.argv[:]
        try:
            sys.argv = argv[:]
            try:
                runpy.run_module("modules.quotation", run_name="__main__", alter_sys=True)
            except SystemExit:
                pass  # CLI 可能 exit(0/2)，能跑到即可
        finally:
            sys.argv = bak
