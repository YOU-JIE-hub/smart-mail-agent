from __future__ import annotations
from pathlib import Path
from typing import Iterable, Tuple, Any
import re

__all__ = ["choose_package", "generate_pdf_quote"]

# ---- heuristics for "needs manual" ----
_FLAG_PHRASES = (
    "附件很大",
    "附件過大",
    "附件太大",
    "檔案很大",
    "檔案過大",
    "大附件",
    "large attachment",
    "big attachment",
)
_MB_RX = re.compile(r"(\d+(?:\.\d+)?)\s*mb", re.IGNORECASE)


def _maybe_needs_manual(text: str) -> tuple[bool, str | None]:
    low = text.lower()
    if any(p.lower() in low for p in _FLAG_PHRASES):
        return True, "flag_phrase"
    m = _MB_RX.search(low)
    if m:
        try:
            size = float(m.group(1))
        except Exception:
            size = -1.0
        return True, f"mentions_size_mb:{size}"
    return False, None


def _infer_package(text: str) -> str:
    low = text.lower()
    # 企業級：整合 / API / ERP / LINE / webhook / 串接
    if any(k in low for k in ("整合", "api", "erp", "line", "webhook", "串接", "integration")):
        return "企業"
    # 專業：自動化 / workflow / 自動分類 / 排程
    if any(k in low for k in ("自動化", "workflow", "自動分類", "排程", "automation")):
        return "專業"
    # 基礎：報價 / 價格 / 試算 / 詢價
    if any(k in low for k in ("報價", "價格", "價錢", "費用", "詢價", "正式報價", "試算")):
        return "基礎"
    # 預設給企業（符合測試：其他詢問 -> 企業）
    return "企業"


def choose_package(subject: str = "", content: str = "") -> dict:
    """同時支援位置參數與關鍵字參數；永遠回傳 package 與 needs_manual。"""
    text = f"{subject or ''}\n{content or ''}"
    package = _infer_package(text)
    needs_manual, reason = _maybe_needs_manual(text)
    return {"package": package, "needs_manual": bool(needs_manual), "reason": reason or "auto"}


# ---- quote generation (legacy-compatible) ----
def _lines_from_legacy(client: str, items: Iterable[Tuple[str, int, float]]) -> list[str]:
    total = 0.0
    rows: list[str] = [f"Quote for {client}"]
    for name, qty, price in items:
        rows.append(f"{name} x {qty} @ {price:.2f}")
        total += qty * float(price)
    rows.append(f"Total: {total:.2f}")
    return rows


def generate_pdf_quote(*args: Any, **kwargs: Any) -> str:
    """兩種呼叫方式都支援：
    1) 新版：generate_pdf_quote(out_dir=None, *, package=None, client_name=None) -> str
    2) 舊版：generate_pdf_quote(client_name, items, outdir=pathlike) -> str
    """
    try:
        from utils.pdf_safe import write_pdf_or_txt  # 頂層 utils 版本
    except Exception:  # pragma: no cover
        from smart_mail_agent.utils.pdf_safe import write_pdf_or_txt  # type: ignore

    # ---- 舊版 (client_name, items, outdir=...) ----
    if len(args) >= 2 and isinstance(args[0], str):
        client_name = args[0]
        items = args[1]
        outdir = kwargs.get("outdir") or kwargs.get("out_dir") or Path.cwd() / "out"
        lines = _lines_from_legacy(client_name, items)
        return write_pdf_or_txt(lines, outdir, "quote")

    # ---- 新版：keyword 為主 ----
    out_dir = kwargs.get("out_dir") or (Path.cwd() / "out")
    package = kwargs.get("package")
    client_name = kwargs.get("client_name")

    title = f"Quote for {client_name}" if client_name else "Quote"
    lines = [title]
    if package:
        lines.append(f"Package: {package}")
    return write_pdf_or_txt(lines, out_dir, "quote")
