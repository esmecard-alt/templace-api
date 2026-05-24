import base64
import subprocess
import tempfile
import jinja2
import jinja2.exceptions
from jinja2 import Undefined
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


class SilentUndefined(Undefined):
    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""
    def __str__(self):
        return ""
    def __iter__(self):
        return iter([])
    def __bool__(self):
        return False


class DocumentService:

    def _get_template_path(self, template_id: str) -> Path:
        return template_service._get_template_path(template_id)

    def _validate_data(self, template_path: Path, data: dict) -> list[str]:
        try:
            doc = DocxTemplate(template_path)
            required_markers = doc.get_undeclared_template_variables()
            provided_keys = set(data.keys())
            missing = []
            for marker in sorted(required_markers):
                if marker not in provided_keys:
                    missing.append(marker)
            return missing
        except Exception:
            return []

    def _render_docx(self, template_path: Path, data: dict, output_path: Path, strict_mode: bool = True) -> None:
        if strict_mode:
            missing = self._validate_data(template_path, data)
            if missing:
                campos = ", ".join(f"'{m}'" for m in missing)
                raise GenerationException(
                    f"Faltan {len(missing)} campo(s) requerido(s) en los datos: {campos}"
                )
        try:
            doc = DocxTemplate(template_path)
            if strict_mode:
                doc.render(data)
            else:
                jinja_env = jinja2.Environment(undefined=SilentUndefined)
                doc.render(data, jinja_env=jinja_env)
            doc.save(output_path)
            logger.info(f"Documento generado ({'estricto' if strict_mode else 'tolerante'}): {output_path.name}")
        except jinja2.exceptions.UndefinedError as e:
            campo = str(e).replace("'", "").replace(" is undefined", "").strip()
            raise GenerationException(f"Campo requerido no encontrado en los datos: '{campo}'")
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
        filename: str = None,
        strict_mode: bool = True
    ) -> dict:
        template_path = self._get_template_path(template_id)
        base_filename = filename or f"documento_{template_id[:8]}"

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docx_output = tmp_path / f"{base_filename}.docx"

            self._render_docx(template_path, data, docx_output, strict_mode)

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