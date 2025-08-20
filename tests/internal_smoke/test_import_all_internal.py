from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

import pytest

PKG = "smart_mail_agent"
BASE = Path("src") / PKG
if not BASE.exists():
    pytest.skip("internal package not found", allow_module_level=True)

SKIP_CONTAINS = (
    ".spam.ml_spam_classifier",
    ".features.spam.ml_spam_classifier",
    ".features.spam.inference_classifier",
    ".spam.pipeline",
    ".spam.spam_llm_filter",
)

mods: list[str] = []
for finder in pkgutil.walk_packages([str(BASE)], prefix=f"{PKG}."):
    name = finder.name
    if any(x in name for x in SKIP_CONTAINS):
        continue
    mods.append(name)


@pytest.mark.parametrize("mod", mods)
def test_import_module(mod: str) -> None:
    importlib.import_module(mod)
mods = [
    "smart_mail_agent.cli_spamcheck",
    "smart_mail_agent.cli.sma",
    "smart_mail_agent.observability.log_writer",
    "smart_mail_agent.utils.templater",
    "smart_mail_agent.ingestion.email_processor",
    "smart_mail_agent.routing.action_handler",
]

import os, pytest
@pytest.mark.parametrize("mod", [m for m in mods if not (os.getenv("OFFLINE") == "1" and m=="skip_mod")])
def test_import_module(mod: str) -> None:
    import importlib; importlib.import_module(mod)
