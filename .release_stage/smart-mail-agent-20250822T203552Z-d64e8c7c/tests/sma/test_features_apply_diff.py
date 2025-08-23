import sqlite3, re
from pathlib import Path
import importlib
mod = importlib.import_module("smart_mail_agent.features.apply_diff")

def _init_db(p: Path):
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (email TEXT PRIMARY KEY, phone TEXT, address TEXT)")
    cur.execute("CREATE TABLE diff_log (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, 欄位 TEXT, 原值 TEXT, 新值 TEXT, created_at TEXT)")
    cur.execute("INSERT INTO users(email,phone,address) VALUES (?,?,?)", ("a@x","0911","A路1號"))
    conn.commit(); conn.close()

def test_extract_fields():
    t = "電話： 0922-334455\n地址: 台北市中正區仁愛路 1 段 1 號"
    f = mod.extract_fields(t)
    assert f["phone"].startswith("0922") and "台北" in f["address"]

def test_update_user_info(tmp_path):
    db = tmp_path/"u.db"; _init_db(db)
    # 無異動
    res1 = mod.update_user_info("a@x", "電話： 0911\n地址：A路1號", db_path=str(db))
    assert res1["status"]=="no_change"
    # 有異動
    res2 = mod.update_user_info("a@x", "電話： 0912\n地址：A路1號", db_path=str(db))
    assert res2["status"]=="updated" and "phone" in res2["changes"]
    # 不存在
    res3 = mod.update_user_info("b@x", "電話： 0900", db_path=str(db))
    assert res3["status"]=="not_found"
