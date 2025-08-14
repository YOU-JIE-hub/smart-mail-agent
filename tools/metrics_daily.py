#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


def _iter_logs(log_dir: Path) -> List[Path]:
    return sorted(log_dir.glob("sma-*.jsonl"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate JSONL logs to daily CSV metrics")
    ap.add_argument("--log-dir", default="logs")
    ap.add_argument("--out-dir", default="data/output/metrics")
    args = ap.parse_args()
    log_dir = Path(args.log_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = _iter_logs(log_dir)
    if not files:
        print("no logs found", file=sys.stderr)
        return 0

    metrics: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(
        lambda: defaultdict(lambda: {"count": 0, "ok": 0, "fail": 0, "dur_sum": 0, "dur_cnt": 0})
    )

    for fp in files:
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ev = obj.get("event") or {}
                ts = ev.get("ts") or ""
                day = ts[:10] if len(ts) >= 10 else "1970-01-01"
                intent = ev.get("intent") or "unknown"
                m = metrics[day][intent]
                m["count"] += 1
                if ev.get("ok") is True:
                    m["ok"] += 1
                elif ev.get("ok") is False:
                    m["fail"] += 1
                dur = ev.get("duration_ms")
                if isinstance(dur, int) and dur >= 0:
                    m["dur_sum"] += dur
                    m["dur_cnt"] += 1

    # output CSV per day
    for day, intents in metrics.items():
        ymd = day.replace("-", "")
        out = out_dir / f"metrics-{ymd}.csv"
        rows = ["date,intent,count,ok,fail,avg_duration_ms"]
        for intent, m in sorted(intents.items()):
            avg = (m["dur_sum"] / m["dur_cnt"]) if m["dur_cnt"] else 0
            rows.append(f"{day},{intent},{m[count]},{m[ok]},{m[fail]},{int(avg)}")
        out.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print(f"已輸出：{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
