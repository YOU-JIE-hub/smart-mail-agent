from __future__ import annotations

import importlib
from pathlib import Path

# 走 shim：優先 utils.pdf_safe，若無則 smart_mail_agent.utils.pdf_safe
try:
    mod = importlib.import_module("utils.pdf_safe")
except Exception:
    mod = importlib.import_module("smart_mail_agent.utils.pdf_safe")

write_pdf_or_txt = getattr(mod, "write_pdf_or_txt", None)


def test_write_pdf_or_txt_blocks_path_traversal(tmp_path):
    if write_pdf_or_txt is None:
        import pytest

        pytest.skip("write_pdf_or_txt not available")
    outdir = tmp_path / "out"
    outdir.mkdir()
    # basename 惡意嘗試跳出 outdir
    fname = write_pdf_or_txt(["hello"], outdir, "../../evil")
    p = Path(fname).resolve()
    assert str(p).startswith(str(outdir.resolve()))
    assert p.exists()


def test_write_pdf_or_txt_handles_non_ascii(tmp_path):
    if write_pdf_or_txt is None:
        import pytest

        pytest.skip("write_pdf_or_txt not available")
    outdir = tmp_path / "出貨"
    outdir.mkdir()
    fname = write_pdf_or_txt(["世界"], outdir, "報價單")
    assert Path(fname).exists()
