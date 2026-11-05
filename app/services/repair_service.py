from pathlib import Path

from app.engines import get_engine
from app.utils.logging import logger


class PDFRepairService:
    def normalize(self, input_path: Path, output_path: Path, preferred_engine: str = "pymupdf") -> Path:
        engines_order = [preferred_engine, "pymupdf", "ghostscript", "qpdf", "pypdf"]
        last_error = None
        for name in engines_order:
            eng = get_engine(name)
            if not eng:
                continue
            try:
                result = eng.normalize(input_path, output_path)
                if result.exists() and result.stat().st_size > 0:
                    return result
            except Exception as e:
                last_error = e
                logger.debug(f"Normalize with {name} failed: {e}")
        raise RuntimeError(f"All normalize engines failed. Last: {last_error}")

    def repair(self, input_path: Path, output_path: Path, preferred_engine: str = "qpdf") -> Path:
        engines_order = [preferred_engine, "qpdf", "ghostscript", "pymupdf"]
        last_error = None
        for name in engines_order:
            eng = get_engine(name)
            if not eng:
                continue
            try:
                result = eng.repair(input_path, output_path)
                if result.exists() and result.stat().st_size > 0:
                    return result
            except Exception as e:
                last_error = e
                logger.debug(f"Repair with {name} failed: {e}")
        raise RuntimeError(f"All repair engines failed. Last: {last_error}")
