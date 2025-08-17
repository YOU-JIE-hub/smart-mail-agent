#!/usr/bin/env python3
# 檔案位置: tests/conftest.py
# 模組用途: 測試全域設定與標記；提供 --online 旗標與 OFFLINE 環境參數整合
# 兼容 pytest 8+，移除舊的 py.path 介面警告

from __future__ import annotations

import os
from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    新增 --online 旗標：顯式要求執行需要對外連線/SMTP 的測試。
    預設值由 OFFLINE 環境變數推導（OFFLINE=0 代表允許 online）。
    """
    parser.addoption(
        "--online",
        action="store_true",
        default=None,
        help="run tests that require network/SMTP. Default derives from OFFLINE env.",
    )


def _should_run_online(config: pytest.Config) -> bool:
    opt = config.getoption("--online")
    if opt is not None:
        return bool(opt)
    offline_env = os.environ.get("OFFLINE", "1").strip().lower()
    return offline_env in ("0", "false", "no")


def pytest_configure(config: pytest.Config) -> None:
    """
    註冊標記並保存是否允許執行 online 測試的布林旗標於 config。
    """
    config.addinivalue_line("markers", "online: mark tests that require network/SMTP")
    config._run_online = _should_run_online(config)  # type: ignore[attr-defined]


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """
    若未允許 online，則跳過所有 @pytest.mark.online 的測試。
    """
    run_online = getattr(config, "_run_online", False)
    skip_online = pytest.mark.skip(
        reason="skipping @online tests (use --online or OFFLINE=0)"
    )
    if not run_online:
        for item in items:
            if "online" in item.keywords:
                item.add_marker(skip_online)


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool:  # type: ignore[override]
    """
    以 pathlib.Path 介面判斷忽略目錄（pytest 8+）
    在離線情境下忽略 tests/online 目錄（若存在），作為標記以外的保險。
    """
    run_online = getattr(config, "_run_online", False)
    if not run_online:
        try:
            if any(part == "online" for part in collection_path.parts):
                return True
        except Exception:
            return False
    return False
