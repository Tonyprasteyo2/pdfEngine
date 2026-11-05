import re
from pathlib import Path
from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import get_settings


def sanitize_filename(filename: str) -> str:
    """Prevent path traversal and dangerous characters."""
    if not filename:
        return "unnamed.pdf"
    name = Path(filename).name
    name = re.sub(r"[^\w\.\-\(\) ]", "_", name)
    name = name.strip("._ ")
    if not name.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif")):
        name = f"{name}.pdf"
    if len(name) > 200:
        name = name[:200]
    return name or "unnamed.pdf"


def validate_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> None:
    settings = get_settings()
    if settings.app_env == "development" and (not settings.api_key or settings.api_key == "CHANGE_THIS"):
        return
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "code": "UNAUTHORIZED",
                "message": "Invalid or missing API key",
            },
        )


def is_safe_path(base: Path, target: Path) -> bool:
    try:
        base = base.resolve()
        target = target.resolve()
        return str(target).startswith(str(base))
    except Exception:
        return False
