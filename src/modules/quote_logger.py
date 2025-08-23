#!/usr/bin/env python3
# 檔案位置: src/modules/quote_logger.py
# 模組用途: 報價紀錄資料庫（SQLite）初始化與寫入；提供 ensure_db_exists() 與 log_quote()。
# 兼容策略: 新版表為 quotes；同時維持舊版表 quote_records（client_name/package/pdf_path），以通過既有測試。

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

__all__ = ["ensure_db_exists", "log_quote", "QuoteRecord"]

_DB_TABLE = "quotes"
_LEGACY_TABLE = "quote_records"

_logger = logging.getLogger("modules.quote_logger")
if not _logger.handlers:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s [quote_logger] %(levelname)s: %(message)s",
    )

@dataclass(frozen=True)
class QuoteRecord:
    """
    報價記錄資料模型（新版標準）
    參數:
        subject: 主旨（必要）
        content: 內容摘要（必要）
        sender: 發送者/客戶識別（舊介面對應 client_name）
        package: 方案名稱
        price: 金額
        meta: 其他欄位（JSON 字串存入）
    """
    subject: str
    content: str
    sender: Optional[str] = None
    package: Optional[str] = None
    price: Optional[float] = None
    meta: Optional[Mapping[str, Any]] = None

def _connect(db_path: str) -> sqlite3.Connection:
    path = Path(db_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def _ensure_legacy_tables(conn: sqlite3.Connection) -> None:
    # 新版標準表
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_DB_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject    TEXT NOT NULL,
            content    TEXT NOT NULL,
            sender     TEXT,
            package    TEXT,
            price      REAL,
            meta       TEXT,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{_DB_TABLE}_created_at ON {_DB_TABLE}(created_at);"
    )
    # 舊版相容表（測試用）
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {_LEGACY_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            package     TEXT,
            pdf_path    TEXT,
            created_at  TEXT NOT NULL
        );
        """
    )
    conn.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{_LEGACY_TABLE}_client ON {_LEGACY_TABLE}(client_name);"
    )

def ensure_db_exists(db_path: str) -> None:
    """
    建立資料庫與資料表（新版 quotes + 舊版 quote_records）
    參數:
        db_path: SQLite 檔案路徑
    """
    with _connect(db_path) as conn:
        _ensure_legacy_tables(conn)
        conn.commit()
    _logger.info("資料庫初始化完成: %s", db_path)

def _coerce_record(record: Mapping[str, Any]) -> QuoteRecord:
    """
    寬鬆鍵名相容：允許 subject/title、content/body/message、sender/from/email
    """
    subj = record.get("subject") or record.get("title")
    cont = record.get("content") or record.get("body") or record.get("message")
    if not subj or not isinstance(subj, str):
        raise ValueError("subject 為必要字串欄位")
    if not cont or not isinstance(cont, str):
        raise ValueError("content 為必要字串欄位")

    sender = record.get("sender") or record.get("from") or record.get("email")
    package = record.get("package")
    price = record.get("price")
    if price is not None:
        try:
            price = float(price)  # type: ignore[assignment]
        except Exception:
            raise ValueError("price 必須可轉為數值")

    known = {"subject", "title", "content", "body", "message", "sender", "from", "email", "package", "price"}
    meta_dict = {k: v for k, v in record.items() if k not in known} or None

    return QuoteRecord(
        subject=str(subj).strip(),
        content=str(cont).strip(),
        sender=(str(sender).strip() if sender else None),
        package=(str(package).strip() if package else None),
        price=price,  # 已在上方轉換
        meta=meta_dict,
    )

def _insert_row(db_path: str, rec: QuoteRecord) -> int:
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        _ensure_legacy_tables(conn)  # 雙保險
        cur = conn.cursor()
        # 寫入新版標準表
        cur.execute(
            f"""
            INSERT INTO {_DB_TABLE} (subject, content, sender, package, price, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.subject,
                rec.content,
                rec.sender,
                rec.package,
                rec.price,
                json.dumps(rec.meta, ensure_ascii=False) if rec.meta is not None else None,
                created_at,
            ),
        )
        rowid = int(cur.lastrowid)

        # 同步寫入舊版相容表（供舊測試查詢）
        # 映射規則：
        #  client_name <- rec.sender 或 meta.client_name
        #  package     <- rec.package
        #  pdf_path    <- meta.pdf_path（若存在）
        legacy_client = (rec.sender or (rec.meta or {}).get("client_name")) if rec else None
        legacy_pdf = (rec.meta or {}).get("pdf_path") if rec and rec.meta else None
        cur.execute(
            f"""
            INSERT INTO {_LEGACY_TABLE} (client_name, package, pdf_path, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (legacy_client, rec.package, legacy_pdf, created_at),
        )

        conn.commit()
        return rowid

def log_quote(
    db_path: Optional[str] = None,
    record: Optional[Mapping[str, Any]] = None,
    *,
    client_name: Optional[str] = None,
    package: Optional[str] = None,
    pdf_path: Optional[str] = None,
) -> int:
    """
    寫入單筆報價（支援新舊兩種介面）

    新介面:
        log_quote(db_path="data/quotes.db", record={"subject": "...", "content": "...", ...})

    舊介面（向後相容，符合舊測試習慣）:
        log_quote(client_name="ACME", package="標準", pdf_path="/path/to.pdf", db_path="data/quotes.db")
    """
    if db_path is None:
        raise ValueError("db_path 為必要參數")
    ensure_db_exists(db_path)

    # 新介面
    if record is not None:
        rec = _coerce_record(record)
        rowid = _insert_row(db_path, rec)
        _logger.info("寫入完成 id=%s subject=%s", rowid, rec.subject)
        return rowid

    # 舊介面：轉成標準紀錄，並在 meta 放入 legacy 欄位
    if client_name or package or pdf_path:
        subject = f"Quotation for {client_name}" if client_name else "Quotation"
        content_parts = []
        if package:
            content_parts.append(f"package={package}")
        if pdf_path:
            content_parts.append(f"pdf={pdf_path}")
        content = "; ".join(content_parts) or "quote logged"

        legacy_rec = {
            "subject": subject,
            "content": content,
            "sender": client_name,
            "package": package,
            "meta": {"pdf_path": pdf_path, "compat": "legacy", "client_name": client_name},
        }
        rec = _coerce_record(legacy_rec)
        rowid = _insert_row(db_path, rec)
        _logger.info("寫入完成 id=%s subject=%s", rowid, rec.subject)
        return rowid

    raise ValueError("請提供 record 或舊介面參數（client_name/package/pdf_path）")

# ----------------------- CLI -----------------------

def _add_db_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument("--db", default=os.environ.get("QUOTE_DB", "data/quotes.db"), help="SQLite 檔案路徑")

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Quote logger CLI")
    _add_db_arg(p)  # 全域 --db
    sub = p.add_subparsers(dest="cmd", required=True)

    # 子命令也加上 --db，允許「init --db ...」與「--db ... init」兩種寫法
    p_init = sub.add_parser("init", help="建立資料庫/資料表（含相容表）")
    _add_db_arg(p_init)
    p_init.set_defaults(func=lambda args: ensure_db_exists(args.db))

    p_add = sub.add_parser("add", help="新增一筆報價（同時寫入新版與相容表）")
    _add_db_arg(p_add)
    p_add.add_argument("--subject", required=True)
    p_add.add_argument("--content", required=True)
    p_add.add_argument("--sender", default=None)
    p_add.add_argument("--package", default=None)
    p_add.add_argument("--price", default=None, type=str)
    p_add.add_argument("--meta", default=None, help="JSON 字串，會存入 meta 欄位")

    def _do_add(args: argparse.Namespace) -> None:
        meta: Optional[Mapping[str, Any]] = None
        if args.meta:
            meta = json.loads(args.meta)
        rec = {
            "subject": args.subject,
            "content": args.content,
            "sender": args.sender,
            "package": args.package,
            "price": args.price,
            "meta": meta,
        }
        rowid = log_quote(args.db, record=rec)
        print(rowid)

    p_add.set_defaults(func=_do_add)
    return p

def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as e:
        _logger.error("執行失敗: %s", e)
        return 1

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
