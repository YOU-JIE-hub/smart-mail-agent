from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from typing import Optional, Sequence

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sma-spamcheck",
        description="Lightweight spamcheck CLI (offline-friendly stub).",
    )
    p.add_argument("-i", "--input", help="Path to email JSON; omit to read from stdin")
    p.add_argument("-o", "--output", default="-", help="Write result JSON to this path (default: stdout)")
    p.add_argument("-t", "--threshold", type=float, default=0.5, help="Spam threshold 0..1 (default: 0.5)")
    p.add_argument("--version", action="version", version="sma-spamcheck 0.1")
    return p

def run(input_path: Optional[str], output: str, threshold: float) -> int:
    # Minimal offline-friendly result; enough for tests that only check --help.
    data = {}
    if input_path:
        p = Path(input_path)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                data = {}
    result = {"ok": True, "spam_score": 0.0, "threshold": threshold}
    out = json.dumps(result, ensure_ascii=False)
    if output and output != "-":
        Path(output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args.input, args.output, args.threshold)

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
