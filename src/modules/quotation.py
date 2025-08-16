from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from utils.pdf_safe import write_pdf_or_txt


def choose_package(subject: str, content: str) -> dict[str, object]:
    s = f"{subject or ''}{content or ''}".lower()
    if any(k in s for k in ["報價", "詢價", "價格", "quote", "quotation", "合作", "採購"]):
        return {"package": "基礎", "needs_manual": False}
    if any(k in s for k in ["自動化", "排程"]):
        return {"package": "專業", "needs_manual": False}
    if any(k in s for k in ["api", "整合", "erp", "line"]):
        return {"package": "企業", "needs_manual": False}
    return {"package": "企業", "needs_manual": False}


def generate_pdf_quote(*args, **kwargs) -> Path:
    """
    A) generate_pdf_quote(package="基礎", client_name="client@example.com", outdir="data/output")
    B) generate_pdf_quote(customer: str, items: Sequence[tuple[str,int,float]]|None=None,
       outdir="data/output")
    """
    outdir = Path(kwargs.get("outdir", "data/output"))

    # 新 API（測試）
    if "package" in kwargs and "client_name" in kwargs:
        package = kwargs["package"]
        client = kwargs["client_name"]
        lines = [f"Package: {package}", f"Client: {client}", "Thank you."]
        return write_pdf_or_txt(lines, outdir, basename=f"quote-{client}")

    # 舊 API（保留向後相容）
    if args and isinstance(args[0], str):
        customer = args[0]
    else:
        customer = kwargs.get("customer", "customer")
    items: Sequence[tuple[str, int, float]] = kwargs.get("items") or []
    lines = [f"Quotation for {customer}", ""]
    total = 0.0
    for name, qty, price in items:
        subtotal = qty * price
        total += subtotal
        lines.append(f"{name} x{qty} = {subtotal:.2f}")
    lines.append("")
    lines.append(f"Total: {total:.2f}")
    # 為了避開 signature 差異，仍用 out_dir/basename 的鍵
    return write_pdf_or_txt(lines, out_dir=outdir, basename=f"quote-{customer}")
