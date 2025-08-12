#!/usr/bin/env python3
# 檔案位置：tools/run_actions_matrix.py
# 用途：一次觸發六大動作的「正常＋異常」案例矩陣，驗證回退與產物存在性

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _detect_root() -> Path:
    # 兼容以檔案執行與以 stdin/IDE 執行
    try:
        f = Path(__file__)
        if str(f) == "<stdin>":
            raise NameError
        return f.resolve().parents[1]
    except Exception:
        return Path.cwd()


ROOT = _detect_root()
SRC = ROOT / "src"
OUT = ROOT / "data" / "output" / "matrix"
OUT.mkdir(parents=True, exist_ok=True)


def _ensure_sys_path() -> None:
    # 同時加入 src 與 repo 根目錄，避免相對匯入問題
    for p in (SRC, ROOT):
        sp = str(p)
        if sp not in sys.path:
            sys.path.insert(0, sp)


def load_handle():
    _ensure_sys_path()
    try:
        from action_handler import handle

        return handle
    except ModuleNotFoundError:
        # 在某些結構下需要模組前綴
        from src.action_handler import handle  # type: ignore

        return handle


def _run_case(handle, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    os.environ.setdefault("OFFLINE", "1")
    res = handle(payload)
    outp = OUT / f"{name}.json"
    outp.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    attachments = []
    for ap in res.get("attachments", []) or []:
        p = Path(ap)
        attachments.append(
            {"path": str(p), "exists": p.exists(), "size": (p.stat().st_size if p.exists() else 0)}
        )
    return {
        "name": name,
        "action": res.get("action") or res.get("action_name"),
        "ok": res.get("ok", True),
        "attachments": attachments,
        "output": str(outp),
    }


def run_matrix() -> Dict[str, Any]:
    handle = load_handle()
    matrix: List[Dict[str, Any]] = []

    # 正常案例（六大動作）
    matrix.append(
        _run_case(
            handle,
            "ok_send_quote",
            {
                "predicted_label": "業務接洽或報價",
                "subject": "API 串接報價",
                "content": "請提供報價與交期",
                "sender": "buyer@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "ok_reply_support",
            {
                "predicted_label": "請求技術支援",
                "subject": "登入錯誤",
                "content": "顯示 500 需要排查",
                "sender": "user@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "ok_apply_info",
            {
                "predicted_label": "申請修改資訊",
                "subject": "更新聯絡方式",
                "content": "電話改為 0987xxxxxx",
                "sender": "alice@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "ok_reply_faq",
            {
                "predicted_label": "詢問流程或規則",
                "subject": "退貨流程",
                "content": "如何退貨？",
                "sender": "bob@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "ok_reply_apology",
            {
                "predicted_label": "投訴與抱怨",
                "subject": "體驗不佳",
                "content": "等待過久",
                "sender": "carol@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "ok_reply_general",
            {
                "predicted_label": "其他",
                "subject": "一般詢問",
                "content": "請問出貨時間",
                "sender": "eve@example.com",
            },
        )
    )

    # 邊界案例
    matrix.append(
        _run_case(
            handle,
            "edge_unknown_label",
            {
                "predicted_label": "未定義分類",
                "subject": "?",
                "content": "?",
                "sender": "x@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "edge_missing_sender",
            {"predicted_label": "其他", "subject": "no sender", "content": "hello"},
        )
    )
    matrix.append(
        _run_case(
            handle,
            "edge_empty_subject",
            {
                "predicted_label": "請求技術支援",
                "subject": "",
                "content": "錯誤代碼 123",
                "sender": "nosub@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "edge_empty_content",
            {
                "predicted_label": "詢問流程或規則",
                "subject": "流程",
                "content": "",
                "sender": "nocontent@example.com",
            },
        )
    )
    matrix.append(
        _run_case(
            handle,
            "edge_apply_no_diff",
            {
                "predicted_label": "申請修改資訊",
                "subject": "更新",
                "content": "您好",
                "sender": "z@example.com",
            },
        )
    )

    return {"cases": matrix, "outputs_dir": str(OUT)}


def main() -> None:
    summary = run_matrix()
    outp = OUT / "matrix_summary.json"
    outp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("完成。請回傳：", str(outp))


if __name__ == "__main__":
    main()
