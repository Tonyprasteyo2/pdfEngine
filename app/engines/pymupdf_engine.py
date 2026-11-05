from pathlib import Path
from typing import List, Optional

from app.engines.base import PDFEngine
from app.utils.logging import logger


class PyMuPDFEngine(PDFEngine):
    name = "pymupdf"

    def is_available(self) -> bool:
        try:
            import fitz  # noqa: F401
            return True
        except ImportError:
            return False

    def merge(self, files: List[Path], output: Path) -> Path:
        import fitz
        result = fitz.open()
        try:
            for f in files:
                with fitz.open(str(f)) as src:
                    result.insert_pdf(src)
            result.save(str(output), garbage=4, deflate=True, clean=True)
        finally:
            result.close()
        return output

    def validate(self, file: Path) -> bool:
        try:
            import fitz
            with fitz.open(str(file)) as doc:
                if doc.page_count == 0:
                    return False
                _ = doc.load_page(0)
                return True
        except Exception as e:
            logger.debug(f"pymupdf validate failed: {e}")
            return False

    def get_page_count(self, file: Path) -> Optional[int]:
        try:
            import fitz
            with fitz.open(str(file)) as doc:
                return doc.page_count
        except Exception:
            return None

    def normalize(self, file: Path, output: Path) -> Path:
        import fitz
        with fitz.open(str(file)) as doc:
            doc.save(str(output), garbage=4, deflate=True, clean=True)
        return output

    def repair(self, file: Path, output: Path) -> Path:
        return self.normalize(file, output)
