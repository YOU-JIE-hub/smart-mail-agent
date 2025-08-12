#!/usr/bin/env python3
from pathlib import Path

JUNK = ["=0.9.0", "=13.0.0", "DELETE", "FROM", "SELECT"]


def main():
    root = Path(".").resolve()
    removed = []
    for name in JUNK:
        p = root / name
        if p.exists():
            p.unlink()
            removed.append(name)
    print("[CLEAN] removed:", removed or "nothing")


if __name__ == "__main__":
    main()
