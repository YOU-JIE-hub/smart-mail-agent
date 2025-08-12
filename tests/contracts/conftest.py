import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def _ensure_matrix():
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    env = os.environ.copy()
    env.update({"OFFLINE": "1", "PYTHONPATH": str(src)})
    msum = root / "data" / "output" / "matrix" / "matrix_summary.json"
    if not msum.exists():
        subprocess.run(
            [sys.executable, str(root / "tools" / "run_actions_matrix.py")],
            check=True,
            cwd=str(root),
            env=env,
            text=True,
        )
    assert msum.exists(), "matrix_summary.json 不存在"
    return msum
