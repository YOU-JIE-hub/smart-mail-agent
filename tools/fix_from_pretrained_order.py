#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def split_top_level_commas(s: str) -> list[str]:
    out, buf = [], []
    depth = 0
    in_str = False
    str_q = ""
    esc = False
    for ch in s:
        if in_str:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == str_q:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            str_q = ch
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
        if ch == "," and depth == 0:
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            continue
        buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def rewrite_calls(src: str) -> tuple[str, int]:
    i = 0
    changed = 0
    need = "from_pretrained("
    out = []
    while True:
        j = src.find(need, i)
        if j == -1:
            out.append(src[i:])
            break
        # write text before call
        out.append(src[i:j])
        # find '(' start and matching ')'
        lp = src.find("(", j)
        k = lp + 1
        depth = 1
        in_str = False
        str_q = ""
        esc = False
        while k < len(src):
            ch = src[k]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == str_q:
                    in_str = False
            else:
                if ch in ('"', "'"):
                    in_str = True
                    str_q = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            k += 1
        if k >= len(src):
            # unmatched, give up
            out.append(src[j:])
            break

        args_str = src[lp + 1 : k]
        args = split_top_level_commas(args_str)
        # 分出位置/關鍵字，保持原始順序
        pos_args = [a for a in args if "=" not in a.split("=", 1)[0]]
        kw_args = [a for a in args if "=" in a.split("=", 1)[0]]

        # 如果先前寫成了「關鍵字在前、位置在後」，這裡會重排為合法順序
        new_args = ", ".join(pos_args + kw_args)

        out.append("from_pretrained(" + new_args + ")")
        changed += 1
        i = k + 1
    return "".join(out), changed


p = Path("src/classifier.py")
src = p.read_text(encoding="utf-8")
new_src, n = rewrite_calls(src)
if n > 0 and new_src != src:
    backup = p.with_suffix(p.suffix + ".bak")
    backup.write_text(src, encoding="utf-8")
    p.write_text(new_src, encoding="utf-8")
    print(f"fixed {n} call(s); backup saved to {backup}")
else:
    print("no change (calls already ordered or not found)")
