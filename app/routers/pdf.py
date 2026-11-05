from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models.pdf_models import JobStatus, JobStatusResponse, ValidateResponse
from app.services.job_service import job_service
from app.services.pdf_service import PDFService
from app.utils.files import cleanup_job, ensure_job_dirs
from app.utils.security import sanitize_filename, validate_api_key

router = APIRouter(prefix="/pdf", tags=["PDF"])
pdf_service = PDFService()
settings = get_settings()


@router.post("/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(...),
    _: None = Depends(validate_api_key),
):
    if not files:
        raise HTTPException(
            400,
            detail={"success": False, "code": "NO_FILES", "message": "Tidak ada file."},
        )

    if len(files) > settings.pdf_max_files:
        raise HTTPException(
            400,
            detail={
                "success": False,
                "code": "TOO_MANY_FILES",
                "message": f"Maksimal {settings.pdf_max_files} file.",
            },
        )

    job_id = pdf_service.create_merge_job()
    dirs = ensure_job_dirs(job_id)
    saved_paths: List[Path] = []
    original_names: List[str] = []

    try:
        for i, upload in enumerate(files):
            safe_name = sanitize_filename(upload.filename or f"file_{i}.pdf")
            dest = dirs["input"] / f"{i:03d}_{safe_name}"
            content = await upload.read()
            if len(content) > settings.max_upload_bytes:
                raise HTTPException(
                    400,
                    detail={
                        "success": False,
                        "code": "FILE_TOO_LARGE",
                        "message": f"File {safe_name} melebihi batas {settings.pdf_max_upload_mb}MB",
                    },
                )
            dest.write_bytes(content)
            saved_paths.append(dest)
            original_names.append(safe_name)

        result = pdf_service.process_merge(job_id, saved_paths, original_names)

        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=422, detail=result)

    except HTTPException:
        raise
    except Exception:
        job_service.set_status(job_id, JobStatus.FAILED)
        raise HTTPException(
            500,
            detail={
                "success": False,
                "job_id": job_id,
                "code": "INTERNAL_ERROR",
                "message": "Terjadi kesalahan internal.",
            },
        )


@router.post("/validate", response_model=ValidateResponse)
async def validate_pdf(
    file: UploadFile = File(...),
    _: None = Depends(validate_api_key),
):
    job_id = job_service.create("validate")
    dirs = ensure_job_dirs(job_id)
    safe_name = sanitize_filename(file.filename or "check.pdf")
    dest = dirs["input"] / safe_name
    content = await file.read()
    dest.write_bytes(content)
    result = pdf_service.validate_pdf(dest)
    return result


@router.post("/repair")
async def repair_pdf(
    file: UploadFile = File(...),
    _: None = Depends(validate_api_key),
):
    job_id = job_service.create("repair")
    dirs = ensure_job_dirs(job_id)
    safe_name = sanitize_filename(file.filename or "repair.pdf")
    dest = dirs["input"] / safe_name
    content = await file.read()
    dest.write_bytes(content)
    result = pdf_service.repair_pdf(job_id, dest)
    if not result.get("success"):
        raise HTTPException(422, detail=result)
    return result


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, _: None = Depends(validate_api_key)):
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(
            404,
            detail={"success": False, "code": "JOB_NOT_FOUND", "message": "Job tidak ditemukan."},
        )
    return JobStatusResponse(
        success=True,
        job_id=job_id,
        status=job["status"],
        operation=job.get("operation"),
        engine=job.get("engine"),
        attempt=job.get("attempt"),
        pages=job.get("pages"),
        created_at=job.get("created_at"),
        finished_at=job.get("finished_at"),
    )


@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str, _: None = Depends(validate_api_key)):
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(404, detail={"success": False, "code": "JOB_NOT_FOUND"})
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            409,
            detail={
                "success": False,
                "code": "JOB_NOT_READY",
                "message": f"Job status: {job['status']}",
            },
        )
    output = job.get("output_path")
    if not output or not Path(output).exists():
        raise HTTPException(404, detail={"success": False, "code": "RESULT_NOT_FOUND"})
    return FileResponse(
        path=output,
        media_type="application/pdf",
        filename="merged.pdf",
        headers={"Content-Disposition": 'attachment; filename="merged.pdf"'},
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, _: None = Depends(validate_api_key)):
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(404, detail={"success": False, "code": "JOB_NOT_FOUND"})
    cleanup_job(job_id, keep_output=False)
    job_service.delete(job_id)
    return {"success": True, "job_id": job_id, "message": "Job dihapus."}
