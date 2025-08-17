#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def split_top_level_commas(s: str) -> list[str]:
    out, buf = [], []
    depth = 0
    in_str = False
    esc = False
    quote = ""
    for ch in s:
        if in_str:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                in_str = False
            continue
        if ch in "\"'":
            in_str = True
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


def fix_source(src: str) -> tuple[str, int]:
    i = 0
    changed = 0
    out = []
    while True:
        j = src.find(".from_pretrained(", i)
        if j == -1:
            out.append(src[i:])
            break
        # 找前綴（物件/類別名）
        k = j - 1
        while k >= 0 and (src[k].isalnum() or src[k] in "._"):
            k -= 1
        prefix = src[
            k + 1 : j
        ]  # 例如 AutoTokenizer 或 AutoModelForSequenceClassification 或某變數.pipeline
        # 括號配對
        lp = j + len(".from_pretrained(")
        pos = lp
        depth = 1
        in_str = False
        esc = False
        quote = ""
        while pos < len(src):
            ch = src[pos]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == quote:
                    in_str = False
            else:
                if ch in "\"'":
                    in_str = True
                    quote = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            pos += 1
        if pos >= len(src):
            # 括號不配對，跳過
            out.append(src[i:])
            break
        args_str = src[lp:pos]
        args = split_top_level_commas(args_str)
        # 重排：位置參數在前，關鍵字在後（保序）
        pos_args = [a for a in args if "=" not in a.split("=", 1)[0]]
        kw_args = [a for a in args if "=" in a.split("=", 1)[0]]
        new_args = ", ".join(pos_args + kw_args)
        out.append(src[i : k + 1] + prefix + ".from_pretrained(" + new_args + ")")
        i = pos + 1
        changed += 1
    return "".join(out), changed


p = Path("src/classifier.py")
src = p.read_text(encoding="utf-8")
new_src, n = fix_source(src)
if n and new_src != src:
    bak = p.with_suffix(p.suffix + ".bak")
    bak.write_text(src, encoding="utf-8")
    p.write_text(new_src, encoding="utf-8")
    print(f"fixed {n} call(s); backup: {bak}")
else:
    print("no change")
