from __future__ import annotations

import re
import sys
from pathlib import Path

# 目標範圍（可用參數覆蓋）
DEFAULT_TARGETS = [Path("src/smart_mail_agent"), Path("src/patches")]

EMOJI = re.compile(
    "["  # emoji 區段
    "\U0001F300-\U0001FAFF"  # symbols & pictographs
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "]+"
)
ASCII_ART = re.compile(r"^[\s\-\=\_\*\#\~\^\.\|\\/]{6,}$")
AIY = re.compile(r"(AI小幫手|AI助手|魔法|神器|ChatGPT|大型語言模型|LLM(?:s)?)")

CTRL_HEAD = re.compile(
    r"^(\s*)"  # indent
    r"("
    r"if\b[^\:]*|elif\b[^\:]*|else|"
    r"for\b[^\:]*|while\b[^\:]*|"
    r"try|except\b[^\:]*|finally|"
    r"with\b[^\:]*"
    r")"
    r"\:\s*(\S.*)$"  # 單行主體（有東西才算違規）
)


def scrub_comment_or_blank(line: str) -> str:
    if line.strip() == "" or line.lstrip().startswith("#"):
        new = EMOJI.sub("", line)
        if ASCII_ART.match(new.strip()):
            return ""
        new = AIY.sub("", new)
        return new
    return line


def split_semicolons(line: str) -> list[str]:
    # 僅在「不在字串/括號內」的 ; 拆分
    if ";" not in line:
        return [line]
    buf = []
    parts = []
    quote = None
    esc = False
    depth = 0
    for ch in line:
        if esc:
            buf.append(ch)
            esc = False
            continue
        if ch == "\\":
            buf.append(ch)
            esc = True
            continue
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            continue
        if ch in "([{":
            depth += 1
            buf.append(ch)
            continue
        if ch in ")]}":
            depth -= 1
            buf.append(ch)
            continue
        if ch == ";" and depth == 0:
            parts.append("".join(buf).rstrip())
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    if len(parts) == 1:
        return [line]
    # 後續分段補上相同縮排
    indent = re.match(r"^(\s*)", line).group(1)  # type: ignore
    normalized = [parts[0]] + [indent + p.lstrip() for p in parts[1:] if p.strip()]
    return normalized


def expand_colon_one_liner(line: str) -> list[str] | None:
    m = CTRL_HEAD.match(line)
    if not m:
        return None
    indent, head, body = m.groups()
    # 只展開單行主體；保持語意不變
    return [f"{indent}{head}:", f"{indent}    {body}"]


def fix_pdf_safe_specifics(text: str) -> str:
    # 精準把 `_escape_pdf_text(l) for l in lines` 換成 ln，避免 E741
    return text.replace(
        "_escape_pdf_text(l) for l in lines", "_escape_pdf_text(ln) for ln in lines"
    )


def process_file(path: Path) -> bool:
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        return False

    changed = False
    out_lines: list[str] = []
    for raw in txt.splitlines():
        line = scrub_comment_or_blank(raw)
        # 先拆 ;
        semi_parts = []
        for part in split_semicolons(line):
            # 再拆「if/try/...: 單行」
            expanded = expand_colon_one_liner(part)
            if expanded is None:
                semi_parts.append(part)
            else:
                semi_parts.extend(expanded)
        if semi_parts != [raw]:
            changed = True
        out_lines.extend(semi_parts)

    out = "\n".join(out_lines).rstrip() + "\n"
    out2 = fix_pdf_safe_specifics(out)
    if out2 != txt:
        changed = True
        path.write_text(out2, encoding="utf-8")
    return changed


def iter_targets(args: list[str]) -> list[Path]:
    if args:
        items = []
        for a in args:
            p = Path(a)
            if p.exists():
                items.append(p)
        return items
    return DEFAULT_TARGETS


def main(argv: list[str]) -> int:
    changed = []
    for target in iter_targets(argv):
        if target.is_file() and target.suffix == ".py":
            if process_file(target):
                changed.append(str(target))
        elif target.is_dir():
            for py in sorted(target.rglob("*.py")):
                if "__pycache__" in py.parts:
                    continue
                if process_file(py):
                    changed.append(str(py))
    print(f"[linewise-fix] files changed: {len(changed)}")
    if changed:
        for p in changed:
            print(" -", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
