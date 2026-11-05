from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.engines import get_available_engines
from app.utils.logging import logger


class PDFValidator:
    PDF_MAGIC = b"%PDF-"

    def validate_file(
        self,
        path: Path,
        max_size: Optional[int] = None,
        check_pages: bool = True,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        details: Dict[str, Any] = {}

        if not path.exists():
            return False, "File does not exist", details

        size = path.stat().st_size
        details["size"] = size
        if size == 0:
            return False, "Empty file", details
        if max_size and size > max_size:
            return False, f"File exceeds size limit ({size} > {max_size})", details

        try:
            with open(path, "rb") as f:
                header = f.read(8)
            if not header.startswith(self.PDF_MAGIC):
                return False, "Invalid PDF header (magic bytes)", details
        except Exception as e:
            return False, f"Cannot read file: {e}", details

        engines = get_available_engines()
        page_count = None
        opened = False

        for name, eng in engines.items():
            try:
                if eng.validate(path):
                    opened = True
                    page_count = eng.get_page_count(path)
                    details["validated_by"] = name
                    break
            except Exception:
                continue

        if not opened:
            return False, "Cannot open PDF with any available engine", details

        details["pages"] = page_count
        if check_pages and (page_count is None or page_count < 1):
            return False, "PDF has no readable pages", details

        return True, "OK", details

    def validate_output(
        self,
        path: Path,
        expected_min_pages: int = 1,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        ok, msg, details = self.validate_file(path, check_pages=True)
        if not ok:
            return False, msg, details
        pages = details.get("pages") or 0
        if pages < expected_min_pages:
            return False, f"Output page count too low ({pages} < {expected_min_pages})", details
        return True, "OK", details
