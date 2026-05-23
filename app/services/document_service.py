import base64
import subprocess
import tempfile
from pathlib import Path
from docxtpl import DocxTemplate
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    TemplateNotFoundException,
    GenerationException
)
from app.services.template_service import template_service
from app.models.documents import OutputFormat

class DocumentService:

    def _get_template_path(self, template_id: str) -> Path:
        return template_service._get_template_path(template_id)

    def _render_docx(self, template_path: Path, data: dict, output_path: Path) -> None:
        try:
            doc = DocxTemplate(template_path)
            doc.render(data)
            doc.save(output_path)
            logger.info(f"Documento generado: {output_path.name}")
        except Exception as e:
            raise GenerationException(f"Error al renderizar plantilla: {str(e)}")

    def _convert_to_pdf(self, docx_path: Path, output_dir: Path) -> Path:
        try:
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(output_dir),
                    str(docx_path)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                raise GenerationException(f"LibreOffice error: {result.stderr}")

            pdf_path = output_dir / (docx_path.stem + ".pdf")
            if not pdf_path.exists():
                raise GenerationException("El PDF no se generó correctamente")

            return pdf_path
        except subprocess.TimeoutExpired:
            raise GenerationException("Tiempo de conversión a PDF agotado")
        except GenerationException:
            raise
        except Exception as e:
            raise GenerationException(f"Error en conversión PDF: {str(e)}")

    async def generate(
        self,
        template_id: str,
        data: dict,
        output_format: OutputFormat,
        filename: str = None
    ) -> dict:
        template_path = self._get_template_path(template_id)
        base_filename = filename or f"documento_{template_id[:8]}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docx_output = tmp_path / f"{base_filename}.docx"

            self._render_docx(template_path, data, docx_output)

            if output_format == OutputFormat.docx:
                content = docx_output.read_bytes()
                return {
                    "filename": docx_output.name,
                    "output_format": "docx",
                    "size_kb": round(len(content) / 1024, 2),
                    "base64_content": base64.b64encode(content).decode(),
                    "download_url": None
                }

            elif output_format == OutputFormat.pdf:
                pdf_path = self._convert_to_pdf(docx_output, tmp_path)
                content = pdf_path.read_bytes()
                return {
                    "filename": pdf_path.name,
                    "output_format": "pdf",
                    "size_kb": round(len(content) / 1024, 2),
                    "base64_content": base64.b64encode(content).decode(),
                    "download_url": None
                }

            elif output_format == OutputFormat.base64:
                content = docx_output.read_bytes()
                return {
                    "filename": docx_output.name,
                    "output_format": "base64",
                    "size_kb": round(len(content) / 1024, 2),
                    "base64_content": base64.b64encode(content).decode(),
                    "download_url": None
                }

document_service = DocumentService()