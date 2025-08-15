#!/usr/bin/env python3
import pathlib
import runpy
import sys

root = pathlib.Path(__file__).resolve().parents[1]
candidates = [
    root / ".dev" / "run_actions_matrix.py",  # 你現在的實際位置
    root / "scripts" / "dev" / "run_actions_matrix.py",  # 舊位置，保相容
]
for p in candidates:
    if p.exists():
        sys.argv[0] = str(p)
        runpy.run_path(str(p), run_name="__main__")
        raise SystemExit(0)
raise SystemExit("compat shim: run_actions_matrix.py not found under .dev/ or scripts/dev/")
