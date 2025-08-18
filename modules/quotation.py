from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

__all__ = ["choose_package", "generate_pdf_quote"]

_SIZE_RX = re.compile(r"(\d+(?:\.\d+)?)\s*MB", re.I)


def choose_package(subject: str = "", content: str = "") -> dict[str, Any]:
    text = f"{subject or ''} {content or ''}"
    # needs manual if explicit phrase or >= 5MB mentioned
    if "附件很大" in text:
        return {"needs_manual": True}
    m = _SIZE_RX.search(text)
    if m and float(m.group(1)) >= 5.0:
        return {"needs_manual": True}

    t = text.lower()
    if "workflow" in t or "自動化" in text:
        return {"needs_manual": False, "package": "進階自動化"}
    if any(x in t for x in ("erp", "sso")) or "整合" in text:
        return {"needs_manual": False, "package": "企業整合"}
    if any(x in text for x in ("報價", "價格")):
        return {"needs_manual": False, "package": "基礎"}

    return {"needs_manual": False, "package": "專業"}


def generate_pdf_quote(*args, **kwargs) -> str:
    """
    Two compatible call styles:
      1) New: generate_pdf_quote(package="基礎", client_name="client@example.com", outdir=".")
      2) Legacy: generate_pdf_quote("ACME", [("Basic", 1, 100.0)], outdir=tmpdir)
    Returns: path to written PDF (or .txt fallback)
    """
    from smart_mail_agent.utils.pdf_safe import write_pdf_or_txt

    # New style
    if not args and "package" in kwargs and "client_name" in kwargs:
        package = str(kwargs["package"])
        client = str(kwargs["client_name"])
        outdir = Path(kwargs.get("outdir") or ".")
        content = f"Package: {package}\nClient: {client}\nThank you."
        return write_pdf_or_txt(content, outdir, "quote.pdf")

    # Legacy style
    if len(args) >= 2:
        company = str(args[0])
        items: Iterable[tuple[str, int, float]] = args[1]  # type: ignore[assignment]
        outdir = Path(kwargs.get("outdir") or ".")
        total = 0.0
        lines = [f"Quotation for {company}", "", "Items:"]
        for name, qty, price in items:
            total += qty * float(price)
            lines.append(f"- {name} x {qty} @ {float(price):.2f}")
        lines.append("")
        lines.append(f"Total: {total:.2f}")
        return write_pdf_or_txt("\n".join(lines), outdir, "quote.pdf")

    # Fallback: write whatever kwargs we got
    outdir = Path(kwargs.get("outdir") or ".")
    content = "\n".join(f"{k}: {v}" for k, v in kwargs.items()) or "Quotation"
    return write_pdf_or_txt(content, outdir, "quote.pdf")
