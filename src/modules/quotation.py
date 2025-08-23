from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable, List, Tuple
import re

class PackageResult(str):
    """同時支援字串比較與 dict 取值的結果型別。"""
    def __new__(cls, label: str, package: str, needs_manual: bool):
        obj = str.__new__(cls, label)
        obj.package = package
        obj.needs_manual = needs_manual
        return obj
    def __getitem__(self, key: str):
        if key == "package":
            return self.package
        if key == "needs_manual":
            return self.needs_manual
        raise KeyError(key)
    def to_dict(self) -> dict:
        return {"package": self.package, "needs_manual": self.needs_manual}

_STD = ("基礎", "標準")           # (字串回傳, dict['package'])
_PRO = ("專業", "進階自動化")
_ENT = ("企業", "企業整合")

_MANUAL_PHRASES = ("附件很大","檔案太大","大附件","附件過大","檔案過大","請協助")
_ENT_KW = ("erp","sso","整合","api","line")
_AUTO_KW = ("workflow","自動化","表單","審批")

_MB_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mb", re.I)

def _needs_manual_by_text(text: str) -> bool:
    if not text:
        return False
    if any(k in text for k in _MANUAL_PHRASES):
        return True
    mbs = [float(x) for x in _MB_RE.findall(text)]
    return any(v >= 5.0 for v in mbs)

def choose_package(*args, **kwargs) -> PackageResult | dict:
    """
    兩種呼叫法皆可：
      - choose_package(subject=..., content=...)
      - choose_package(<subject>, <content>)   （舊測試用）
    回傳：
      - 若以 kwargs 呼叫：dict(package='標準|進階自動化|企業整合', needs_manual=bool)
      - 若以位置參數呼叫：PackageResult（可直接與 '基礎|專業|企業' 比較；也支援 ['package'] 與 ['needs_manual']）
    """
    if kwargs:
        subject = kwargs.get("subject") or ""
        content = kwargs.get("content") or ""
        ret_dict = True
    else:
        subject = args[0] if len(args) > 0 else ""
        content = args[1] if len(args) > 1 else ""
        ret_dict = False

    s = f"{subject or ''} {content or ''}"
    s_low = s.lower()

    needs_manual = _needs_manual_by_text(subject) or _needs_manual_by_text(content) or _needs_manual_by_text(s)

    # 先判斷企業/自動化，再讓「大附件」覆蓋成標準+人工
    if any(k in s_low for k in _ENT_KW):
        label, pkg = _ENT
    elif any(k in s_low for k in _AUTO_KW):
        label, pkg = _PRO
    else:
        label, pkg = _STD

    if needs_manual:
        label, pkg = _STD  # 大附件一律走標準方案 + 需人工

    result = PackageResult(label, pkg, needs_manual)
    return result.to_dict() if ret_dict else result

_SAN_RE = re.compile(r'[^0-9A-Za-z\u4e00-\u9fff\-_. ]+')

def _sanitize_filename(name: str) -> str:
    n = _SAN_RE.sub("_", name or "").strip()
    return n or "quotation"

def _lines_for(company: str, items: Iterable[Tuple[str, int, float]]) -> List[str]:
    total = 0.0
    lines = [f"Quotation for: {company}", "", "Items:"]
    for name, qty, price in items:
        total += float(qty) * float(price)
        lines.append(f"- {name} x{qty} @ {price}")
    lines.append(f"Total: {total}")
    return lines

def generate_pdf_quote(*args, **kwargs) -> str:
    """
    新簽名：
      generate_pdf_quote(company: str, items: list[tuple[str,int,float]], outdir=Path|str)
    舊簽名（相容）：
      generate_pdf_quote(out_dir: Path|str = None, *, package: str = None, client_name: str = None)

    回傳實際產物路徑（.pdf 或 .txt）。
    """
    company: str
    items: List[Tuple[str, int, float]]
    outdir = kwargs.get("outdir") or kwargs.get("out_dir")

    # 新版：("ACME", [("Basic",1,100.0)], outdir=...)
    if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], list):
        company, items = args[0], args[1]
    else:
        # 舊版：只給 out_dir，其他以具名參數補齊
        pkg = kwargs.get("package") or "標準"
        client = kwargs.get("client_name") or "客戶"
        company = str(client)
        items = [(str(pkg), 1, 0.0)]

    out_dir = Path(outdir) if outdir else (Path.home() / "quotes")
    out_dir.mkdir(parents=True, exist_ok=True)
    base = out_dir / f"{_sanitize_filename(company)}.pdf"
    lines = _lines_for(company, items)

    # 優先使用 pdf_safe（若環境/相依缺，就 fallback）
    try:
        from smart_mail_agent.utils import pdf_safe
        out = pdf_safe.write_pdf_or_txt(lines, str(base))
        return str(out)
    except Exception:
        txt = base.with_suffix(".txt")
        txt.write_text("\n".join(lines), encoding="utf-8")
        return str(txt)
