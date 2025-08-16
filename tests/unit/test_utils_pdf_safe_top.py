from __future__ import annotations

from pathlib import Path

from utils.pdf_safe import write_pdf_or_txt  # 頂層 utils 版本


def test_write_txt_fallback_and_outdir_creation(tmp_path):
    outdir = tmp_path / "nested"
    path = write_pdf_or_txt(["Hello", "World"], outdir, "demo-smoke")
    p = Path(path)
    assert p.exists()
    assert p.suffix in (".pdf", ".txt")
    assert outdir.exists()


def test_write_with_custom_basename(tmp_path):
    path = write_pdf_or_txt(["Line"], tmp_path, "q-123_測試")
    assert Path(path).exists()
