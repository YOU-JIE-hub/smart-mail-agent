from __future__ import annotations
import sys
import types
import pathlib
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT / "src"

# 確保搜尋路徑
for p in (ROOT, SRC):
    ps = str(p)
    if ps not in sys.path:
        sys.path.insert(0, ps)

def _ensure_pkg_namespace(name: str, paths: list[pathlib.Path]) -> None:
    """
    若找不到實體套件，才建立 shim；shim 會帶 __path__ 讓其為套件。
    若已被注入成「無 __path__ 的普通模組」，而實體目錄存在，則移除讓 import 走檔案系統。
    """
    spec = importlib.util.find_spec(name)
    real_dirs = [str(p) for p in paths if p.exists()]
    # 若 sys.modules 內已有普通模組但我們有真實目錄，清掉讓後續 import 用到實體套件
    m = sys.modules.get(name)
    if m is not None and not hasattr(m, "__path__") and real_dirs:
        sys.modules.pop(name, None)
        spec = importlib.util.find_spec(name)  # 重新探測

    if spec is None and real_dirs:
        # 建 namespace-shim（是「套件」）
        pkg = types.ModuleType(name)
        pkg.__path__ = real_dirs  # 讓其被視為 package
        sys.modules[name] = pkg

# 僅在需要時建立 modules 的 namespace（指向 ./modules 與 ./src/modules）
_ensure_pkg_namespace("modules", [ROOT / "modules", SRC / "modules"])
