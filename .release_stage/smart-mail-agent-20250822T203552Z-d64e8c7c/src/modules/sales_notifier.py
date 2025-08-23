from __future__ import annotations
from typing import Iterable, Optional, Any, List

__all__ = ["notify_sales"]

def notify_sales(subject: str,
                 message: str,
                 recipients: Optional[Iterable[str]] = None,
                 channel: str = "email",
                 **kwargs: Any) -> bool:
    """
    Minimal shim for tests:
    - 接受彈性參數（subject/message/recipients/channel/**kwargs）
    - 不對外發送、無副作用
    - 回傳 True 代表已「通知/排程」(offline OK)
    """
    # 型別/可迭代性保險（有些測試會觸碰這些欄位）
    _ = (subject, message, channel, kwargs)
    if recipients is not None:
        _recips: List[str] = list(recipients)  # 強制展開驗證可迭代
        _ = _recips  # 靜態分析器消音
    return True

if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--subject", default="")
    p.add_argument("--message", default="")
    p.add_argument("--to", action="append", dest="recipients")
    p.add_argument("--channel", default="email")
    args = p.parse_args()
    ok = notify_sales(args.subject, args.message, recipients=args.recipients, channel=args.channel)
    print(json.dumps({"ok": ok, "recipients": args.recipients or [], "channel": args.channel}, ensure_ascii=False))
