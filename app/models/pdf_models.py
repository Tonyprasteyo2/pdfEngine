from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EngineAttempt(BaseModel):
    engine: str
    status: str
    error: Optional[str] = None
    duration: Optional[float] = None


class FailedFile(BaseModel):
    index: int
    filename: str
    reason: str


class MergeSuccessResponse(BaseModel):
    success: bool = True
    job_id: str
    operation: str = "merge"
    engine: str
    attempt: int
    fallback_used: bool
    pages: int
    output_size: int
    filename: str = "merged.pdf"


class MergeErrorResponse(BaseModel):
    success: bool = False
    job_id: str
    operation: str = "merge"
    code: str
    message: str
    failed_files: List[FailedFile] = Field(default_factory=list)
    attempts: List[EngineAttempt] = Field(default_factory=list)


class JobStatusResponse(BaseModel):
    success: bool = True
    job_id: str
    status: JobStatus
    operation: Optional[str] = None
    engine: Optional[str] = None
    attempt: Optional[int] = None
    pages: Optional[int] = None
    message: Optional[str] = None
    created_at: Optional[str] = None
    finished_at: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    engines: Dict[str, bool]


class ValidateResponse(BaseModel):
    success: bool
    valid: bool
    pages: Optional[int] = None
    file_size: Optional[int] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
