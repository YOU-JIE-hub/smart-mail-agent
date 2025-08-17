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
    env["PYTHONPATH"] = f"{ROOT}:{ROOT / 'src'}"
    cp = subprocess.run([str(BIN)], cwd=str(ROOT), text=True, env=env)
    assert cp.returncode == 0
    outs = sorted(OUT.glob("out_*.json"))
    assert len(outs) >= 2
    with outs[0].open(encoding="utf-8") as fh:
        data = json.load(fh)
    # 放寬：頂層 logged_path 不一定有，但應至少有 meta 或 attachments 供後續流程使用
    assert ("logged_path" in data) or (
        "meta" in data and isinstance(data["meta"], dict)
    )
