import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from app.engines.base import PDFEngine
from app.utils.logging import logger


class GhostscriptEngine(PDFEngine):
    name = "ghostscript"

    def is_available(self) -> bool:
        return shutil.which("gs") is not None or shutil.which("gswin64c") is not None

    def _gs_cmd(self) -> str:
        return shutil.which("gs") or shutil.which("gswin64c") or "gs"

    def merge(self, files: List[Path], output: Path) -> Path:
        cmd = [
            self._gs_cmd(),
            "-dBATCH",
            "-dNOPAUSE",
            "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-sOutputFile={output}",
        ]
        cmd.extend(str(f) for f in files)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Ghostscript merge failed: {result.stderr[:500]}")
        return output

    def validate(self, file: Path) -> bool:
        try:
            cmd = [
                self._gs_cmd(),
                "-dBATCH",
                "-dNOPAUSE",
                "-dSAFER",
                "-sDEVICE=nullpage",
                str(file),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"gs validate failed: {e}")
            return False

    def normalize(self, file: Path, output: Path) -> Path:
        cmd = [
            self._gs_cmd(),
            "-dBATCH",
            "-dNOPAUSE",
            "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/prepress",
            f"-sOutputFile={output}",
            str(file),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.returncode != 0:
            raise RuntimeError(f"Ghostscript normalize failed: {result.stderr[:500]}")
        return output

    def repair(self, file: Path, output: Path) -> Path:
        return self.normalize(file, output)

    def get_page_count(self, file: Path) -> Optional[int]:
        return None
