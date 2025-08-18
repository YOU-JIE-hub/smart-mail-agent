from __future__ import annotations
# 直接 re-export orchestrator_offline 的實作，避免舊路徑 import 失敗
from .orchestrator_offline import (
    Thresholds,
    SpamFilterOrchestratorOffline,
    orchestrate,
    _main,
)
