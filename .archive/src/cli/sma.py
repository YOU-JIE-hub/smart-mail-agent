from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Any

from spam.pipeline import analyze
from spam.rules import load_rules


def _read_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _read_eml(p: Path) -> dict[str, Any]:
    # 超輕量 .eml 解析：抓 From/Subject 與全文；附件略過（非關鍵）
    sender, subject = "", ""
    content_lines: list[str] = []
    for line in p.read_text(errors="ignore", encoding="utf-8").splitlines():
        if line.lower().startswith("from:"):
            sender = line.split(":", 1)[1].strip()
        elif line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
        else:
            content_lines.append(line)
    return {
        "sender": sender,
        "subject": subject,
        "content": "\n".join(content_lines),
        "attachments": [],
    }


def spam_scan(inbox: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for ext in ("*.json", "*.eml"):
        for f in inbox.rglob(ext):
            try:
                email = _read_json(f) if f.suffix.lower() == ".json" else _read_eml(f)
                res = analyze(email)
                rows.append({"file": str(f.relative_to(inbox)), **res})
            except Exception as e:
                rows.append(
                    {
                        "file": str(f.relative_to(inbox)),
                        "label": "error",
                        "score": 0,
                        "reasons": [str(e)],
                        "subject": "",
                    }
                )
    # 輸出 CSV / JSON / HTML
    json_path = out_dir / "spam_scan.json"
    csv_path = out_dir / "spam_scan.csv"
    html_path = out_dir / "spam_scan.html"

    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["file", "label", "score", "subject", "reasons"])
        for r in rows:
            w.writerow(
                [
                    r.get("file", ""),
                    r.get("label", ""),
                    r.get("score", ""),
                    r.get("subject", ""),
                    " | ".join(r.get("reasons", [])),
                ]
            )

    # HTML 簡表
    table_rows = []
    for r in rows:
        reasons = " | ".join(html.escape(x) for x in r.get("reasons", []))
        table_rows.append(
            f"<tr><td>{html.escape(r.get('file', ''))}</td><td>{html.escape(str(r.get('label', '')))}</td><td>{int(r.get('score', 0))}</td><td>{html.escape(r.get('subject', ''))}</td><td>{reasons}</td></tr>"
        )
    html_doc = (
        "<!doctype html><meta charset='utf-8'><title>Spam Scan Report</title>"
        "<style>body{font-family:system-ui,Segoe UI,Arial} table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:6px} th{background:#fafafa;text-align:left}</style>"
        "<h2>Spam Scan Report</h2>"
        f"<p>Total: {len(rows)}</p>"
        "<table><tr><th>File</th><th>Label</th><th>Score</th><th>Subject</th><th>Reasons</th></tr>" + "".join(table_rows) + "</table>"
    )
    html_path.write_text(html_doc, encoding="utf-8")
    return {
        "json": str(json_path),
        "csv": str(csv_path),
        "html": str(html_path),
        "count": len(rows),
    }


def main():
    ap = argparse.ArgumentParser(prog="sma")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("spam-scan", help="批量掃描 inbox 並輸出 CSV/JSON/HTML 報告")
    s.add_argument("--inbox", default="data/inbox", help="來源目錄（預設 data/inbox）")
    s.add_argument("--out", default="reports", help="報告輸出目錄（預設 reports）")
    s.add_argument("--reload", action="store_true", help="執行前強制重載規則")
    args = ap.parse_args()

    if args.cmd == "spam-scan":
        if args.reload:
            load_rules(force=True)
        inbox = Path(args.inbox)
        outd = Path(args.out)
        res = spam_scan(inbox, outd)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
