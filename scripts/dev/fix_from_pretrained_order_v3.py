#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def split_top_level_commas(s: str) -> list[str]:
    out, buf = [], []
    depth, in_str, esc = 0, False, False
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
            in_str, quote = True, ch
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
    i, changed = 0, 0
    out = []
    while True:
        j = src.find(".from_pretrained(", i)
        if j == -1:
            out.append(src[i:])
            break
        # 找前綴（AutoTokenizer / AutoModelForSequenceClassification / 變數等）
        k = j - 1
        while k >= 0 and (src[k].isalnum() or src[k] in "._"):
            k -= 1
        prefix = src[k + 1 : j]  # 不動它
        # 尋找對應右括號
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
                    in_str, quote = True, ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            pos += 1
        if pos >= len(src):  # 括號不配對：放棄改寫
            out.append(src[i:])
            break

        args_str = src[lp:pos]
        tokens = split_top_level_commas(args_str)

        # 分出位置/關鍵字（保留原順序），並去除明顯重複的 KW
        pos_args_raw = []
        kw_args_order, seen_kw = [], set()
        for t in tokens:
            if "=" in t.split("=", 1)[0]:
                key = t.split("=", 1)[0].strip()
                if key in seen_kw:
                    continue
                seen_kw.add(key)
                kw_args_order.append(t.strip())
            else:
                pos_args_raw.append(t.strip())

        # 選擇最合理的第一個位置參數：優先 model_path / MODEL_NAME / MODEL_PATH
        preferred = None
        for cand in ("model_path", "MODEL_NAME", "MODEL_PATH"):
            if cand in pos_args_raw:
                preferred = cand
                break
        if preferred is None:
            # 若只有 'main' 這種字面字串，且同時存在 revision=，就丟掉 'main'
            cleaned = [p for p in pos_args_raw if p.strip("'\"") != "main"]
            pos_args = cleaned or pos_args_raw or ["model_path"]  # 最後保守用 model_path
        else:
            pos_args = [preferred]

        # 確保 revision/trust_remote_code/local_files_only 若存在則保留，缺少可不補
        # （我們不強行新增，以避免引用未宣告變數）
        new_args = ", ".join(pos_args + kw_args_order)

        out.append(src[i : k + 1] + prefix + ".from_pretrained(" + new_args + ")")
        i = pos + 1
        changed += 1

    return "".join(out), changed


p = Path("src/classifier.py")
src = p.read_text(encoding="utf-8")
new_src, n = rewrite_calls(src)
if n and new_src != src:
    bak = p.with_suffix(p.suffix + ".bak")
    bak.write_text(src, encoding="utf-8")
    p.write_text(new_src, encoding="utf-8")
    print(f"fixed {n} call(s); backup at {bak}")
else:
    print("no change or nothing to fix")
