#!/usr/bin/env python3
from __future__ import annotations

# 為舊匯入相容：把公用符號 re-export 出來（不動 loader / sys.modules）
from smart_mail_agent.cli.sma_spamcheck import *  # noqa: F401,F403

# 為 python -m / runpy 相容：直接委派到真正 main()
def _run() -> int:
    from smart_mail_agent.cli.sma_spamcheck import main as _main
    return int(_main() or 0)

if __name__ == "__main__":
    raise SystemExit(_run())
