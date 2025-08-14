#!/usr/bin/env python3
# 檔案位置: src/smart_mail_agent/cli/sma.py
import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, "-m", "smart_mail_agent", *sys.argv[1:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
