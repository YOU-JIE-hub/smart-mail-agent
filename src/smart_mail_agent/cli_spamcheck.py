#!/usr/bin/env python3
from __future__ import annotations
from smart_mail_agent.cli.sma_spamcheck import _score, build_parser, main
__all__ = ["_score", "build_parser", "main"]
def _run() -> int:
    return int(main() or 0)
if __name__ == "__main__":
    raise SystemExit(_run())
