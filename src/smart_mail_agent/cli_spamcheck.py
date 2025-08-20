#!/usr/bin/env python3
# 位置：src/smart_mail_agent/cli_spamcheck.py
# 目的：兼容入口（import 與 -m/RunModule 執行），統一委派到 smart_mail_agent.cli.sma_spamcheck
from __future__ import annotations
import sys as _sys, importlib as _im

# 供 import 相容：將當前模組映射到真正實作
_mod = _im.import_module("smart_mail_agent.cli.sma_spamcheck")
_sys.modules[__name__] = _mod

# 供執行相容：被 runpy 以 __main__ 執行、或 python -m ... 時，直接跑真正 main()
if __name__ == "__main__":
    from smart_mail_agent.cli.sma_spamcheck import main as _main
    raise SystemExit(_main() or 0)
