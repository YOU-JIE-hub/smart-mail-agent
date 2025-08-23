from __future__ import annotations
import argparse, sys
from smart_mail_agent.observability.stats_collector import DB_PATH, init_stats_db, increment_counter

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true")
    p.add_argument("--label")
    p.add_argument("--elapsed", type=float)
    ns = p.parse_args(argv)
    if ns.init:
        init_stats_db()
        print("資料庫初始化完成")
        return 0
    if ns.label is not None and ns.elapsed is not None:
        increment_counter(ns.label, ns.elapsed)
        print("已新增統計紀錄")
        return 0
    p.print_help()
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
