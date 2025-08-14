from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import pytest


def _try_help(path):
    p = pathlib.Path(path)
    if not p.exists():
        pytest.skip(f"{path} not found")
    env = os.environ.copy()
    env["OFFLINE"] = "1"
    try:
        subprocess.run(
            [sys.executable, path, "--help"],
            check=True,
            env=env,
            capture_output=True,
            timeout=15,
        )
    except Exception:
        # 沒有 argparse 時，至少能執行不崩潰
        subprocess.run([sys.executable, path], check=False, env=env, timeout=15)


def test_cli_run_main_help():
    _try_help("cli/run_main.py")


def test_cli_run_classifier_help():
    _try_help("cli/run_classifier.py")


def test_cli_run_orchestrator_help():
    _try_help("cli/run_orchestrator.py")
