import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from app.config import get_settings


def generate_job_id() -> str:
    now = datetime.utcnow()
    short = uuid.uuid4().hex[:6].upper()
    return f"PDF-{now.strftime('%Y%m%d')}-{short}"


def job_dirs(job_id: str) -> dict:
    settings = get_settings()
    root = settings.storage_root_path
    return {
        "input": root / "input" / job_id,
        "working": root / "working" / job_id,
        "normalized": root / "working" / job_id / "normalized",
        "repaired": root / "working" / job_id / "repaired",
        "temporary": root / "working" / job_id / "temporary",
        "output": root / "output" / job_id,
    }


def ensure_job_dirs(job_id: str) -> dict:
    dirs = job_dirs(job_id)
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def cleanup_job(job_id: str, keep_output: bool = True) -> None:
    settings = get_settings()
    if not settings.pdf_cleanup_enabled:
        return
    dirs = job_dirs(job_id)
    for key, path in dirs.items():
        if keep_output and key == "output":
            continue
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def list_files_ordered(directory: Path, pattern: str = "*.pdf") -> List[Path]:
    files = sorted(directory.glob(pattern), key=lambda p: p.name)
    return files
