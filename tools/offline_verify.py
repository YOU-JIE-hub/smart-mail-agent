#!/usr/bin/env python3
# 檔案位置：tools/offline_verify.py
# 模組用途：一鍵離線驗證（pytest -k "not online"）與六類動作 Demo 產物檢查

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "data" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def _ensure_sys_path() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def run_offline_tests() -> int:
    env = os.environ.copy()
    env["OFFLINE"] = "1"
    env["PYTHONPATH"] = str(SRC)
    cmd = ["pytest", "-q", "-k", "not online"]
    p = subprocess.run(cmd, cwd=str(ROOT), env=env, text=True)
    return p.returncode


def demo_actions() -> Dict[str, Any]:
    _ensure_sys_path()
    os.environ.setdefault("OFFLINE", "1")
    from action_handler import handle

    cases = [
        (
            "業務接洽或報價",
            {
                "subject": "API 串接報價",
                "content": "請提供報價與交期",
                "sender": "buyer@example.com",
            },
        ),
        (
            "請求技術支援",
            {"subject": "登入錯誤", "content": "顯示 500 需要排查", "sender": "user@example.com"},
        ),
        (
            "申請修改資訊",
            {
                "subject": "更新聯絡方式",
                "content": "電話改為 0987xxxxxx",
                "sender": "alice@example.com",
            },
        ),
        (
            "詢問流程或規則",
            {"subject": "退貨流程", "content": "不良品如何退貨？", "sender": "bob@example.com"},
        ),
        (
            "投訴與抱怨",
            {"subject": "體驗不佳", "content": "等待過久", "sender": "carol@example.com"},
        ),
        ("其他", {"subject": "一般詢問", "content": "請問出貨時間", "sender": "eve@example.com"}),
    ]
    results = {}
    for label, payload in cases:
        payload = dict(payload)
        payload["predicted_label"] = label
        res = handle(payload)
        # 逐案寫檔，便於你檢視
        out_path = OUT / f"demo_{res.get('action') or res.get('action_name','unknown')}.json"
        out_path.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        results[label] = {
            "action": res.get("action") or res.get("action_name"),
            "output": str(out_path),
        }
        # 若有附件路徑，檢查其存在性
        for ap in res.get("attachments", []) or []:
            apath = Path(ap)
            results[label].setdefault("attachments", []).append(
                {
                    "path": str(apath),
                    "exists": apath.exists(),
                    "size": apath.stat().st_size if apath.exists() else 0,
                }
            )
    # 總覽寫檔
    (OUT / "offline_verify_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results


def main() -> None:
    print("[VERIFY] 開始離線測試")
    code = run_offline_tests()
    print(f"[VERIFY] pytest -k 'not online' 結束，exit={code}")
    print("[VERIFY] 產出六類動作 Demo")
    summary = demo_actions()
    print("[VERIFY] 結果總覽：", json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
