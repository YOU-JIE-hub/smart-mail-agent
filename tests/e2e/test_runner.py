import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "bin" / "smarun"
OUT = ROOT / "data" / "output"


def test_runner_outputs():
    env = os.environ.copy()
    env["OFFLINE"] = env.get("OFFLINE", "1")
    env["PYTHONPATH"] = str(ROOT / "src")

    cp = subprocess.run([str(BIN)], cwd=str(ROOT), text=True, env=env)
    assert cp.returncode == 0

    outs = sorted(OUT.glob("out_*.json"))
    assert len(outs) >= 2

    with outs[0].open(encoding="utf-8") as fh:
        data = json.load(fh)
    assert "logged_path" in data
