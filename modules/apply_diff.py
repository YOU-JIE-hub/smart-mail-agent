#!/usr/bin/env python3
# 檔案位置：modules/apply_diff.py
# 模組用途：比對並更新使用者資料庫（SQLite）。若無異動則不更新。
from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DB_DEFAULT = "data/users.db"
TABLE = "users"


@dataclass
class UserRow:
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


def _ensure_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                email   TEXT PRIMARY KEY,
                name    TEXT,
                phone   TEXT,
                address TEXT
            )
            """
        )
        conn.commit()


def _get_user(db_path: str, email: str) -> Optional[UserRow]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT email, name, phone, address FROM {TABLE} WHERE email = ?", (email,))
        row = cur.fetchone()
        if row:
            return UserRow(email=row[0], name=row[1], phone=row[2], address=row[3])
        return None


def _insert_user(db_path: str, row: UserRow) -> None:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {TABLE} (email, name, phone, address) VALUES (?,?,?,?)",
            (row.email, row.name, row.phone, row.address),
        )
        conn.commit()


def _update_user(db_path: str, email: str, updates: Dict[str, Any]) -> None:
    fields = []
    values = []
    for k, v in updates.items():
        if k == "email":
            continue
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        return
    values.append(email)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE {TABLE} SET {', '.join(fields)} WHERE email = ?", tuple(values))
        conn.commit()


def update_user_info(db_path: str, email: str, new_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    根據 email 對使用者資料進行「有差異才更新」：
    參數:
        db_path: SQLite 檔案路徑
        email:   目標使用者 email（作為主鍵）
        new_info: 欲更新欄位（name/phone/address）
    回傳:
        dict: { ok, updated(bool), updated_fields(list[str]), before(dict|None), after(dict) }
    """
    _ensure_db(db_path)
    before = _get_user(db_path, email)

    # 正規化輸入
    candidate = {
        "email": email,
        "name": new_info.get("name"),
        "phone": new_info.get("phone"),
        "address": new_info.get("address"),
    }

    if before is None:
        # 新增
        _insert_user(db_path, UserRow(**candidate))
        return {
            "ok": True,
            "updated": True,
            "updated_fields": ["name", "phone", "address"],
            "before": None,
            "after": candidate,
        }

    # 計算差異
    to_update: Dict[str, Any] = {}
    updated_fields = []
    before_dict = asdict(before)
    for k in ("name", "phone", "address"):
        nv = candidate.get(k)
        if nv is not None and nv != before_dict.get(k):
            to_update[k] = nv
            updated_fields.append(k)

    if not updated_fields:
        return {
            "ok": True,
            "updated": False,
            "updated_fields": [],
            "before": before_dict,
            "after": before_dict,
        }

    _update_user(db_path, email, to_update)
    after = _get_user(db_path, email)
    return {
        "ok": True,
        "updated": True,
        "updated_fields": updated_fields,
        "before": before_dict,
        "after": asdict(after) if after else candidate,
    }


__all__ = ["update_user_info"]
