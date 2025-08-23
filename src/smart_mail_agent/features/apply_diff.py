from __future__ import annotations
import re, sqlite3
from typing import Dict, Optional

_phone_re = re.compile(r"(?:電話|手機)\D*([0-9\-]{3,})")
_addr_re  = re.compile(r"(?:地址)\D*([^\n\r]+)")

def extract_fields(text: str) -> Dict[str, Optional[str]]:
    phone = None; addr = None
    m = _phone_re.search(text or "")
    if m: phone = m.group(1).strip()
    m = _addr_re.search(text or "")
    if m: addr = m.group(1).strip()
    return {"phone": phone, "address": addr}

def update_user_info(email: str, text: str, db_path: str) -> Dict:
    fields = extract_fields(text)
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("SELECT phone, address FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if not row:
            return {"status":"not_found", "email": email}
        old_phone, old_addr = row
        changes = {}
        if fields["phone"] and fields["phone"] != old_phone:
            changes["phone"] = {"old": old_phone, "new": fields["phone"]}
        if fields["address"] and fields["address"] != old_addr:
            changes["address"] = {"old": old_addr, "new": fields["address"]}
        if not changes:
            return {"status":"no_change", "email": email}
        # apply
        new_phone = changes.get("phone",{}).get("new", old_phone)
        new_addr  = changes.get("address",{}).get("new", old_addr)
        cur.execute("UPDATE users SET phone=?, address=? WHERE email=?", (new_phone, new_addr, email))
        con.commit()
        return {"status":"updated", "email": email, "changes": changes}
    finally:
        con.close()
