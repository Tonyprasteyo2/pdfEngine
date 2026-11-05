from datetime import datetime
from typing import Any, Dict, Optional

from app.models.pdf_models import JobStatus
from app.utils.files import generate_job_id


class JobService:
    """In-memory job store. Can be replaced with Redis later."""

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create(self, operation: str) -> str:
        job_id = generate_job_id()
        self._jobs[job_id] = {
            "job_id": job_id,
            "operation": operation,
            "status": JobStatus.QUEUED,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "engine": None,
            "attempt": None,
            "pages": None,
            "output_path": None,
            "error": None,
            "attempts": [],
        }
        return job_id

    def update(self, job_id: str, **kwargs) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(kwargs)

    def set_status(self, job_id: str, status: JobStatus) -> None:
        self.update(job_id, status=status)
        if status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            self.update(job_id, finished_at=datetime.utcnow().isoformat() + "Z")

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def delete(self, job_id: str) -> bool:
        return self._jobs.pop(job_id, None) is not None


job_service = JobService()
