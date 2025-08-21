#!/usr/bin/env python3
from __future__ import annotations
from smart_mail_agent.cli.sma_spamcheck import _heuristics, _rules_score, _score, build_parser, main

__all__ = ["_heuristics", "_rules_score", "_score", "build_parser", "main"]
if __name__ == "__main__":
    raise SystemExit(main())
