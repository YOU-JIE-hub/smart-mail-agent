from __future__ import annotations
from pathlib import Path
from typing import Sequence, Tuple
import inspect

try:
    from utils.pdf_safe import write_pdf_or_txt  # 專案 util
except Exception:
    def write_pdf_or_txt(lines, out_dir=Path("data/output"), basename="attachment", font_candidates=None):
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{basename}.txt"
        if isinstance(lines, (list, tuple)):
            out.write_text("\n".join(map(str, lines)), encoding="utf-8")
        else:
            out.write_text(str(lines), encoding="utf-8")
        return out

_ZH_BASIC = "基礎"
_ZH_STD   = "專業"
_ZH_PRO   = "企業"

def _needs_manual_flag(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in ["附件","attach","attachment","mb","兆","很大","大檔","big","large","6mb"," 6 mb"])

def choose_package(subject_or_budget, content: str | None = None) -> dict:
    """
    兩種呼叫：
      1) choose_package(subject, content) -> {"package": "基礎|專業|企業", "needs_manual": bool}
      2) choose_package(budget_number)    -> {"package": "basic|standard|pro", "needs_manual": False}
    """
    if content is None:
        try:
            b = float(subject_or_budget or 0)
        except Exception:
            b = 0.0
        if b >= 400: return {"package": "pro", "needs_manual": False}
        if b >= 150: return {"package": "standard", "needs_manual": False}
        return {"package": "basic", "needs_manual": False}

    text = f"{subject_or_budget or ''} {content or ''}"
    if any(k in text for k in ["ERP","API","整合","LINE","line","Api","api"]):
        pkg = _ZH_PRO
    elif any(k in text for k in ["自動","排程","workflow","automation"]):
        pkg = _ZH_STD
    elif any(k in text for k in ["報價","詢價","quote","quotation","價格","price"]):
        pkg = _ZH_BASIC
    else:
        pkg = _ZH_PRO
    return {"package": pkg, "needs_manual": _needs_manual_flag(text)}

def _write_path_adaptive(lines, outdir: Path, basename: str):
    """
    適配 utils.pdf_safe.write_pdf_or_txt 的不同簽名：
      A) (lines, out_dir=..., basename="...")
      B) (lines, out_path)  # 直接給檔名
    """
    sig = inspect.signature(write_pdf_or_txt)
    params = list(sig.parameters.keys())
    if len(params) >= 2 and params[1] in {"out_dir", "outdir"}:
        # 用位置參數避免關鍵字不相容
        return write_pdf_or_txt(lines, outdir, basename)
    if len(params) >= 2 and params[1] in {"out_path", "path"}:
        return write_pdf_or_txt(lines, outdir / f"{basename}.pdf")
    # 保守退回 (lines, out_dir, basename)
    return write_pdf_or_txt(lines, outdir, basename)

def generate_pdf_quote(*args, **kwargs) -> str:
    """
    A) generate_pdf_quote(package="基礎", client_name="client@example.com", outdir="data/output")
    B) generate_pdf_quote(customer: str, items: Sequence[Tuple[str,int,float]]|None=None, outdir="data/output")
    """
    outdir = Path(kwargs.get("outdir", "data/output"))

    # 新 API（測試）
    if "package" in kwargs and "client_name" in kwargs:
        package = kwargs["package"]
        client  = kwargs["client_name"]
        content = f"Package: {package}\nClient: {client}\nThank you."
        path = _write_path_adaptive([content], outdir, f"quote-{client}")
        return str(path)

    # 舊 API
    if args:
        customer = args[0]
    else:
        customer = kwargs.get("customer", "customer")
    items: Sequence[Tuple[str, int, float]] = kwargs.get("items") or []
    lines = [f"Quotation for {customer}", ""]
    total = 0.0
    for name, qty, price in items:
        total += qty * float(price)
        lines.append(f"{name} x{qty} @ {price} = {qty*float(price):.2f}")
    lines += ["", f"Total: {total:.2f}"]
    path = _write_path_adaptive(lines, outdir, f"quote-{customer}")
    return str(path)
