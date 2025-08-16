#!/usr/bin/env python3
# 檔案位置：tools/dev_runner.py
# 模組用途：一鍵執行 flake8 + pytest；失敗時顯示第一個錯誤並產生 PROJECT_STATUS.md

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT).returncode


def main():
    v = ROOT / ".venv" / "bin"
    flake8 = str(v / "flake8") if (v / "flake8").exists() else "flake8"
    pytest = str(v / "pytest") if (v / "pytest").exists() else "pytest"
    py = str(v / "python") if (v / "python").exists() else sys.executable

    rc = run([flake8, "."])
    if rc != 0:
        sys.exit(rc)

    rc = run([pytest, "-q"])
    if rc != 0:
        print("\n[test] 顯示第一個失敗的詳細訊息…\n")
        run([pytest, "-x", "-vv"])
        sys.exit(1)

    print("\n[info] 產生 PROJECT_STATUS.md…")
    run([py, "tools/project_catalog.py"])


if __name__ == "__main__":
    main()
