import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from app.engines.base import PDFEngine
from app.utils.logging import logger


class QPDFEngine(PDFEngine):
    name = "qpdf"

    def is_available(self) -> bool:
        return shutil.which("qpdf") is not None

    def merge(self, files: List[Path], output: Path) -> Path:
        cmd = ["qpdf", "--empty", "--pages"]
        for f in files:
            cmd.extend([str(f), "1-z"])
        cmd.extend(["--", str(output)])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if result.returncode != 0:
            raise RuntimeError(f"qpdf merge failed: {result.stderr[:500]}")
        return output

    def validate(self, file: Path) -> bool:
        try:
            cmd = ["qpdf", "--check", str(file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"qpdf validate failed: {e}")
            return False

    def normalize(self, file: Path, output: Path) -> Path:
        cmd = ["qpdf", "--linearize", str(file), str(output)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            cmd = ["qpdf", str(file), str(output)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise RuntimeError(f"qpdf normalize failed: {result.stderr[:500]}")
        return output

    def repair(self, file: Path, output: Path) -> Path:
        cmd = ["qpdf", "--object-streams=generate", str(file), str(output)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"qpdf repair failed: {result.stderr[:500]}")
        return output

    def get_page_count(self, file: Path) -> Optional[int]:
        try:
            cmd = ["qpdf", "--show-npages", str(file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass
        return None
