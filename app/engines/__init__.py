from typing import Dict, Optional

from app.engines.base import PDFEngine
from app.engines.ghostscript_engine import GhostscriptEngine
from app.engines.pymupdf_engine import PyMuPDFEngine
from app.engines.pypdf_engine import PyPDFEngine
from app.engines.qpdf_engine import QPDFEngine


def get_all_engines() -> Dict[str, PDFEngine]:
    return {
        "pypdf": PyPDFEngine(),
        "pymupdf": PyMuPDFEngine(),
        "ghostscript": GhostscriptEngine(),
        "qpdf": QPDFEngine(),
    }


def get_available_engines() -> Dict[str, PDFEngine]:
    return {name: eng for name, eng in get_all_engines().items() if eng.is_available()}


def get_engine(name: str) -> Optional[PDFEngine]:
    engines = get_all_engines()
    eng = engines.get(name)
    if eng and eng.is_available():
        return eng
    return None


def get_engine_status() -> Dict[str, bool]:
    return {name: eng.is_available() for name, eng in get_all_engines().items()}
