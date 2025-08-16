from __future__ import annotations
try:
    # 優先走專案 shim
    from utils.pdf_safe import write_pdf_or_txt  # type: ignore
except Exception:
    import time
    from pathlib import Path
    from typing import Sequence, Union

    __all__ = ["write_pdf_or_txt"]

    def _safe_join(outdir: Union[str, Path], basename: str) -> Path:
        out = Path(outdir).resolve()
        out.mkdir(parents=True, exist_ok=True)
        name = Path(basename or "output").name
        stem = name[:-4] if name.lower().endswith(".pdf") else name
        ts = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{stem}_{ts}.pdf"
        p = (out / fname).resolve()
        if not str(p).startswith(str(out)):
            p = (out / fname).resolve()
        return p

    def write_pdf_or_txt(lines: Sequence[str], outdir: Union[str, Path], basename: str) -> str:
        p = _safe_join(outdir, basename)
        content = "\n".join(str(x) for x in lines)
        p.write_text(content, encoding="utf-8")
        return str(p)
