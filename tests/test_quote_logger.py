#!/usr/bin/env python3
# 測試檔案位置：tests/test_quote_logger.py
# 測試用途：驗證 quote_logger 是否能正確寫入資料庫

import os
import sqlite3
import tempfile

import pytest

from modules.quote_logger import ensure_db_exists, log_quote


def test_log_quote_to_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    ensure_db_exists(db_path)

    # 執行寫入
    log_quote(client_name="test_client", package="基礎", pdf_path="/tmp/fake.pdf", db_path=db_path)

    # 驗證是否寫入成功
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quote_records WHERE client_name = ?", ("test_client",))
    row = cursor.fetchone()
    conn.close()
    os.remove(db_path)

    assert row is not None
