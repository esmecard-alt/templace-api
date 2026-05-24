import base64
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
from app.services.excel_service import excel_service
from app.services.document_service import document_service
from app.models.documents import OutputFormat
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/generate-from-excel")
async def generate_from_excel(
    template_id: str = Form(...),
    excel_file: UploadFile = File(...),
    output_format: OutputFormat = Form(OutputFormat.docx),
    filename: Optional[str] = Form(None),
    strict_mode: bool = Form(False)
):
    if not excel_file.filename.endswith((".xlsx", ".xls")):
        from app.core.exceptions import InvalidTemplateException
        raise InvalidTemplateException("El archivo de datos debe ser .xlsx o .xls")

    excel_content = await excel_file.read()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        excel_path = tmp_path / excel_file.filename
        excel_path.write_bytes(excel_content)

        data = excel_service.excel_to_data(excel_path)
        logger.info(f"Excel procesado: {list(data.keys())}")

    result = await document_service.generate(
        template_id=template_id,
        data=data,
        output_format=output_format,
        filename=filename,
        strict_mode=strict_mode
    )

    if output_format == OutputFormat.base64:
        return {**result, "sheets_loaded": list(data.keys())}

    content = base64.b64decode(result["base64_content"])
    media_type = "application/pdf" if output_format == OutputFormat.pdf \
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={result['filename']}"
        }
    )