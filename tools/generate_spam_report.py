from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data" / "output" / "spam_demo.json"


def main():
    if not DATA.exists():
        print("[WARN] spam_demo.json 不存在，先跑: python tools/run_spam_demo.py")
        return
    obj = json.loads(DATA.read_text(encoding="utf-8"))
    rows = obj.get("rows", [])
    ok = sum(1 for r in rows if r["label"] == "legit")
    sp = sum(1 for r in rows if r["label"] == "spam")
    su = sum(1 for r in rows if r["label"] == "suspect")
    html = ["<html><head><meta charset='utf-8'><title>Spam Report</title></head><body>"]
    html.append(f"<h2>Spam Demo Report</h2><p>TS = {obj.get('ts')}</p>")
    html.append(f"<p>legit={ok} , suspect={su} , spam={sp}</p>")
    html.append("<table border='1' cellspacing='0' cellpadding='6'>")
    html.append(
        "<tr><th>name</th><th>label</th><th>score</th><th>hits</th><th>components</th></tr>"
    )
    for r in rows:
        comp = r["rationale"]
        hits = ", ".join(h["rule"] for h in comp.get("hits", [])) or "-"
        components = f"rule={comp['rule_score']}, link={comp['link_score']}, header={comp['header_score']}, attach={comp['attach_score']}"
        html.append(
            f"<tr><td>{r['name']}</td><td>{r['label']}</td><td>{r['score']}</td><td>{hits}</td><td>{components}</td></tr>"
        )
    html.append("</table></body></html>")
    out = OUT / "spam_report.html"
    out.write_text("\n".join(html), encoding="utf-8")
    print("[REPORT]", out)


if __name__ == "__main__":
    main()
