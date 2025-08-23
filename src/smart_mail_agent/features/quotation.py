from __future__ import annotations
import os, re, pathlib

QUOTES_DIR = pathlib.Path(os.environ.get("QUOTES_DIR", "quotes"))
QUOTES_DIR.mkdir(parents=True, exist_ok=True)

def _safe_stem(name: str) -> str:
    # 允許中英數與常見 CJK，其他統一成底線；壓縮多個底線；去除結尾的 '.' 或 '_'
    s = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", name or "")
    s = re.sub(r"_+", "_", s).strip("._")
    return s or "_"

def generate_pdf_quote(*, package: str="標準", client_name: str|None=None, subject: str|None=None) -> str:
    # 取用 client_name，沒有就退而求其次用 subject
    stem = _safe_stem(client_name or subject or "")
    pdf_path = QUOTES_DIR / f"{stem}.pdf"
    # 這裡用極簡 mock 內容；你的專案裡若已有真實 PDF 生成邏輯，保留即可
    pdf_path.write_bytes(b"%PDF-1.4\n% Mock PDF Content\n")
    return str(pdf_path)
