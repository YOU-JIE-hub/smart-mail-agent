# Re-export WITHOUT shadowing submodules
from . import logger as logger          # module object, allows importlib.reload(logger)
from .logger import get_logger          # helper function
from . import pdf_safe as pdf_safe
from .pdf_safe import _escape_pdf_text, write_pdf_or_txt, _write_minimal_pdf

__all__ = [
    "logger",
    "get_logger",
    "pdf_safe",
    "_escape_pdf_text",
    "write_pdf_or_txt",
    "_write_minimal_pdf",
]
