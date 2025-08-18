from __future__ import annotations

import os
import pathlib

import pytest


def _load_env_file(fp: pathlib.Path) -> None:
    if not fp.exists():
        return
    for raw in fp.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if k and v and k not in os.environ:
            os.environ[k] = v


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_env() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    env = root / ".env"
    env_example = root / ".env.example"
    _load_env_file(env_example)
    _load_env_file(env)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "online: tests requiring network or external services"
    )
    config.addinivalue_line(
        "markers", "contracts: contract tests for outputs and schemas"
    )
    config.addinivalue_line("markers", "slow: slow tests")
