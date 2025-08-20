from __future__ import annotations
from pathlib import Path
import runpy, sys
import smart_mail_agent.utils.pdf_safe as pdf_safe

def test_cli_main_runs(tmp_path):
    # 用 stub 避免不受控寫檔；維持新簽名介面
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
                pass
        finally:
            sys.argv = bak
