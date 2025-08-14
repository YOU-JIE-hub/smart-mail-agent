"""
Compatibility proxy so tests using `import utils.*` resolve to `src.utils.*`.
"""

from importlib import import_module as _im

# Re-export logger symbols for direct import: from utils import logger, get_logger
try:
    _logger_mod = _im("src.utils.logger")
    logger = getattr(_logger_mod, "logger")
    get_logger = getattr(_logger_mod, "get_logger")
except Exception:  # 極端情況退回同目錄 logger.py（若存在）
    from .logger import get_logger, logger  # type: ignore

__all__ = ["logger", "get_logger"]
