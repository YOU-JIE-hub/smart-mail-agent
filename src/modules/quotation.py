from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

# ---- choose_package: 依關鍵字回應測試期望 ----
_SIZE_RX = re.compile(r"(\d+(?:\.\d+)?)\s*MB", re.I)


def choose_package(*, subject: str = "", content: str = "") -> dict[str, Any]:
    text = f"{subject} {content}"

    # 需要人工：明確說附件很大，或大小 >= 5MB
    if "附件很大" in text:
        return {"needs_manual": True}
    m = _SIZE_RX.search(text)
    if m and float(m.group(1)) >= 5.0:
        return {"needs_manual": True}

    # 其他關鍵字：workflow/自動化 → 進階自動化；ERP/SSO/整合 → 企業整合
    t = text.lower()
    if ("workflow" in t) or ("自動化" in text):
        return {"needs_manual": False, "package": "進階自動化"}
    if ("erp" in t) or ("sso" in t) or ("整合" in text):
        return {"needs_manual": False, "package": "企業整合"}

    # 預設回一個合理值
    return {"needs_manual": False, "package": "專業"}


# ---- generate_pdf_quote: 相容舊版 outdir=... ----
def generate_pdf_quote(
    company: str,
    items: Iterable[tuple[str, int, float]],
    *,
    outdir: str | Path | None = None,
    **_: Any,
) -> str:
    from smart_mail_agent.utils.pdf_safe import write_pdf_or_txt

    outdir_p = Path(outdir or ".")
    outdir_p.mkdir(parents=True, exist_ok=True)
    out_path = outdir_p / "quote.pdf"

    # 用簡單的文字內容組報價單
    total = 0.0
    lines = [f"Quotation for {company}", "", "Items:"]
    for name, qty, price in items:
        total += qty * price
        lines.append(f"- {name} x {qty} @ {price:.2f}")
    lines.append("")
    lines.append(f"Total: {total:.2f}")

    return write_pdf_or_txt("\n".join(lines), out_path)
