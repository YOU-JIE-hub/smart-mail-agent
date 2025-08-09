#!/usr/bin/env python3
# pytest 全域設定：自動載入 .env 檔案

import os

from dotenv import load_dotenv


def pytest_configure():
    env_path = os.path.join(os.path.dirname(__file__), "../.env")
    load_dotenv(dotenv_path=env_path, override=True)
