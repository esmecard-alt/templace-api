import uuid
import re
from pathlib import Path
from datetime import datetime
from docxtpl import DocxTemplate
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    TemplateNotFoundException,
    TemplateTooBigException,
    InvalidTemplateException
)

class TemplateService:

    def __init__(self):
        self.storage_dir = settings.TEMPLATES_DIR
        self.storage_dir.mkdir(exist_ok=True)

    def _get_template_path(self, template_id: str) -> Path:
        matches = list(self.storage_dir.glob(f"{template_id}_*"))
        if not matches:
            raise TemplateNotFoundException(template_id)
        return matches[0]

    def _extract_markers(self, path: Path) -> list[str]:
        try:
            doc = DocxTemplate(path)
            variables = doc.get_undeclared_template_variables()
            return sorted(list(variables))
        except Exception as e:
            raise InvalidTemplateException(str(e))

    async def save_template(self, filename: str, content: bytes) -> dict:
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.MAX_TEMPLATE_SIZE_MB:
            raise TemplateTooBigException(size_mb, settings.MAX_TEMPLATE_SIZE_MB)

        if not filename.endswith(".docx"):
            raise InvalidTemplateException("El archivo debe ser .docx")

        template_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ", "_")
        dest_path = self.storage_dir / f"{template_id}_{safe_filename}"

        dest_path.write_bytes(content)
        logger.info(f"Plantilla guardada: {dest_path.name}")

        markers = self._extract_markers(dest_path)
        size_kb = round(len(content) / 1024, 2)

        return {
            "template_id": template_id,
            "filename": filename,
            "size_kb": size_kb,
            "markers_detected": markers,
            "uploaded_at": datetime.utcnow()
        }

    async def get_template_preview(self, template_id: str) -> dict:
        path = self._get_template_path(template_id)
        markers = self._extract_markers(path)
        size_kb = round(path.stat().st_size / 1024, 2)

        return {
            "template_id": template_id,
            "filename": "_".join(path.name.split("_")[1:]),
            "markers": markers,
            "size_kb": size_kb
        }

    async def delete_template(self, template_id: str) -> None:
        path = self._get_template_path(template_id)
        path.unlink()
        logger.info(f"Plantilla eliminada: {template_id}")

    async def list_templates(self) -> list[dict]:
        templates = []
        for path in self.storage_dir.glob("*.docx"):
            parts = path.name.split("_", 1)
            if len(parts) == 2:
                template_id = parts[0]
                try:
                    markers = self._extract_markers(path)
                except Exception:
                    markers = []
                templates.append({
                    "template_id": template_id,
                    "filename": parts[1],
                    "size_kb": round(path.stat().st_size / 1024, 2),
                    "markers": markers
                })
        return templates

template_service = TemplateService()