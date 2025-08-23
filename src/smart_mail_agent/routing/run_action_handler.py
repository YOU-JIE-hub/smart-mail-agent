from __future__ import annotations
from typing import Any, Dict, List
from .action_handler import main as _main, handle as handle, _attachment_risks as _attachment_risks

def main(argv: List[str] | None = None) -> int:
    return _main(argv)
