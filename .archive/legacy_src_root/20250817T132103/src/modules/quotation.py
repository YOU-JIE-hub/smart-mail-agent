from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path

# 盡量走本倉庫的 shim；若不可用再退回 smart_mail_agent 位置
try:
    from utils.pdf_safe import write_pdf_or_txt  # type: ignore
except Exception:  # pragma: no cover
    from smart_mail_agent.utils.pdf_safe import write_pdf_or_txt  # type: ignore

__all__ = ["choose_package", "generate_pdf_quote"]

RE_PRICE = re.compile(r"(報價|詢價|價格|費用|報價單|quote|quotation)", re.I)
RE_PRO = re.compile(r"(自動化|自動分類|排程|workflow|自動)", re.I)
RE_ENT = re.compile(r"(整合|API|ERP|LINE|Webhook|單點登入|SSO)", re.I)
RE_BIG = re.compile(r"(\d+(?:\.\d+)?)\s*(MB|M|兆)", re.I)


def _needs_manual(subject: str, content: str) -> bool:
    if "附件很大" in (subject or ""):
        return True
    m = RE_BIG.search(content or "")
    if m:
        try:
            if float(m.group(1)) >= 5:
                return True
        except Exception:
            pass
    return False


def choose_package(subject: str, content: str) -> dict:
    s = subject or ""
    c = content or ""

    if RE_ENT.search(s) or RE_ENT.search(c):
        pkg = "企業"
    elif RE_PRO.search(s) or RE_PRO.search(c):
        pkg = "專業"
    elif RE_PRICE.search(s) or RE_PRICE.search(c):
        pkg = "基礎"
    else:
        pkg = "企業"  # 其他詢問 → 企業

    return {"package": pkg, "needs_manual": _needs_manual(s, c)}


def generate_pdf_quote(*args, **kwargs) -> str:
    """
    A) generate_pdf_quote(package="基礎", client_name="client@example.com", outdir="data/output")
    B) generate_pdf_quote(customer: str, items: Sequence[tuple[str,int,float]]|None=None,
       outdir="data/output")

    回傳實際輸出的檔案路徑（str）。
    """
    outdir = Path(kwargs.get("outdir", "data/output"))

    # 新 API（測試）
    if "package" in kwargs and "client_name" in kwargs:
        package = kwargs["package"]
        client = kwargs["client_name"]
        lines = [f"Package: {package}", f"Client: {client}", "Thank you."]
        return str(write_pdf_or_txt(lines, outdir, f"quote-{client}"))

    # 舊 API（相容）
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
        lines.append(f"- {name} x{qty} @ {price:.2f} = {subtotal:.2f}")
    lines.append("")
    lines.append(f"Total: {total:.2f}")
    return str(write_pdf_or_txt(lines, outdir, f"quote-{customer}"))
