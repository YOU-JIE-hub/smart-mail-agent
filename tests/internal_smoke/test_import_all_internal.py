from __future__ import annotations
import importlib
import pkgutil
from pathlib import Path
import pytest

PKG = "smart_mail_agent"
BASE = Path("src") / PKG

if not BASE.exists():
    pytest.skip("internal package not found", allow_module_level=True)

# 這些模組在離線環境或缺少 heavy 依賴時應跳過（transformers/torch 等）
SKIP_CONTAINS = (
    ".spam.ml_spam_classifier",
    ".features.spam.ml_spam_classifier",
    ".features.spam.inference_classifier",
    ".spam.spam_llm_filter",
    ".spam.pipeline",
)

modules: list[str] = []
for mod in pkgutil.walk_packages([str(BASE)], prefix=f"{PKG}."):
    name = mod.name
    if any(x in name for x in SKIP_CONTAINS):
        continue
    modules.append(name)

@pytest.mark.parametrize("mod", modules)
def test_import_module(mod: str) -> None:
    importlib.import_module(mod)
