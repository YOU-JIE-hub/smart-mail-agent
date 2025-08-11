#!/usr/bin/env python3
from __future__ import annotations

import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

DB_DEFAULT = "data/users.db"
TABLE = "users"


@dataclass
class UserRow:
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


def _ensure_db(db: str) -> None:
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as c:
        c.execute(
            f"""CREATE TABLE IF NOT EXISTS {TABLE}(
            email TEXT PRIMARY KEY, name TEXT, phone TEXT, address TEXT)"""
        )
        c.commit()


def _get(db: str, email: str) -> Optional[UserRow]:
    with sqlite3.connect(db) as c:
        cur = c.cursor()
        cur.execute(f"SELECT email,name,phone,address FROM {TABLE} WHERE email=?", (email,))
        r = cur.fetchone()
        return UserRow(*r) if r else None


def _insert(db: str, row: UserRow) -> None:
    with sqlite3.connect(db) as c:
        c.execute(
            f"INSERT INTO {TABLE}(email,name,phone,address) VALUES(?,?,?,?)",
            (row.email, row.name, row.phone, row.address),
        )
        c.commit()


def _update(db: str, email: str, updates: Dict[str, Any]) -> None:
    if not updates:
        return
    cols = ", ".join(f"{k}=?" for k in updates.keys())
    vals = list(updates.values()) + [email]
    with sqlite3.connect(db) as c:
        c.execute(f"UPDATE {TABLE} SET {cols} WHERE email=?", vals)
        c.commit()


# 內容解析（字串/字典都吃）
_R_PHONE = re.compile(r"(?:09\d{8})")
_R_ADDR = re.compile(r"(?:地址)[：:]?\s*([^\s，。；]+)")
_R_NAME = re.compile(r"(?:姓名|名字)[：:]?\s*([^\s，。；]{2,})")
_R_TO = re.compile(r"(?:改為|更新為|變更為)[：:]?\s*([^\s，。；]+)")


def _parse(content: Any) -> Dict[str, Optional[str]]:
    if isinstance(content, dict):
        return {
            "name": content.get("name"),
            "phone": content.get("phone"),
            "address": content.get("address"),
        }
    t = (content or "").strip()
    to = _R_TO.findall(t)
    if not t:
        return {"name": None, "phone": None, "address": None}

    phone = next((s for s in to if re.fullmatch(r"09\d{8}", s)), None)
    if not phone:
        m = _R_PHONE.search(t)
        phone = m.group(0) if m else None
    addr = None
    m = _R_ADDR.search(t)
    addr = m.group(1) if m else None
    if not addr:
        addr = next((s for s in to if not re.fullmatch(r"09\d{8}", s)), None)
    name = None
    m = _R_NAME.search(t)
    name = m.group(1) if m else None
    return {"name": name, "phone": phone, "address": addr}


def update_user_info(email: str, content: Any, *, db_path: str = DB_DEFAULT) -> Dict[str, Any]:
    _ensure_db(db_path)
    before = _get(db_path, email)
    before_dict = asdict(before) if before else None
    parsed = _parse(content)
    if not any(parsed.values()):
        return {
            "ok": True,
            "updated": False,
            "updated_fields": [],
            "before": before_dict,
            "after": before_dict,
        }
    if before is None:
        row = UserRow(email=email, **parsed)
        _insert(db_path, row)
        return {
            "ok": True,
            "updated": True,
            "updated_fields": [k for k, v in parsed.items() if v is not None],
            "before": None,
            "after": asdict(row),
        }
    cur = asdict(before)

    to_update = {}
    updated = []
    for k in ("name", "phone", "address"):
        nv = parsed.get(k)
        if nv is not None and nv != cur.get(k):
            to_update[k] = nv
            updated.append(k)
    if not updated:
        return {"ok": True, "updated": False, "updated_fields": [], "before": cur, "after": cur}
    _update(db_path, email, to_update)
    after = _get(db_path, email)
    return {
        "ok": True,
        "updated": True,
        "updated_fields": updated,
        "before": cur,
        "after": asdict(after) if after else None,
    }


__all__ = ["update_user_info"]
