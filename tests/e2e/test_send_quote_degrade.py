import builtins
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def break_reportlab_import():
    real = builtins.__import__

    def fake(name, *a, **k):
        if name.startswith("reportlab"):
            raise ImportError("blocked reportlab for test")
        return real(name, *a, **k)

    builtins.__import__ = fake
    try:
        yield
    finally:
        builtins.__import__ = real


def test_send_quote_degrade():
    from action_handler import handle

    with break_reportlab_import():
        res = handle(
            {
                "predicted_label": "業務接洽或報價",
                "subject": "需要報價",
                "content": "請評估交期",
                "sender": "buyer2@example.com",
            }
        )
    atts = res.get("attachments") or []
    assert len(atts) >= 1
    p = Path(atts[0])
    assert p.exists() and p.stat().st_size > 0
