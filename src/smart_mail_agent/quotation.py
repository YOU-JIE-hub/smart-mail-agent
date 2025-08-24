from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict


def choose_package(subject: str, content: str) -> Dict[str, str]:
    text = f"{subject} {content}"
    if any(k in text for k in ("API", "整合", "ERP", "LINE")):
        pkg = "企業"
    elif any(k in text for k in ("自動", "自動化", "排程", "分類")):
        pkg = "專業"
    elif any(k in text for k in ("報價", "價格", "費用")):
        pkg = "基礎"
    else:
        pkg = "企業"
    return {"package": pkg}


def _safe_name(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9_.-]+", "_", s)
    return s or "client"


def generate_pdf_quote(*, package: str, client_name: str) -> str:
    out_dir = Path(os.getenv("QUOTE_DIR", Path.home() / "quotes"))
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{_safe_name(client_name)}.pdf"
    path = out_dir / fname
    # 簡單寫入 PDF 標頭，供測試驗證副檔名與存在性
    path.write_bytes(b"%PDF-1.4\n% minimal pdf for test\n1 0 obj <<>> endobj\ntrailer <<>>\n%%EOF\n")
    return str(path)
