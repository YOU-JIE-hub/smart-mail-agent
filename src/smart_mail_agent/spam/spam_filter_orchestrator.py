# Shim: 舊介面 `SpamFilterOrchestrator` 轉向 Offline 版本，維持測試與舊程式相容
try:
    from .orchestrator_offline import (  # type: ignore
        SpamFilterOrchestratorOffline as SpamFilterOrchestrator,
        Thresholds,
        orchestrate,
        _main,
    )
except Exception as e:  # 極端 fallback（幾乎用不到）
    raise ImportError(f"Failed to load offline orchestrator: {e}")

__all__ = ["SpamFilterOrchestrator", "Thresholds", "orchestrate", "_main"]
