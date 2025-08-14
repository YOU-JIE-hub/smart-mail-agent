import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import stats_collector as sc

TEST_DB_PATH = Path("data/stats.db")


@pytest.fixture(autouse=True)
def clean_db():
    """每次測試前清空 stats.db"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_init_stats_db():
    """測試初始化資料庫與資料表建立"""
    assert not TEST_DB_PATH.exists()
    sc.init_stats_db()
    assert TEST_DB_PATH.exists()

    # 確認 stats 資料表存在
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats'")
    assert cursor.fetchone()[0] == "stats"
    conn.close()


def test_increment_counter():
    """測試插入一筆統計資料"""
    sc.init_stats_db()
    sc.increment_counter("業務接洽", 1.23)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT label, elapsed FROM stats")
    row = cursor.fetchone()
    assert row[0] == "業務接洽"
    assert abs(row[1] - 1.23) < 1e-3
    conn.close()


def test_cli_init_and_insert():
    """使用 CLI 執行 init 與 insert"""
    result = subprocess.run(["python3", "src/stats_collector.py", "--init"], capture_output=True, text=True)
    assert "資料庫初始化完成" in result.stdout

    result2 = subprocess.run(
        ["python3", "src/stats_collector.py", "--label", "投訴", "--elapsed", "0.56"],
        capture_output=True,
        text=True,
    )
    assert "已新增統計紀錄" in result2.stdout

    # 驗證寫入成功
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT label, elapsed FROM stats ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    assert row[0] == "投訴"
    assert abs(row[1] - 0.56) < 1e-3
    conn.close()
