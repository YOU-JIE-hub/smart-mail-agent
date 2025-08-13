# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys


def main() -> None:
    base = os.path.abspath(os.path.dirname(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)

    import action_handler as ah  # type: ignore

    os.environ.setdefault("OFFLINE", "1")

    patched = False
    try:
        from patches.handle_router_patch import handle as router_handle  # type: ignore

        ah.handle = router_handle
        patched = True
    except Exception:
        patched = False

    if not patched:
        try:
            from patches.handle_safe_patch import handle as safe_handle  # type: ignore

            ah.handle = safe_handle
        except Exception:
            pass

    from action_handler import main as action_main  # type: ignore

    action_main()


if __name__ == "__main__":
    main()
