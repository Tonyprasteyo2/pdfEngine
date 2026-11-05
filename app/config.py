from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "simrs-pdf-service"
    app_env: str = "production"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_version: str = "ga tau"

    api_key: str = "CHANGE_THIS"

    pdf_max_upload_mb: int = 50
    pdf_max_files: int = 30
    pdf_max_pages: int = 500
    pdf_request_timeout: int = 120

    pdf_storage_root: str = "storage"
    pdf_temp_dir: str = "storage/working"
    pdf_output_dir: str = "storage/output"
    pdf_input_dir: str = "storage/input"
    pdf_log_dir: str = "storage/logs"

    pdf_engine_primary: str = "pypdf"
    pdf_engine_fallback: str = "pymupdf,ghostscript,qpdf"

    pdf_cleanup_enabled: bool = True
    pdf_retention_minutes: int = 60

    log_level: str = "INFO"

    @property
    def max_upload_bytes(self) -> int:
        return self.pdf_max_upload_mb * 1024 * 1024

    @property
    def fallback_engines(self) -> List[str]:
        return [e.strip() for e in self.pdf_engine_fallback.split(",") if e.strip()]

    @property
    def storage_root_path(self) -> Path:
        return Path(self.pdf_storage_root)

    def ensure_dirs(self) -> None:
        for d in [
            self.pdf_input_dir,
            self.pdf_temp_dir,
            self.pdf_output_dir,
            self.pdf_log_dir,
        ]:
            Path(d).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
