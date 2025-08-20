#!/usr/bin/env python3
from __future__ import annotations
from smart_mail_agent.cli.sma_spamcheck import *  # re-export for compatibility
def _run() -> int:
    from smart_mail_agent.cli.sma_spamcheck import main as _main
    return int(_main() or 0)
if __name__ == "__main__":
    raise SystemExit(_run())
