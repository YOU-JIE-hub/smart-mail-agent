#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    mout = root / "data" / "output" / "matrix"
    reports = root / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    msum = mout / "matrix_summary.json"
    data = json.loads(msum.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    by = {}
    ok = 0
    for c in cases:
        by[c.get("action", "UNKNOWN")] = by.get(c.get("action", "UNKNOWN"), 0) + 1
        ok += 1 if c.get("ok", True) else 0
    rows = []
    for c in cases:
        atts = "<br/>".join(f"<code>{a}</code>" for a in (c.get("attachments") or []))
        rows.append(
            f"<tr><td>{c.get('name')}</td><td>{c.get('action')}</td><td>{'✅' if c.get('ok', True) else '❌'}</td><td><code>{c.get('output')}</code></td><td>{atts}</td></tr>"
        )
    html = f"""<!doctype html><meta charset="utf-8">
<title>Smart Mail Agent — 離線報告</title>
<style>body{{font-family:system-ui,Roboto,"PingFang TC","Microsoft JhengHei",sans-serif;padding:24px}}
table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:8px}}th{{background:#f6f8fa;text-align:left}}
code{{background:#f3f3f3;padding:2px 4px;border-radius:4px}}</style>
<h1>Smart Mail Agent — 離線 Demo 報告</h1>
<p>根目錄：<code>{root}</code>　產生時間：{dt.datetime.now():%Y-%m-%d %H:%M:%S}</p>
<p>案例數：{len(cases)}　成功：{ok}/{len(cases)}　各動作：{" 、".join(f"{k}:{v}" for k, v in by.items())}</p>
<table><thead><tr><th>name</th><th>action</th><th>ok</th><th>output</th><th>attachments</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>"""
    out = reports / "offline_demo_report.html"
    out.write_text(html, encoding="utf-8")
    print("[REPORT]", out)


if __name__ == "__main__":
    main()
