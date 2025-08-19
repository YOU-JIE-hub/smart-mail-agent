#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Any, Dict
import re

__all__ = ["generate_pdf_quote", "choose_package"]

def _contains(s: str, *keywords: str) -> bool:
    s = (s or "").lower()
    return any(k.lower() in s for k in keywords)

def choose_package(*, subject: str = "", content: str = "") -> Dict[str, Any]:
    """
    規則：
      - 含「附件很大 / 請協助 / 需要人工」或偵測到 >=5MB 的 '...MB' => needs_manual=True
      - 含 'ERP' 或 'SSO' => package='企業整合'
      - 含 'workflow' 或 '自動化' => package='進階自動化'
      - 其餘 => package='標準'
    回傳: {"package": str, "needs_manual": bool}
    """
    subj = subject or ""
    body = content or ""
    text = f"{subj}\n{body}"

    needs_manual = False
    if _contains(text, "附件很大", "請協助", "需要人工"):
        needs_manual = True
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*MB", text, flags=re.IGNORECASE)
        if m:
            try:
                if float(m.group(1)) >= 5.0:
                    needs_manual = True
            except ValueError:
                pass

    if _contains(text, "ERP", "SSO"):
        package = "企業整合"
    elif _contains(text, "workflow", "自動化"):
        package = "進階自動化"
    else:
        package = "標準"

    return {"package": package, "needs_manual": needs_manual}

def generate_pdf_quote(
    company: str,
    items: Iterable[tuple[str, int, float]],
    *,
    outdir: str | Path | None = None,
    **_: Any,
) -> str:
    """
    產生極簡報價單；相容舊/新 utils.pdf_safe.write_pdf_or_txt 簽名：
      - 新版: write_pdf_or_txt(content, outdir, basename)
      - 舊版: write_pdf_or_txt(content, out_path)
    回傳輸出檔路徑（字串）
    """
    from smart_mail_agent.utils.pdf_safe import write_pdf_or_txt

    outdir_p = Path(outdir or ".")
    outdir_p.mkdir(parents=True, exist_ok=True)

    total = 0.0
    lines = [f"Quotation for {company}", "", "Items:"]
    for name, qty, price in items:
        total += qty * price
        lines.append(f"- {name} x {qty} @ {price:.2f}")
    lines.append("")
    lines.append(f"Total: {total:.2f}")
    content = "\n".join(lines)

    try:
        # 偏向新版簽名
        return write_pdf_or_txt(content, outdir_p, "quote.pdf")
    except TypeError:
        # 回退到舊版簽名
        return write_pdf_or_txt(content, outdir_p / "quote.pdf")
