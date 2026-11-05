from pathlib import Path
from typing import List, Optional

from app.engines.base import PDFEngine
from app.utils.logging import logger


class PyPDFEngine(PDFEngine):
    name = "pypdf"

    def is_available(self) -> bool:
        try:
            import pypdf  
            return True
        except ImportError:
            return False

    def merge(self, files: List[Path], output: Path) -> Path:
        from pypdf import PdfReader, PdfWriter

        writer = PdfWriter()
        for f in files:
            reader = PdfReader(str(f), strict=False)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    pass
            for page in reader.pages:
                writer.add_page(page)
        with open(output, "wb") as fp:
            writer.write(fp)
        return output

    def validate(self, file: Path) -> bool:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file), strict=False)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return False
            n = len(reader.pages)
            return n > 0
        except Exception as e:
            logger.debug(f"pypdf validate failed: {e}")
            return False

    def get_page_count(self, file: Path) -> Optional[int]:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file), strict=False)
            return len(reader.pages)
        except Exception:
            return None

    def normalize(self, file: Path, output: Path) -> Path:
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(str(file), strict=False)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output, "wb") as fp:
            writer.write(fp)
        return output
