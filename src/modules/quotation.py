from __future__ import annotations
from pathlib import Path
from typing import Sequence, Tuple
try:
    from utils.pdf_safe import write_pdf_or_txt
except Exception:
    def write_pdf_or_txt(path, text): Path(path).write_text(str(text), encoding="utf-8")

PACKAGES = {
    "basic":    {"price": 99,  "features": ["Email support"]},
    "standard": {"price": 199, "features": ["Email+Phone", "SLA 48h"]},
    "pro":      {"price": 499, "features": ["Priority", "SLA 4h"]},
}

def choose_package(budget: float | int) -> str:
    b = float(budget or 0)
    if b >= 400: return "pro"
    if b >= 150: return "standard"
    return "basic"

def generate_pdf_quote(customer: str,
                       items: Sequence[Tuple[str, int, float]] | None = None,
                       outdir: str = "data/output") -> str:
    Path(outdir).mkdir(parents=True, exist_ok=True)
    total = 0.0
    lines = [f"Quotation for {customer}", ""]
    for name, qty, price in (items or []):
        total += qty * float(price)
        lines.append(f"{name} x{qty} @ {price} = {qty*float(price):.2f}")
    lines += ["", f"Total: {total:.2f}"]
    out = Path(outdir) / f"quote-{customer}.pdf"
    write_pdf_or_txt(out, "\n".join(lines))
    return str(out)
