from pathlib import Path
from typing import List

from app.config import get_settings
from app.services.job_service import job_service
from app.services.merge_service import PDFOrchestrator
from app.services.repair_service import PDFRepairService
from app.utils.files import ensure_job_dirs
from app.validators.pdf_validator import PDFValidator


class PDFService:
    def __init__(self):
        self.orchestrator = PDFOrchestrator()
        self.repair_service = PDFRepairService()
        self.validator = PDFValidator()
        self.settings = get_settings()

    def create_merge_job(self) -> str:
        return job_service.create("merge")

    def process_merge(
        self,
        job_id: str,
        saved_paths: List[Path],
        original_names: List[str],
    ) -> dict:
        return self.orchestrator.merge(job_id, saved_paths, original_names)

    def validate_pdf(self, path: Path) -> dict:
        ok, msg, details = self.validator.validate_file(path)
        return {
            "success": True,
            "valid": ok,
            "pages": details.get("pages"),
            "file_size": details.get("size"),
            "message": msg,
            "details": details,
        }

    def repair_pdf(self, job_id: str, input_path: Path) -> dict:
        dirs = ensure_job_dirs(job_id)
        output = dirs["output"] / "repaired.pdf"
        try:
            self.repair_service.repair(input_path, output)
            ok, msg, details = self.validator.validate_file(output)
            if ok:
                return {
                    "success": True,
                    "job_id": job_id,
                    "operation": "repair",
                    "pages": details.get("pages"),
                    "output_size": output.stat().st_size,
                    "filename": "repaired.pdf",
                }
            return {
                "success": False,
                "job_id": job_id,
                "code": "PDF_REPAIR_FAILED",
                "message": msg,
            }
        except Exception as e:
            return {
                "success": False,
                "job_id": job_id,
                "code": "PDF_REPAIR_FAILED",
                "message": str(e)[:200],
            }
