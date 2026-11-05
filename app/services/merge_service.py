import time
from pathlib import Path
from typing import Any, Dict, List

from app.config import get_settings
from app.engines import get_engine
from app.models.pdf_models import EngineAttempt, FailedFile, JobStatus
from app.services.job_service import job_service
from app.services.repair_service import PDFRepairService
from app.utils.files import ensure_job_dirs
from app.utils.logging import log_job, logger
from app.validators.pdf_validator import PDFValidator


class PDFOrchestrator:
    """
    Multi-engine PDF merge with automatic fallback.
    Order: pypdf → PyMuPDF normalize + merge → Ghostscript → qpdf
    """

    def __init__(self):
        self.validator = PDFValidator()
        self.repair = PDFRepairService()
        self.settings = get_settings()

    def merge(
        self,
        job_id: str,
        input_files: List[Path],
        original_filenames: List[str],
    ) -> Dict[str, Any]:
        start = time.time()
        dirs = ensure_job_dirs(job_id)
        job_service.set_status(job_id, JobStatus.PROCESSING)

        attempts: List[EngineAttempt] = []
        failed_files: List[FailedFile] = []

        # 1. Validate all inputs
        valid_files: List[Path] = []

        for idx, (path, name) in enumerate(zip(input_files, original_filenames)):
            ok, reason, details = self.validator.validate_file(
                path, max_size=self.settings.max_upload_bytes
            )
            if not ok:
                failed_files.append(FailedFile(index=idx, filename=name, reason=reason))
                log_job(job_id, "merge", "input_invalid", file=name, reason=reason)
            else:
                valid_files.append(path)

        if not valid_files:
            result = {
                "success": False,
                "job_id": job_id,
                "operation": "merge",
                "code": "PDF_INPUT_INVALID",
                "message": "Semua file input tidak valid.",
                "failed_files": [f.model_dump() for f in failed_files],
                "attempts": [],
            }
            job_service.update(job_id, status=JobStatus.FAILED, error=result)
            return result

        if failed_files:
            log_job(job_id, "merge", "partial_input", valid=len(valid_files), invalid=len(failed_files))

        # 2. Fallback strategy
        strategies = self._build_strategies(valid_files)

        for attempt_num, strategy in enumerate(strategies, start=1):
            engine_name = strategy["engine"]
            files_to_merge = strategy["files"]
            action = strategy.get("action", "merge")

            eng = get_engine(engine_name)
            if not eng:
                attempts.append(EngineAttempt(engine=engine_name, status="skipped", error="not available"))
                continue

            t0 = time.time()
            try:
                output_path = dirs["output"] / "merged.pdf"
                if output_path.exists():
                    output_path.unlink()

                log_job(job_id, "merge", "attempt", engine=engine_name, attempt=attempt_num, action=action)

                if action == "normalize_then_merge":
                    normalized = []
                    for i, f in enumerate(files_to_merge):
                        out_n = dirs["normalized"] / f"norm_{i:03d}.pdf"
                        eng.normalize(f, out_n)
                        normalized.append(out_n)
                    files_to_merge = normalized
                    merge_eng = get_engine("pypdf") or get_engine("pymupdf") or eng
                    merge_eng.merge(files_to_merge, output_path)
                elif action == "repair_then_merge":
                    repaired = []
                    for i, f in enumerate(files_to_merge):
                        out_r = dirs["repaired"] / f"rep_{i:03d}.pdf"
                        eng.repair(f, out_r)
                        repaired.append(out_r)
                    files_to_merge = repaired
                    merge_eng = get_engine("pypdf") or get_engine("pymupdf") or eng
                    merge_eng.merge(files_to_merge, output_path)
                else:
                    eng.merge(files_to_merge, output_path)

                # Validate output
                ok, msg, details = self.validator.validate_output(output_path, expected_min_pages=1)
                duration = time.time() - t0

                if ok:
                    pages = details.get("pages") or 0
                    size = output_path.stat().st_size
                    attempts.append(
                        EngineAttempt(engine=engine_name, status="success", duration=round(duration, 3))
                    )
                    log_job(
                        job_id,
                        "merge",
                        "success",
                        engine=engine_name,
                        attempt=attempt_num,
                        pages=pages,
                        duration=duration,
                        output_size=size,
                    )
                    job_service.update(
                        job_id,
                        status=JobStatus.COMPLETED,
                        engine=engine_name,
                        attempt=attempt_num,
                        pages=pages,
                        output_path=str(output_path),
                        attempts=[a.model_dump() for a in attempts],
                    )
                    return {
                        "success": True,
                        "job_id": job_id,
                        "operation": "merge",
                        "engine": engine_name,
                        "attempt": attempt_num,
                        "fallback_used": attempt_num > 1,
                        "pages": pages,
                        "output_size": size,
                        "filename": "merged.pdf",
                    }
                else:
                    attempts.append(
                        EngineAttempt(
                            engine=engine_name,
                            status="failed",
                            error=f"Output validation failed: {msg}",
                            duration=round(duration, 3),
                        )
                    )
                    log_job(job_id, "merge", "output_invalid", engine=engine_name, reason=msg)

            except Exception as e:
                duration = time.time() - t0
                err_msg = str(e)[:300]
                attempts.append(
                    EngineAttempt(
                        engine=engine_name,
                        status="failed",
                        error=err_msg,
                        duration=round(duration, 3),
                    )
                )
                log_job(job_id, "merge", "failed", engine=engine_name, attempt=attempt_num, error=err_msg)
                logger.exception(f"[{job_id}] Engine {engine_name} failed")

        # All strategies failed
        total_duration = time.time() - start
        result = {
            "success": False,
            "job_id": job_id,
            "operation": "merge",
            "code": "PDF_MERGE_FAILED",
            "message": "PDF tidak dapat diproses menggunakan engine yang tersedia.",
            "failed_files": [f.model_dump() for f in failed_files],
            "attempts": [a.model_dump() for a in attempts],
        }
        job_service.update(job_id, status=JobStatus.FAILED, error=result, attempts=result["attempts"])
        log_job(job_id, "merge", "all_failed", duration=total_duration)
        return result

    def _build_strategies(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Ordered strategies from lightest to heaviest."""
        strategies = []

        if get_engine("pypdf"):
            strategies.append({"engine": "pypdf", "files": files, "action": "merge"})

        if get_engine("pymupdf"):
            strategies.append({"engine": "pymupdf", "files": files, "action": "normalize_then_merge"})
            strategies.append({"engine": "pymupdf", "files": files, "action": "merge"})

        if get_engine("ghostscript"):
            strategies.append({"engine": "ghostscript", "files": files, "action": "normalize_then_merge"})
            strategies.append({"engine": "ghostscript", "files": files, "action": "merge"})

        if get_engine("qpdf"):
            strategies.append({"engine": "qpdf", "files": files, "action": "repair_then_merge"})
            strategies.append({"engine": "qpdf", "files": files, "action": "merge"})

        return strategies
