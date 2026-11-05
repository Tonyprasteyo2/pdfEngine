from fastapi import APIRouter

from app.config import get_settings
from app.engines import get_engine_status
from app.models.pdf_models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    engines = get_engine_status()
    available = sum(1 for v in engines.values() if v)
    status = "ok" if available >= 1 else "down"
    if available < len(engines) and available >= 1:
        status = "degraded"
    return HealthResponse(
        status=status,
        service=settings.app_name,
        version=settings.app_version,
        engines=engines,
    )
