#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sma", description="Smart Mail Agent CLI")
    p.add_argument("-V", "--version", action="store_true", help="show version and exit")
    return p

def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # 短路：--help 由 argparse 處理，避免子行程遞迴
    if any(a in ("-h", "--help") for a in argv):
        build_parser().print_help()
        return 0
    ns, rest = build_parser().parse_known_args(argv)
    if ns.version:
        print("smart-mail-agent")
        return 0
    # 其餘交給舊的 module runner
    return subprocess.call([sys.executable, "-m", "smart_mail_agent", *rest])

if __name__ == "__main__":
    raise SystemExit(main())
