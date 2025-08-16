from __future__ import annotations
import time
from pathlib import Path
from typing import Sequence, Union

__all__ = ["write_pdf_or_txt"]

def _safe_join(outdir: Union[str, Path], basename: str) -> Path:
    out = Path(outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    # 只取檔名，砍掉任何路徑（防 ../../ 跳脫）
    name = Path(basename or "output").name
    # 統一 .pdf 後綴，但內容以 UTF-8 純文字寫入即可（避免外部 PDF 依賴）
    stem = name[:-4] if name.lower().endswith(".pdf") else name
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{stem}_{ts}.pdf"
    p = (out / fname).resolve()

    # 最終保險：強制結果仍位於 outdir 裡
    if not str(p).startswith(str(out)):
        p = (out / fname).resolve()
    return p

def write_pdf_or_txt(lines: Sequence[str], outdir: Union[str, Path], basename: str) -> str:
    p = _safe_join(outdir, basename)
    content = "\n".join(str(x) for x in lines)
    p.write_text(content, encoding="utf-8")
    return str(p)
