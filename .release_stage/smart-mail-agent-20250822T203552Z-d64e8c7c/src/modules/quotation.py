from __future__ import annotations
import re, json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# 優先用我們實作的最小 PDF writer（先前已放在 shim）
try:
    from smart_mail_agent.smart_mail_agent.utils.pdf_safe import _write_minimal_pdf as _write_pdf  # type: ignore
except Exception:
    _write_pdf = None  # type: ignore

def _extract_size_mb(text: str) -> float:
    """抓取像 6MB / 10.5 MB 的大小，沒有就回 0."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*MB\b", text, re.I)
    return float(m.group(1)) if m else 0.0

def choose_package(subject: str, body: str) -> Dict[str, Any]:
    """
    回傳 dict：
      - package/name: 方案名稱（入門/標準）
      - needs_manual: bool 是否需要人工確認
      - reason: 決策說明
      - meta.size_mb: 推測附件大小
    規則：
      - 若附件 >=5MB 或要求「正式報價」→ 標準
      - 其他 → 入門
      - 若附件 >=10MB 或文字提到「人工/手動/manual review」→ needs_manual=True
    """
    text = f"{subject}\n{body}".strip()
    size_mb = _extract_size_mb(text)
    wants_formal = bool(re.search(r"(正式報價|正式报价|formal\s+quote)", text))
    manual_hint = bool(re.search(r"(人工|手動|手动|manual\s+review)", text, re.I))
    pkg = "標準" if (size_mb >= 5 or wants_formal) else "入門"
    reason = "附件較大或需要正式報價" if pkg == "標準" else "需求一般，附件不大"
    needs_manual = manual_hint or size_mb >= 10.0
    return {
        "package": pkg,
        "name": pkg,
        "needs_manual": bool(needs_manual),
        "reason": reason,
        "meta": {"size_mb": size_mb},
    }

def _coerce_package_name(selection: Union[str, Dict[str, Any]]) -> str:
    if isinstance(selection, str):
        return selection
    if isinstance(selection, dict):
        return str(selection.get("package") or selection.get("name") or "入門")
    return "入門"

def generate_pdf_quote(selection: Union[str, Dict[str, Any]], out_path: Union[str, Path] = "quote.pdf") -> Path:
    """產生極簡 PDF 報價單；selection 可為字串或 dict。"""
    pkg = _coerce_package_name(selection)
    lines: List[str] = [
        "Smart Mail Agent 报价单",
        f"方案：{pkg}",
        "感謝您的洽詢！",
    ]
    out = Path(out_path)
    if _write_pdf is not None:
        return _write_pdf(lines, out)
    # 退路（簡單且合法即可）
    out.write_bytes(("%PDF-1.4\n" + "\n".join(lines) + "\n").encode("utf-8"))
    return out

def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover
    import argparse, sys
    p = argparse.ArgumentParser()
    p.add_argument("--subject", default="")
    p.add_argument("--body", default="")
    p.add_argument("--out", default="quote.pdf")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    res = choose_package(args.subject, args.body)
    pdf = generate_pdf_quote(res, args.out)
    if args.json:
        print(json.dumps({"selection": res, "pdf": str(pdf)}, ensure_ascii=False))
    else:
        print(f"✅ 產生：{pdf}，方案：{res['package']} 手動? {res['needs_manual']}")
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
